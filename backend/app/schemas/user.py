"""User, Auth, and Token Schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str
    role: str
    full_name: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[str] = "FRAUD_ANALYST"
    department: Optional[str] = "Risk Operations"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    department: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
