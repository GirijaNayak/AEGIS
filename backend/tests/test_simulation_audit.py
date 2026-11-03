"""
Independent Physical & Simulation Audit Tests for AEGIS Infrastructure Engine.
Tests:
1. Exact Kirchhoff-like flow conservation: sum(generation) == sum(supplied_power).
2. Substation DEGRADED operational status preservation after derating.
3. Dual-feeder critical facility rerouting: St. Jude Hospital (HOSP1) surviving SUB3 failure via SUB1 backup feeder.
4. Source generation capacity clamping: no source can supply more than its physical rating.
"""

import pytest
from app.simulation.default_network import get_default_network
from app.models.infrastructure import OperationalStatus, ConsumerCategory
from app.simulation.load_distribution import calculate_load_distribution
from app.simulation.failure_engine import inject_failure
from app.models.events import FailureInjectionRequest, FailureType


def test_flow_conservation_normal_and_stressed():
    """
    Verifies that total power generation across all power stations and active backup generators
    strictly equals the total power supplied to consumers:
    sum(P_gen) == sum(P_supplied), with floating point tolerance <= 0.05 MW.
    """
    # 1. Normal equilibrium
    network = get_default_network()
    metrics = calculate_load_distribution(network)

    total_gen = sum(ps.current_generation for ps in network.power_stations) + sum(
        bg.current_utilization for bg in network.backup_generators if bg.is_active
    )
    total_supplied = sum(c.supplied_power for c in network.consumers)

    assert abs(total_gen - total_supplied) < 0.05, (
        f"Flow conservation violation in normal grid: Total Gen={total_gen} MW vs Supplied={total_supplied} MW"
    )
    assert abs(metrics.current_generation - metrics.total_supplied_power) < 0.05

    # 2. Stressed state with partial line trips
    for line in network.transmission_lines:
        if line.id in ["TL5", "TL9"]:
            line.operational_status = OperationalStatus.FAILED

    stressed_metrics = calculate_load_distribution(network)
    total_gen_stressed = sum(ps.current_generation for ps in network.power_stations) + sum(
        bg.current_utilization for bg in network.backup_generators if bg.is_active
    )
    total_supplied_stressed = sum(c.supplied_power for c in network.consumers)

    assert abs(total_gen_stressed - total_supplied_stressed) < 0.05, (
        f"Flow conservation violation under stress: Total Gen={total_gen_stressed} MW vs Supplied={total_supplied_stressed} MW"
    )


def test_substation_degraded_status_preservation():
    """
    Verifies that substations with impaired health (<80%) maintain DEGRADED status
    and are not erroneously overwritten to OPERATIONAL by load distribution.
    """
    network = get_default_network()
    sub2 = next(s for s in network.substations if s.id == "SUB2")
    sub2.health_percentage = 65.0
    sub2.operational_status = OperationalStatus.DEGRADED

    calculate_load_distribution(network)

    assert sub2.operational_status == OperationalStatus.DEGRADED, (
        f"Substation SUB2 status was overwritten to {sub2.operational_status} instead of DEGRADED"
    )


def test_dual_feeder_hospital_transfer_on_substation_failure():
    """
    Verifies that when primary substation SUB3 fails, critical facility HOSP1 (St. Jude Medical Center)
    transfers to its dual-feeder backup substation SUB1 and remains powered.
    """
    network = get_default_network()
    hosp1 = next(c for c in network.consumers if c.id == "HOSP1")
    assert hosp1.connected_substation_id == "SUB3"
    assert hosp1.backup_substation_id == "SUB1"

    # Fail SUB3
    sub3 = next(s for s in network.substations if s.id == "SUB3")
    sub3.operational_status = OperationalStatus.FAILED

    metrics = calculate_load_distribution(network)

    # HOSP1 should remain supplied through SUB1
    assert hosp1.operational_status in [OperationalStatus.OPERATIONAL, OperationalStatus.DEGRADED], (
        f"HOSP1 failed completely despite functional dual-feeder backup SUB1! Status={hosp1.operational_status}"
    )
    assert hosp1.supplied_power > 0.0, f"HOSP1 supplied power is {hosp1.supplied_power} MW"

    # Non-dual-feeder consumer on SUB3 (e.g. IND2) should be FAILED
    ind2 = next(c for c in network.consumers if c.id == "IND2")
    assert ind2.operational_status == OperationalStatus.FAILED
    assert ind2.supplied_power == 0.0


def test_source_generation_capacity_bounds():
    """
    Verifies that no power station or generator is ever dispatched beyond its rated capacity.
    """
    network = get_default_network()
    # Artificially inflate consumer demand to 5000 MW to test boundary saturation
    for c in network.consumers:
        c.demand = 500.0

    calculate_load_distribution(network)

    for ps in network.power_stations:
        assert ps.current_generation <= ps.generation_capacity + 1e-4, (
            f"Power Station {ps.id} dispatched {ps.current_generation} MW exceeding capacity {ps.generation_capacity} MW"
        )

    for bg in network.backup_generators:
        if bg.is_active:
            assert bg.current_utilization <= bg.capacity + 1e-4, (
                f"Generator {bg.id} utilized {bg.current_utilization} MW exceeding capacity {bg.capacity} MW"
            )
