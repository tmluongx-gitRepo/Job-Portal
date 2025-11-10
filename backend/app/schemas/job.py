from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobBase(BaseModel):
    """Base job schema"""

    title: str
    company: str
    description: str
    requirements: str | None = None
    responsibilities: list[str] = []
    location: str
    job_type: str  # "Full-time", "Part-time", "Contract", "Internship"
    remote_ok: bool = False
    salary_min: int | None = None
    salary_max: int | None = None
    experience_required: str | None = None  # "0-2 years", "3-5 years", "5+ years"
    education_required: str | None = None  # "High School", "Bachelor's Degree", "Master's Degree"
    industry: str | None = None
    company_size: str | None = None  # "startup", "small", "medium", "large", "enterprise"
    benefits: list[str] = []
    skills_required: list[str] = []
    application_deadline: datetime | None = None


class JobCreate(JobBase):
    """Schema for creating a job"""


class JobUpdate(BaseModel):
    """Schema for updating a job"""

    title: str | None = None
    company: str | None = None
    description: str | None = None
    requirements: str | None = None
    responsibilities: list[str] | None = None
    location: str | None = None
    job_type: str | None = None
    remote_ok: bool | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    experience_required: str | None = None
    education_required: str | None = None
    industry: str | None = None
    company_size: str | None = None
    benefits: list[str] | None = None
    skills_required: list[str] | None = None
    application_deadline: datetime | None = None
    is_active: bool | None = None


class JobResponse(JobBase):
    """Schema for job response"""

    id: str
    is_active: bool = True
    view_count: int = 0
    application_count: int = 0
    posted_by: str | None = None  # user_id of employer who posted
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
