from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from ..models.schemas import (
    RouteCalculateRequest, RouteCalculateResponse, LocationPoint,
    AccessibilityProfile, RouteOption
)
from ..services.routing import calculate_multi_routes

router = APIRouter(prefix="/api/routes", tags=["routes"])

# In-memory storage for active session routes
ROUTES_CACHE = {}

@router.post("/calculate", response_model=RouteCalculateResponse)
def calculate_routes_endpoint(req: RouteCalculateRequest):
    if req.from_lat == req.to_lat and req.from_lng == req.to_lng:
        raise HTTPException(status_code=400, detail="Starting point and destination cannot be the same location.")
    
    profile = req.profile or AccessibilityProfile()
    from_pt = LocationPoint(name=req.from_name, latitude=req.from_lat, longitude=req.from_lng)
    to_pt = LocationPoint(name=req.to_name, latitude=req.to_lat, longitude=req.to_lng)

    routes = calculate_multi_routes(
        from_point=from_pt,
        to_point=to_pt,
        profile=profile,
        avoid_barrier_ids=req.avoid_barrier_ids
    )

    for r in routes:
        ROUTES_CACHE[r.id] = r

    return RouteCalculateResponse(
        from_point=from_pt,
        to_point=to_pt,
        routes=routes,
        active_profile=profile,
        is_demo=False,
        message="Route calculated successfully."
    )

@router.get("")
def get_routes_query(
    from_lat: float = Query(...),
    from_lng: float = Query(...),
    to_lat: float = Query(...),
    to_lng: float = Query(...),
    from_name: str = Query("Starting Point"),
    to_name: str = Query("Destination"),
    user_type: str = Query("wheelchair"),
    avoid_stairs: bool = Query(True),
    avoid_steep_slopes: bool = Query(True),
    prefer_ramps: bool = Query(True)
):
    profile = AccessibilityProfile(
        user_type=user_type,
        avoid_stairs=avoid_stairs,
        avoid_steep_slopes=avoid_steep_slopes,
        prefer_ramps=prefer_ramps
    )
    from_pt = LocationPoint(name=from_name, latitude=from_lat, longitude=from_lng)
    to_pt = LocationPoint(name=to_name, latitude=to_lat, longitude=to_lng)

    routes = calculate_multi_routes(from_pt, to_pt, profile)
    for r in routes:
        ROUTES_CACHE[r.id] = r

    return {
        "from": from_pt.model_dump(),
        "to": to_pt.model_dump(),
        "routes": [r.model_dump() for r in routes]
    }

@router.get("/{route_id}", response_model=RouteOption)
def get_route_by_id(route_id: str):
    if route_id in ROUTES_CACHE:
        return ROUTES_CACHE[route_id]
    raise HTTPException(status_code=404, detail="Route not found.")
