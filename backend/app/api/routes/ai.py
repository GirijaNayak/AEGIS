"""
API routes for directly testing and inspecting the three core AI algorithms independently:
1. Fuzzy Logic Risk Assessment
2. A* Search Algorithm
3. Genetic Algorithm Recovery Optimization
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.simulation_service import simulation_service
from app.models.recovery import (
    FuzzyInputValues,
    FuzzyEvaluationResult,
    AStarRouteRequest,
    AStarRouteResult,
    GAConfig,
    GARecoveryResult,
)
from app.ai.fuzzy_logic.inference import evaluate_fuzzy_risk
from app.ai.fuzzy_logic.rules import get_rule_base
from app.ai.astar.algorithm import astar_search
from app.ai.genetic_algorithm.optimizer import optimize_recovery_strategy

router = APIRouter(prefix="/api/ai", tags=["ai"])


# ==========================================
# 1. Fuzzy Logic Endpoints
# ==========================================

class FuzzyEvalRequest(BaseModel):
    load_percentage: float = Field(default=75.0, ge=0.0, le=100.0)
    health_percentage: float = Field(default=60.0, ge=0.0, le=100.0)
    temperature: float = Field(default=65.0, ge=0.0, le=120.0)
    component_id: Optional[str] = "CUSTOM_SUB"
    component_name: Optional[str] = "Laboratory Substation Test"


@router.post("/fuzzy/evaluate", response_model=FuzzyEvaluationResult)
def evaluate_fuzzy_endpoint(request: FuzzyEvalRequest):
    """Executes transparent Mamdani fuzzy inference on user-specified operating parameters."""
    return evaluate_fuzzy_risk(
        load=request.load_percentage,
        health=request.health_percentage,
        temperature=request.temperature,
        component_id=request.component_id or "SUB",
        component_name=request.component_name or "Substation",
    )


@router.get("/fuzzy/rules")
def get_fuzzy_rule_catalog():
    """Returns the complete documented Mamdani fuzzy rule catalog for academic explanation."""
    rules = get_rule_base()
    return [
        {
            "rule_id": r.rule_id,
            "load": r.load,
            "health": r.health,
            "temperature": r.temp,
            "risk_consequent": r.risk,
            "description": r.description,
        }
        for r in rules
    ]


# ==========================================
# 2. A* Search Endpoints
# ==========================================

@router.post("/astar/find-route", response_model=AStarRouteResult)
def find_astar_route(request: AStarRouteRequest):
    """Executes capacity-constrained A* search with admissible heuristic on the current network graph."""
    return astar_search(simulation_service.current_network, request)


# ==========================================
# 3. Genetic Algorithm Endpoints
# ==========================================

@router.post("/genetic/optimize", response_model=GARecoveryResult)
def optimize_with_ga(config: Optional[GAConfig] = None):
    """Executes Genetic Algorithm optimization to generate an optimal grid recovery strategy."""
    if config is None:
        config = GAConfig()
    return optimize_recovery_strategy(simulation_service.current_network, config)
