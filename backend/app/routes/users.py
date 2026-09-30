from fastapi import APIRouter
from ..models.schemas import UserProfile, AccessibilityProfile
from ..database.db import save_user_profile, get_user_profile

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/profile", response_model=UserProfile)
def update_profile(profile: UserProfile):
    save_user_profile(
        user_id=profile.id,
        name=profile.name,
        email=profile.email or "",
        profile_dict=profile.model_dump()
    )
    return profile

@router.get("/profile/{user_id}", response_model=UserProfile)
def fetch_profile(user_id: str = "user-default"):
    saved = get_user_profile(user_id)
    if saved:
        return UserProfile(**saved)
    return UserProfile(id=user_id)
