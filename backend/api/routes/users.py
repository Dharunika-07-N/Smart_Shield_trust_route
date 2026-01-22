from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, RiderProfile
from api.schemas.auth import UserResponse, RiderProfileSchema
from api.deps import get_current_active_user, get_current_dispatcher
from loguru import logger
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    full_name: str = None,
    phone: str = None,
    email: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile basic info."""
    if full_name: current_user.full_name = full_name
    if phone: current_user.phone = phone
    if email: current_user.email = email
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/rider-profile", response_model=RiderProfileSchema)
def update_rider_profile(
    profile_in: RiderProfileSchema,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update rider-specific profile info."""
    if current_user.role != "rider":
        raise HTTPException(status_code=400, detail="Only riders have rider profiles")
    
    profile = db.query(RiderProfile).filter(RiderProfile.user_id == current_user.id).first()
    if not profile:
        profile = RiderProfile(user_id=current_user.id)
        db.add(profile)
    
    if profile_in.vehicle_type: profile.vehicle_type = profile_in.vehicle_type
    if profile_in.license_number: profile.license_number = profile_in.license_number
    if profile_in.gender: profile.gender = profile_in.gender
    if profile_in.preferences: profile.preferences = profile_in.preferences
    
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/riders", response_model=List[UserResponse])
def list_riders(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_dispatcher)
):
    """List all riders (Admin/Dispatcher only)."""
    riders = db.query(User).filter(User.role == "rider").all()
    return riders
