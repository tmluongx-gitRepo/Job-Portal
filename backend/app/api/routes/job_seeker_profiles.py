"""Job Seeker Profile API routes."""

from collections.abc import Iterable

from fastapi import APIRouter, HTTPException, Query, status

from app.crud import job_seeker_profile as profile_crud
from app.schemas.job_seeker import (
    JobSeekerPreferencesSchema,
    JobSeekerProfileCreate,
    JobSeekerProfileResponse,
    JobSeekerProfileUpdate,
)
from app.types import JobSeekerProfileDocument

router = APIRouter()


def _serialize_profile(document: JobSeekerProfileDocument) -> JobSeekerProfileResponse:
    """Convert a job seeker document into the response schema."""

    skills = document.get("skills", [])
    raw_preferences = document.get("preferences")
    resume_url = document.get("resume_url")
    resume_file_url = document.get("resume_file_url")
    resume_file_name = document.get("resume_file_name")
    education_level = document.get("education_level")
    profile_views = document.get("profile_views", 0)
    profile_completion = document.get("profile_completion_percentage")

    return JobSeekerProfileResponse(
        id=str(document["_id"]),
        user_id=str(document["user_id"]),
        first_name=document.get("first_name", ""),
        last_name=document.get("last_name", ""),
        email=document.get("email", ""),
        phone=document.get("phone"),
        location=document.get("location"),
        bio=document.get("bio"),
        resume_file_url=resume_url or resume_file_url,
        resume_file_name=resume_file_name,
        skills=skills,
        experience_years=document.get("experience_years", 0),
        education_level=education_level,
        preferences=(
            JobSeekerPreferencesSchema.model_validate(raw_preferences)
            if raw_preferences is not None
            else None
        ),
        profile_views=profile_views,
        profile_completion_percentage=profile_completion,
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


def _serialize_profiles(documents: Iterable[JobSeekerProfileDocument]) -> list[JobSeekerProfileResponse]:
    return [_serialize_profile(doc) for doc in documents]


@router.post("", response_model=JobSeekerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: JobSeekerProfileCreate) -> JobSeekerProfileResponse:
    """Create a new job seeker profile."""
    try:
        # Convert to dict and remove None values
        profile_data = profile.model_dump(exclude={"user_id"}, exclude_none=True)

        created_profile = await profile_crud.create_profile(
            user_id=profile.user_id, profile_data=profile_data
        )

        return _serialize_profile(created_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=list[JobSeekerProfileResponse])
async def get_profiles(skip: int = 0, limit: int = 100) -> list[JobSeekerProfileResponse]:
    """Get all job seeker profiles."""
    profiles = await profile_crud.get_profiles(skip=skip, limit=limit)

    return _serialize_profiles(profiles)


@router.get("/search", response_model=list[JobSeekerProfileResponse])
async def search_profiles(
    skills: list[str] | None = Query(None, description="Skills to search for"),
    location: str | None = Query(None, description="Location to search for"),
    min_experience: int | None = Query(None, ge=0, description="Minimum years of experience"),
    max_experience: int | None = Query(None, ge=0, description="Maximum years of experience"),
    skip: int = 0,
    limit: int = 100,
)-> list[JobSeekerProfileResponse]:
    """Search job seeker profiles by criteria."""
    profiles = await profile_crud.search_profiles(
        skills=skills,
        location=location,
        min_experience=min_experience,
        max_experience=max_experience,
        skip=skip,
        limit=limit,
    )

    return _serialize_profiles(profiles)


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

    return _serialize_profile(profile)


@router.get("/user/{user_id}", response_model=JobSeekerProfileResponse)
async def get_profile_by_user(user_id: str) -> JobSeekerProfileResponse:
    """Get profile by user ID."""
    profile = await profile_crud.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found for this user")

    return _serialize_profile(profile)


@router.put("/{profile_id}", response_model=JobSeekerProfileResponse)
async def update_profile(profile_id: str, profile_update: JobSeekerProfileUpdate) -> JobSeekerProfileResponse:
    """Update profile."""
    # Build update dict (only include provided fields)
    update_data = profile_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated_profile = await profile_crud.update_profile(profile_id, update_data)

    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return _serialize_profile(updated_profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str) -> None:
    """Delete profile."""
    deleted = await profile_crud.delete_profile(profile_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
