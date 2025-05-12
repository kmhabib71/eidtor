from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class TokenPayload(BaseModel):
    sub: str
    exp: int

class Token(BaseModel):
    access_token: str
    token_type: str
    
class UserInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    subscription_end_date: Optional[datetime] = None
    processing_minutes_used: int = 0
    processing_minutes_limit: int = 60  # Free tier limit per month
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    is_admin: bool
    subscription_tier: SubscriptionTier
    subscription_end_date: Optional[datetime] = None
    processing_minutes_used: int
    processing_minutes_limit: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 