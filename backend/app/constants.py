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
    """
    Application status enum.

    Workflow:
        SUBMITTED → UNDER_REVIEW → INTERVIEW_SCHEDULED → INTERVIEWED
        → OFFER_EXTENDED → ACCEPTED (final)

    Alternative paths:
        - Any status → REJECTED (final)
        - INTERVIEW_SCHEDULED → INTERVIEW_CANCELLED → back to UNDER_REVIEW

    Final states (no further transitions allowed):
        - ACCEPTED: Candidate hired, job filled
        - REJECTED: Application declined at any stage
    """

    SUBMITTED = "Application Submitted"
    UNDER_REVIEW = "Under Review"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    INTERVIEWED = "Interviewed"
    INTERVIEW_CANCELLED = "Interview Cancelled"
    REJECTED = "Rejected"
    OFFER_EXTENDED = "Offer Extended"
    ACCEPTED = "Accepted"
