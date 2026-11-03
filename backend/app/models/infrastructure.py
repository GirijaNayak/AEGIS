"""
Data models representing the electricity distribution network infrastructure.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    POWER_STATION = "power_station"
    SUBSTATION = "substation"
    TRANSMISSION_LINE = "transmission_line"
    CONSUMER = "consumer"
    BACKUP_GENERATOR = "backup_generator"


class OperationalStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    FAILED = "failed"
    OFFLINE = "offline"


class ConsumerCategory(str, Enum):
    HOSPITAL = "hospital"
    EDUCATIONAL = "educational"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    COMMERCIAL = "commercial"


class CriticalityLevel(str, Enum):
    CRITICAL = "critical"  # Priority 1 (e.g. Trauma Hospital)
    HIGH = "high"          # Priority 2 (e.g. Regular Hospital, Emergency Services)
    MEDIUM = "medium"      # Priority 3 (e.g. University, Commercial centers)
    LOW = "low"            # Priority 4-5 (e.g. Residential, Heavy industrial)


class RiskCategory(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class Position(BaseModel):
    x: float
    y: float


class PowerStation(BaseModel):
    id: str
    name: str
    generation_capacity: float = Field(..., description="Maximum generation capacity in MW")
    current_generation: float = Field(default=0.0, description="Current power dispatched in MW")
    operational_status: OperationalStatus = OperationalStatus.OPERATIONAL
    health_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    position: Position


class Substation(BaseModel):
    id: str
    name: str
    max_capacity: float = Field(..., description="Maximum throughput capacity in MW")
    current_load: float = Field(default=0.0, description="Current load traversing the substation in MW")
    health_percentage: float = Field(default=95.0, ge=0.0, le=100.0)
    temperature: float = Field(default=45.0, description="Operating temperature in degrees Celsius (0-120)")
    operational_status: OperationalStatus = OperationalStatus.OPERATIONAL
    risk_score: float = Field(default=15.0, ge=0.0, le=100.0)
    risk_category: RiskCategory = RiskCategory.LOW
    position: Position


class TransmissionLine(BaseModel):
    id: str
    source_id: str
    destination_id: str
    max_capacity: float = Field(..., description="Maximum transfer rating in MW")
    current_flow: float = Field(default=0.0, description="Current real flow in MW")
    transfer_cost: float = Field(default=1.0, description="Normalized line impedance / length cost for routing")
    operational_status: OperationalStatus = OperationalStatus.OPERATIONAL
    is_backup_feeder: bool = Field(default=False, description="Whether line is normally open tie-line / backup feeder")


class Consumer(BaseModel):
    id: str
    name: str
    category: ConsumerCategory
    demand: float = Field(..., description="Electricity demand in MW")
    supplied_power: float = Field(default=0.0, description="Current supplied power in MW")
    criticality: CriticalityLevel = CriticalityLevel.MEDIUM
    priority: int = Field(default=3, ge=1, le=5, description="1 is highest priority (Hospital), 5 is lowest (Industrial)")
    connected_substation_id: str
    operational_status: OperationalStatus = OperationalStatus.OPERATIONAL
    position: Position


class BackupGenerator(BaseModel):
    id: str
    name: str
    capacity: float = Field(..., description="Maximum generator capacity in MW")
    current_utilization: float = Field(default=0.0, description="Current dispatched power in MW")
    location_substation_id: str
    operational_status: OperationalStatus = OperationalStatus.OPERATIONAL
    is_active: bool = False
    fuel_cost_per_mw: float = Field(default=25.0, description="Operating cost per MW generated")
    position: Position


class InfrastructureNetwork(BaseModel):
    power_stations: List[PowerStation]
    substations: List[Substation]
    transmission_lines: List[TransmissionLine]
    consumers: List[Consumer]
    backup_generators: List[BackupGenerator]
    name: str = "Metropolitan Electricity Grid"
    description: str = "Regional high-voltage transmission & sub-transmission distribution network"
