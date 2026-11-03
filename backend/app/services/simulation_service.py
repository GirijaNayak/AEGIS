"""
Simulation Service maintaining persistent in-memory state of the electrical grid,
event history, experiment benchmarks, and orchestrating AI recovery workflows.
"""

import copy
import datetime
import uuid
from typing import Dict, List, Optional, Any, Tuple
from app.models.infrastructure import (
    InfrastructureNetwork,
    OperationalStatus,
    ConsumerCategory,
    CriticalityLevel,
    RiskCategory,
)
from app.models.events import (
    FailureType,
    FailureInjectionRequest,
    MultipleFailureRequest,
    EventLogEntry,
    SimulationMetrics,
)
from app.models.recovery import (
    FuzzyEvaluationResult,
    AStarRouteRequest,
    AStarRouteResult,
    GAConfig,
    ChromosomeDecisions,
    GARecoveryResult,
    RecoveryAnalysisResponse,
    RecoveryExecutionResponse,
    BaselineComparison,
)
from app.simulation.default_network import get_default_network
from app.simulation.load_distribution import calculate_load_distribution
from app.simulation.failure_engine import inject_failure
from app.ai.fuzzy_logic.inference import evaluate_fuzzy_risk
from app.ai.astar.algorithm import astar_search
from app.ai.genetic_algorithm.optimizer import (
    optimize_recovery_strategy,
    run_baseline_recovery,
)


