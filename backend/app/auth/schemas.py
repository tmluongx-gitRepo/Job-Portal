"""
Pydantic schemas for authentication endpoints.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserSignUp(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    account_type: Literal["job_seeker", "employer"] = Field(..., description="Account type")
    full_name: str | None = Field(None, description="User's full name")


class UserSignIn(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str
    user: "UserInfo"


class UserInfo(BaseModel):
    """Schema for user information."""
    id: str
    email: str
    account_type: str | None = None
    email_verified: bool = False
    provider: str = "email"
    created_at: datetime | None = None


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordUpdate(BaseModel):
    """Schema for password update."""
    password: str = Field(..., min_length=8, description="New password must be at least 8 characters")


class CurrentUser(BaseModel):
    """Schema for current authenticated user."""
    id: str
    email: str
    account_type: str | None = None
    provider: str
    email_verified: bool
    role: str
    metadata: dict = {}


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str

