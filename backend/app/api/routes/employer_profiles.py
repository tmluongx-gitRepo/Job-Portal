"""
Employer Profile API routes.
"""
from fastapi import APIRouter, HTTPException,, status


from app.schemas.employer import (
    EmployerProfileCreate,
    EmployerProfileUpdate,
    EmployerProfileResponse,
)
from app.crud import employer_profile as profile_crud


router = APIRouter()


@router.post("", response_model=EmployerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: EmployerProfileCreate):
    """Create a new employer profile."""
    try:
        profile_data = profile.model_dump(exclude={"user_id"}, exclude_none=True)
        created_profile = await profile_crud.create_profile(
            user_id=profile.user_id,
            profile_data=profile_data,
        )

        return EmployerProfileResponse(
            id=str(created_profile["_id"]),
            user_id=str(created_profile["user_id"]),
            **{k: v for k, v in created_profile.items() if k not in ["_id", "user_id"]},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[EmployerProfileResponse])
async def get_profiles(skip: int = 0, limit: int = 100):
    """Get all employer profiles."""
    profiles = await profile_crud.get_profiles(skip=skip, limit=limit)

    return [
        EmployerProfileResponse(
            id=str(profile["_id"]),
            user_id=str(profile["user_id"]),
            **{k: v for k, v in profile.items() if k not in ["_id", "user_id"]},
        )
        for profile in profiles
    ]


@router.get("/{profile_id}", response_model=EmployerProfileResponse)
async def get_profile(profile_id: str):
    """Get employer profile by ID."""
    profile = await profile_crud.get_profile_by_id(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")

    return EmployerProfileResponse(
        id=str(profile["_id"]),
        user_id=str(profile["user_id"]),
        **{k: v for k, v in profile.items() if k not in ["_id", "user_id"]},
    )


@router.get("/user/{user_id}", response_model=EmployerProfileResponse)
async def get_profile_by_user(user_id: str):
    """Get employer profile by user ID."""
    profile = await profile_crud.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Employer profile not found for this user")

    return EmployerProfileResponse(
        id=str(profile["_id"]),
        user_id=str(profile["user_id"]),
        **{k: v for k, v in profile.items() if k not in ["_id", "user_id"]},
    )


@router.put("/{profile_id}", response_model=EmployerProfileResponse)
async def update_profile(profile_id: str, profile_update: EmployerProfileUpdate):
    """Update employer profile."""
    update_data = profile_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated_profile = await profile_crud.update_profile(profile_id, update_data)

    if not updated_profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")

    return EmployerProfileResponse(
        id=str(updated_profile["_id"]),
        user_id=str(updated_profile["user_id"]),
        **{k: v for k, v in updated_profile.items() if k not in ["_id", "user_id"]},
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str):
    """Delete employer profile."""
    deleted = await profile_crud.delete_profile(profile_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Employer profile not found")