class SimulationService:
    def __init__(self):
        self.reset()

    def reset(self):
        """Resets the simulation to the initial clean baseline state."""
        self.initial_network = get_default_network()
        self.current_network = copy.deepcopy(self.initial_network)
        self.metrics = calculate_load_distribution(self.current_network)
        self.event_history: List[EventLogEntry] = []
        self.active_scenario_name = "Normal Operating Equilibrium"
        self.saved_experiments: List[Dict[str, Any]] = []
        self.recovery_history: List[Dict[str, Any]] = []

    def get_state(self) -> Dict[str, Any]:
        """Returns the complete current simulation state."""
        return {
            "network": self.current_network.model_dump(),
            "metrics": self.metrics.model_dump(),
            "active_scenario": self.active_scenario_name,
            "events_count": len(self.event_history),
        }

    def trigger_failure(self, request: FailureInjectionRequest) -> Tuple[EventLogEntry, SimulationMetrics]:
        """Applies a single failure and updates simulation state."""
        event, metrics = inject_failure(self.current_network, request)
        self.metrics = metrics
        self.event_history.insert(0, event)
        self.active_scenario_name = f"Failure: {request.component_id} ({request.failure_type.value})"
        return event, metrics

    def load_preset_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Loads one of the pre-configured academic demonstration scenarios."""
        self.reset()
        sid = scenario_id.lower()

        if sid in ["scenario_a", "substation_failure"]:
            # Scenario A: Single Substation Failure (Metro Core SUB3)
            self.active_scenario_name = "Scenario A: Metro Core Substation Failure (SUB3)"
            req = FailureInjectionRequest(
                component_id="SUB3",
                component_type="substation",
                failure_type=FailureType.SUBSTATION_FAILURE,
                severity=1.0,
                description="Transformer explosion at SUB3 disconnecting Metro Core and St. Jude Hospital",
            )
            event, metrics = self.trigger_failure(req)

        elif sid in ["scenario_b", "line_failure"]:
            # Scenario B: Transmission Line Failure (TL1 & TL6 north corridor collapse)
            self.active_scenario_name = "Scenario B: North Transmission Corridor Cut (TL1 & TL6)"
            req1 = FailureInjectionRequest(
                component_id="TL1",
                component_type="transmission_line",
                failure_type=FailureType.TRANSMISSION_LINE_FAILURE,
                severity=1.0,
                description="High-voltage tower collapse on main feeder TL1",
            )
            self.trigger_failure(req1)
            req2 = FailureInjectionRequest(
                component_id="TL6",
                component_type="transmission_line",
                failure_type=FailureType.TRANSMISSION_LINE_FAILURE,
                severity=1.0,
                description="Overheating cascade trip on parallel line TL6",
            )
            event, metrics = self.trigger_failure(req2)

        elif sid in ["scenario_c", "multiple_failures", "station_loss"]:
            # Scenario C: Major Power Station Loss + Substation Stress
            self.active_scenario_name = "Scenario C: Grand Hydroelectric Station Loss (PS1 450MW)"
            req1 = FailureInjectionRequest(
                component_id="PS1",
                component_type="power_station",
                failure_type=FailureType.POWER_STATION_FAILURE,
                severity=1.0,
                description="Complete turbine shutdown at Grand Hydroelectric Station PS1",
            )
            self.trigger_failure(req1)
            req2 = FailureInjectionRequest(
                component_id="SUB5",
                component_type="substation",
                failure_type=FailureType.CAPACITY_REDUCTION,
                severity=0.5,
                description="50% capacity reduction on SUB5 from thermal stress",
            )
            event, metrics = self.trigger_failure(req2)

        elif sid in ["scenario_d", "critical_hospital"]:
            # Scenario D: Hospital Isolation
            self.active_scenario_name = "Scenario D: Critical Hospital Isolation (SUB6 Trauma Center)"
            req = FailureInjectionRequest(
                component_id="SUB6",
                component_type="substation",
                failure_type=FailureType.SUBSTATION_FAILURE,
                severity=1.0,
                description="West Hills Substation failure cutting power to Westside Trauma Center",
            )
            event, metrics = self.trigger_failure(req)

        return self.get_state()

    def analyze_recovery_pipeline(self) -> RecoveryAnalysisResponse:
        """
        Executes Steps 1 through 4 of the AEGIS recovery workflow:
        1. Failure Analysis
        2. Fuzzy Risk Assessment on surviving substations
        3. A* Search for alternative routes
        4. Genetic Algorithm Strategy Optimization recommendation
        """
        # Step 1: Identify failed and isolated infrastructure
        failed_comps = []
        for ps in self.current_network.power_stations:
            if ps.operational_status == OperationalStatus.FAILED:
                failed_comps.append(ps.id)
        for sub in self.current_network.substations:
            if sub.operational_status == OperationalStatus.FAILED:
                failed_comps.append(sub.id)
        for line in self.current_network.transmission_lines:
            if line.operational_status == OperationalStatus.FAILED:
                failed_comps.append(line.id)

        affected_consumers = [c.id for c in self.current_network.consumers if c.supplied_power < c.demand]
        isolated_subs = [s.id for s in self.current_network.substations if s.current_load < 0.1 and s.operational_status != OperationalStatus.FAILED]

        # Step 2: Fuzzy Risk Assessment on all operational substations
        fuzzy_results: List[FuzzyEvaluationResult] = []
        for sub in self.current_network.substations:
            if sub.operational_status != OperationalStatus.FAILED:
                load_pct = (sub.current_load / max(1.0, sub.max_capacity)) * 100.0
                eval_res = evaluate_fuzzy_risk(
                    load=load_pct,
                    health=sub.health_percentage,
                    temperature=sub.temperature,
                    component_id=sub.id,
                    component_name=sub.name,
                )
                fuzzy_results.append(eval_res)
                # Update substation risk values in memory
                sub.risk_score = eval_res.defuzzified_risk_score
                sub.risk_category = RiskCategory(eval_res.risk_category.lower())

        # Step 3: A* Alternative Routing
        # Find paths from available power stations or backup generators to affected substations
        astar_results: List[AStarRouteResult] = []
        active_sources = [ps.id for ps in self.current_network.power_stations if ps.operational_status == OperationalStatus.OPERATIONAL]
        active_sources += [bg.id for bg in self.current_network.backup_generators if bg.operational_status != OperationalStatus.FAILED]

        target_subs = [s.id for s in self.current_network.substations if s.operational_status == OperationalStatus.OPERATIONAL and s.current_load < s.max_capacity]

        for src in active_sources[:2]:
            for tgt in target_subs[:3]:
                if src != tgt:
                    route_req = AStarRouteRequest(
                        source_id=src,
                        destination_id=tgt,
                        required_capacity=15.0,
                    )
                    res = astar_search(self.current_network, route_req)
                    if res.path_found:
                        astar_results.append(res)

        # Step 4: Genetic Algorithm Optimization
        ga_config = GAConfig(population_size=30, generations=25, random_seed=42)
        ga_plan = optimize_recovery_strategy(self.current_network, ga_config)

        summary = (
            f"Analysis complete: {len(failed_comps)} failed components detected. "
            f"Fuzzy assessment classified {sum(1 for r in fuzzy_results if r.risk_category in ['High', 'Critical'])} substations at elevated risk. "
            f"A* identified {len(astar_results)} feasible rerouting corridors. "
            f"GA generated optimal recovery plan restoring {round(self.metrics.total_demand - ga_plan.best_chromosome.consumer_curtailment.get('HOSP1', 0), 1)} MW."
        )

        return RecoveryAnalysisResponse(
            failed_components=failed_comps,
            isolated_substations=isolated_subs,
            affected_consumers=affected_consumers,
            unserved_demand_mw=self.metrics.unserved_demand,
            critical_unserved_mw=self.metrics.critical_unserved_demand,
            fuzzy_risk_assessments=fuzzy_results,
            alternative_astar_routes=astar_results,
            recommended_ga_plan=ga_plan,
            summary=summary,
        )

    def execute_recovery_plan(self, decisions: ChromosomeDecisions) -> RecoveryExecutionResponse:
        """
        Applies recovery strategy actions to the live simulation network:
        - Dispatches backup generators
        - Reconfigures transmission line switches
        - Adjusts consumer loads according to priority curtailment
        - Recalculates full load distribution and records before/after metrics
        """
        before_metrics = self.metrics.model_dump()

        # 1. Apply generator dispatches
        for bg in self.current_network.backup_generators:
            target_mw = decisions.generator_dispatch.get(bg.id, 0.0)
            if target_mw > 0.1 and bg.operational_status != OperationalStatus.FAILED:
                bg.is_active = True
                bg.current_utilization = min(bg.capacity, target_mw)
            else:
                bg.is_active = False
                bg.current_utilization = 0.0

        # 2. Apply line switches (ignoring physically failed lines)
        for line in self.current_network.transmission_lines:
            if line.operational_status != OperationalStatus.FAILED:
                sw = decisions.line_switches.get(line.id, True)
                line.operational_status = OperationalStatus.OPERATIONAL if sw else OperationalStatus.OFFLINE

        # 3. Recalculate load distribution
        self.metrics = calculate_load_distribution(self.current_network)
        after_metrics = self.metrics.model_dump()

        # Compute improvements
        unserved_recovered = max(0.0, before_metrics["unserved_demand"] - after_metrics["unserved_demand"])
        critical_recovered = max(0.0, before_metrics["critical_unserved_demand"] - after_metrics["critical_unserved_demand"])
        reliability_gain = round(after_metrics["grid_reliability_index"] - before_metrics["grid_reliability_index"], 1)

        improvements = {
            "unserved_demand_recovered_mw": round(unserved_recovered, 2),
            "critical_demand_recovered_mw": round(critical_recovered, 2),
            "reliability_index_gain": reliability_gain,
            "facilities_restored": max(0, after_metrics["critical_facilities_supplied"] - before_metrics["critical_facilities_supplied"]),
        }

        # Log recovery action
        recovery_entry = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "plan": decisions.model_dump(),
            "before_metrics": before_metrics,
            "after_metrics": after_metrics,
            "improvements": improvements,
        }
        self.recovery_history.insert(0, recovery_entry)

        return RecoveryExecutionResponse(
            success=True,
            plan_applied=decisions,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            improvements=improvements,
            status_message=f"Recovery executed: Restored {round(unserved_recovered, 1)} MW total and {round(critical_recovered, 1)} MW critical demand.",
        )

    def run_experiment_comparison(self, scenario_id: str, ga_config: Optional[GAConfig] = None) -> Dict[str, Any]:
        """
        Executes a rigorous experimental comparison on the specified scenario:
        Runs Baseline vs AI-Assisted (GA + A* + Fuzzy) recovery and logs reproducible metrics.
        """
        # Load fresh scenario
        self.load_preset_scenario(scenario_id)
        if ga_config is None:
            ga_config = GAConfig(population_size=40, generations=30, random_seed=42)

        # Baseline execution
        baseline = run_baseline_recovery(self.current_network, ga_config)

        # AI-Assisted execution
        ga_result = optimize_recovery_strategy(self.current_network, ga_config)

        experiment_record = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scenario": self.active_scenario_name,
            "ga_config": ga_config.model_dump(),
            "baseline": baseline.model_dump(),
            "ai_assisted": {
                "fitness": ga_result.best_fitness,
                "cost": ga_result.best_cost,
                "unserved_demand_mw": ga_result.generations_history[-1].unserved_demand_mw,
                "critical_unserved_mw": ga_result.generations_history[-1].critical_unserved_mw,
                "execution_time_ms": ga_result.execution_time_ms,
                "is_valid": ga_result.is_valid,
                "generations_history": [g.model_dump() for g in ga_result.generations_history],
            },
            "comparison": {
                "cost_reduction_percentage": round(max(0.0, (baseline.cost - ga_result.best_cost) / max(1.0, baseline.cost)) * 100.0, 1),
                "unserved_reduction_mw": round(max(0.0, baseline.unserved_demand_mw - ga_result.generations_history[-1].unserved_demand_mw), 2),
                "critical_facilities_saved": 1 if baseline.critical_unserved_mw > ga_result.generations_history[-1].critical_unserved_mw else 0,
            }
        }
        self.saved_experiments.insert(0, experiment_record)
        return experiment_record


# Singleton service instance
simulation_service = SimulationService()
