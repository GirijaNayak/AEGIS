"""
API routes for orchestrating the multi-stage AI recovery pipeline:
Step 1: Failure Analysis -> Step 2: Fuzzy Assessment -> Step 3: A* Routing -> Step 4: GA Optimization -> Step 5: Validation -> Step 6: Execution.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from app.services.simulation_service import simulation_service
from app.models.recovery import (
    RecoveryAnalysisResponse,
    RecoveryExecutionRequest,
    RecoveryExecutionResponse,
)

router = APIRouter(prefix="/api/recovery", tags=["recovery"])


@router.post("/analyze", response_model=RecoveryAnalysisResponse)
def run_recovery_analysis():
    """Runs automated failure triage, fuzzy risk assessment, A* path discovery, and GA optimization."""
    return simulation_service.analyze_recovery_pipeline()


@router.post("/execute", response_model=RecoveryExecutionResponse)
def execute_recovery_plan(request: RecoveryExecutionRequest):
    """Applies a candidate recovery plan directly to the active electricity network."""
    return simulation_service.execute_recovery_plan(request.recovery_plan)


@router.get("/history")
def get_recovery_history():
    """Returns past recovery operations and quantified before/after improvements."""
    return simulation_service.recovery_history
