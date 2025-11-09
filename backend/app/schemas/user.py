from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    account_type: str = "job_seeker"  # or "employer"


class UserCreate(UserBase):
    """Schema for creating a user"""


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: EmailStr | None = None
    account_type: str | None = None


class UserResponse(UserBase):
    """Schema for user response"""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
