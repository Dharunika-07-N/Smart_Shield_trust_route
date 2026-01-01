from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from api.schemas.auth import UserCreate, UserResponse, Token, UserLogin
from api.services.security import get_password_hash, verify_password, create_access_token
from loguru import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_in.username).first()
        if existing_user:
            logger.warning(f"Signup failed: Username {user_in.username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Verify admin code for admin role
        ADMIN_CODE = "Grunt123"
        if user_in.role == "admin":
            if not user_in.admin_code or user_in.admin_code != ADMIN_CODE:
                logger.warning(f"Signup failed: Invalid admin code for {user_in.username}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid admin access code"
                )
        
        # Create new user
        new_user = User(
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            full_name=user_in.full_name,
            phone=user_in.phone,
            email=user_in.email,
            license_number=user_in.license_number if user_in.role == "delivery_person" else None,
            vehicle_type=user_in.vehicle_type if user_in.role == "delivery_person" else None,
            company_name=user_in.company_name,
            gender=user_in.gender if user_in.role in ["rider", "customer"] else None,
            emergency_contact_name=user_in.emergency_contact_name if user_in.role in ["rider", "customer"] else None,
            emergency_contact_phone=user_in.emergency_contact_phone if user_in.role in ["rider", "customer"] else None,
            emergency_contact_email=user_in.emergency_contact_email
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user signed up: {new_user.username} (role: {new_user.role})")
        return new_user
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    logger.info(f"User logged in: {user.username}")
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }
