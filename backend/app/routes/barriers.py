from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional
import uuid
import base64
from datetime import datetime, timedelta
from ..models.schemas import (
    Barrier, BarrierReportRequest, AIDetectionResponse, VoiceNLPResponse
)
from ..database.db import (
    get_all_barriers, insert_barrier, update_barrier_status
)
from ..ai.barrier_detector import analyze_barrier_image
from ..ai.nlp_parser import parse_voice_transcript

router = APIRouter(prefix="/api/barriers", tags=["barriers"])

@router.get("/nearby", response_model=List[Barrier])
def get_nearby_barriers(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: float = 15.0
):
    all_b = get_all_barriers()
    # If coordinates given, we can sort or filter by proximity
    return [Barrier(**b) for b in all_b]

@router.post("/report", response_model=Barrier)
def report_barrier(report: BarrierReportRequest):
    barrier_id = f"bar-{uuid.uuid4().hex[:8]}"
    now = datetime.now()
    expires = (now + timedelta(hours=report.duration_hours or 48)).isoformat() if report.temporary else None

    # Map barrier type to readable impact
    impact_map = {
        "stairs": "Concrete stairs present; prevents wheelchair access without ramp.",
        "blocked_ramp": "Ramp pathway blocked; detour required for mobility devices.",
        "broken_footpath": "Cracked pavement; severe trip hazard for visually impaired.",
        "unsafe_crossing": "High traffic road crossing without accessible audio beacon.",
        "broken_elevator": "Elevator non-operational; requires ground-level alternative.",
        "steep_slope": "Steep gradient exceeding 8% grade; risk of wheelchair tipping.",
        "obstacle": "Pathway blocked by physical obstruction."
    }

    title_map = {
        "stairs": "Flight of Concrete Stairs",
        "blocked_ramp": "Blocked Wheelchair Ramp",
        "broken_footpath": "Broken Footpath & Drain Opening",
        "unsafe_crossing": "Unsafe Roadway Crossing",
        "broken_elevator": "Broken Public Elevator",
        "steep_slope": "Steep Path Incline",
        "obstacle": "Obstacle in Pedestrian Pathway"
    }

    new_barrier = {
        "id": barrier_id,
        "type": report.type,
        "title": title_map.get(report.type, "Reported Accessibility Barrier"),
        "description": report.description,
        "latitude": report.latitude,
        "longitude": report.longitude,
        "photo_url": report.photo_base64 if report.photo_base64 and report.photo_base64.startswith("data:") else None,
        "timestamp": now.isoformat(),
        "reporter": report.reporter or "Community User",
        "ai_confidence": report.ai_confidence or 0.92,
        "verification_status": "New",
        "temporary": bool(report.temporary),
        "expires_at": expires,
        "severity": "high" if report.type in ["stairs", "blocked_ramp", "broken_elevator"] else "medium",
        "impact_summary": impact_map.get(report.type, "Accessibility barrier identified by community report.")
    }

    saved = insert_barrier(new_barrier)
    return Barrier(**saved)

@router.post("/detect", response_model=AIDetectionResponse)
async def detect_barrier_from_photo(
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()
        res = analyze_barrier_image(contents, file.filename)
        
        # Create base64 preview
        b64 = f"data:{file.content_type};base64,{base64.b64encode(contents).decode('utf-8')}"
        return AIDetectionResponse(
            detected_barrier=res["detected_barrier"],
            barrier_type=res["barrier_type"],
            confidence=res["confidence"],
            explanation=res["explanation"],
            suggested_severity=res["suggested_severity"],
            image_url=b64
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image analysis error: {str(e)}")

@router.post("/voice-parse", response_model=VoiceNLPResponse)
def parse_voice_report(data: dict):
    transcript = data.get("transcript", "")
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript text is required.")
    
    parsed = parse_voice_transcript(transcript)
    return VoiceNLPResponse(
        transcript=parsed["transcript"],
        detected_barrier_type=parsed["detected_barrier_type"],
        barrier_title=parsed["barrier_title"],
        confidence=parsed["confidence"],
        extracted_notes=parsed["extracted_notes"]
    )

@router.post("/{barrier_id}/verify")
def verify_barrier(barrier_id: str):
    update_barrier_status(barrier_id, "Verified")
    return {"message": "Barrier verified successfully", "barrier_id": barrier_id, "status": "Verified"}

@router.delete("/{barrier_id}")
def delete_barrier(barrier_id: str):
    update_barrier_status(barrier_id, "Resolved")
    return {"message": "Barrier marked as resolved/deleted", "barrier_id": barrier_id}
