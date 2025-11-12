"""
Job Seeker Profile API routes.
"""

from collections.abc import Iterable

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user, get_optional_user, require_job_seeker
from app.crud import job_seeker_profile as profile_crud
from app.schemas.job_seeker import (
    JobSeekerPreferencesSchema,
    JobSeekerProfileCreate,
    JobSeekerProfileResponse,
    JobSeekerProfileUpdate,
)
from app.schemas.stats import JobSeekerApplicationStatsResponse
from app.type_definitions import JobSeekerProfileDocument

router = APIRouter()


async def _serialize_profile(document: JobSeekerProfileDocument) -> JobSeekerProfileResponse:
    """Convert a database document to the response schema."""
    first_name = document.get("first_name", "")
    last_name = document.get("last_name", "")
    email = document.get("email", "")
    phone = document.get("phone")
    location = document.get("location")
    bio = document.get("bio")
    skills = document.get("skills", [])
    experience_years = document.get("experience_years", 0)
    education_level = document.get("education_level")
    preferences_data = document.get("preferences")
    preferences = JobSeekerPreferencesSchema(**preferences_data) if preferences_data else None
    profile_views = document.get("profile_views", 0)
    profile_completion_percentage = document.get("profile_completion_percentage")

    # Populate resume fields from resumes collection
    resume_file_url = None
    resume_file_name = None

    from app.crud import resume as resume_crud

    resume = await resume_crud.get_resume_by_job_seeker(str(document["user_id"]))
    if resume:
        resume_file_url = f"/api/resumes/{resume['_id']}/download"
        resume_file_name = resume["original_filename"]

    return JobSeekerProfileResponse(
        id=str(document["_id"]),
        user_id=str(document["user_id"]),
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        location=location,
        bio=bio,
        skills=skills,
        experience_years=experience_years,
        education_level=education_level,
        resume_file_url=resume_file_url,
        resume_file_name=resume_file_name,
        preferences=preferences,
        profile_views=profile_views,
        profile_completion_percentage=profile_completion_percentage,
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


async def _serialize_profiles(
    documents: Iterable[JobSeekerProfileDocument],
) -> list[JobSeekerProfileResponse]:
    """
    Convert multiple job seeker profile documents into API response schemas.

    Optimized to batch-fetch resumes to avoid N+1 queries.
    """
    from app.database import get_resumes_collection

    # Convert to list to allow multiple iterations
    docs_list = list(documents)

    if not docs_list:
        return []

    # Batch fetch all resumes for these profiles
    user_ids = [str(doc["user_id"]) for doc in docs_list]
    resumes_collection = get_resumes_collection()
    resumes_cursor = resumes_collection.find({"job_seeker_id": {"$in": user_ids}})
    # Motor requires an integer length; use max of user count or 1000 as reasonable limit
    resumes_list = await resumes_cursor.to_list(length=max(len(user_ids), 1000))

    # Create a map of user_id -> resume for O(1) lookup
    resume_map = {resume["job_seeker_id"]: resume for resume in resumes_list}

    # Serialize profiles with pre-fetched resumes
    results = []
    for doc in docs_list:
        user_id_str = str(doc["user_id"])
        resume = resume_map.get(user_id_str)

        # Build resume fields
        resume_file_url = None
        resume_file_name = None
        if resume:
            resume_file_url = f"/api/resumes/{resume['_id']}/download"
            resume_file_name = resume["original_filename"]

        # Serialize profile without additional DB call
        first_name = doc.get("first_name", "")
        last_name = doc.get("last_name", "")
        email = doc.get("email", "")
        phone = doc.get("phone")
        location = doc.get("location")
        bio = doc.get("bio")
        skills = doc.get("skills", [])
        experience_years = doc.get("experience_years", 0)
        education_level = doc.get("education_level")
        preferences_data = doc.get("preferences")
        preferences = JobSeekerPreferencesSchema(**preferences_data) if preferences_data else None
        profile_views = doc.get("profile_views", 0)
        profile_completion_percentage = doc.get("profile_completion_percentage")

        results.append(
            JobSeekerProfileResponse(
                id=str(doc["_id"]),
                user_id=user_id_str,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                location=location,
                bio=bio,
                skills=skills,
                experience_years=experience_years,
                education_level=education_level,
                resume_file_url=resume_file_url,
                resume_file_name=resume_file_name,
                preferences=preferences,
                profile_views=profile_views,
                profile_completion_percentage=profile_completion_percentage,
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
            )
        )

    return results


@router.post("", response_model=JobSeekerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile: JobSeekerProfileCreate, job_seeker: dict = Depends(require_job_seeker)
) -> JobSeekerProfileResponse:
    """
    Create a new job seeker profile.

    **Requires:** Job Seeker account
    **Limit:** One profile per user

    The profile will be automatically linked to your user account.
    """
    try:
        # Check if user already has a profile
        existing_profile = await profile_crud.get_profile_by_user_id(job_seeker["id"])
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a job seeker profile",
            )

        # Convert to dict and remove None values
        profile_data = profile.model_dump(exclude={"user_id"}, exclude_none=True)

        # Use authenticated user's ID
        created_profile = await profile_crud.create_profile(
            user_id=job_seeker["id"], profile_data=profile_data
        )

        return await _serialize_profile(created_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=list[JobSeekerProfileResponse])
