"""
Chromosome representation and constraint repair for Genetic Algorithm.
Encodes recovery decisions: backup generator dispatches, emergency line switches, and consumer curtailments.
"""

import random
from typing import Dict, List, Optional
from app.models.infrastructure import InfrastructureNetwork, ConsumerCategory, CriticalityLevel, OperationalStatus


class RecoveryChromosome:
    def __init__(
        self,
        generator_dispatch: Dict[str, float],
        line_switches: Dict[str, bool],
        consumer_curtailment: Dict[str, float],
    ):
        self.generator_dispatch = generator_dispatch       # bg_id -> MW dispatched [0.0, capacity]
        self.line_switches = line_switches                 # line_id -> True/False
        self.consumer_curtailment = consumer_curtailment   # cons_id -> fraction shed [0.0, 1.0]
        self.fitness: float = 0.0
        self.total_cost: float = float("inf")
        self.unserved_demand: float = 0.0
        self.critical_unserved: float = 0.0

    @classmethod
    def create_random(cls, network: InfrastructureNetwork, rng: random.Random) -> "RecoveryChromosome":
        """
        Creates a randomized valid candidate recovery chromosome.
        """
        # 1. Generator dispatch
        gen_dispatch = {}
        for bg in network.backup_generators:
            # Chance of activating generator
            if rng.random() > 0.4:
                # Random dispatch up to capacity
                gen_dispatch[bg.id] = round(rng.uniform(10.0, bg.capacity), 2)
            else:
                gen_dispatch[bg.id] = 0.0

        # 2. Line switches (particularly backup feeders and tie lines)
        line_switches = {}
        for line in network.transmission_lines:
            if line.operational_status == OperationalStatus.FAILED:
                line_switches[line.id] = False
            elif line.is_backup_feeder:
                # Randomly activate backup feeders
                line_switches[line.id] = rng.random() > 0.5
            else:
                # Keep normal lines active unless failed
                line_switches[line.id] = True

        # 3. Consumer curtailment (load shedding)
        curtailments = {}
        for cons in network.consumers:
            # Critical facilities (Hospitals) should ideally never be curtailed
            if cons.category == ConsumerCategory.HOSPITAL or cons.criticality == CriticalityLevel.CRITICAL:
                curtailments[cons.id] = 0.0 if rng.random() > 0.05 else round(rng.uniform(0.0, 0.1), 2)
            elif cons.category == ConsumerCategory.INDUSTRIAL:
                # Industrial loads can be curtailed more aggressively to save the grid
                curtailments[cons.id] = round(rng.uniform(0.0, 0.8), 2)
            else:
                curtailments[cons.id] = round(rng.uniform(0.0, 0.4), 2)

        return cls(gen_dispatch, line_switches, curtailments)

    def repair_constraints(self, network: InfrastructureNetwork):
        """
        Repairs chromosome boundaries to maintain physical validity:
        - Clamps generator outputs between 0 and generator capacity.
        - Clamps curtailments between 0.0 and 1.0.
        - Enforces that physically failed components cannot be operated.
        """
        gen_map = {bg.id: bg for bg in network.backup_generators}
        for bg_id, val in list(self.generator_dispatch.items()):
            if bg_id in gen_map:
                bg = gen_map[bg_id]
                if bg.operational_status == OperationalStatus.FAILED:
                    self.generator_dispatch[bg_id] = 0.0
                else:
                    max_c = bg.capacity
                    self.generator_dispatch[bg_id] = max(0.0, min(max_c, round(val, 2)))
            else:
                self.generator_dispatch[bg_id] = 0.0

        for line in network.transmission_lines:
            if line.operational_status == OperationalStatus.FAILED:
                self.line_switches[line.id] = False

        for c_id, fraction in self.consumer_curtailment.items():
            self.consumer_curtailment[c_id] = max(0.0, min(1.0, round(fraction, 3)))

    def clone(self) -> "RecoveryChromosome":
        c = RecoveryChromosome(
            dict(self.generator_dispatch),
            dict(self.line_switches),
            dict(self.consumer_curtailment),
        )
        c.fitness = self.fitness
        c.total_cost = self.total_cost
        c.unserved_demand = self.unserved_demand
        c.critical_unserved = self.critical_unserved
        return c
