"""
Application constants and enums.
"""

from enum import Enum


class InterviewType(str, Enum):
    """Interview type enum."""

    PHONE = "phone"
    VIDEO = "video"
    IN_PERSON = "in-person"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"


class InterviewStatus(str, Enum):
    """Interview status enum."""

    SCHEDULED = "scheduled"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ApplicationStatus(str, Enum):
    """Application status enum."""

    SUBMITTED = "Application Submitted"
    UNDER_REVIEW = "Under Review"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    INTERVIEWED = "interviewed"
    INTERVIEW_CANCELLED = "interview_cancelled"
    REJECTED = "Rejected"
    OFFER_EXTENDED = "Offer Extended"
    ACCEPTED = "Accepted"
