"""
Employer Profile API routes.
"""

from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth_utils import is_admin
from app.auth.dependencies import get_current_user, get_optional_user, require_employer
from app.crud import employer_profile as profile_crud
from app.database import get_applications_collection, get_jobs_collection
from app.schemas.employer import (
    EmployerProfileCreate,
    EmployerProfileResponse,
    EmployerProfileUpdate,
)
from app.schemas.stats import EmployerJobStatsResponse, TopJobStats
from app.type_definitions import EmployerProfileDocument
from app.utils.datetime_utils import ensure_utc_datetime

router = APIRouter()


def _serialize_profile(document: EmployerProfileDocument) -> EmployerProfileResponse:
    """Convert a database document to the response schema."""
    company_name = document.get("company_name", "")
    company_website = document.get("website") or document.get("company_website")
    company_logo_url = document.get("logo_url") or document.get("company_logo_url")
    industry = document.get("industry")
    company_size = document.get("company_size")
    location = document.get("location")
    # Support both 'description' and 'company_description' for backwards compatibility
    description = document.get("description") or document.get("company_description")
    founded_year = document.get("founded_year")
    contact_email = document.get("contact_email")
    contact_phone = document.get("contact_phone")
    benefits = document.get("benefits_offered", [])
    company_culture = document.get("company_culture")
    jobs_posted_count = document.get("jobs_posted_count", 0)
    active_jobs_count = document.get("active_jobs_count", 0)
    verified = document.get("verified", False)

    return EmployerProfileResponse(
        id=str(document["_id"]),
        user_id=str(document["user_id"]),
        company_name=company_name,
        company_website=company_website,  # type: ignore[arg-type]
        company_logo_url=company_logo_url,  # type: ignore[arg-type]
        industry=industry,
        company_size=company_size,
        location=location,
        description=description,  # type: ignore[arg-type]
        founded_year=founded_year,
        contact_email=contact_email,
        contact_phone=contact_phone,
        benefits_offered=benefits,
        company_culture=company_culture,
        jobs_posted_count=jobs_posted_count,
        active_jobs_count=active_jobs_count,
        verified=verified,
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


def _serialize_profiles(
    documents: Iterable[EmployerProfileDocument],
) -> list[EmployerProfileResponse]:
    """Convert multiple employer profile documents into API response schemas."""
    return [_serialize_profile(doc) for doc in documents]


@router.post("", response_model=EmployerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile: EmployerProfileCreate, employer: dict = Depends(require_employer)
) -> EmployerProfileResponse:
    """
    Create a new employer profile.

    **Requires:** Employer account
    **Limit:** One profile per user

    The profile will be automatically linked to your user account.
    """
    try:
        # Check if user already has a profile
        existing_profile = await profile_crud.get_profile_by_user_id(employer["id"])
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an employer profile",
            )

        profile_data = profile.model_dump(exclude={"user_id"}, exclude_none=True)

        # Use authenticated user's ID
        created_profile = await profile_crud.create_profile(
            user_id=employer["id"],
            profile_data=profile_data,
        )

        return _serialize_profile(created_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=list[EmployerProfileResponse])
async def get_profiles(
    skip: int = 0, limit: int = 100, _current_user: dict | None = Depends(get_optional_user)
) -> list[EmployerProfileResponse]:
    """
    Get all employer profiles.

    **Public endpoint** - Anyone can browse company profiles
    """
    profiles = await profile_crud.get_profiles(skip=skip, limit=limit)

    return _serialize_profiles(profiles)


