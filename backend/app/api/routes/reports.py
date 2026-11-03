"""
API routes for exporting comprehensive technical simulation and experiment reports in JSON and CSV format.
"""

import io
import csv
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Response
from app.services.simulation_service import simulation_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/current/json")
def get_current_simulation_report():
    """Generates a complete technical audit report of the current simulation state."""
    state = simulation_service.get_state()
    history = simulation_service.event_history
    recoveries = simulation_service.recovery_history

    return {
        "report_title": "AEGIS Infrastructure Failure & AI Recovery Report",
        "generated_at": state.get("active_scenario"),
        "scenario": simulation_service.active_scenario_name,
        "metrics": state["metrics"],
        "components_summary": {
            "power_stations": len(state["network"]["power_stations"]),
            "substations": len(state["network"]["substations"]),
            "transmission_lines": len(state["network"]["transmission_lines"]),
            "consumers": len(state["network"]["consumers"]),
            "backup_generators": len(state["network"]["backup_generators"]),
        },
        "event_log_count": len(history),
        "recent_events": [e.model_dump() for e in history[:10]],
        "recent_recoveries": recoveries[:5],
        "methodology": {
            "fuzzy_logic": "Mamdani Inference (MIN antecedent, MAX aggregation, Centroid Defuzzification)",
            "astar_pathfinding": "Admissible Euclidean Distance Heuristic, Capacity-Constrained Feasibility",
            "genetic_algorithm": "Multi-Objective Cost Minimization (Tournament Selection, Uniform Crossover, Gaussian Mutation)",
        },
        "limitations": "Academic graph-based flow simulation. Does not model AC reactive power, phase angles, or dynamic frequency oscillations.",
    }


@router.get("/experiments/{experiment_id}/csv")
def export_experiment_csv(experiment_id: str):
    """Exports generation-by-generation convergence data of a specific experiment to CSV format."""
    target_exp = None
    for exp in simulation_service.saved_experiments:
        if exp["id"] == experiment_id:
            target_exp = exp
            break

    if not target_exp:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Generation", "Best Fitness", "Average Fitness", "Best Cost", "Unserved Demand (MW)", "Critical Unserved (MW)"])

    for gen in target_exp["ai_assisted"]["generations_history"]:
        writer.writerow([
            gen["generation"],
            gen["best_fitness"],
            gen["average_fitness"],
            gen["best_cost"],
            gen["unserved_demand_mw"],
            gen["critical_unserved_mw"],
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=aegis_experiment_{experiment_id}.csv"},
    )
