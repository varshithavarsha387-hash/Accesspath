import re
from typing import Dict, Any

def parse_voice_transcript(text: str) -> Dict[str, Any]:
    """
    Extracts accessibility barrier category and details from spoken voice transcripts.
    Supports English as well as transliterated Telugu / Hindi keywords.
    """
    t = text.lower()
    
    # Keyword taxonomy
    if any(k in t for k in ["blocked ramp", "ramp blocked", "ramp is blocked", "ramp mundhu", "ramp bandh"]):
        return {
            "transcript": text,
            "detected_barrier_type": "blocked_ramp",
            "barrier_title": "Blocked Wheelchair Ramp",
            "confidence": 0.94,
            "extracted_notes": "User reported wheelchair ramp obstruction or blockade."
        }
    elif any(k in t for k in ["stair", "stairs", "steps", "metlu", "seedhiyan", "flight of stairs"]):
        return {
            "transcript": text,
            "detected_barrier_type": "stairs",
            "barrier_title": "Flight of Concrete Stairs",
            "confidence": 0.95,
            "extracted_notes": "User reported stairs without ramp or wheelchair elevator."
        }
    elif any(k in t for k in ["broken footpath", "broken sidewalk", "pothole", "pagilina footpath", "toota footpath", "drain hole"]):
        return {
            "transcript": text,
            "detected_barrier_type": "broken_footpath",
            "barrier_title": "Broken Footpath / Damaged Pavers",
            "confidence": 0.92,
            "extracted_notes": "User reported uneven or broken pedestrian pavement."
        }
    elif any(k in t for k in ["unsafe crossing", "dangerous crossing", "traffic", "no signal", "crossing", "road crossing"]):
        return {
            "transcript": text,
            "detected_barrier_type": "unsafe_crossing",
            "barrier_title": "Unsafe Pedestrian Road Crossing",
            "confidence": 0.91,
            "extracted_notes": "User reported crossing with fast vehicular traffic or missing pedestrian signals."
        }
    elif any(k in t for k in ["elevator", "lift", "lift not working", "lift pani cheyatledu", "broken elevator"]):
        return {
            "transcript": text,
            "detected_barrier_type": "broken_elevator",
            "barrier_title": "Out-of-Service Public Elevator",
            "confidence": 0.96,
            "extracted_notes": "User reported non-functional elevator at pedestrian overpass/metro."
        }
    elif any(k in t for k in ["steep", "slope", "incline", "dhal", "ettuga undi"]):
        return {
            "transcript": text,
            "detected_barrier_type": "steep_slope",
            "barrier_title": "Steep Path Incline / Grade",
            "confidence": 0.89,
            "extracted_notes": "User reported excessive incline angle exceeding safe wheelchair standards."
        }
    else:
        return {
            "transcript": text,
            "detected_barrier_type": "obstacle",
            "barrier_title": "Reported Path Obstruction",
            "confidence": 0.85,
            "extracted_notes": f"General accessibility barrier reported: '{text}'"
        }
