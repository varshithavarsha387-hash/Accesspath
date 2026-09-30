from fastapi import APIRouter
from typing import Dict, Any, List
from ..models.schemas import DashboardStats, Barrier
from ..database.db import get_all_barriers

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("", response_model=DashboardStats)
def get_dashboard_summary():
    all_b = get_all_barriers()
    
    # Counts
    nearby_barriers_count = len(all_b)
    blocked_paths_count = sum(1 for b in all_b if b["type"] in ["blocked_ramp", "broken_footpath", "obstacle"])
    verified_ramps_count = 12 # Audited municipal ramp points
    recent_reports_count = sum(1 for b in all_b if b.get("verification_status") in ["New", "Verified"])

    active_alerts = [
        {
            "id": "alert-1",
            "title": "Road 36 Construction Work",
            "type": "warning",
            "description": "Footpath excavation underway near Metro Pillar 1042. Use service lane ramp."
        },
        {
            "id": "alert-2",
            "title": "Tactile Paving Upgrade Complete",
            "type": "success",
            "description": "Continuous tactile paving and audio beacons verified along Gachibowli junction."
        }
    ]

    return DashboardStats(
        nearby_barriers_count=nearby_barriers_count,
        verified_ramps_count=verified_ramps_count,
        blocked_paths_count=blocked_paths_count,
        recent_reports_count=recent_reports_count,
        recent_reports=[Barrier(**b) for b in all_b[:6]],
        active_alerts=active_alerts
    )
