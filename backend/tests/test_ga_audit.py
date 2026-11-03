"""
Independent Audit and Verification Tests for Genetic Algorithm Recovery Optimizer.
Tests:
1. Elitism monotonicity across generations.
2. Multi-seed statistical stability (10 random seeds: min, max, mean, std dev).
3. Hard constraint repair and physical feasibility.
4. Heuristic baseline comparison (GA cost <= baseline cost).
"""

import math
import statistics
import pytest
from app.simulation.default_network import get_default_network
from app.models.infrastructure import OperationalStatus
from app.models.recovery import GAConfig
from app.ai.genetic_algorithm.optimizer import optimize_recovery_strategy, run_baseline_recovery
from app.ai.genetic_algorithm.chromosome import RecoveryChromosome


def test_ga_elitism_monotonicity():
    """
    Verifies that with elitism enabled (elitism_count >= 1), the best fitness
    across successive generations never regresses: best_fitness[t+1] >= best_fitness[t].
    """
    network = get_default_network()
    # Induce a realistic failure: SUB1 failure
    for s in network.substations:
        if s.id == "SUB1":
            s.operational_status = OperationalStatus.FAILED
    for line in network.transmission_lines:
        if line.source_id == "SUB1" or line.destination_id == "SUB1":
            line.operational_status = OperationalStatus.FAILED

    config = GAConfig(
        population_size=20,
        generations=15,
        crossover_rate=0.8,
        mutation_rate=0.15,
        elitism_count=2,
        random_seed=42,
    )

    result = optimize_recovery_strategy(network, config)

    history = result.generations_history
    assert len(history) == 15

    for i in range(len(history) - 1):
        fit_curr = history[i].best_fitness
        fit_next = history[i + 1].best_fitness
        assert fit_next >= fit_curr - 1e-6, (
            f"Elitism regression at generation {history[i+1].generation}: "
            f"{fit_next} < {fit_curr}"
        )


def test_ga_statistical_stability_across_10_seeds():
    """
    Evaluates GA performance across 10 distinct random seeds (100 to 109).
    Calculates best, mean, worst, and standard deviation for fitness and cost.
    Asserts consistent convergence without catastrophic outliers.
    """
    network = get_default_network()
    for s in network.substations:
        if s.id == "SUB2":
            s.operational_status = OperationalStatus.FAILED
    for line in network.transmission_lines:
        if line.source_id == "SUB2" or line.destination_id == "SUB2":
            line.operational_status = OperationalStatus.FAILED

    costs = []
    fitnesses = []

    for seed in range(100, 110):
        config = GAConfig(
            population_size=15,
            generations=10,
            elitism_count=2,
            random_seed=seed,
        )
        res = optimize_recovery_strategy(network, config)
        costs.append(res.best_cost)
        fitnesses.append(res.best_fitness)
        assert res.is_valid is True

    mean_cost = statistics.mean(costs)
    stdev_cost = statistics.stdev(costs)
    min_cost = min(costs)
    max_cost = max(costs)

    mean_fit = statistics.mean(fitnesses)
    stdev_fit = statistics.stdev(fitnesses)

    print(f"\n[GA 10-Seed Audit Results]")
    print(f"Cost: min={min_cost:.2f}, max={max_cost:.2f}, mean={mean_cost:.2f}, std={stdev_cost:.2f}")
    print(f"Fitness: min={min(fitnesses):.4f}, max={max(fitnesses):.4f}, mean={mean_fit:.4f}, std={stdev_fit:.4f}")

    # Standard deviation should be bounded (stable optimization, not chaotic)
    assert stdev_cost < mean_cost * 0.5, "GA cost exhibits excessive variance across random seeds."
    assert all(c > 0 for c in costs)


def test_ga_hard_constraint_repair():
    """
    Verifies that RecoveryChromosome.repair_constraints physically repairs:
    - Out-of-bounds generator dispatches (negative or > capacity)
    - Failed generator dispatch attempts
    - Failed transmission line activations
    - Out-of-bounds curtailments (<0 or >1)
    """
    network = get_default_network()
    # Mark BG1 as failed and TL1 as failed
    for bg in network.backup_generators:
        if bg.id == "BG1":
            bg.operational_status = OperationalStatus.FAILED
    for line in network.transmission_lines:
        if line.id == "TL1":
            line.operational_status = OperationalStatus.FAILED

    # Intentionally malformed chromosome
    invalid_chromosome = RecoveryChromosome(
        generator_dispatch={
            "BG1": 50.0,          # FAILED generator
            "BG2": 9999.0,        # Exceeds capacity (40 MW)
            "UNKNOWN_GEN": 25.0,  # Unknown generator
        },
        line_switches={
            "TL1": True,          # FAILED line
            "TL2": True,
        },
        consumer_curtailment={
            "HOSP1": -0.5,        # Negative curtailment
            "IND1": 2.5,          # Exceeds 1.0
        },
    )

    invalid_chromosome.repair_constraints(network)

    # Validate repaired values
    assert invalid_chromosome.generator_dispatch["BG1"] == 0.0, "Failed generator was not set to 0.0"
    gen_b2_cap = next(bg.capacity for bg in network.backup_generators if bg.id == "BG2")
    assert invalid_chromosome.generator_dispatch["BG2"] == gen_b2_cap, "Oversized dispatch was not clamped to capacity"
    assert invalid_chromosome.generator_dispatch["UNKNOWN_GEN"] == 0.0, "Unknown generator was not clamped to 0.0"

    assert invalid_chromosome.line_switches["TL1"] is False, "Physically failed line was not forced False"

    assert invalid_chromosome.consumer_curtailment["HOSP1"] == 0.0, "Negative curtailment was not clamped to 0.0"
    assert invalid_chromosome.consumer_curtailment["IND1"] == 1.0, "Excessive curtailment was not clamped to 1.0"


def test_ga_superiority_over_greedy_baseline():
    """
    Verifies that the optimized GA recovery plan matches or outperforms the unoptimized greedy baseline.
    """
    network = get_default_network()
    # Trip substation SUB3
    for s in network.substations:
        if s.id == "SUB3":
            s.operational_status = OperationalStatus.FAILED
    for line in network.transmission_lines:
        if line.source_id == "SUB3" or line.destination_id == "SUB3":
            line.operational_status = OperationalStatus.FAILED

    config = GAConfig(
        population_size=20,
        generations=15,
        random_seed=777,
    )

    baseline = run_baseline_recovery(network, config)
    result = optimize_recovery_strategy(network, config)

    assert result.best_cost <= baseline.cost + 1e-4, (
        f"GA failed to match or beat baseline: GA cost {result.best_cost} vs baseline {baseline.cost}"
    )
