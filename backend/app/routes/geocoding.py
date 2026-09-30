from fastapi import APIRouter, Query
from typing import List, Dict, Any
import requests

router = APIRouter(prefix="/api/geocoding", tags=["geocoding"])

# Curated Preset Locations (Hyderabad Technology Corridor & Landmarks)
PRESET_LOCATIONS = [
    {
        "name": "Madhapur Metro Station",
        "display_name": "Madhapur Metro Station, Hitech City Main Rd, Madhapur, Hyderabad",
        "latitude": 17.4483,
        "longitude": 78.3915,
        "type": "transit"
    },
    {
        "name": "Cyber Towers, HITEC City",
        "display_name": "Cyber Towers, HITEC City, Madhapur, Hyderabad",
        "latitude": 17.4504,
        "longitude": 78.3808,
        "type": "landmark"
    },
    {
        "name": "Kondapur RTO Junction",
        "display_name": "Kondapur RTO Junction, Gachibowli - Miyapur Rd, Kondapur, Hyderabad",
        "latitude": 17.4699,
        "longitude": 78.3578,
        "type": "junction"
    },
    {
        "name": "Gachibowli Stadium",
        "display_name": "Gachibowli Stadium, Old Mumbai Highway, Gachibowli, Hyderabad",
        "latitude": 17.4401,
        "longitude": 78.3489,
        "type": "landmark"
    },
    {
        "name": "Hyderabad Airport (RGIA)",
        "display_name": "Rajiv Gandhi International Airport (RGIA), Shamshabad, Hyderabad",
        "latitude": 17.2403,
        "longitude": 78.4294,
        "type": "airport"
    },
    {
        "name": "Inorbit Mall Cyberabad",
        "display_name": "Inorbit Mall, Mindspace, Madhapur, Hyderabad",
        "latitude": 17.4346,
        "longitude": 78.3867,
        "type": "mall"
    },
    {
        "name": "Kukatpally Y-Junction",
        "display_name": "Kukatpally Y-Junction, NH65, Kukatpally, Hyderabad",
        "latitude": 17.4849,
        "longitude": 78.4138,
        "type": "junction"
    },
    {
        "name": "AIG Hospitals Gachibowli",
        "display_name": "AIG Hospitals, Mindspace Rd, Gachibowli, Hyderabad",
        "latitude": 17.4442,
        "longitude": 78.3667,
        "type": "hospital"
    },
    {
        "name": "JNTU Hyderabad College of Engineering",
        "display_name": "JNTU College of Engineering, Kukatpally, Hyderabad",
        "latitude": 17.4933,
        "longitude": 78.3914,
        "type": "college"
    },
    {
        "name": "Secunderabad Railway Station",
        "display_name": "Secunderabad Junction Railway Station, Secunderabad, Hyderabad",
        "latitude": 17.4341,
        "longitude": 78.5015,
        "type": "railway_station"
    }
]

@router.get("/search")
def search_places(q: str = Query(..., min_length=1)) -> List[Dict[str, Any]]:
    query_lower = q.lower().strip()
    
    # 1. Filter local presets first for lightning-fast responsive autocomplete
    matches = [
        loc for loc in PRESET_LOCATIONS
        if query_lower in loc["name"].lower() or query_lower in loc["display_name"].lower()
    ]

    # 2. Try Nominatim (OpenStreetMap) if internet is available
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "AccessPath-Accessibility-Navigator/1.0"}
        params = {
            "q": q,
            "format": "json",
            "limit": 5,
            "addressdetails": 1
        }
        res = requests.get(url, params=params, headers=headers, timeout=2.5)
        if res.status_code == 200:
            remote_items = res.json()
            for item in remote_items:
                name = item.get("display_name", "").split(",")[0]
                matches.append({
                    "name": name,
                    "display_name": item.get("display_name", ""),
                    "latitude": float(item.get("lat")),
                    "longitude": float(item.get("lon")),
                    "type": item.get("type", "address")
                })
    except Exception:
        # Gracefully handle network timeouts or offline mode
        pass

    # Deduplicate matches by name
    seen = set()
    deduped = []
    for m in matches:
        if m["name"] not in seen:
            seen.add(m["name"])
            deduped.append(m)

    return deduped[:8]

@router.get("/presets")
def get_presets():
    return PRESET_LOCATIONS
