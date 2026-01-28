from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    role: str = "rider"
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str
    # Admin verification
    admin_code: Optional[str] = None
    # Delivery Info
    license_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    company_name: Optional[str] = None
    # Driver Specific
    vehicle_number: Optional[str] = None
    uploaded_documents: Optional[dict] = None
    # Rider Info
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None
    
    # Rider Profile specific
    preferences: Optional[dict] = None


class UserLogin(BaseModel):
    username: str
    password: str
    role: Optional[str] = "rider" # Added role check for login

class UserResponse(UserBase):
    id: str
    status: str
    is_active: bool
    created_at: datetime
    # Include other profile fields if needed
    license_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    company_name: Optional[str] = None
    vehicle_number: Optional[str] = None
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None

    class Config:
        from_attributes = True

class RiderProfileSchema(BaseModel):
    vehicle_type: Optional[str] = None
    license_number: Optional[str] = None
    gender: Optional[str] = None
    preferences: Optional[dict] = None

    class Config:
        from_attributes = True

class TokenRefresh(BaseModel):
    refresh_token: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
