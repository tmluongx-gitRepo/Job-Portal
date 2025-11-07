from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr, ConfigDict


class JobSeekerPreferencesSchema(BaseModel):
    """Job seeker preferences schema"""
    desired_salary_min: int | None = None
    desired_salary_max: int | None = None
    job_types: List[str] = []  # ["Full-time", "Part-time", "Contract", "Internship"]
    remote_ok: bool = False
    preferred_locations: List[str] = []
    industry_preferences: List[str] = []
    company_size_preferences: List[str] = []  # ["startup", "small", "medium", "large", "enterprise"]
    work_environment_preferences: List[str] = []  # ["collaborative", "independent", "fast-paced", "structured"]


class JobSeekerProfileBase(BaseModel):
    """Base job seeker profile schema"""
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    location: str | None = None
    bio: str | None = None
    skills: List[str] = []
    experience_years: int | None = None
    education_level: str | None = None  # "High School", "Bachelor's", "Master's", "PhD"
    preferences: JobSeekerPreferencesSchema = JobSeekerPreferencesSchema()


class JobSeekerProfileCreate(JobSeekerProfileBase):
    """Schema for creating a job seeker profile"""
    user_id: str  # Which user this profile belongs to


class JobSeekerProfileUpdate(BaseModel):
    """Schema for updating a job seeker profile"""
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None
    bio: str | None = None
    skills: List[str] | None = None
    experience_years: int | None = None
    education_level: str | None = None
    preferences: JobSeekerPreferencesSchema | None = None


class JobSeekerProfileResponse(JobSeekerProfileBase):
    """Schema for job seeker profile response"""
    id: str
    user_id: str
    resume_file_url: str | None = None
    resume_file_name: str | None = None
    profile_views: int = 0
    profile_completion_percentage: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

