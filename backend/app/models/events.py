"""
Data models for simulation events, failure injections, and grid performance metrics.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class FailureType(str, Enum):
    POWER_STATION_FAILURE = "power_station_failure"
    SUBSTATION_FAILURE = "substation_failure"
    TRANSMISSION_LINE_FAILURE = "transmission_line_failure"
    CAPACITY_REDUCTION = "capacity_reduction"
    MULTIPLE_FAILURES = "multiple_failures"


class FailureInjectionRequest(BaseModel):
    component_id: str
    component_type: str
    failure_type: FailureType
    severity: float = Field(default=1.0, ge=0.0, le=1.0, description="1.0 = total failure, < 1.0 = partial degradation")
    description: Optional[str] = None


class MultipleFailureRequest(BaseModel):
    failures: List[FailureInjectionRequest]
    description: Optional[str] = "Multiple simultaneous infrastructure failure injection"


class CascadingEventStep(BaseModel):
    step_number: int
    component_id: str
    component_name: str
    component_type: str
    event_reason: str
    flow_before: float
    capacity: float
    overload_percentage: float
    new_status: str


class EventLogEntry(BaseModel):
    id: str
    timestamp: str
    component_id: str
    component_name: str
    event_type: str
    severity: float
    directly_affected_components: List[str]
    secondary_effects: List[str]
    cascading_steps: List[CascadingEventStep] = []
    description: str


class SimulationMetrics(BaseModel):
    total_demand: float
    total_generation_capacity: float
    current_generation: float
    total_supplied_power: float
    unserved_demand: float
    restoration_percentage: float
    critical_facilities_total: int
    critical_facilities_supplied: int
    critical_facilities_unserved: int
    critical_unserved_demand: float
    operational_components_count: int
    failed_components_count: int
    overloaded_lines_count: int
    grid_reliability_index: float  # Percentage (0-100)
    system_health_average: float   # Percentage (0-100)
