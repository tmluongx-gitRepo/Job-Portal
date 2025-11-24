"""
Analytics and statistics response schemas.

These schemas provide aggregated data for job postings, employer dashboards,
and job seeker application tracking.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TopJobStats(BaseModel):
    """Statistics for a single job in the top jobs list."""

    job_id: str
    title: str
    applications: int
    is_active: bool


class JobAnalyticsResponse(BaseModel):
    """Analytics for a single job posting."""

    job_id: str
    job_title: str
    total_applications: int = Field(..., description="Total number of applications for this job")
    applications_by_status: dict[str, int] = Field(
        ..., description="Application count grouped by status"
    )
    recent_applications_count: int = Field(
        ..., description="Applications received in the last 7 days"
    )
    interviews_scheduled: int = Field(..., description="Total interviews scheduled")
    interviews_completed: int = Field(..., description="Total interviews completed")
    avg_interview_rating: float | None = Field(
        None, description="Average rating from completed interviews"
    )
    last_application_date: datetime | None = Field(
        None, description="Date of the most recent application"
    )


class EmployerJobStatsResponse(BaseModel):
    """Job management statistics for an employer."""

    employer_id: str
    total_jobs: int = Field(..., description="Total number of jobs posted")
    active_jobs: int = Field(..., description="Number of active jobs")
    inactive_jobs: int = Field(..., description="Number of inactive jobs")
    total_applications_received: int = Field(..., description="Total applications across all jobs")
    applications_this_week: int = Field(..., description="Applications received in the last 7 days")
    top_jobs: list[TopJobStats] = Field(..., description="Top 5 jobs by application count")


class JobSeekerApplicationStatsResponse(BaseModel):
    """Application statistics for a job seeker."""

    job_seeker_id: str
    total_applications: int = Field(..., description="Total applications submitted")
    applications_by_status: dict[str, int] = Field(
        ..., description="Application count grouped by status"
    )
    applications_this_week: int = Field(
        ..., description="Applications submitted in the last 7 days"
    )
    interviews_scheduled: int = Field(..., description="Total interviews scheduled")
    interviews_completed: int = Field(..., description="Total interviews completed")
    avg_interview_rating: float | None = Field(
        None, description="Average rating from completed interviews (if visible)"
    )
    last_application_date: datetime | None = Field(
        None, description="Date of the most recent application"
    )
