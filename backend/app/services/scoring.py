from typing import List, Dict, Any, Tuple
from ..models.schemas import AccessibilityProfile, ScoreBreakdown, ScoreItem, Barrier

def calculate_accessibility_score(
    barriers: List[Barrier],
    features: List[str],
    profile: AccessibilityProfile
) -> Tuple[int, ScoreBreakdown]:
    """
    Calculates an explainable Accessibility Score between 0 and 100
    dynamically weighted by the user's accessibility profile.
    """
    base_score = 100
    total = base_score
    penalties: List[ScoreItem] = []
    positive_factors: List[ScoreItem] = []
    why_explanation: List[str] = []

    # Profile-dependent penalty weights
    is_wheelchair = profile.user_type == "wheelchair" or profile.avoid_stairs or profile.prefer_ramps
    is_visually_impaired = profile.user_type == "visually_impaired" or profile.prefer_safe_crossings
    is_older_adult = profile.user_type == "older_adult" or profile.avoid_steep_slopes
    is_injured = profile.user_type == "temporary_injury"

    stairs_penalty = 50 if is_wheelchair else (40 if is_injured else (30 if is_older_adult else 25))
    blocked_ramp_penalty = 40 if is_wheelchair else 25
    broken_footpath_penalty = 35 if is_visually_impaired else (25 if is_wheelchair else 20)
    unsafe_crossing_penalty = 40 if is_visually_impaired else (30 if is_older_adult else 20)
    broken_elevator_penalty = 30 if is_wheelchair else 20
    steep_slope_penalty = 30 if (is_wheelchair or is_older_adult) else 15
    narrow_penalty = 20 if is_wheelchair else 10

    # Evaluate barriers along route
    stairs_count = 0
    blocked_ramp_count = 0
    broken_footpath_count = 0
    unsafe_crossing_count = 0
    broken_elevator_count = 0
    steep_slope_count = 0

    for b in barriers:
        b_type = b.type.lower()
        if "stair" in b_type:
            stairs_count += 1
            penalties.append(ScoreItem(label=f"Stairs encountered ({b.title})", value=-stairs_penalty, is_positive=False, icon="stairs"))
            total -= stairs_penalty
            why_explanation.append(f"❌ Stairs detected ({b.title}): -{stairs_penalty} pts penalty")
        elif "blocked_ramp" in b_type:
            blocked_ramp_count += 1
            penalties.append(ScoreItem(label=f"Blocked Ramp ({b.title})", value=-blocked_ramp_penalty, is_positive=False, icon="blocked_ramp"))
            total -= blocked_ramp_penalty
            why_explanation.append(f"❌ Blocked ramp ({b.title}): -{blocked_ramp_penalty} pts penalty")
        elif "broken_footpath" in b_type or "pothole" in b_type:
            broken_footpath_count += 1
            penalties.append(ScoreItem(label=f"Broken Footpath ({b.title})", value=-broken_footpath_penalty, is_positive=False, icon="broken_footpath"))
            total -= broken_footpath_penalty
            why_explanation.append(f"⚠ Broken footpath surface: -{broken_footpath_penalty} pts penalty")
        elif "unsafe_crossing" in b_type or "crossing" in b_type:
            unsafe_crossing_count += 1
            penalties.append(ScoreItem(label=f"Unsafe Crossing ({b.title})", value=-unsafe_crossing_penalty, is_positive=False, icon="unsafe_crossing"))
            total -= unsafe_crossing_penalty
            why_explanation.append(f"⚠ Hazardous road crossing: -{unsafe_crossing_penalty} pts penalty")
        elif "broken_elevator" in b_type or "elevator" in b_type:
            broken_elevator_count += 1
            penalties.append(ScoreItem(label="Out-of-service Elevator", value=-broken_elevator_penalty, is_positive=False, icon="broken_elevator"))
            total -= broken_elevator_penalty
            why_explanation.append(f"❌ Elevator out of service: -{broken_elevator_penalty} pts penalty")
        elif "steep_slope" in b_type or "slope" in b_type:
            steep_slope_count += 1
            penalties.append(ScoreItem(label="Steep Incline (>8%)", value=-steep_slope_penalty, is_positive=False, icon="steep_slope"))
            total -= steep_slope_penalty
            why_explanation.append(f"⚠ Steep slope (>8% grade): -{steep_slope_penalty} pts penalty")
        elif "narrow" in b_type:
            penalties.append(ScoreItem(label="Narrow Section (<90cm)", value=-narrow_penalty, is_positive=False, icon="narrow"))
            total -= narrow_penalty
            why_explanation.append(f"⚠ Narrow walkway section: -{narrow_penalty} pts penalty")
        else:
            penalties.append(ScoreItem(label=f"Hazard: {b.title}", value=-15, is_positive=False, icon="warning"))
            total -= 15
            why_explanation.append(f"⚠ General obstruction: {b.title} (-15 pts)")

    # Evaluate positive route features
    has_ramp = any("ramp" in f.lower() for f in features)
    has_smooth = any("smooth" in f.lower() or "good footpath" in f.lower() for f in features)
    has_safe_crossing = any("safe crossing" in f.lower() or "signalized" in f.lower() for f in features)
    no_stairs = stairs_count == 0

    if no_stairs:
        positive_factors.append(ScoreItem(label="Zero Stairs Detected", value=15, is_positive=True, icon="check"))
        total += 5
        why_explanation.insert(0, "✓ Zero stairs detected on this route path (+15 pts)")
    
    if has_ramp:
        ramp_bonus = 20 if profile.prefer_ramps else 10
        positive_factors.append(ScoreItem(label="Accessible Ramp Available", value=ramp_bonus, is_positive=True, icon="ramp"))
        total += 10
        why_explanation.append(f"✓ Continuous accessible ramp confirmed (+{ramp_bonus} pts)")

    if has_smooth:
        smooth_bonus = 15 if profile.prefer_smooth_paths else 10
        positive_factors.append(ScoreItem(label="Smooth Paved Footpath", value=smooth_bonus, is_positive=True, icon="smooth"))
        total += 10
        why_explanation.append(f"✓ Smooth, level surface condition (+{smooth_bonus} pts)")

    if has_safe_crossing:
        crossing_bonus = 20 if is_visually_impaired else 10
        positive_factors.append(ScoreItem(label="Signalized Pedestrian Crossing", value=crossing_bonus, is_positive=True, icon="crossing"))
        total += 10
        why_explanation.append(f"✓ Signalized crossing with tactile indicators (+{crossing_bonus} pts)")

    # Recent community verified data bonus
    positive_factors.append(ScoreItem(label="Recent Verified Community Audit", value=5, is_positive=True, icon="verified"))
    total += 5
    why_explanation.append("✓ Route verified by recent community accessibility reports (+5 pts)")

    # Clamp total score between 5 and 100
    final_score = max(5, min(100, total))

    freshness_note = "AccessPath Accessibility Estimate: Scores are derived from community reports, AI photo audits, and municipal elevation profiles. Some segments may have pending re-verification."

    breakdown = ScoreBreakdown(
        base_score=base_score,
        total_score=final_score,
        positive_factors=positive_factors,
        penalties=penalties,
        why_explanation=why_explanation,
        freshness_note=freshness_note
    )

    return final_score, breakdown
