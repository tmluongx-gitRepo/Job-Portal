from datetime import datetime
from pydantic import BaseModel, ConfigDict


class JobBase(BaseModel):
    """Base job schema."""
    title: str
    company: str
    location: str
    description: str
    requirements: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    job_type: str  # full-time, part-time, contract


class JobCreate(JobBase):
    """Schema for creating a job."""
    pass


class JobUpdate(BaseModel):
    """Schema for updating a job."""
    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str | None = None
    requirements: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    job_type: str | None = None
    is_active: bool | None = None


class JobResponse(JobBase):
    """Schema for job response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
