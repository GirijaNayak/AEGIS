"""
Data models for AI Recovery: Fuzzy Risk Assessment, A* Pathfinding, and Genetic Algorithm Strategy Optimization.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# ==========================================
# 1. Fuzzy Logic Models
# ==========================================

class FuzzyInputValues(BaseModel):
    load_percentage: float = Field(..., ge=0.0, le=100.0, description="Current load as % of capacity")
    health_percentage: float = Field(..., ge=0.0, le=100.0, description="Equipment health index %")
    temperature: float = Field(..., ge=0.0, le=120.0, description="Operating temperature in °C")


class MembershipDegrees(BaseModel):
    low: float = 0.0
    medium: float = 0.0
    high: float = 0.0


class HealthMemberships(BaseModel):
    poor: float = 0.0
    average: float = 0.0
    good: float = 0.0


class TemperatureMemberships(BaseModel):
    normal: float = 0.0
    elevated: float = 0.0
    critical: float = 0.0


class ActivatedFuzzyRule(BaseModel):
    rule_id: int
    antecedent: str
    consequent: str
    firing_strength: float


class FuzzyEvaluationResult(BaseModel):
    component_id: str
    component_name: str
    inputs: FuzzyInputValues
    load_memberships: MembershipDegrees
    health_memberships: HealthMemberships
    temperature_memberships: TemperatureMemberships
    activated_rules: List[ActivatedFuzzyRule]
    aggregated_risk_distribution: List[float] = Field(..., description="101 discrete sample points from 0 to 100 for defuzzification")
    defuzzified_risk_score: float = Field(..., description="Exact Centroid Defuzzified score 0-100")
    risk_category: str = Field(..., description="Low, Moderate, High, or Critical")
    explanation: str


# ==========================================
# 2. A* Search Models
# ==========================================

class AStarRouteRequest(BaseModel):
    source_id: str
    destination_id: str
    required_capacity: float = Field(default=10.0, description="Required transmission capacity in MW")
    avoid_node_ids: List[str] = Field(default_factory=list)
    avoid_edge_ids: List[str] = Field(default_factory=list)


class ExploredNodeStep(BaseModel):
    step: int
    node_id: str
    node_name: str
    g_cost: float
    h_cost: float
    f_cost: float
    parent_id: Optional[str] = None


class AStarRouteResult(BaseModel):
    source_id: str
    destination_id: str
    path_found: bool
    path_nodes: List[str]
    path_node_names: List[str]
    path_edges: List[str]
    total_cost: float
    total_distance_km: float
    bottleneck_capacity_mw: float
    nodes_explored_count: int
    exploration_steps: List[ExploredNodeStep] = []
    admissible_heuristic_used: str = "Scaled Euclidean Distance to Destination"
    explanation: str


# ==========================================
# 3. Genetic Algorithm Models
# ==========================================

class GAConfig(BaseModel):
    population_size: int = Field(default=50, ge=10, le=200)
    generations: int = Field(default=40, ge=5, le=150)
    crossover_rate: float = Field(default=0.8, ge=0.1, le=1.0)
    mutation_rate: float = Field(default=0.15, ge=0.01, le=0.5)
    elitism_count: int = Field(default=2, ge=1, le=10)
    tournament_size: int = Field(default=3, ge=2, le=8)
    random_seed: Optional[int] = Field(default=42)
    # Objective weights:
    weight_unserved: float = Field(default=10.0, description="w1: Unserved demand penalty")
    weight_recovery_time: float = Field(default=1.5, description="w2: Recovery operational time")
    weight_resource_cost: float = Field(default=0.8, description="w3: Fuel and backup resource usage cost")
    weight_overload: float = Field(default=25.0, description="w4: Overloaded connection penalty")
    weight_critical: float = Field(default=50.0, description="w5: Critical facility (hospital) loss penalty")


class ChromosomeDecisions(BaseModel):
    generator_dispatch: Dict[str, float] = Field(..., description="Generator ID to dispatched MW")
    line_switches: Dict[str, bool] = Field(..., description="Transmission Line ID to active state")
    consumer_curtailment: Dict[str, float] = Field(..., description="Consumer ID to curtailed fraction [0.0 - 1.0]")


class GenerationMetric(BaseModel):
    generation: int
    best_fitness: float
    average_fitness: float
    best_cost: float
    unserved_demand_mw: float
    critical_unserved_mw: float


class BaselineComparison(BaseModel):
    strategy_name: str
    cost: float
    fitness: float
    unserved_demand_mw: float
    critical_unserved_mw: float
    generators_used_mw: float
    recovery_time_min: float


class GARecoveryResult(BaseModel):
    best_fitness: float
    best_cost: float
    best_chromosome: ChromosomeDecisions
    generations_history: List[GenerationMetric]
    execution_time_ms: float
    is_valid: bool
    validation_notes: List[str]
    baseline_comparison: BaselineComparison
    explanation: str


# ==========================================
# 4. End-to-End Recovery Pipeline Models
# ==========================================

class RecoveryAnalysisResponse(BaseModel):
    failed_components: List[str]
    isolated_substations: List[str]
    affected_consumers: List[str]
    unserved_demand_mw: float
    critical_unserved_mw: float
    fuzzy_risk_assessments: List[FuzzyEvaluationResult]
    alternative_astar_routes: List[AStarRouteResult]
    recommended_ga_plan: Optional[GARecoveryResult] = None
    summary: str


class RecoveryExecutionRequest(BaseModel):
    recovery_plan: ChromosomeDecisions


class RecoveryExecutionResponse(BaseModel):
    success: bool
    plan_applied: ChromosomeDecisions
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    improvements: Dict[str, Any]
    status_message: str
