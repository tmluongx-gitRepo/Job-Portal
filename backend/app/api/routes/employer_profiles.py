"""Employer Profile API routes."""

from collections.abc import Iterable

from fastapi import APIRouter, HTTPException, status

from app.crud import employer_profile as profile_crud
from app.schemas.employer import (
    EmployerProfileCreate,
    EmployerProfileResponse,
    EmployerProfileUpdate,
)
from app.types import EmployerProfileDocument

router = APIRouter()


def _serialize_profile(document: EmployerProfileDocument) -> EmployerProfileResponse:
    """Convert a database document to the response schema."""

    company_name = document.get("company_name", "")
    company_website = document.get("website")
    company_logo_url = document.get("logo_url")
    industry = document.get("industry")
    company_size = document.get("company_size")
    location = document.get("location")
    company_description = document.get("company_description")
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
        company_website=company_website,
        company_logo_url=company_logo_url,
        industry=industry,
        company_size=company_size,
        location=location,
        description=company_description,
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


def _serialize_profiles(documents: Iterable[EmployerProfileDocument]) -> list[EmployerProfileResponse]:
    return [_serialize_profile(doc) for doc in documents]


@router.post("", response_model=EmployerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: EmployerProfileCreate) -> EmployerProfileResponse:
    """Create a new employer profile."""
    try:
        profile_data = profile.model_dump(exclude={"user_id"}, exclude_none=True)
        created_profile = await profile_crud.create_profile(
            user_id=profile.user_id,
            profile_data=profile_data,
        )

        return _serialize_profile(created_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=list[EmployerProfileResponse])
async def get_profiles(skip: int = 0, limit: int = 100) -> list[EmployerProfileResponse]:
    """Get all employer profiles."""
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
async def update_profile(profile_id: str, profile_update: EmployerProfileUpdate) -> EmployerProfileResponse:
    """Update employer profile."""
    update_data = profile_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated_profile = await profile_crud.update_profile(profile_id, update_data)

    if not updated_profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")

    return _serialize_profile(updated_profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str) -> None:
    """Delete employer profile."""
    deleted = await profile_crud.delete_profile(profile_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Employer profile not found")
