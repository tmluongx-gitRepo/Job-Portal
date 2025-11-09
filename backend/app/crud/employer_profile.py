"""
CRUD operations for Employer Profile model.
"""

from datetime import UTC, datetime
from typing import cast

from bson import ObjectId

from app.database import get_employer_profiles_collection
from app.types import EmployerProfileDocument


async def create_profile(user_id: str, profile_data: dict[str, object]) -> EmployerProfileDocument:
    """Create a new employer profile."""
    collection = get_employer_profiles_collection()

    existing_profile = await collection.find_one({"user_id": ObjectId(user_id)})
    if existing_profile:
        raise ValueError(f"Employer profile already exists for user {user_id}")

    profile_doc = {
        "user_id": ObjectId(user_id),
        **profile_data,
        "jobs_posted_count": 0,
        "active_jobs_count": 0,
        "verified": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    result = await collection.insert_one(profile_doc)
    profile_doc["_id"] = result.inserted_id
    return cast(EmployerProfileDocument, profile_doc)


async def get_profile_by_id(profile_id: str) -> EmployerProfileDocument | None:
    """Get employer profile by ID."""
    collection = get_employer_profiles_collection()

    try:
        result = await collection.find_one({"_id": ObjectId(profile_id)})
        return cast(EmployerProfileDocument, result) if result else None
    except Exception:
        return None


async def get_profile_by_user_id(user_id: str) -> EmployerProfileDocument | None:
    """Get employer profile by user ID."""
    collection = get_employer_profiles_collection()

    try:
        result = await collection.find_one({"user_id": ObjectId(user_id)})
        return cast(EmployerProfileDocument, result) if result else None
    except Exception:
        return None


async def get_profiles(skip: int = 0, limit: int = 100, filters: dict[str, object] | None = None) -> list[EmployerProfileDocument]:
    """Get all employer profiles."""
    collection = get_employer_profiles_collection()

    query: dict[str, object] = dict(filters) if filters else {}
    cursor = collection.find(query).skip(skip).limit(limit).sort("updated_at", -1)
    results = await cursor.to_list(length=limit)

    return cast(list[EmployerProfileDocument], results)


async def update_profile(profile_id: str, update_data: dict[str, object]) -> EmployerProfileDocument | None:
    """Update employer profile."""
    collection = get_employer_profiles_collection()

    update_data["updated_at"] = datetime.now(UTC)

    try:
        result = await collection.find_one_and_update(
            {"_id": ObjectId(profile_id)},
            {"$set": update_data},
            return_document=True,
        )
        return cast(EmployerProfileDocument, result) if result else None
    except Exception:
        return None


async def delete_profile(profile_id: str) -> bool:
    """Delete employer profile."""
    collection = get_employer_profiles_collection()

    try:
        result = await collection.delete_one({"_id": ObjectId(profile_id)})
    except Exception:
        return False
    else:
        return bool(result.deleted_count > 0)


async def increment_job_counts(
    profile_id: str, posted_delta: int = 0, active_delta: int = 0
) -> bool:
    """Adjust job counters for an employer profile."""
    collection = get_employer_profiles_collection()

    try:
        increments: dict[str, int] = {}
        if posted_delta:
            increments["jobs_posted_count"] = posted_delta
        if active_delta:
            increments["active_jobs_count"] = active_delta

        if not increments:
            return True

        update = {"$inc": increments}
        result = await collection.update_one({"_id": ObjectId(profile_id)}, update)
    except Exception:
        return False
    else:
        return bool(result.modified_count > 0)
