"""
Failure injection and cascading failure simulation engine for AEGIS.
Handles component failure injection, thermal overload propagation, cascading disconnects,
and chronological event logging.
"""

import datetime
import uuid
from typing import Dict, List, Optional, Tuple
from app.models.infrastructure import (
    InfrastructureNetwork,
    OperationalStatus,
    ComponentType,
)
from app.models.events import (
    FailureType,
    FailureInjectionRequest,
    MultipleFailureRequest,
    CascadingEventStep,
    EventLogEntry,
    SimulationMetrics,
)
from app.simulation.load_distribution import calculate_load_distribution


def inject_failure(
    network: InfrastructureNetwork,
    request: FailureInjectionRequest,
) -> Tuple[EventLogEntry, SimulationMetrics]:
    """
    Injects a single failure into the network and computes immediate + cascading consequences.
    """
    target_id = request.component_id
    comp_type = request.component_type.lower()
    comp_name = target_id
    directly_affected = [target_id]
    secondary_effects = []
    cascade_steps: List[CascadingEventStep] = []

    # 1. Apply primary failure
    if comp_type in ["power_station", "station"] or target_id.startswith("PS"):
        for ps in network.power_stations:
            if ps.id == target_id:
                comp_name = ps.name
                if request.failure_type == FailureType.CAPACITY_REDUCTION:
                    ps.generation_capacity = round(ps.generation_capacity * (1.0 - request.severity), 2)
                    ps.health_percentage = round(ps.health_percentage * (1.0 - request.severity), 1)
                    ps.operational_status = OperationalStatus.DEGRADED
                else:
                    ps.operational_status = OperationalStatus.FAILED
                    ps.health_percentage = 0.0
                    ps.current_generation = 0.0
                break

    elif comp_type in ["substation", "sub"] or target_id.startswith("SUB"):
        for sub in network.substations:
            if sub.id == target_id:
                comp_name = sub.name
                if request.failure_type == FailureType.CAPACITY_REDUCTION:
                    sub.max_capacity = round(sub.max_capacity * (1.0 - request.severity), 2)
                    sub.health_percentage = round(sub.health_percentage * (1.0 - request.severity), 1)
                    sub.operational_status = OperationalStatus.DEGRADED
                else:
                    sub.operational_status = OperationalStatus.FAILED
                    sub.health_percentage = 0.0
                    sub.current_load = 0.0
                    sub.temperature = 110.0
                break
        
        # When a substation fails completely, mark all directly connected lines as unavailable
        if request.failure_type != FailureType.CAPACITY_REDUCTION:
            for line in network.transmission_lines:
                if line.source_id == target_id or line.destination_id == target_id:
                    line.operational_status = OperationalStatus.FAILED
                    directly_affected.append(line.id)

    elif "line" in comp_type or target_id.startswith("TL"):
        for line in network.transmission_lines:
            if line.id == target_id:
                comp_name = f"Line {line.id} ({line.source_id}->{line.destination_id})"
                if request.failure_type == FailureType.CAPACITY_REDUCTION:
                    line.max_capacity = round(line.max_capacity * (1.0 - request.severity), 2)
                    line.operational_status = OperationalStatus.DEGRADED
                else:
                    line.operational_status = OperationalStatus.FAILED
                    line.current_flow = 0.0
                break

    # 2. Run initial load distribution after primary failure
    metrics = calculate_load_distribution(network)

    # 3. Simulate cascading failure loop (thermal overloads tripping lines)
    max_cascade_depth = 4
    step_num = 1

    for depth in range(max_cascade_depth):
        tripped_in_this_step = False
        
        # Check transmission lines for catastrophic overload (> 125% rating)
        for line in network.transmission_lines:
            if line.operational_status == OperationalStatus.OVERLOADED:
                overload_pct = (line.current_flow / max(1.0, line.max_capacity)) * 100.0
                if overload_pct >= 125.0:
                    line.operational_status = OperationalStatus.FAILED
                    line_name = f"Line {line.id} ({line.source_id}->{line.destination_id})"
                    cascade_steps.append(
                        CascadingEventStep(
                            step_number=step_num,
                            component_id=line.id,
                            component_name=line_name,
                            component_type="transmission_line",
                            event_reason=f"Severe thermal overload ({round(overload_pct, 1)}% of {line.max_capacity} MW rating) exceeded protection threshold",
                            flow_before=line.current_flow,
                            capacity=line.max_capacity,
                            overload_percentage=round(overload_pct, 1),
                            new_status="FAILED",
                        )
                    )
                    secondary_effects.append(f"Line {line.id} tripped due to severe thermal overload ({round(overload_pct, 1)}%)")
                    step_num += 1
                    tripped_in_this_step = True
                    break  # Recalculate load distribution after each trip

        if tripped_in_this_step:
            metrics = calculate_load_distribution(network)
        else:
            break

    # 4. Construct detailed event log entry
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    desc = request.description or f"{request.failure_type.value.replace('_', ' ').title()} on {comp_name}"
    
    event_entry = EventLogEntry(
        id=str(uuid.uuid4())[:8],
        timestamp=timestamp_str,
        component_id=target_id,
        component_name=comp_name,
        event_type=request.failure_type.value,
        severity=request.severity,
        directly_affected_components=directly_affected,
        secondary_effects=secondary_effects,
        cascading_steps=cascade_steps,
        description=desc,
    )

    return event_entry, metrics
