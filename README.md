# AccessPath – Real-Time Accessibility Navigation

> **Navigate Without Barriers**  
> An AI-powered, accessibility-first full-stack navigation platform that generates routes based on individual mobility and physical accessibility needs.

---

## 1. Project Overview

Standard navigation platforms (Google Maps, Apple Maps) optimize almost exclusively for distance and travel time. For wheelchair users, people with visual impairments, older adults, and individuals with temporary injuries, the shortest route can be a dead end: concrete stairs, broken sidewalks, blocked curb ramps, or hazardous unsignalized crossings.

**AccessPath** flips the navigation paradigm:
1. Users specify their **FROM** (start location or GPS) and **TO** (destination).
2. Users select their **Accessibility Needs** (Wheelchair, Visually Impaired, Older Adult, Temporary Injury, custom preferences).
3. AccessPath computes multiple route alternatives:
   - **Route A – Fastest** (may include stairs or pavement hazards)
   - **Route B – Accessible** (avoids stairs, utilizes ramps)
   - **Route C – Most Accessible & Safest** (zero stairs, continuous ADA-grade ramps, audio crossings)
4. Every route presents an **Explainable Accessibility Confidence Score (0–100%)** with an interactive **"Why this score?"** breakdown.
5. While navigating, users experience **voice guidance** in **English, Telugu (తెలుగు), and Hindi (हिंदी)**, mobile **vibration pulses** for turns, and real-time **Dynamic Re-Routing** when unexpected barriers are encountered.
6. The community can report obstacles via **AI photograph classification** (Computer Vision) or **Voice speech-to-text reporting**.

---

## 2. Hackathon Story Demonstrated

```
Wheelchair User selects Profile
        ↓
Enters: FROM "Madhapur Metro" → TO "Gachibowli Stadium"
        ↓
AccessPath generates three distinct routes
        ↓
Shortest route contains stairs (Route A: score 20%)
        ↓
Accessibility engine identifies obstacle & penalizes Route A
        ↓
Accessible route (Route C: score 100%) is visually recommended with "Wheelchair-Friendly Route" badge
        ↓
User starts Live Navigation
        ↓
Hears localized audio instruction + sees visual guidance & vibration cues
        ↓
Simulated obstacle alert: "Broken Footpath 80m ahead"
        ↓
User taps [Find Accessible Alternative]
        ↓
AccessPath dynamically recalculates detour, updates polyline and navigation steps
        ↓
User reports a blocked ramp via AI Photo / Voice Reporting
        ↓
Barrier is instantly recorded in SQLite DB and updates future calculations
```

---

## 3. Technology Stack

- **Frontend**:
  - React 19 + Vite 8
  - Tailwind CSS v4 (Accessible high-contrast themes, scalable font sizing, reduced-motion controls)
  - React Router v7
  - Leaflet & React-Leaflet (Custom DivIcon markers, route polylines, clickable barrier popups)
  - Lucide React icons
  - Web Speech API (`SpeechSynthesis` Text-to-Speech + `SpeechRecognition` Voice reporting)
  - Mobile Vibration API (`navigator.vibrate`)

- **Backend**:
  - Python 3.13 + FastAPI + Uvicorn
  - Pydantic v2 schemas and request validation
  - SQLite database (`accesspath.db`) with automatic table creation & initial seed data
  - Computer Vision classifier (PIL & NumPy edge gradient and texture variance analysis)
  - Natural Language Processing (NLP keyword taxonomy for multi-lingual barrier extraction)
  - OpenStreetMap Nominatim geocoding proxy with instant offline preset fallback

---

## 4. Key Features

### 4.1 "FROM → TO" Navigation Search
- **FROM**:
  - `📍 Use My Current Location` (Browser Geolocation API with graceful denial handling)
  - Instant autocomplete search powered by OpenStreetMap Nominatim
  - Quick preset buttons: Madhapur, HITEC City, Kondapur, Gachibowli, Hyderabad Airport, Kukatpally
- **TO**:
  - Landmark, hospital, airport, transit, and college autocomplete
- **↕ Swap Locations**:
  - Instantly inverts start and destination coordinates and recalculates routes.
- **Multi-Stage Animated Loading**:
  - Stage 1: "Finding route..."
  - Stage 2: "Checking accessibility..."
  - Stage 3: "Analyzing barriers..."
  - Stage 4: "Finding accessible alternatives..."
  - Stage 5: "Route ready."

### 4.2 Explainable Accessibility Scoring Engine
- Base score: 100 points
- **Penalties**:
  - Stairs: -50 pts (wheelchair), -40 pts (injured), -30 pts (seniors)
  - Blocked ramp: -40 pts (wheelchair)
  - Broken footpath: -35 pts (visually impaired)
  - Unsafe crossing: -40 pts (visually impaired), -30 pts (seniors)
  - Broken elevator: -30 pts
  - Steep slope (>8% grade): -30 pts
- **Positive Factors**:
  - Zero stairs: +15 pts
  - Continuous ramp: +20 pts
  - Smooth pavement: +15 pts
  - Signalized audio crossing: +15 pts
  - Recent community audit: +5 pts
- **"Why this score?" Modal**:
  - Shows positive features, negative deductions, and uncertainty disclaimers.

### 4.3 Route-Specific Barrier Filtering & "Avoid This Barrier"
- Only barriers along the active selected route are highlighted.
- Clicking any barrier displays severity, AI confidence, and impact summary.
- Clicking **[ Avoid This Barrier ]** immediately reroutes around that obstruction!

### 4.4 Live Turn-by-Turn Guidance & Dynamic Re-Routing
- Large turn banners with arrows and ramp icons
- Multi-lingual voice guidance:
  - **English**: *"Turn left onto the continuous accessible ramped passage"*
  - **Telugu**: *"Continuous ramp unna passage vaipuki edamaki tiragandi"*
  - **Hindi**: *"Continuous ramp wale marg par baayein muden"*
- Mobile vibration haptic feedback:
  - Left turn: Single pulse `[200ms]`
  - Right turn: Double pulse `[200ms, 100ms, 200ms]`
  - Barrier / Warning: Long warning pulse `[500ms]`
- Dynamic barrier alert simulation with immediate accessible detour calculation.

### 4.5 AI Barrier Detection & Voice Reporting
- **Option A (Photograph Upload)**:
  - Upload image or select quick test samples (*Blocked Ramp, Concrete Stairs, Broken Sidewalk*).
  - Computer Vision classifier outputs detected barrier class and confidence percentage.
- **Option B (Voice Reporting)**:
  - Tap microphone, speak in English, Telugu, or Hindi.
  - NLP engine classifies barrier type and fills out the incident report.

### 4.6 Accessibility Features of AccessPath Itself
- **Text Size**: Normal (100%), Large (120%), Extra Large (140%)
- **High Contrast Mode**: High-visibility yellow/cyan contrast theme
- **Reduced Motion**: Disables transitions and animations
- **Keyboard Navigation & Screen Reader Friendly**

---

## 5. Project Structure

```
acesspath/
│
├── frontend/
│   ├── public/
│   │   └── sample_images/       # Sample photos for AI testing
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── NavigationSearchCard.jsx
│   │   │   ├── RouteCard.jsx
│   │   │   ├── MapView.jsx
│   │   │   ├── ScoreExplanationModal.jsx
│   │   │   ├── BarrierDetailsModal.jsx
│   │   │   ├── DynamicRerouteBanner.jsx
│   │   │   └── AccessibilitySettingsModal.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── NavigationPage.jsx
│   │   │   ├── ReportBarrierPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   └── ProfilePage.jsx
│   │   ├── context/
│   │   │   ├── AccessibilityContext.jsx
│   │   │   └── NavigationContext.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── speech.js
│   │   │   └── vibration.js
│   │   ├── utils/
│   │   │   ├── translations.js
│   │   │   └── demoData.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── database/
│   │   │   ├── db.py
│   │   │   └── seed_data.py
│   │   ├── services/
│   │   │   ├── scoring.py
│   │   │   └── routing.py
│   │   ├── ai/
│   │   │   ├── barrier_detector.py
│   │   │   └── nlp_parser.py
│   │   └── routes/
│   │       ├── routes.py
│   │       ├── barriers.py
│   │       ├── navigation.py
│   │       ├── users.py
│   │       ├── dashboard.py
│   │       └── geocoding.py
│   └── requirements.txt
│
├── run.py                       # Unified full-stack runner
├── start.bat                    # Windows one-click start script
├── test_api.py                  # End-to-end API test verification suite
└── README.md
```

---

## 6. How to Run Locally

### Option 1: One-Command Launcher (Recommended)

From the project root:
```bash
python run.py
```
Or double-click `start.bat`.

This script:
1. Detects available ports (defaults to `8000`).
2. Starts the **FastAPI Backend** (`http://127.0.0.1:8000`).
3. Starts the **Vite React Frontend** (`http://localhost:5173`).
4. Manages clean shutdown when pressing `Ctrl+C`.

---

### Option 2: Running Backend and Frontend in Separate Terminals

#### Terminal 1 – Backend:
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation: `http://127.0.0.1:8000/docs`

#### Terminal 2 – Frontend:
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your web browser.

---

## 7. Running the Automated Test Suite

A comprehensive test script is included to verify all backend and AI components:
```bash
python test_api.py
```
This tests:
1. Health check & status
2. Geocoding search & presets
3. Route calculation with Wheelchair profile penalties
4. Nearby community barriers database retrieval
5. Voice NLP transcript parsing
6. AI barrier classification from sample images
7. Community dashboard statistics
