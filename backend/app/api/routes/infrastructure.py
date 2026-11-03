"""
API routes for querying infrastructure network components and operational metadata.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from app.services.simulation_service import simulation_service

router = APIRouter(prefix="/api/infrastructure", tags=["infrastructure"])


@router.get("", response_model=Dict[str, Any])
def get_infrastructure():
    """Returns the current state of all infrastructure network components."""
    net = simulation_service.current_network
    return net.model_dump()


@router.get("/components/{component_id}")
def get_component_details(component_id: str):
    """Returns detailed operational attributes and telemetry for an individual component."""
    net = simulation_service.current_network
    
    # Check power stations
    for ps in net.power_stations:
        if ps.id == component_id:
            return {"type": "power_station", "data": ps.model_dump()}

    # Check substations
    for sub in net.substations:
        if sub.id == component_id:
            connected_lines = [l.id for l in net.transmission_lines if l.source_id == sub.id or l.destination_id == sub.id]
            connected_consumers = [c.name for c in net.consumers if c.connected_substation_id == sub.id]
            return {
                "type": "substation",
                "data": sub.model_dump(),
                "connected_lines": connected_lines,
                "connected_consumers": connected_consumers,
            }

    # Check transmission lines
    for line in net.transmission_lines:
        if line.id == component_id:
            return {"type": "transmission_line", "data": line.model_dump()}

    # Check consumers
    for cons in net.consumers:
        if cons.id == component_id:
            return {"type": "consumer", "data": cons.model_dump()}

    # Check backup generators
    for bg in net.backup_generators:
        if bg.id == component_id:
            return {"type": "backup_generator", "data": bg.model_dump()}

    raise HTTPException(status_code=404, detail=f"Component {component_id} not found in infrastructure network.")
