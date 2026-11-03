"""
API routes for experimental benchmarking, comparing baseline vs AI-assisted recovery.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.simulation_service import simulation_service
from app.models.recovery import GAConfig

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


class RunExperimentRequest(BaseModel):
    scenario_id: str = "scenario_a"
    ga_config: Optional[GAConfig] = None


@router.post("/run")
def run_experiment(request: RunExperimentRequest):
    """Executes a comparative benchmark between Baseline and AI recovery on the chosen scenario."""
    return simulation_service.run_experiment_comparison(
        scenario_id=request.scenario_id,
        ga_config=request.ga_config,
    )


@router.get("")
def list_experiments():
    """Returns all saved benchmark experiment runs."""
    return simulation_service.saved_experiments


@router.get("/{experiment_id}")
def get_experiment_details(experiment_id: str):
    """Returns full details and generation logs for a specific experiment."""
    for exp in simulation_service.saved_experiments:
        if exp["id"] == experiment_id:
            return exp
    raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found.")


@router.get("/compare/summary")
def get_comparison_summary():
    """Returns aggregate comparison metrics across all recorded experiments."""
    exps = simulation_service.saved_experiments
    if not exps:
        return {
            "total_experiments": 0,
            "average_cost_reduction_percentage": 0.0,
            "average_unserved_reduction_mw": 0.0,
            "experiments": [],
        }

    cost_reductions = [e["comparison"]["cost_reduction_percentage"] for e in exps]
    unserved_reductions = [e["comparison"]["unserved_reduction_mw"] for e in exps]

    return {
        "total_experiments": len(exps),
        "average_cost_reduction_percentage": round(sum(cost_reductions) / len(cost_reductions), 1),
        "average_unserved_reduction_mw": round(sum(unserved_reductions) / len(unserved_reductions), 2),
        "experiments": exps,
    }
