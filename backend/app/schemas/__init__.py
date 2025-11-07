from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.job import JobBase, JobCreate, JobUpdate, JobResponse
from app.schemas.job_seeker import (
    JobSeekerPreferencesSchema,
    JobSeekerProfileBase,
    JobSeekerProfileCreate,
    JobSeekerProfileUpdate,
    JobSeekerProfileResponse,
)
from app.schemas.application import (
    StatusHistoryEntrySchema,
    ApplicationBase,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
)
from app.schemas.employer import (
    EmployerProfileBase,
    EmployerProfileCreate,
    EmployerProfileUpdate,
    EmployerProfileResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Job schemas
    "JobBase",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    # Job Seeker schemas
    "JobSeekerPreferencesSchema",
    "JobSeekerProfileBase",
    "JobSeekerProfileCreate",
    "JobSeekerProfileUpdate",
    "JobSeekerProfileResponse",
    # Application schemas
    "StatusHistoryEntrySchema",
    "ApplicationBase",
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    # Employer schemas
    "EmployerProfileBase",
    "EmployerProfileCreate",
    "EmployerProfileUpdate",
    "EmployerProfileResponse",
]
