"""
Pydantic schemas for Interview API.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.constants import InterviewStatus, InterviewType


class InterviewCreate(BaseModel):
    """Schema for creating a new interview."""

    application_id: str = Field(..., description="Application ID")
    interview_type: Literal[
        InterviewType.PHONE,
        InterviewType.VIDEO,
        InterviewType.IN_PERSON,
        InterviewType.TECHNICAL,
        InterviewType.BEHAVIORAL,
        InterviewType.PANEL,
    ] = Field(
        ...,
        description="Type of interview (phone, video, in-person, technical, behavioral, panel)",
    )
    scheduled_date: datetime = Field(..., description="Scheduled date and time")
    duration_minutes: int = Field(..., description="Duration in minutes", ge=15, le=480)
    timezone: str = Field(..., description="Timezone (e.g., America/New_York)")
    location: str | None = Field(None, description="Physical address or meeting link")
    interviewer_name: str | None = Field(None, description="Interviewer's name")
    interviewer_email: EmailStr | None = Field(None, description="Interviewer's email")
    interviewer_phone: str | None = Field(None, description="Interviewer's phone")
    notes: str | None = Field(None, description="Notes visible to job seeker")
    internal_notes: str | None = Field(None, description="Internal notes (employer only)")


class InterviewUpdate(BaseModel):
    """
    Schema for updating an interview.

    Note: Field-level authorization is enforced at the route level.
    - Employers/Admins: Can update all fields
    - Job Seekers: Cannot update interviews (403 Forbidden)
    - Sensitive fields (internal_notes, feedback, rating) are only visible to employers/admins
    """

    scheduled_date: datetime | None = Field(None, description="New scheduled date and time")
    duration_minutes: int | None = Field(None, description="Duration in minutes", ge=15, le=480)
    timezone: str | None = Field(None, description="Timezone")
    location: str | None = Field(None, description="Physical address or meeting link")
    interviewer_name: str | None = Field(None, description="Interviewer's name")
    interviewer_email: EmailStr | None = Field(None, description="Interviewer's email")
    interviewer_phone: str | None = Field(None, description="Interviewer's phone")
    notes: str | None = Field(None, description="Notes visible to job seeker")
    internal_notes: str | None = Field(None, description="Internal notes (employer only)")


class InterviewCancel(BaseModel):
    """Schema for cancelling an interview."""

    reason: str = Field(..., description="Reason for cancellation")


class InterviewComplete(BaseModel):
    """Schema for marking an interview as complete."""

    feedback: str | None = Field(None, description="Interview feedback")
    rating: int | None = Field(None, description="Rating (1-5)", ge=1, le=5)
    next_step: str | None = Field(None, description="Next step in the process")


class InterviewResponse(BaseModel):
    """Schema for interview response."""

    id: str
    application_id: str
    job_id: str
    job_seeker_id: str
    employer_id: str
    interview_type: str
    scheduled_date: datetime
    duration_minutes: int
    timezone: str
    location: str | None = None
    interviewer_name: str | None = None
    interviewer_email: str | None = None
    interviewer_phone: str | None = None
    notes: str | None = None
    internal_notes: str | None = None
    status: Literal[
        InterviewStatus.SCHEDULED,
        InterviewStatus.RESCHEDULED,
        InterviewStatus.COMPLETED,
        InterviewStatus.CANCELLED,
        InterviewStatus.NO_SHOW,
    ]
    feedback: str | None = None
    rating: int | None = None
    reminder_sent: bool
    cancelled_by: str | None = None
    cancelled_reason: str | None = None
    rescheduled_from: datetime | None = None
    created_at: datetime
    updated_at: datetime
    # Populated fields
    job_title: str | None = None
    company: str | None = None
    job_seeker_name: str | None = None
    job_seeker_email: str | None = None


class InterviewListResponse(BaseModel):
    """Schema for paginated interview list response."""

    interviews: list[InterviewResponse]
    total: int
