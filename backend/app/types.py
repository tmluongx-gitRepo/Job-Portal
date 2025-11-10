"""
Type definitions for MongoDB documents.

All MongoDB document structures defined as TypedDict for proper type checking.
"""

from datetime import datetime
from typing import Any, NotRequired, TypedDict

from bson import ObjectId


class UserDocument(TypedDict):
    """MongoDB User document structure."""

    _id: ObjectId
    email: str
    account_type: str
    created_at: datetime
    updated_at: datetime


class JobSeekerProfileDocument(TypedDict):
    """MongoDB JobSeekerProfile document structure."""

    _id: ObjectId
    user_id: ObjectId
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    email: NotRequired[str]
    phone: NotRequired[str]
    location: NotRequired[str]
    bio: NotRequired[str]
    skills: NotRequired[list[str]]
    experience_years: NotRequired[int]
    education: NotRequired[list[dict[str, Any]]]
    education_level: NotRequired[str]
    work_history: NotRequired[list[dict[str, Any]]]
    certifications: NotRequired[list[str]]
    languages: NotRequired[list[str]]
    resume_url: NotRequired[str]
    resume_file_url: NotRequired[str]
    resume_file_name: NotRequired[str]
    portfolio_url: NotRequired[str]
    linkedin_url: NotRequired[str]
    github_url: NotRequired[str]
    preferences: NotRequired[dict[str, Any]]
    profile_views: int
    profile_completion_percentage: NotRequired[int]
    created_at: datetime
    updated_at: datetime


class EmployerProfileDocument(TypedDict):
    """MongoDB EmployerProfile document structure."""

    _id: ObjectId
    user_id: ObjectId
    company_name: NotRequired[str]
    company_description: NotRequired[str]
    industry: NotRequired[str]
    company_size: NotRequired[str]
    website: NotRequired[str]
    logo_url: NotRequired[str]
    location: NotRequired[str]
    founded_year: NotRequired[int]
    contact_email: NotRequired[str]
    contact_phone: NotRequired[str]
    benefits_offered: NotRequired[list[str]]
    company_culture: NotRequired[str]
    jobs_posted_count: int
    active_jobs_count: int
    verified: bool
    created_at: datetime
    updated_at: datetime


class JobDocument(TypedDict):
    """MongoDB Job document structure."""

    _id: ObjectId
    title: str
    company: str
    location: str
    description: str
    requirements: NotRequired[str]
    responsibilities: NotRequired[list[str]]
    skills_required: NotRequired[list[str]]
    experience_required: NotRequired[str]
    education_required: NotRequired[str]
    salary_min: NotRequired[int]
    salary_max: NotRequired[int]
    salary_currency: NotRequired[str]
    job_type: NotRequired[str]
    remote_ok: NotRequired[bool]
    benefits: NotRequired[list[str]]
    application_deadline: NotRequired[datetime]
    posted_by: NotRequired[str]
    industry: NotRequired[str]
    company_size: NotRequired[str]
    is_active: bool
    view_count: int
    application_count: int
    created_at: datetime
    updated_at: datetime


class StatusHistoryEntry(TypedDict):
    """Status history entry in application."""

    status: str
    changed_at: datetime
    notes: str
    changed_by: str


class ApplicationDocument(TypedDict):
    """MongoDB Application document structure."""

    _id: ObjectId
    job_id: str
    job_seeker_id: str
    status: str
    cover_letter: NotRequired[str]
    resume_url: NotRequired[str]
    status_history: list[StatusHistoryEntry]
    notes: NotRequired[str]
    next_step: NotRequired[str | None]
    interview_scheduled_date: NotRequired[datetime | None]
    rejection_reason: NotRequired[str | None]
    applied_date: datetime
    created_at: datetime
    updated_at: datetime


class MatchFactorDocument(TypedDict):
    """Individual matching factor stored for a recommendation."""

    factor: str
    weight: float
    explanation: str
    score: int


class RecommendationDocument(TypedDict):
    """MongoDB Recommendation document structure."""

    _id: ObjectId
    job_seeker_id: str
    job_id: str
    match_percentage: int
    reasoning: str
    factors: NotRequired[list[MatchFactorDocument]]
    ai_generated: NotRequired[bool]
    viewed: bool
    dismissed: bool
    applied: bool
    created_at: datetime
    job_details: NotRequired[dict[str, object]]
    seeker_details: NotRequired[dict[str, object]]


class SavedJobDocument(TypedDict):
    """MongoDB SavedJob document structure."""

    _id: ObjectId
    job_seeker_id: str
    job_id: str
    notes: NotRequired[str]
    saved_date: datetime
    created_at: datetime
