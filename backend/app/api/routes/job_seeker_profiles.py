"""
Job Seeker Profile API routes.
"""
from fastapi import APIRouter, HTTPException, status, Query


from app.schemas.job_seeker import (
    JobSeekerProfileCreate,
    JobSeekerProfileUpdate,
    JobSeekerProfileResponse
)
from app.crud import job_seeker_profile as profile_crud


router = APIRouter()


@router.post("", response_model=JobSeekerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: JobSeekerProfileCreate):
    """Create a new job seeker profile."""
    try:
        # Convert to dict and remove None values
        profile_data = profile.model_dump(exclude={"user_id"}, exclude_none=True)

        created_profile = await profile_crud.create_profile(
            user_id=profile.user_id,
            profile_data=profile_data
        )

        return JobSeekerProfileResponse(
            id=str(created_profile["_id"]),
            user_id=str(created_profile["user_id"]),
            **{k: v for k, v in created_profile.items() if k not in ["_id", "user_id"]},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[JobSeekerProfileResponse])
async def get_profiles(skip: int = 0, limit: int = 100):
    """Get all job seeker profiles."""
    profiles = await profile_crud.get_profiles(skip=skip, limit=limit)

    return [
        JobSeekerProfileResponse(
            id=str(profile["_id"]),
            user_id=str(profile["user_id"]),
            **{k: v for k, v in profile.items() if k not in ["_id", "user_id"]},
        )
        for profile in profiles
    ]


@router.get("/search", response_model=list[JobSeekerProfileResponse])
async def search_profiles(
    skills: list[str] = Query(None, description="Skills to search for"),
    location: str = Query(None, description="Location to search for"),
    min_experience: int = Query(None, ge=0, description="Minimum years of experience"),
    max_experience: int = Query(None, ge=0, description="Maximum years of experience"),
    skip: int = 0,
    limit: int = 100
):
    """Search job seeker profiles by criteria."""
    profiles = await profile_crud.search_profiles(
        skills=skills,
        location=location,
        min_experience=min_experience,
        max_experience=max_experience,
        skip=skip,
        limit=limit
    )

    return [
        JobSeekerProfileResponse(
            id=str(profile["_id"]),
            user_id=str(profile["user_id"]),
            **{k: v for k, v in profile.items() if k not in ["_id", "user_id"]},
        )
        for profile in profiles
    ]


@router.get("/{profile_id}", response_model=JobSeekerProfileResponse)
async def get_profile(profile_id: str, increment_views: bool = Query(False)):
    """Get profile by ID."""
    profile = await profile_crud.get_profile_by_id(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Optionally increment view count
    if increment_views:
        await profile_crud.increment_profile_views(profile_id)
        profile["profile_views"] = profile.get("profile_views", 0) + 1

    return JobSeekerProfileResponse(
        id=str(profile["_id"]),
        user_id=str(profile["user_id"]),
        **{k: v for k, v in profile.items() if k not in ["_id", "user_id"]},
    )


@router.get("/user/{user_id}", response_model=JobSeekerProfileResponse)
async def get_profile_by_user(user_id: str):
    """Get profile by user ID."""
    profile = await profile_crud.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found for this user")

    return JobSeekerProfileResponse(
        id=str(profile["_id"]),
        user_id=str(profile["user_id"]),
        **{k: v for k, v in profile.items() if k not in ["_id", "user_id"]},
    )


@router.put("/{profile_id}", response_model=JobSeekerProfileResponse)
async def update_profile(profile_id: str, profile_update: JobSeekerProfileUpdate):
    """Update profile."""
    # Build update dict (only include provided fields)
    update_data = profile_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated_profile = await profile_crud.update_profile(profile_id, update_data)

    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return JobSeekerProfileResponse(
        id=str(updated_profile["_id"]),
        user_id=str(updated_profile["user_id"]),
        **{k: v for k, v in updated_profile.items() if k not in ["_id", "user_id"]},
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str):
    """Delete profile."""
    deleted = await profile_crud.delete_profile(profile_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")


