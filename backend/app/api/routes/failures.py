"""
API routes for manual failure injection and event history retrieval.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from app.services.simulation_service import simulation_service
from app.models.events import FailureInjectionRequest, MultipleFailureRequest, EventLogEntry

router = APIRouter(prefix="/api/failures", tags=["failures"])


@router.post("/trigger")
def trigger_failure_event(request: FailureInjectionRequest):
    """Triggers an infrastructure failure on a specific component with cascading effects."""
    event, metrics = simulation_service.trigger_failure(request)
    return {
        "status": "success",
        "event": event.model_dump(),
        "metrics": metrics.model_dump(),
        "network": simulation_service.current_network.model_dump(),
    }


@router.post("/multiple")
def trigger_multiple_failures(request: MultipleFailureRequest):
    """Triggers a batch sequence of simultaneous failures."""
    events = []
    for fail_req in request.failures:
        event, metrics = simulation_service.trigger_failure(fail_req)
        events.append(event.model_dump())

    return {
        "status": "success",
        "events": events,
        "metrics": simulation_service.metrics.model_dump(),
        "network": simulation_service.current_network.model_dump(),
    }


@router.get("/history", response_model=List[EventLogEntry])
def get_failure_history():
    """Returns the chronological audit log of all failure and cascading events."""
    return simulation_service.event_history
