"""
CRUD operations for Employer Profile model.
"""
from datetime import datetime
from bson import ObjectId

from app.database import get_employer_profiles_collection


async def create_profile(user_id: str, profile_data: dict) -> dict:
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await collection.insert_one(profile_doc)
    profile_doc["_id"] = result.inserted_id
    return profile_doc


async def get_profile_by_id(profile_id: str) -> dict | None:
    """Get employer profile by ID."""
    collection = get_employer_profiles_collection()

    try:
        return await collection.find_one({"_id": ObjectId(profile_id)})
    except Exception:
        return None


async def get_profile_by_user_id(user_id: str) -> dict | None:
    """Get employer profile by user ID."""
    collection = get_employer_profiles_collection()

    try:
        return await collection.find_one({"user_id": ObjectId(user_id)})
    except Exception:
        return None


async def get_profiles(skip: int = 0, limit: int = 100, filters: dict | None = None) -> list[dict]:
    """Get all employer profiles."""
    collection = get_employer_profiles_collection()

    query = filters or {}
    cursor = collection.find(query).skip(skip).limit(limit).sort("updated_at", -1)
    return await cursor.to_list(length=limit)


async def update_profile(profile_id: str, update_data: dict) -> dict | None:
    """Update employer profile."""
    collection = get_employer_profiles_collection()

    update_data["updated_at"] = datetime.utcnow()

    try:
        return await collection.find_one_and_update(
            {"_id": ObjectId(profile_id)},
            {"$set": update_data},
            return_document=True,
        )
    except Exception:
        return None


async def delete_profile(profile_id: str) -> bool:
    """Delete employer profile."""
    collection = get_employer_profiles_collection()

    try:
        result = await collection.delete_one({"_id": ObjectId(profile_id)})
        return result.deleted_count > 0
    except Exception:
        return False


async def increment_job_counts(profile_id: str, posted_delta: int = 0, active_delta: int = 0) -> bool:
    """Adjust job counters for an employer profile."""
    collection = get_employer_profiles_collection()

    try:
        update = {"$inc": {}}
        if posted_delta:
            update["$inc"]["jobs_posted_count"] = posted_delta
        if active_delta:
            update["$inc"]["active_jobs_count"] = active_delta

        if not update["$inc"]:
            return True

        result = await collection.update_one({"_id": ObjectId(profile_id)}, update)
        return result.modified_count > 0
    except Exception:
        return False
