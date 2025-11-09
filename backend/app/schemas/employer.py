from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmployerProfileBase(BaseModel):
    """Base employer profile schema"""

    company_name: str
    company_website: str | None = None
    company_logo_url: str | None = None
    industry: str | None = None
    company_size: str | None = None  # "1-10", "11-50", "51-200", "201-500", "500+"
    location: str | None = None
    description: str | None = None
    founded_year: int | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    benefits_offered: list[str] = []
    company_culture: str | None = None


class EmployerProfileCreate(EmployerProfileBase):
    """Schema for creating an employer profile"""

    user_id: str  # Which user this profile belongs to


class EmployerProfileUpdate(BaseModel):
    """Schema for updating an employer profile"""

    company_name: str | None = None
    company_website: str | None = None
    company_logo_url: str | None = None
    industry: str | None = None
    company_size: str | None = None
    location: str | None = None
    description: str | None = None
    founded_year: int | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    benefits_offered: list[str] | None = None
    company_culture: str | None = None
    verified: bool | None = None


class EmployerProfileResponse(EmployerProfileBase):
    """Schema for employer profile response"""

    id: str
    user_id: str
    jobs_posted_count: int = 0
    active_jobs_count: int = 0
    verified: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
