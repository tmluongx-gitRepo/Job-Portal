"""Employer Profile API routes."""

from typing import Iterable

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

    company_name = document["company_name"] if "company_name" in document else ""
    company_website = document["website"] if "website" in document else None
    company_logo_url = document["logo_url"] if "logo_url" in document else None
    industry = document["industry"] if "industry" in document else None
    company_size = document["company_size"] if "company_size" in document else None
    location = document["location"] if "location" in document else None
    company_description = (
        document["company_description"] if "company_description" in document else None
    )
    founded_year = document["founded_year"] if "founded_year" in document else None
    contact_email = document["contact_email"] if "contact_email" in document else None
    contact_phone = document["contact_phone"] if "contact_phone" in document else None
    benefits = document["benefits_offered"] if "benefits_offered" in document else []
    company_culture = document["company_culture"] if "company_culture" in document else None
    jobs_posted_count = document["jobs_posted_count"] if "jobs_posted_count" in document else 0
    active_jobs_count = document["active_jobs_count"] if "active_jobs_count" in document else 0
    verified = document["verified"] if "verified" in document else False

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
