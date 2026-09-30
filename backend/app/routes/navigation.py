from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ..models.schemas import RouteOption, RouteStep, AccessibilityProfile, LocationPoint
from ..services.routing import calculate_multi_routes

router = APIRouter(prefix="/api/navigation", tags=["navigation"])

ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

@router.post("/start")
def start_navigation(data: Dict[str, Any]):
    session_id = data.get("session_id", "session-active")
    route = data.get("route")
    profile = data.get("profile")

    if not route:
        raise HTTPException(status_code=400, detail="Route data is required to start navigation.")

    ACTIVE_SESSIONS[session_id] = {
        "session_id": session_id,
        "route": route,
        "profile": profile,
        "current_step_index": 0,
        "status": "in_progress"
    }

    return {
        "session_id": session_id,
        "status": "started",
        "route_name": route.get("name"),
        "total_steps": len(route.get("steps", [])),
        "initial_step": route.get("steps", [])[0] if route.get("steps") else None
    }

@router.get("/{session_id}")
def get_navigation_status(session_id: str):
    if session_id in ACTIVE_SESSIONS:
        return ACTIVE_SESSIONS[session_id]
    raise HTTPException(status_code=404, detail="Navigation session not found.")

@router.post("/reroute")
def reroute_around_barrier(data: Dict[str, Any]):
    """
    Dynamic Re-routing: When a user encounters a barrier during navigation,
    recalculates an alternative accessible path that avoids the detected barrier!
    """
    barrier_id = data.get("barrier_id")
    from_pt_data = data.get("from_point", {})
    to_pt_data = data.get("to_point", {})
    profile_data = data.get("profile", {})

    from_pt = LocationPoint(
        name=from_pt_data.get("name", "Current Location"),
        latitude=from_pt_data.get("latitude", 17.4483),
        longitude=from_pt_data.get("longitude", 78.3915)
    )
    to_pt = LocationPoint(
        name=to_pt_data.get("name", "Destination"),
        latitude=to_pt_data.get("latitude", 17.4401),
        longitude=to_pt_data.get("longitude", 78.3489)
    )
    profile = AccessibilityProfile(**profile_data) if profile_data else AccessibilityProfile()

    avoid_ids = [barrier_id] if barrier_id else []
    new_routes = calculate_multi_routes(from_pt, to_pt, profile, avoid_barrier_ids=avoid_ids)

    # Pick the best accessible route
    recommended_route = new_routes[0]

    return {
        "message": "Alternative accessible route successfully calculated.",
        "avoided_barrier_id": barrier_id,
        "rerouted": True,
        "new_route": recommended_route.model_dump(),
        "summary": f"Alternative route is {recommended_route.distance_km} km ({recommended_route.duration_minutes} min) and avoids the detected obstruction."
    }
