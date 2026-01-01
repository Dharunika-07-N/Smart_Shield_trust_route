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
    # Delivery Info
    license_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    company_name: Optional[str] = None
    # Rider Info
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    # Include other profile fields if needed
    license_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    company_name: Optional[str] = None
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
