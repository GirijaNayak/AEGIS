"""
Genetic Algorithm reproduction operators: Selection, Crossover, Mutation, and Elitism.
"""

import random
from typing import List, Tuple
from app.models.infrastructure import InfrastructureNetwork
from app.ai.genetic_algorithm.chromosome import RecoveryChromosome


def tournament_selection(
    population: List[RecoveryChromosome],
    tournament_size: int,
    rng: random.Random,
) -> RecoveryChromosome:
    """
    Selects the fittest chromosome among k randomly chosen competitors.
    """
    contenders = rng.sample(population, min(tournament_size, len(population)))
    contenders.sort(key=lambda c: c.fitness, reverse=True)
    return contenders[0].clone()


def uniform_crossover(
    parent1: RecoveryChromosome,
    parent2: RecoveryChromosome,
    crossover_rate: float,
    rng: random.Random,
) -> Tuple[RecoveryChromosome, RecoveryChromosome]:
    """
    Performs uniform crossover between two parent chromosomes.
    """
    if rng.random() > crossover_rate:
        return parent1.clone(), parent2.clone()

    child1_gen = {}
    child2_gen = {}
    for k in parent1.generator_dispatch:
        if rng.random() > 0.5:
            child1_gen[k] = parent1.generator_dispatch[k]
            child2_gen[k] = parent2.generator_dispatch.get(k, parent1.generator_dispatch[k])
        else:
            child1_gen[k] = parent2.generator_dispatch.get(k, parent1.generator_dispatch[k])
            child2_gen[k] = parent1.generator_dispatch[k]

    child1_lines = {}
    child2_lines = {}
    for k in parent1.line_switches:
        if rng.random() > 0.5:
            child1_lines[k] = parent1.line_switches[k]
            child2_lines[k] = parent2.line_switches.get(k, parent1.line_switches[k])
        else:
            child1_lines[k] = parent2.line_switches.get(k, parent1.line_switches[k])
            child2_lines[k] = parent1.line_switches[k]

    child1_curt = {}
    child2_curt = {}
    for k in parent1.consumer_curtailment:
        if rng.random() > 0.5:
            child1_curt[k] = parent1.consumer_curtailment[k]
            child2_curt[k] = parent2.consumer_curtailment.get(k, parent1.consumer_curtailment[k])
        else:
            child1_curt[k] = parent2.consumer_curtailment.get(k, parent1.consumer_curtailment[k])
            child2_curt[k] = parent1.consumer_curtailment[k]

    c1 = RecoveryChromosome(child1_gen, child1_lines, child1_curt)
    c2 = RecoveryChromosome(child2_gen, child2_lines, child2_curt)
    return c1, c2


def mutate_chromosome(
    chromosome: RecoveryChromosome,
    mutation_rate: float,
    network: InfrastructureNetwork,
    rng: random.Random,
):
    """
    Applies Gaussian mutation to continuous parameters and bit-flip to discrete switches.
    """
    # 1. Mutate generator dispatch
    for bg_id in chromosome.generator_dispatch:
        if rng.random() < mutation_rate:
            delta = rng.gauss(0, 10.0)
            chromosome.generator_dispatch[bg_id] = max(0.0, chromosome.generator_dispatch[bg_id] + delta)

    # 2. Mutate line switches
    for l_id in chromosome.line_switches:
        if rng.random() < mutation_rate * 0.7:
            chromosome.line_switches[l_id] = not chromosome.line_switches[l_id]

    # 3. Mutate consumer curtailment
    for c_id in chromosome.consumer_curtailment:
        if rng.random() < mutation_rate:
            delta = rng.gauss(0, 0.1)
            chromosome.consumer_curtailment[c_id] = max(0.0, min(1.0, chromosome.consumer_curtailment[c_id] + delta))

    # Repair any boundary violations
    chromosome.repair_constraints(network)
