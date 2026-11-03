"""
Default infrastructure network topology for AEGIS.
Configures 2 Power Stations, 6 Substations, 16 Transmission Lines, 12 Consumers, and 2 Backup Generators.
"""

import copy
from typing import Dict, Any
from app.models.infrastructure import (
    InfrastructureNetwork,
    PowerStation,
    Substation,
    TransmissionLine,
    Consumer,
    BackupGenerator,
    Position,
    OperationalStatus,
    ConsumerCategory,
    CriticalityLevel,
    RiskCategory,
)


def get_default_network() -> InfrastructureNetwork:
    """Returns a freshly instantiated default infrastructure network."""

    power_stations = [
        PowerStation(
            id="PS1",
            name="Grand Hydroelectric Station",
            generation_capacity=450.0,
            current_generation=230.0,
            operational_status=OperationalStatus.OPERATIONAL,
            health_percentage=98.0,
            position=Position(x=140, y=100),
        ),
        PowerStation(
            id="PS2",
            name="East Thermal Station",
            generation_capacity=350.0,
            current_generation=183.0,
            operational_status=OperationalStatus.OPERATIONAL,
            health_percentage=94.0,
            position=Position(x=780, y=100),
        ),
    ]

    substations = [
        Substation(
            id="SUB1",
            name="North Gateway 230kV Substation",
            max_capacity=250.0,
            current_load=63.0,
            health_percentage=95.0,
            temperature=44.0,
            operational_status=OperationalStatus.OPERATIONAL,
            risk_score=14.0,
            risk_category=RiskCategory.LOW,
            position=Position(x=280, y=260),
        ),
        Substation(
            id="SUB2",
            name="Central Distribution 115kV Substation",
            max_capacity=220.0,
            current_load=75.0,
            health_percentage=92.0,
            temperature=48.0,
            operational_status=OperationalStatus.OPERATIONAL,
            risk_score=18.0,
            risk_category=RiskCategory.LOW,
            position=Position(x=500, y=260),
        ),
        Substation(
            id="SUB3",
            name="Metro Core 115kV Substation",
            max_capacity=200.0,
            current_load=95.0,
            health_percentage=90.0,
            temperature=52.0,
            operational_status=OperationalStatus.OPERATIONAL,
            risk_score=22.0,
            risk_category=RiskCategory.LOW,
            position=Position(x=320, y=460),
        ),
        Substation(
            id="SUB4",
            name="South Valley 115kV Substation",
            max_capacity=180.0,
            current_load=55.0,
            health_percentage=94.0,
            temperature=46.0,
            operational_status=OperationalStatus.OPERATIONAL,
            risk_score=16.0,
            risk_category=RiskCategory.LOW,
            position=Position(x=640, y=460),
        ),
        Substation(
            id="SUB5",
            name="Industrial Park 115kV Substation",
            max_capacity=220.0,
            current_load=100.0,
            health_percentage=89.0,
            temperature=54.0,
            operational_status=OperationalStatus.OPERATIONAL,
            risk_score=24.0,
            risk_category=RiskCategory.LOW,
            position=Position(x=760, y=290),
        ),
        Substation(
            id="SUB6",
            name="West Hills 115kV Substation",
            max_capacity=150.0,
            current_load=50.0,
            health_percentage=96.0,
            temperature=42.0,
            operational_status=OperationalStatus.OPERATIONAL,
            risk_score=12.0,
            risk_category=RiskCategory.LOW,
            position=Position(x=120, y=430),
        ),
    ]

    transmission_lines = [
        TransmissionLine(id="TL1", source_id="PS1", destination_id="SUB1", max_capacity=260.0, current_flow=150.0, transfer_cost=1.5, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL2", source_id="PS1", destination_id="SUB6", max_capacity=160.0, current_flow=80.0, transfer_cost=2.2, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL3", source_id="PS2", destination_id="SUB5", max_capacity=240.0, current_flow=110.0, transfer_cost=1.6, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL4", source_id="PS2", destination_id="SUB2", max_capacity=200.0, current_flow=73.0, transfer_cost=2.4, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL5", source_id="SUB1", destination_id="SUB2", max_capacity=180.0, current_flow=35.0, transfer_cost=1.4, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL6", source_id="SUB1", destination_id="SUB3", max_capacity=180.0, current_flow=52.0, transfer_cost=1.8, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL7", source_id="SUB2", destination_id="SUB3", max_capacity=150.0, current_flow=25.0, transfer_cost=1.7, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL8", source_id="SUB2", destination_id="SUB4", max_capacity=160.0, current_flow=28.0, transfer_cost=1.9, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL9", source_id="SUB2", destination_id="SUB5", max_capacity=140.0, current_flow=15.0, transfer_cost=2.0, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL10", source_id="SUB3", destination_id="SUB4", max_capacity=140.0, current_flow=10.0, transfer_cost=2.1, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL11", source_id="SUB3", destination_id="SUB6", max_capacity=120.0, current_flow=8.0, transfer_cost=1.9, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL12", source_id="SUB4", destination_id="SUB5", max_capacity=150.0, current_flow=17.0, transfer_cost=2.0, operational_status=OperationalStatus.OPERATIONAL),
        TransmissionLine(id="TL13", source_id="SUB6", destination_id="SUB1", max_capacity=100.0, current_flow=0.0, transfer_cost=2.5, operational_status=OperationalStatus.OPERATIONAL),
        # Backup & emergency lines:
        TransmissionLine(id="TL14", source_id="BG1", destination_id="SUB3", max_capacity=55.0, current_flow=0.0, transfer_cost=0.5, operational_status=OperationalStatus.OPERATIONAL, is_backup_feeder=True),
        TransmissionLine(id="TL15", source_id="BG2", destination_id="SUB4", max_capacity=45.0, current_flow=0.0, transfer_cost=0.5, operational_status=OperationalStatus.OPERATIONAL, is_backup_feeder=True),
        TransmissionLine(id="TL16", source_id="SUB5", destination_id="SUB3", max_capacity=110.0, current_flow=0.0, transfer_cost=3.2, operational_status=OperationalStatus.OFFLINE, is_backup_feeder=True),
    ]

    consumers = [
        # Hospitals (Critical Priority 1)
        Consumer(id="HOSP1", name="St. Jude Medical Center", category=ConsumerCategory.HOSPITAL, demand=25.0, supplied_power=25.0, criticality=CriticalityLevel.CRITICAL, priority=1, connected_substation_id="SUB3", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=240, y=600)),
        Consumer(id="HOSP2", name="General Memorial Hospital", category=ConsumerCategory.HOSPITAL, demand=30.0, supplied_power=30.0, criticality=CriticalityLevel.CRITICAL, priority=1, connected_substation_id="SUB2", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=480, y=390)),
        Consumer(id="HOSP3", name="Westside Trauma Center", category=ConsumerCategory.HOSPITAL, demand=20.0, supplied_power=20.0, criticality=CriticalityLevel.CRITICAL, priority=1, connected_substation_id="SUB6", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=40, y=550)),
        # Educational Institutions (Priority 2)
        Consumer(id="EDU1", name="State University Campus", category=ConsumerCategory.EDUCATIONAL, demand=28.0, supplied_power=28.0, criticality=CriticalityLevel.HIGH, priority=2, connected_substation_id="SUB1", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=220, y=190)),
        Consumer(id="EDU2", name="Civic High School & Tech Center", category=ConsumerCategory.EDUCATIONAL, demand=15.0, supplied_power=15.0, criticality=CriticalityLevel.HIGH, priority=2, connected_substation_id="SUB4", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=620, y=600)),
        # Residential Areas (Priority 3-4)
        Consumer(id="RES1", name="North Hill Residential", category=ConsumerCategory.RESIDENTIAL, demand=35.0, supplied_power=35.0, criticality=CriticalityLevel.MEDIUM, priority=3, connected_substation_id="SUB1", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=360, y=180)),
        Consumer(id="RES2", name="Central Heights", category=ConsumerCategory.RESIDENTIAL, demand=45.0, supplied_power=45.0, criticality=CriticalityLevel.MEDIUM, priority=3, connected_substation_id="SUB2", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=590, y=190)),
        Consumer(id="RES3", name="South Park Community", category=ConsumerCategory.RESIDENTIAL, demand=40.0, supplied_power=40.0, criticality=CriticalityLevel.MEDIUM, priority=3, connected_substation_id="SUB4", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=730, y=420)),
        Consumer(id="RES4", name="Westwood Estates", category=ConsumerCategory.RESIDENTIAL, demand=30.0, supplied_power=30.0, criticality=CriticalityLevel.LOW, priority=4, connected_substation_id="SUB6", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=40, y=340)),
        Consumer(id="RES5", name="East Riverside District", category=ConsumerCategory.RESIDENTIAL, demand=35.0, supplied_power=35.0, criticality=CriticalityLevel.LOW, priority=4, connected_substation_id="SUB5", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=880, y=220)),
        # Industrial Facilities (Priority 5)
        Consumer(id="IND1", name="Apex Heavy Smelting Works", category=ConsumerCategory.INDUSTRIAL, demand=65.0, supplied_power=65.0, criticality=CriticalityLevel.LOW, priority=5, connected_substation_id="SUB5", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=890, y=360)),
        Consumer(id="IND2", name="Metro Logistics & Cold Storage", category=ConsumerCategory.INDUSTRIAL, demand=45.0, supplied_power=45.0, criticality=CriticalityLevel.MEDIUM, priority=4, connected_substation_id="SUB3", operational_status=OperationalStatus.OPERATIONAL, position=Position(x=380, y=590)),
    ]

    backup_generators = [
        BackupGenerator(
            id="BG1",
            name="Metro Emergency Diesel Plant",
            capacity=50.0,
            current_utilization=0.0,
            location_substation_id="SUB3",
            operational_status=OperationalStatus.OPERATIONAL,
            is_active=False,
            fuel_cost_per_mw=30.0,
            position=Position(x=190, y=480),
        ),
        BackupGenerator(
            id="BG2",
            name="Valley Quick-Start Gas Turbine",
            capacity=40.0,
            current_utilization=0.0,
            location_substation_id="SUB4",
            operational_status=OperationalStatus.OPERATIONAL,
            is_active=False,
            fuel_cost_per_mw=25.0,
            position=Position(x=780, y=480),
        ),
    ]

    return InfrastructureNetwork(
        power_stations=power_stations,
        substations=substations,
        transmission_lines=transmission_lines,
        consumers=consumers,
        backup_generators=backup_generators,
    )
