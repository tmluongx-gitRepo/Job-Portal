"""
Saved Job schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SavedJobBase(BaseModel):
    """Base saved job schema"""

    job_id: str
    notes: str | None = None


class SavedJobCreate(SavedJobBase):
    """Schema for creating a saved job"""

    job_seeker_id: str


class SavedJobUpdate(BaseModel):
    """Schema for updating a saved job"""

    notes: str | None = None


class SavedJobResponse(SavedJobBase):
    """Schema for saved job response"""

    id: str
    job_seeker_id: str
    saved_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
