"""
Multi-objective fitness evaluation function for Genetic Algorithm recovery optimization.
Evaluates unserved demand, critical facility protection, recovery operational time,
resource fuel costs, and electrical overload penalties.
"""

import copy
from typing import Tuple
from app.models.infrastructure import (
    InfrastructureNetwork,
    OperationalStatus,
    ConsumerCategory,
    CriticalityLevel,
)
from app.models.recovery import GAConfig
from app.ai.genetic_algorithm.chromosome import RecoveryChromosome
from app.simulation.load_distribution import calculate_load_distribution


def evaluate_chromosome_fitness(
    chromosome: RecoveryChromosome,
    network: InfrastructureNetwork,
    config: GAConfig,
) -> Tuple[float, float]:
    """
    Evaluates a recovery chromosome on a clone of the infrastructure network.
    Returns (fitness_score, total_cost).
    """
    # 1. Deep copy network to isolate evaluation
    sim_net = copy.deepcopy(network)

    # 2. Apply generator dispatches
    generators_dispatched_count = 0
    total_generator_mw = 0.0
    total_fuel_cost = 0.0

    for bg in sim_net.backup_generators:
        target_mw = chromosome.generator_dispatch.get(bg.id, 0.0)
        if target_mw > 0.1 and bg.operational_status != OperationalStatus.FAILED:
            bg.is_active = True
            bg.current_utilization = min(bg.capacity, target_mw)
            generators_dispatched_count += 1
            total_generator_mw += bg.current_utilization
            total_fuel_cost += bg.current_utilization * bg.fuel_cost_per_mw
        else:
            bg.is_active = False
            bg.current_utilization = 0.0

    # 3. Apply line switches (cannot reactivate physically FAILED lines)
    line_switches_count = 0
    for line in sim_net.transmission_lines:
        if line.operational_status == OperationalStatus.FAILED:
            continue
        switch_state = chromosome.line_switches.get(line.id, True)
        if switch_state:
            line.operational_status = OperationalStatus.OPERATIONAL
            line_switches_count += 1
        else:
            line.operational_status = OperationalStatus.OFFLINE

    # 4. Apply consumer curtailment to nominal demand
    for cons in sim_net.consumers:
        curtail_frac = chromosome.consumer_curtailment.get(cons.id, 0.0)
        cons.demand = round(cons.demand * (1.0 - curtail_frac), 2)

    # 5. Execute load distribution calculation
    metrics = calculate_load_distribution(sim_net)

    # 6. Extract raw performance metrics
    # Re-evaluate true unserved demand against original baseline consumer demand
    orig_demand_map = {c.id: c.demand for c in network.consumers}
    actual_unserved = 0.0
    critical_unserved = 0.0

    for cons in sim_net.consumers:
        orig_d = orig_demand_map.get(cons.id, cons.demand)
        supplied = cons.supplied_power
        unserved = max(0.0, orig_d - supplied)
        actual_unserved += unserved
        
        if cons.category == ConsumerCategory.HOSPITAL or cons.criticality == CriticalityLevel.CRITICAL:
            critical_unserved += unserved

    # Overload penalty: sum of excess MW on overloaded lines
    overload_penalty_mw = 0.0
    for line in sim_net.transmission_lines:
        if line.current_flow > line.max_capacity:
            overload_penalty_mw += (line.current_flow - line.max_capacity)

    # Recovery time estimation in simulated minutes:
    # 12 min per cold-start generator + 2 min per line switching operation
    recovery_time_minutes = (generators_dispatched_count * 12.0) + (line_switches_count * 2.0)

    # 7. Compute weighted Multi-Objective Cost Function
    # Cost = w1*Unserved + w2*Time + w3*ResourceCost + w4*Overloads + w5*CriticalUnserved
    w1 = config.weight_unserved
    w2 = config.weight_recovery_time
    w3 = config.weight_resource_cost
    w4 = config.weight_overload
    w5 = config.weight_critical

    total_cost = (
        (w1 * actual_unserved)
        + (w2 * recovery_time_minutes)
        + (w3 * (total_fuel_cost / 10.0))
        + (w4 * overload_penalty_mw * 5.0)
        + (w5 * critical_unserved * 20.0)
    )

    # Fitness score (higher is better)
    fitness_score = 10000.0 / (1.0 + total_cost)

    chromosome.fitness = round(fitness_score, 4)
    chromosome.total_cost = round(total_cost, 2)
    chromosome.unserved_demand = round(actual_unserved, 2)
    chromosome.critical_unserved = round(critical_unserved, 2)

    return chromosome.fitness, chromosome.total_cost
