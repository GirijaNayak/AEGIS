"""
Unit tests for Genetic Algorithm recovery optimizer.
"""

import random
import pytest
from app.simulation.default_network import get_default_network
from app.simulation.failure_engine import inject_failure
from app.models.events import FailureInjectionRequest, FailureType
from app.models.recovery import GAConfig
from app.ai.genetic_algorithm.chromosome import RecoveryChromosome
from app.ai.genetic_algorithm.fitness import evaluate_chromosome_fitness
from app.ai.genetic_algorithm.optimizer import optimize_recovery_strategy


def test_chromosome_initialization_and_repair():
    network = get_default_network()
    rng = random.Random(42)
    chromo = RecoveryChromosome.create_random(network, rng)

    assert len(chromo.generator_dispatch) == len(network.backup_generators)
    assert len(chromo.consumer_curtailment) == len(network.consumers)

    # Violate boundaries deliberately
    bg_first = network.backup_generators[0]
    chromo.generator_dispatch[bg_first.id] = 9999.0
    chromo.consumer_curtailment["HOSP1"] = -5.0

    chromo.repair_constraints(network)
    assert chromo.generator_dispatch[bg_first.id] == bg_first.capacity
    assert chromo.consumer_curtailment["HOSP1"] == 0.0


def test_fitness_evaluation_penalizes_unserved_hospitals():
    network = get_default_network()
    config = GAConfig()

    # Case 1: Chromosome with 0 generator dispatch and complete curtailment
    bad_chromo = RecoveryChromosome(
        generator_dispatch={bg.id: 0.0 for bg in network.backup_generators},
        line_switches={line.id: False for line in network.transmission_lines},
        consumer_curtailment={c.id: 1.0 for c in network.consumers},
    )
    fit_bad, cost_bad = evaluate_chromosome_fitness(bad_chromo, network, config)

    # Case 2: Healthy chromosome with full line operations and 0 curtailment
    good_chromo = RecoveryChromosome(
        generator_dispatch={bg.id: 0.0 for bg in network.backup_generators},
        line_switches={line.id: True for line in network.transmission_lines},
        consumer_curtailment={c.id: 0.0 for c in network.consumers},
    )
    fit_good, cost_good = evaluate_chromosome_fitness(good_chromo, network, config)

    assert cost_good < cost_bad
    assert fit_good > fit_bad


def test_ga_optimizer_convergence_and_reproducibility():
    network = get_default_network()
    # Inject substation failure to create recovery challenge
    inject_failure(network, FailureInjectionRequest(
        component_id="SUB3",
        component_type="substation",
        failure_type=FailureType.SUBSTATION_FAILURE,
    ))

    config1 = GAConfig(population_size=20, generations=10, random_seed=123)
    result1 = optimize_recovery_strategy(network, config1)

    assert result1.best_fitness > 0.0
    assert len(result1.generations_history) == 10
    # Fitness should generally improve or stay equal across generations
    initial_best = result1.generations_history[0].best_cost
    final_best = result1.generations_history[-1].best_cost
    assert final_best <= initial_best
    assert result1.is_valid is True

    # Reproducibility check with same seed
    config2 = GAConfig(population_size=20, generations=10, random_seed=123)
    result2 = optimize_recovery_strategy(network, config2)
    assert result1.best_fitness == result2.best_fitness
    assert result1.best_cost == result2.best_cost
