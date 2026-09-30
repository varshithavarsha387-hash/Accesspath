from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AccessibilityProfile(BaseModel):
    user_type: str = Field(default="wheelchair", description="wheelchair, visually_impaired, older_adult, temporary_injury, custom")
    avoid_stairs: bool = True
    avoid_steep_slopes: bool = True
    prefer_ramps: bool = True
    prefer_elevators: bool = True
    avoid_broken_footpaths: bool = True
    prefer_safe_crossings: bool = True
    prefer_smooth_paths: bool = True
    voice_enabled: bool = True
    vibration_enabled: bool = True
    language: str = "en" # "en", "te", "hi"

class UserProfile(BaseModel):
    id: str = "user-default"
    name: str = "Demo User"
    email: Optional[str] = "user@accesspath.local"
    accessibility_profile: AccessibilityProfile = Field(default_factory=AccessibilityProfile)
    language: str = "en"
    voice_enabled: bool = True
    vibration_enabled: bool = True

class LocationPoint(BaseModel):
    name: str
    latitude: float
    longitude: float

class Barrier(BaseModel):
    id: str
    type: str  # stairs, blocked_ramp, broken_footpath, obstacle, unsafe_crossing, broken_elevator, steep_slope, narrow_pathway
    title: str
    description: str
    latitude: float
    longitude: float
    photo_url: Optional[str] = None
    timestamp: str
    reporter: str = "AccessPath Community"
    ai_confidence: float = 0.92
    verification_status: str = "Verified"  # New, Verified, Expired, Resolved
    temporary: bool = True
    expires_at: Optional[str] = None
    severity: str = "high"  # high, medium, low
    impact_summary: str = "May obstruct wheelchair and mobility aid users."

class BarrierReportRequest(BaseModel):
    type: str
    description: str
    latitude: float
    longitude: float
    photo_base64: Optional[str] = None
    reporter: Optional[str] = "Community User"
    temporary: Optional[bool] = True
    duration_hours: Optional[int] = 48
    ai_confidence: Optional[float] = 0.90

class RouteStep(BaseModel):
    instruction_en: str
    instruction_te: str
    instruction_hi: str
    distance_m: int
    duration_s: int
    turn_type: str  # straight, left, right, ramp, warning, destination
    latitude: float
    longitude: float
    barrier_warning: Optional[str] = None

class ScoreItem(BaseModel):
    label: str
    value: int
    is_positive: bool
    icon: str

class ScoreBreakdown(BaseModel):
    base_score: int
    total_score: int
    positive_factors: List[ScoreItem]
    penalties: List[ScoreItem]
    why_explanation: List[str]
    freshness_note: str

class RouteOption(BaseModel):
    id: str
    name: str
    mode: str  # fastest, accessible, safest
    distance_km: float
    duration_minutes: int
    accessibility_score: int
    recommended: bool
    badge_text: Optional[str] = None
    recommendation_reason: str
    issues: List[str]
    features: List[str]
    score_breakdown: ScoreBreakdown
    coordinates: List[List[float]]  # [[lat, lng], ...]
    barriers: List[Barrier]
    steps: List[RouteStep]

class RouteCalculateRequest(BaseModel):
    from_name: str
    from_lat: float
    from_lng: float
    to_name: str
    to_lat: float
    to_lng: float
    profile: Optional[AccessibilityProfile] = None
    avoid_barrier_ids: List[str] = []

class RouteCalculateResponse(BaseModel):
    from_point: LocationPoint
    to_point: LocationPoint
    routes: List[RouteOption]
    active_profile: AccessibilityProfile
    is_demo: bool = False
    message: Optional[str] = None

class AIDetectionResponse(BaseModel):
    detected_barrier: str
    barrier_type: str
    confidence: float
    explanation: str
    suggested_severity: str
    image_url: Optional[str] = None

class VoiceNLPResponse(BaseModel):
    transcript: str
    detected_barrier_type: str
    barrier_title: str
    confidence: float
    extracted_notes: str

class DashboardStats(BaseModel):
    nearby_barriers_count: int
    verified_ramps_count: int
    blocked_paths_count: int
    recent_reports_count: int
    recent_reports: List[Barrier]
    active_alerts: List[Dict[str, Any]]
