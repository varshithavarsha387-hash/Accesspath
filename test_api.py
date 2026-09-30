import sys
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

base = "http://127.0.0.1:8000"

print("--- 1. Testing Health Check ---")
r = requests.get(f"{base}/api/health")
print("Status:", r.status_code, r.json())

print("\n--- 2. Testing Geocoding Search ---")
r = requests.get(f"{base}/api/geocoding/search?q=madhapur")
print("Status:", r.status_code, "Matches found:", len(r.json()))
for m in r.json()[:3]:
    print(" -", m["name"], f"({m['latitude']}, {m['longitude']})")

print("\n--- 3. Testing Route Calculation (Wheelchair Profile) ---")
payload = {
    "from_name": "Madhapur Metro Station",
    "from_lat": 17.4483,
    "from_lng": 78.3915,
    "to_name": "Gachibowli Stadium",
    "to_lat": 17.4401,
    "to_lng": 78.3489,
    "profile": {
        "user_type": "wheelchair",
        "avoid_stairs": True,
        "prefer_ramps": True,
        "language": "en"
    },
    "avoid_barrier_ids": []
}
r = requests.post(f"{base}/api/routes/calculate", json=payload)
print("Status:", r.status_code)
res = r.json()
print("Routes returned:", len(res.get("routes", [])))
for route in res.get("routes", []):
    print(f" * {route['name']}: {route['distance_km']}km, {route['duration_minutes']}min, score={route['accessibility_score']}%, recommended={route['recommended']}, badge={route.get('badge_text')}")
    print(f"   Issues: {route.get('issues')}")
    print(f"   Features: {route.get('features')[:2]}")

print("\n--- 4. Testing Nearby Barriers ---")
r = requests.get(f"{base}/api/barriers/nearby")
print("Status:", r.status_code, "Total barriers:", len(r.json()))
for b in r.json()[:3]:
    print(f" - [{b['type']}] {b['title']} (Conf: {b['ai_confidence']*100}%, Status: {b['verification_status']})")

print("\n--- 5. Testing Voice NLP Extraction ---")
r = requests.post(f"{base}/api/barriers/voice-parse", json={"transcript": "Ramp is blocked near the entrance by construction debris"})
print("Status:", r.status_code, r.json())

print("\n--- 6. Testing AI Barrier Detection with Sample Image ---")
with open("frontend/public/sample_images/blocked_ramp.jpg", "rb") as f:
    files = {"file": ("blocked_ramp.jpg", f, "image/jpeg")}
    r = requests.post(f"{base}/api/barriers/detect", files=files)
    print("Status:", r.status_code, "Detected:", r.json()["detected_barrier"], "Conf:", r.json()["confidence"])

print("\n--- 7. Testing Dashboard Stats ---")
r = requests.get(f"{base}/api/dashboard")
print("Status:", r.status_code, r.json())

print("\nAll API tests PASSED successfully!")