@router.get("/{profile_id}", response_model=EmployerProfileResponse)
async def get_profile(profile_id: str) -> EmployerProfileResponse:
    """Get employer profile by ID."""
    profile = await profile_crud.get_profile_by_id(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")

    return _serialize_profile(profile)


@router.get("/user/{user_id}", response_model=EmployerProfileResponse)
async def get_profile_by_user(user_id: str) -> EmployerProfileResponse:
    """Get employer profile by user ID."""
    profile = await profile_crud.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Employer profile not found for this user")

    return _serialize_profile(profile)


@router.put("/{profile_id}", response_model=EmployerProfileResponse)
async def update_profile(
    profile_id: str,
    profile_update: EmployerProfileUpdate,
    current_user: dict = Depends(get_current_user),
) -> EmployerProfileResponse:
    """
    Update employer profile.

    **Requires:** Authentication
    **Authorization:** Owner only (or admin)
    """
    # Get existing profile
    existing_profile = await profile_crud.get_profile_by_id(profile_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")

    # Check ownership
    if str(existing_profile.get("user_id")) != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own profile"
        )

    update_data = profile_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated_profile = await profile_crud.update_profile(profile_id, update_data)

    if not updated_profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")

    return _serialize_profile(updated_profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str, current_user: dict = Depends(get_current_user)) -> None:
    """
    Delete employer profile.

    **Requires:** Authentication
    **Authorization:** Owner only (or admin)
    """
    # Get existing profile
    existing_profile = await profile_crud.get_profile_by_id(profile_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")

    # Check ownership
    if str(existing_profile.get("user_id")) != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own profile"
        )

    deleted = await profile_crud.delete_profile(profile_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Employer profile not found")


@router.get("/user/{user_id}/job-stats", response_model=EmployerJobStatsResponse)
async def get_employer_job_stats(
    user_id: str, current_user: dict = Depends(get_current_user)
) -> EmployerJobStatsResponse:
    """
    Get job management statistics for an employer.

    **Requires:** Authentication
    **Authorization:** Only the employer user or admin

    **Note:** Current implementation loads all jobs/applications into memory.
    For production use with large datasets, consider implementing pagination or
    MongoDB aggregation pipelines.

    Returns aggregated statistics including:
    - Total jobs posted (active vs inactive)
    - Total applications received across all jobs
    - Recent application activity (last 7 days)
    - Top 5 jobs by application count
    """
    # Check authorization
    if user_id != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own job statistics",
        )

    jobs_collection = get_jobs_collection()
    applications_collection = get_applications_collection()

    # Get all jobs posted by this employer
    jobs_cursor = jobs_collection.find({"posted_by": user_id})
    jobs = await jobs_cursor.to_list(length=10000)

    total_jobs = len(jobs)
    active_jobs = sum(1 for job in jobs if job.get("is_active", True))
    inactive_jobs = total_jobs - active_jobs

    # Get all job IDs
    job_ids = [str(job["_id"]) for job in jobs]

    # Get all applications for these jobs
    total_applications_received = 0
    applications_this_week = 0
    job_application_counts: dict[str, int] = {}

    if job_ids:
        applications_cursor = applications_collection.find({"job_id": {"$in": job_ids}})
        applications = await applications_cursor.to_list(length=10000)

        total_applications_received = len(applications)

        # Calculate recent applications (last 7 days)
        seven_days_ago = datetime.now(UTC) - timedelta(days=7)
        applications_this_week = 0
        for app in applications:
            applied_date = app.get("applied_date")
            if applied_date:
                # Use utility function for timezone-aware comparison
                applied_date = ensure_utc_datetime(applied_date)
                if applied_date and applied_date >= seven_days_ago:
                    applications_this_week += 1

        # Count applications per job
        for app in applications:
            job_id = app.get("job_id", "")
            job_application_counts[job_id] = job_application_counts.get(job_id, 0) + 1

    # Create job lookup map
    job_map = {str(job["_id"]): job for job in jobs}

    # Build top jobs list
    top_jobs_data = []
    for job_id, app_count in sorted(
        job_application_counts.items(), key=lambda x: x[1], reverse=True
    )[:5]:
        job = job_map.get(job_id)
        if job:
            top_jobs_data.append(
                TopJobStats(
                    job_id=job_id,
                    title=job["title"],
                    applications=app_count,
                    is_active=job.get("is_active", True),
                )
            )

    return EmployerJobStatsResponse(
        employer_id=user_id,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        inactive_jobs=inactive_jobs,
        total_applications_received=total_applications_received,
        applications_this_week=applications_this_week,
        top_jobs=top_jobs_data,
    )
