"""Application-wide constants and enums."""

from enum import Enum


class InterviewStatus(str, Enum):
    """Interview status enum."""

    SCHEDULED = "Scheduled"
    RESCHEDULED = "Rescheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class InterviewType(str, Enum):
    """Interview type enum."""

    PHONE = "phone"
    VIDEO = "video"
    IN_PERSON = "in-person"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"


class ApplicationStatus(str, Enum):
    """
    Application status enum.

    States marked as 'TERMINAL' should not allow further transitions.
    """

    # Active states
    SUBMITTED = "Application Submitted"
    UNDER_REVIEW = "Under Review"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    INTERVIEWED = "Interviewed"
    OFFER_EXTENDED = "Offer Extended"

    # Terminal states (no further transitions allowed)
    ACCEPTED = "Accepted"  # Also known as "Hired" - employer accepted applicant
    REJECTED = "Rejected"  # Application rejected
    INTERVIEW_CANCELLED = "Interview Cancelled"

    @classmethod
    def terminal_states(cls) -> set[str]:
        """Return set of terminal states that should not allow transitions."""
        return {cls.ACCEPTED, cls.REJECTED}

    @classmethod
    def is_terminal(cls, status: str) -> bool:
        """Check if a status is terminal (no further transitions allowed)."""
        return status in cls.terminal_states()


# Display labels for application statuses (optional - for future use)
APPLICATION_STATUS_LABELS = {
    ApplicationStatus.SUBMITTED: "Application Submitted",
    ApplicationStatus.UNDER_REVIEW: "Under Review",
    ApplicationStatus.INTERVIEW_SCHEDULED: "Interview Scheduled",
    ApplicationStatus.INTERVIEWED: "Interviewed",
    ApplicationStatus.OFFER_EXTENDED: "Offer Extended",
    ApplicationStatus.ACCEPTED: "Hired",
    ApplicationStatus.REJECTED: "Rejected",
    ApplicationStatus.INTERVIEW_CANCELLED: "Interview Cancelled",
}
