"""
Job Seeker Profile schemas.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict



class JobSeekerPreferencesSchema(BaseModel):
    """Job seeker preferences schema"""
    desired_salary_min: int | None = None
    desired_salary_max: int | None = None
    job_types: list[str] = []  # ["Full-time", "Part-time", "Contract"]
    remote_ok: bool = True
    preferred_locations: list[str] = []
    industry_preferences: list[str] = []
    company_size_preferences: list[str] = []  # ["startup", "medium", "enterprise"]
    work_environment_preferences: list[str] = []  # ["collaborative", "independent", etc.]


class JobSeekerProfileBase(BaseModel):
    """Base job seeker profile schema"""
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    location: str | None = None
    bio: str | None = None
    resume_file_url: str | None = None
    resume_file_name: str | None = None
    skills: list[str] = []
    experience_years: int = 0
    education_level: str | None = None
    preferences: JobSeekerPreferencesSchema | None = None


class JobSeekerProfileCreate(JobSeekerProfileBase):
    """Schema for creating a job seeker profile"""
    user_id: str  # Links to the user account


class JobSeekerProfileUpdate(BaseModel):
    """Schema for updating a job seeker profile"""
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None
    bio: str | None = None
    resume_file_url: str | None = None
    resume_file_name: str | None = None
    skills: list[str] | None = None
    experience_years: int | None = None
    education_level: str | None = None
    preferences: JobSeekerPreferencesSchema | None = None


class JobSeekerProfileResponse(JobSeekerProfileBase):
    """Schema for job seeker profile response"""
    id: str
    user_id: str
    profile_views: int = 0
    profile_completion_percentage: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

