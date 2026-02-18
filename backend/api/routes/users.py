from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, RiderProfile
from api.schemas.auth import UserResponse, RiderProfileSchema
from api.deps import get_current_active_user, get_current_dispatcher, get_current_admin
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

@router.post("/settings")
def update_settings(
    settings_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user settings/preferences."""
    logger.info(f"Updating settings for user {current_user.id}: {settings_data}")

    # 1. Update User level info if provided in 'profile' key
    profile_data = settings_data.get('profile', {})
    if profile_data:
        if 'full_name' in profile_data:
            current_user.full_name = profile_data['full_name']
        if 'phone' in profile_data:
            current_user.phone = profile_data['phone']
        if 'email' in profile_data:
            current_user.email = profile_data['email']
        
    # 2. Update Emergency Contacts
    if 'emergency_contacts' in settings_data:
        current_user.emergency_contacts = settings_data['emergency_contacts']

    # 3. Update Rider Profile preferences
    if current_user.role == "rider":
        # Check if RiderProfile exists
        from database.models import RiderProfile
        profile = db.query(RiderProfile).filter(RiderProfile.user_id == current_user.id).first()
        
        if not profile:
            profile = RiderProfile(user_id=current_user.id)
            db.add(profile)
            
        # Update preferences
        prefs = profile.preferences or {}
        if 'location_sharing' in settings_data:
            prefs['location_sharing'] = settings_data['location_sharing']
        if 'notifications' in settings_data:
            prefs['notifications'] = settings_data['notifications']
        if 'theme' in settings_data:
            prefs['theme'] = settings_data['theme']
            
        profile.preferences = prefs
        
        # Update vehicle type if provided
        if profile_data.get('vehicle_type'):
            profile.vehicle_type = profile_data['vehicle_type']

    db.commit()
    return {"message": "Settings updated successfully", "status": "success"}


@router.get("/riders", response_model=List[UserResponse])
def list_riders(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_dispatcher)
):
    """List all riders (Admin/Dispatcher only)."""
    riders = db.query(User).filter(User.role == "rider").all()
    return riders


@router.get("/all")
def list_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """List ALL users across every role (Admin only)."""
    users = db.query(User).order_by(User.role, User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "status": u.status,
            "phone": u.phone,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.patch("/{user_id}/status")
def toggle_user_status(
    user_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Activate or deactivate a user (Admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own status")
    user.status = payload.get("status", user.status)
    db.commit()
    return {"message": f"User {user.username} status set to {user.status}"}


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Delete a user (Admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted"}