async def get_profiles(
    skip: int = 0, limit: int = 100, _current_user: dict | None = Depends(get_optional_user)
) -> list[JobSeekerProfileResponse]:
    """
    Get all job seeker profiles.

    **Public endpoint** - Employers can browse candidates
    """
    profiles = await profile_crud.get_profiles(skip=skip, limit=limit)

    return await _serialize_profiles(profiles)


@router.get("/search", response_model=list[JobSeekerProfileResponse])
async def search_profiles(
    skills: list[str] = Query(None, description="Skills to search for"),
    location: str = Query(None, description="Location to search for"),
    min_experience: int = Query(None, ge=0, description="Minimum years of experience"),
    max_experience: int = Query(None, ge=0, description="Maximum years of experience"),
    skip: int = 0,
    limit: int = 100,
) -> list[JobSeekerProfileResponse]:
    """Search job seeker profiles by criteria."""
    profiles = await profile_crud.search_profiles(
        skills=skills,
        location=location,
        min_experience=min_experience,
        max_experience=max_experience,
        skip=skip,
        limit=limit,
    )

    return await _serialize_profiles(profiles)


@router.get("/{profile_id}", response_model=JobSeekerProfileResponse)
async def get_profile(
    profile_id: str, increment_views: bool = Query(False)
) -> JobSeekerProfileResponse:
    """Get profile by ID."""
    profile = await profile_crud.get_profile_by_id(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Optionally increment view count
    if increment_views:
        await profile_crud.increment_profile_views(profile_id)
        profile["profile_views"] = profile.get("profile_views", 0) + 1

    return await _serialize_profile(profile)


@router.get("/user/{user_id}", response_model=JobSeekerProfileResponse)
async def get_profile_by_user(user_id: str) -> JobSeekerProfileResponse:
    """Get profile by user ID."""
    profile = await profile_crud.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found for this user")

    return await _serialize_profile(profile)


@router.put("/{profile_id}", response_model=JobSeekerProfileResponse)
async def update_profile(
    profile_id: str,
    profile_update: JobSeekerProfileUpdate,
    current_user: dict = Depends(get_current_user),
) -> JobSeekerProfileResponse:
    """
    Update profile.

    **Requires:** Authentication
    **Authorization:** Owner only (or admin)
    """
    # Get existing profile
    existing_profile = await profile_crud.get_profile_by_id(profile_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check ownership
    from app.auth.auth_utils import is_admin

    if str(existing_profile.get("user_id")) != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own profile"
        )

    # Build update dict (only include provided fields)
    update_data = profile_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated_profile = await profile_crud.update_profile(profile_id, update_data)

    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return await _serialize_profile(updated_profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str, current_user: dict = Depends(get_current_user)) -> None:
    """
    Delete profile.

    **Requires:** Authentication
    **Authorization:** Owner only (or admin)
    """
    # Get existing profile
    existing_profile = await profile_crud.get_profile_by_id(profile_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check ownership
    from app.auth.auth_utils import is_admin

    if str(existing_profile.get("user_id")) != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own profile"
        )

    deleted = await profile_crud.delete_profile(profile_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")


@router.get("/user/{user_id}/application-stats", response_model=JobSeekerApplicationStatsResponse)
async def get_job_seeker_application_stats(  # noqa: PLR0912
    user_id: str, current_user: dict = Depends(get_current_user)
) -> JobSeekerApplicationStatsResponse:
    """
    Get application statistics for a job seeker.

    **Requires:** Authentication
    **Authorization:** Only the job seeker user or admin

    Returns aggregated statistics including:
    - Total applications submitted
    - Applications by status breakdown
    - Recent application activity (last 7 days)
    - Interview metrics (scheduled, completed, average rating if visible)
    - Last application date

    **Note:** Current implementation loads all applications/interviews into memory.
    For production use with large datasets, consider implementing pagination or
    MongoDB aggregation pipelines.
    """
    from datetime import UTC, datetime, timedelta

    from app.auth.auth_utils import is_admin
    from app.database import get_applications_collection, get_interviews_collection

    # Check authorization
    if user_id != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own application statistics",
        )

    # Get job seeker profile
    profile = await profile_crud.get_profile_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job seeker profile not found for this user",
        )

    job_seeker_id = str(profile["_id"])

    applications_collection = get_applications_collection()
    interviews_collection = get_interviews_collection()

    # Get all applications for this job seeker
    applications_cursor = applications_collection.find({"job_seeker_id": job_seeker_id})
    applications = await applications_cursor.to_list(length=10000)

    total_applications = len(applications)

    # Calculate applications by status
    applications_by_status: dict[str, int] = {}
    for app in applications:
        status_val = app.get("status", "Unknown")
        applications_by_status[status_val] = applications_by_status.get(status_val, 0) + 1

    # Calculate recent applications (last 7 days)
    seven_days_ago = datetime.now(UTC) - timedelta(days=7)
    applications_this_week = 0
    for app in applications:
        applied_date = app.get("applied_date")
        if applied_date:
            # Ensure timezone-aware comparison
            if applied_date.tzinfo is None:
                applied_date = applied_date.replace(tzinfo=UTC)
            if applied_date >= seven_days_ago:
                applications_this_week += 1

    # Get last application date
    last_application_date = None
    if applications:
        last_application_date = max(
            (app.get("applied_date") for app in applications if app.get("applied_date")),
            default=None,
        )

    # Get application IDs for interview lookup
    application_ids = [str(app["_id"]) for app in applications]

    # Get interviews for these applications
    interviews_scheduled = 0
    interviews_completed = 0
    ratings: list[float] = []

    if application_ids:
        interviews_cursor = interviews_collection.find({"application_id": {"$in": application_ids}})
        interviews = await interviews_cursor.to_list(length=10000)

        for interview in interviews:
            interview_status = interview.get("status", "")
            if interview_status in ["scheduled", "rescheduled"]:
                interviews_scheduled += 1
            elif interview_status == "completed":
                interviews_completed += 1
                # Job seekers can see their own ratings if they exist
                rating = interview.get("rating")
                # Validate rating is numeric before adding
                if rating is not None and isinstance(rating, int | float):
                    ratings.append(float(rating))

    # Calculate average interview rating
    avg_interview_rating = sum(ratings) / len(ratings) if ratings else None

    return JobSeekerApplicationStatsResponse(
        job_seeker_id=job_seeker_id,
        total_applications=total_applications,
        applications_by_status=applications_by_status,
        applications_this_week=applications_this_week,
        interviews_scheduled=interviews_scheduled,
        interviews_completed=interviews_completed,
        avg_interview_rating=avg_interview_rating,
        last_application_date=last_application_date,
    )
