from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StatusHistoryEntrySchema(BaseModel):
    """Status history entry schema"""

    status: str
    changed_at: datetime
    notes: str | None = None
    changed_by: str | None = None  # user_id or "system"


class ApplicationBase(BaseModel):
    """Base application schema"""

    job_id: str
    notes: str | None = None


class ApplicationCreate(ApplicationBase):
    """Schema for creating an application"""

    job_seeker_id: str  # Which profile is applying


class ApplicationUpdate(BaseModel):
    """Schema for updating an application"""

    status: str | None = None
    notes: str | None = None
    next_step: str | None = None
    interview_scheduled_date: datetime | None = None
    rejection_reason: str | None = None


class ApplicationResponse(ApplicationBase):
    """Schema for application response"""

    id: str
    job_seeker_id: str
    status: str  # "Application Submitted", "Under Review", "Interview Scheduled", "Rejected", "Accepted"
    applied_date: datetime
    next_step: str | None = None
    interview_scheduled_date: datetime | None = None
    rejection_reason: str | None = None
    status_history: list[StatusHistoryEntrySchema] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
