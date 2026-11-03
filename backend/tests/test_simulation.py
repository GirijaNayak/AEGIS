"""
Unit tests for the infrastructure simulation and failure propagation engine.
"""

import pytest
from app.simulation.default_network import get_default_network
from app.simulation.load_distribution import calculate_load_distribution
from app.simulation.failure_engine import inject_failure
from app.models.events import FailureInjectionRequest, FailureType
from app.models.infrastructure import OperationalStatus


def test_initial_network_equilibrium():
    network = get_default_network()
    metrics = calculate_load_distribution(network)

    assert metrics.total_demand > 300.0
    assert metrics.unserved_demand == 0.0
    assert metrics.critical_unserved_demand == 0.0
    assert metrics.critical_facilities_unserved == 0
    assert metrics.grid_reliability_index >= 95.0


def test_power_station_failure():
    network = get_default_network()
    # Trip Power Station 1 (450 MW)
    event, metrics = inject_failure(network, FailureInjectionRequest(
        component_id="PS1",
        component_type="power_station",
        failure_type=FailureType.POWER_STATION_FAILURE,
    ))

    ps1 = next(ps for ps in network.power_stations if ps.id == "PS1")
    assert ps1.operational_status == OperationalStatus.FAILED
    assert ps1.health_percentage == 0.0
    assert metrics.failed_components_count >= 1
    assert event.component_id == "PS1"


def test_substation_failure_disconnects_connected_lines():
    network = get_default_network()
    # Trip SUB3
    event, metrics = inject_failure(network, FailureInjectionRequest(
        component_id="SUB3",
        component_type="substation",
        failure_type=FailureType.SUBSTATION_FAILURE,
    ))

    sub3 = next(s for s in network.substations if s.id == "SUB3")
    assert sub3.operational_status == OperationalStatus.FAILED
    
    # Lines attached to SUB3 should be marked failed
    sub3_lines = [l for l in network.transmission_lines if l.source_id == "SUB3" or l.destination_id == "SUB3"]
    for l in sub3_lines:
        assert l.operational_status == OperationalStatus.FAILED

    # Consumers attached to SUB3 (like HOSP1 and IND2) should have unserved demand
    hosp1 = next(c for c in network.consumers if c.id == "HOSP1")
    assert hosp1.supplied_power == 0.0
    assert metrics.unserved_demand > 0.0
