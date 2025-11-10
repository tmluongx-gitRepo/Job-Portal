"""
CRUD operations for Job Seeker Profile model.
"""

from datetime import UTC, datetime
from typing import cast

from bson import ObjectId

from app.database import get_job_seeker_profiles_collection
from app.type_definitions import JobSeekerProfileDocument


async def create_profile(user_id: str, profile_data: dict[str, object]) -> JobSeekerProfileDocument:
    """Create a new job seeker profile."""
    collection = get_job_seeker_profiles_collection()

    # Check if profile already exists for this user
    existing_profile = await collection.find_one({"user_id": ObjectId(user_id)})
    if existing_profile:
        raise ValueError(f"Profile already exists for user {user_id}")

    profile_doc = {
        "user_id": ObjectId(user_id),
        **profile_data,
        "profile_views": 0,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    result = await collection.insert_one(profile_doc)
    profile_doc["_id"] = result.inserted_id
    return cast(JobSeekerProfileDocument, profile_doc)


async def get_profile_by_id(profile_id: str) -> JobSeekerProfileDocument | None:
    """Get profile by ID."""
    collection = get_job_seeker_profiles_collection()

    try:
        result = await collection.find_one({"_id": ObjectId(profile_id)})
        return cast(JobSeekerProfileDocument, result) if result else None
    except Exception:
        return None


async def get_profile_by_user_id(user_id: str) -> JobSeekerProfileDocument | None:
    """Get profile by user ID."""
    collection = get_job_seeker_profiles_collection()

    try:
        result = await collection.find_one({"user_id": ObjectId(user_id)})
        return cast(JobSeekerProfileDocument, result) if result else None
    except Exception:
        return None


async def get_profiles(
    skip: int = 0, limit: int = 100, filters: dict[str, object] | None = None
) -> list[JobSeekerProfileDocument]:
    """Get all profiles with pagination and optional filters."""
    collection = get_job_seeker_profiles_collection()

    query: dict[str, object] = dict(filters) if filters else {}
    cursor = collection.find(query).skip(skip).limit(limit).sort("updated_at", -1)
    results = await cursor.to_list(length=limit)

    return cast(list[JobSeekerProfileDocument], results)


async def search_profiles(
    skills: list[str] | None = None,
    location: str | None = None,
    min_experience: int | None = None,
    max_experience: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[JobSeekerProfileDocument]:
    """Search profiles with various criteria."""
    collection = get_job_seeker_profiles_collection()

    query: dict[str, object] = {}

    if skills:
        # Match any of the provided skills
        query["skills"] = {"$in": skills}

    if location:
        # Case-insensitive location search
        query["location"] = {"$regex": location, "$options": "i"}

    if min_experience is not None or max_experience is not None:
        experience_filter: dict[str, int] = {}
        if min_experience is not None:
            experience_filter["$gte"] = min_experience
        if max_experience is not None:
            experience_filter["$lte"] = max_experience
        query["experience_years"] = experience_filter

    cursor = collection.find(query).skip(skip).limit(limit).sort("updated_at", -1)
    results = await cursor.to_list(length=limit)

    return cast(list[JobSeekerProfileDocument], results)


async def update_profile(
    profile_id: str, update_data: dict[str, object]
) -> JobSeekerProfileDocument | None:
    """Update profile."""
    collection = get_job_seeker_profiles_collection()

    # Add updated_at timestamp
    update_data["updated_at"] = datetime.now(UTC)

    try:
        result = await collection.find_one_and_update(
            {"_id": ObjectId(profile_id)}, {"$set": update_data}, return_document=True
        )
        return cast(JobSeekerProfileDocument, result) if result else None
    except Exception:
        return None


async def increment_profile_views(profile_id: str) -> bool:
    """Increment profile view count."""
    collection = get_job_seeker_profiles_collection()

    try:
        result = await collection.update_one(
            {"_id": ObjectId(profile_id)}, {"$inc": {"profile_views": 1}}
        )
    except Exception:
        return False
    else:
        return bool(result.modified_count > 0)


async def delete_profile(profile_id: str) -> bool:
    """Delete profile."""
    collection = get_job_seeker_profiles_collection()

    try:
        result = await collection.delete_one({"_id": ObjectId(profile_id)})
    except Exception:
        return False
    else:
        return bool(result.deleted_count > 0)
