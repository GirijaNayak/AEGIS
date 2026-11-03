"""
End-to-End Workflow Audit Test for AEGIS Infrastructure Failure and Recovery Pipeline.
Validates the complete 8-step lifecycle:
1. Initialize Network & Verify Clean Baseline
2. Inject Multi-Component Infrastructure Failure
3. Analyze Infrastructure Disruption & Isolate Components
4. Execute Mamdani Fuzzy Risk Assessment on surviving assets
5. Compute Alternative Capacity-Constrained Paths via A* Search
6. Formulate & Solve Multi-Objective Optimization via Genetic Algorithm
7. Execute Recommended Recovery Decisions on Live Network
8. Validate Post-Recovery Metric Improvements and State Consistency
"""

import pytest
from app.services.simulation_service import SimulationService
from app.models.events import FailureInjectionRequest, FailureType
from app.models.recovery import GAConfig
from app.models.infrastructure import OperationalStatus


def test_complete_e2e_failure_and_recovery_workflow():
    service = SimulationService()
    service.reset()

    # Step 1: Initial Baseline Verification
    state_0 = service.get_state()
    metrics_0 = state_0["metrics"]
    assert metrics_0["unserved_demand"] == 0.0, "Initial grid should have zero unserved demand"
    assert metrics_0["restoration_percentage"] == 100.0
    assert metrics_0["critical_unserved_demand"] == 0.0
    assert metrics_0["failed_components_count"] == 0

    # Step 2: Inject Scenario A (Metro Core Substation Failure: SUB3)
    service.load_preset_scenario("scenario_a")
    state_failed = service.get_state()
    metrics_failed = state_failed["metrics"]

    assert metrics_failed["failed_components_count"] >= 1
    # Verify unserved demand created by failure (e.g. IND2 loses power)
    assert metrics_failed["unserved_demand"] > 0.0 or metrics_failed["grid_reliability_index"] < 100.0

    # Step 3 to 6: Full Recovery Pipeline Analysis
    analysis = service.analyze_recovery_pipeline()

    # Verify Step 3: Failure Analysis Results
    assert len(analysis.failed_components) >= 1
    assert "SUB3" in analysis.failed_components

    # Verify Step 4: Fuzzy Risk Assessment on surviving substations
    fuzzy_assessments = analysis.fuzzy_risk_assessments
    assert len(fuzzy_assessments) > 0
    for fa in fuzzy_assessments:
        assert 0.0 <= fa.defuzzified_risk_score <= 100.0
        assert fa.risk_category in ["Low", "Moderate", "High", "Critical"]
        assert len(fa.activated_rules) > 0
        assert 0.0 <= fa.inputs.load_percentage <= 100.0

    # Verify Step 5: A* Search Paths Computed
    astar_paths = analysis.alternative_astar_routes
    assert len(astar_paths) > 0
    for alt in astar_paths:
        if alt.path_found:
            assert len(alt.path_nodes) >= 2
            assert alt.total_cost > 0.0
            assert alt.bottleneck_capacity_mw > 0.0

    # Verify Step 6: Genetic Algorithm Optimization Solution
    ga_plan = analysis.recommended_ga_plan
    assert ga_plan is not None
    assert ga_plan.is_valid is True
    assert ga_plan.best_fitness > 0.0
    assert len(ga_plan.generations_history) > 0
    assert ga_plan.baseline_comparison is not None
    # GA must match or outperform baseline
    assert ga_plan.best_cost <= ga_plan.baseline_comparison.cost + 1e-4

    # Step 7: Execute Recommended Recovery Plan on Grid
    recovery_resp = service.execute_recovery_plan(ga_plan.best_chromosome)

    assert recovery_resp.success is True
    assert recovery_resp.improvements is not None

    # Step 8: Validate Post-Recovery Metric Improvements and State Consistency
    after_metrics = recovery_resp.after_metrics
    before_metrics = recovery_resp.before_metrics

    # Restoration improvement check:
    assert after_metrics["restoration_percentage"] >= before_metrics["restoration_percentage"]
    assert after_metrics["critical_unserved_demand"] <= before_metrics["critical_unserved_demand"]

    # History logged
    assert len(service.recovery_history) >= 1
    assert service.recovery_history[0]["plan"] is not None
