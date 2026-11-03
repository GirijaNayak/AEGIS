"""
API routes for simulation state, equilibrium calculation, state resets, and preset scenarios.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.services.simulation_service import simulation_service
from app.models.events import SimulationMetrics

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.get("/state")
def get_simulation_state() -> Dict[str, Any]:
    """Returns the full active simulation state, network topology, and performance metrics."""
    return simulation_service.get_state()


@router.get("/metrics", response_model=SimulationMetrics)
def get_simulation_metrics():
    """Returns current real-time grid reliability and capacity metrics."""
    return simulation_service.metrics


@router.post("/reset")
def reset_simulation() -> Dict[str, Any]:
    """Resets the simulation network to the pristine normal equilibrium state."""
    simulation_service.reset()
    return {
        "status": "success",
        "message": "Simulation reset to pristine initial state.",
        "state": simulation_service.get_state(),
    }


@router.post("/preset/{scenario_id}")
def load_scenario(scenario_id: str) -> Dict[str, Any]:
    """Loads a pre-configured failure scenario for academic demonstration and viva."""
    valid_scenarios = ["scenario_a", "scenario_b", "scenario_c", "scenario_d", "substation_failure", "line_failure", "multiple_failures", "critical_hospital"]
    if scenario_id.lower() not in valid_scenarios:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario ID '{scenario_id}'. Available presets: {valid_scenarios}",
        )
    return simulation_service.load_preset_scenario(scenario_id)
