from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, RiderProfile, DriverProfile, UserSession
from api.schemas.auth import UserCreate, UserResponse, Token, UserLogin, TokenRefresh
from api.services.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from loguru import logger
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (Rider or Driver publicly, Others via restricted paths)."""
    try:
        # 1. Check if registration is allowed for this role publicly
        allowed_public_roles = ["rider", "driver"]
        if user_in.role not in allowed_public_roles and not user_in.admin_code:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Registration for role '{user_in.role}' is not allowed publicly."
            )

        # 2. Check if user already exists
        existing_user = db.query(User).filter(User.username == user_in.username).first()
        if existing_user:
            logger.warning(f"Registration failed: Username {user_in.username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # 3. Handle status based on role
        user_status = "active"
        if user_in.role == "driver":
            user_status = "pending_approval"
        
        # 4. Create new user
        new_user = User(
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            full_name=user_in.full_name,
            phone=user_in.phone,
            email=user_in.email,
            status=user_status
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 5. Create specific Profiles
        if new_user.role == "rider":
            rider_profile = RiderProfile(
                user_id=new_user.id,
                vehicle_type=user_in.vehicle_type,
                license_number=user_in.license_number,
                gender=user_in.gender,
                preferences=user_in.preferences or {}
            )
            db.add(rider_profile)
            db.commit()
        elif new_user.role == "driver":
            driver_profile = DriverProfile(
                user_id=new_user.id,
                license_number=user_in.license_number,
                vehicle_type=user_in.vehicle_type,
                vehicle_number=user_in.vehicle_number,
                documents=user_in.uploaded_documents or {}
            )
            db.add(driver_profile)
            db.commit()
        
        logger.info(f"New user registered: {new_user.username} (role: {new_user.role}, status: {new_user.status})")
        return new_user
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Login and status verification."""
    user = db.query(User).filter(User.username == user_in.username).first()
    
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if the logging in role matches the user's role
    if user_in.role and user.role != user_in.role:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Unauthorized: This account is registered as a {user.role}, but you are trying to log in as a {user_in.role}."
        )

    # Status Checks
    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended. Please contact support."
        )
    
    if user.status == "pending_approval" and user.role == "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your application is under review. You will be notified once approved."
        )
    
    if user.status == "rejected" and user.role == "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your application was not approved. Please contact support for details."
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}"
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Store session
    session = UserSession(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(session)
    db.commit()
    
    logger.info(f"User logged in: {user.username} as {user.role}")
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

@router.post("/refresh", response_model=Token)
def refresh(token_in: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    session = db.query(UserSession).filter(UserSession.token == token_in.refresh_token).first()
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

@router.post("/logout")
def logout(token_in: TokenRefresh, db: Session = Depends(get_db)):
    """Logout and invalidate refresh token."""
    session = db.query(UserSession).filter(UserSession.token == token_in.refresh_token).first()
    if session:
        db.delete(session)
        db.commit()
    return {"message": "Logged out successfully"}
