"""
Genetic Algorithm Optimizer for Infrastructure Recovery.
Executes the evolutionary cycle, logs generation convergence history, validates constraints,
and evaluates against a benchmark baseline strategy.
"""

import copy
import random
import time
from typing import Dict, List, Optional, Tuple
from app.models.infrastructure import (
    InfrastructureNetwork,
    OperationalStatus,
)
from app.models.recovery import (
    GAConfig,
    ChromosomeDecisions,
    GenerationMetric,
    BaselineComparison,
    GARecoveryResult,
)
from app.ai.genetic_algorithm.chromosome import RecoveryChromosome
from app.ai.genetic_algorithm.fitness import evaluate_chromosome_fitness
from app.ai.genetic_algorithm.operators import (
    tournament_selection,
    uniform_crossover,
    mutate_chromosome,
)


def run_baseline_recovery(network: InfrastructureNetwork, config: GAConfig) -> BaselineComparison:
    """
    Constructs an unoptimized heuristic baseline recovery strategy:
    Activates all available backup generators at 100% indiscriminately and leaves consumers unmanaged.
    """
    gen_dispatch = {bg.id: bg.capacity for bg in network.backup_generators if bg.operational_status != OperationalStatus.FAILED}
    line_switches = {line.id: True for line in network.transmission_lines if line.operational_status != OperationalStatus.FAILED}
    curtailments = {cons.id: 0.0 for cons in network.consumers}

    base_chromo = RecoveryChromosome(gen_dispatch, line_switches, curtailments)
    fitness, cost = evaluate_chromosome_fitness(base_chromo, network, config)

    gen_mw = sum(gen_dispatch.values())
    rec_time = len(gen_dispatch) * 12.0

    return BaselineComparison(
        strategy_name="Greedy Full-Dispatch Baseline",
        cost=round(cost, 2),
        fitness=round(fitness, 4),
        unserved_demand_mw=round(base_chromo.unserved_demand, 2),
        critical_unserved_mw=round(base_chromo.critical_unserved, 2),
        generators_used_mw=round(gen_mw, 2),
        recovery_time_min=round(rec_time, 1),
    )


def optimize_recovery_strategy(
    network: InfrastructureNetwork,
    config: Optional[GAConfig] = None,
) -> GARecoveryResult:
    """
    Executes the full Genetic Algorithm optimization workflow.
    """
    start_time = time.time()
    if config is None:
        config = GAConfig()

    rng = random.Random(config.random_seed)

    # 1. Initialize population
    population: List[RecoveryChromosome] = [
        RecoveryChromosome.create_random(network, rng)
        for _ in range(config.population_size)
    ]

    # Evaluate initial population
    for ind in population:
        evaluate_chromosome_fitness(ind, network, config)

    generations_history: List[GenerationMetric] = []

    # 2. Evolutionary Loop
    for gen in range(config.generations):
        # Sort current population descending by fitness
        population.sort(key=lambda c: c.fitness, reverse=True)

        # Elitism: preserve top k individuals
        new_population: List[RecoveryChromosome] = [
            population[i].clone() for i in range(min(config.elitism_count, len(population)))
        ]

        # Generate offspring
        while len(new_population) < config.population_size:
            p1 = tournament_selection(population, config.tournament_size, rng)
            p2 = tournament_selection(population, config.tournament_size, rng)

            c1, c2 = uniform_crossover(p1, p2, config.crossover_rate, rng)

            mutate_chromosome(c1, config.mutation_rate, network, rng)
            mutate_chromosome(c2, config.mutation_rate, network, rng)

            evaluate_chromosome_fitness(c1, network, config)
            evaluate_chromosome_fitness(c2, network, config)

            new_population.append(c1)
            if len(new_population) < config.population_size:
                new_population.append(c2)

        population = new_population
        population.sort(key=lambda c: c.fitness, reverse=True)
        best_ind = population[0]
        avg_fit = sum(c.fitness for c in population) / len(population)

        generations_history.append(
            GenerationMetric(
                generation=gen + 1,
                best_fitness=round(best_ind.fitness, 4),
                average_fitness=round(avg_fit, 4),
                best_cost=round(best_ind.total_cost, 2),
                unserved_demand_mw=round(best_ind.unserved_demand, 2),
                critical_unserved_mw=round(best_ind.critical_unserved, 2),
            )
        )

    best_chromosome = population[0]

    # 3. Constraint Validation
    validation_notes: List[str] = []
    is_valid = True

    # Validate generator dispatch limits
    for bg in network.backup_generators:
        disp = best_chromosome.generator_dispatch.get(bg.id, 0.0)
        if disp > bg.capacity:
            is_valid = False
            validation_notes.append(f"VIOLATION: Generator {bg.id} allocated {disp} MW exceeding capacity {bg.capacity} MW.")
        elif disp > 0.0 and bg.operational_status == OperationalStatus.FAILED:
            is_valid = False
            validation_notes.append(f"VIOLATION: Generator {bg.id} is FAILED but was allocated dispatch.")
    
    # Validate transmission line switches
    for line in network.transmission_lines:
        sw = best_chromosome.line_switches.get(line.id, False)
        if sw and line.operational_status == OperationalStatus.FAILED:
            is_valid = False
            validation_notes.append(f"VIOLATION: Line {line.id} is physically FAILED and cannot be switched active.")

    if is_valid:
        validation_notes.append("VALIDATION PASSED: All operational generator bounds and network physical constraints satisfied.")

    # 4. Baseline Evaluation
    baseline = run_baseline_recovery(network, config)

    exec_time = round((time.time() - start_time) * 1000.0, 1)

    # 5. Technical explanation for college viva presentation
    active_bgs = [f"{k}: {v} MW" for k, v in best_chromosome.generator_dispatch.items() if v > 0.1]
    active_bg_str = ", ".join(active_bgs) if active_bgs else "None"
    
    explanation = (
        f"GA converged over {config.generations} generations (Population: {config.population_size}) in {exec_time} ms. "
        f"Optimal recovery plan achieved objective cost {round(best_chromosome.total_cost, 2)} "
        f"(Fitness: {round(best_chromosome.fitness, 4)}). "
        f"Restored critical unserved demand to {round(best_chromosome.critical_unserved, 2)} MW. "
        f"Dispatched backup generation: [{active_bg_str}]. "
        f"Versus greedy baseline cost {baseline.cost}, GA reduced multi-objective cost by "
        f"{round(max(0.0, baseline.cost - best_chromosome.total_cost), 2)} points."
    )

    return GARecoveryResult(
        best_fitness=best_chromosome.fitness,
        best_cost=best_chromosome.total_cost,
        best_chromosome=ChromosomeDecisions(
            generator_dispatch={k: round(v, 2) for k, v in best_chromosome.generator_dispatch.items()},
            line_switches=best_chromosome.line_switches,
            consumer_curtailment={k: round(v, 3) for k, v in best_chromosome.consumer_curtailment.items()},
        ),
        generations_history=generations_history,
        execution_time_ms=exec_time,
        is_valid=is_valid,
        validation_notes=validation_notes,
        baseline_comparison=baseline,
        explanation=explanation,
    )
