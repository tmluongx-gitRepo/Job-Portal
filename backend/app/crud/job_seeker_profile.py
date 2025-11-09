"""
CRUD operations for Job Seeker Profile model.
"""
from datetime import datetime

from bson import ObjectId

from app.database import get_job_seeker_profiles_collection



async def create_profile(user_id: str, profile_data: dict) -> dict:
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await collection.insert_one(profile_doc)
    profile_doc["_id"] = result.inserted_id
    return profile_doc


async def get_profile_by_id(profile_id: str) -> dict | None:
    """Get profile by ID."""
    collection = get_job_seeker_profiles_collection()

    try:
        profile = await collection.find_one({"_id": ObjectId(profile_id)})
        return profile
    except Exception:
        return None


async def get_profile_by_user_id(user_id: str) -> dict | None:
    """Get profile by user ID."""
    collection = get_job_seeker_profiles_collection()

    try:
        profile = await collection.find_one({"user_id": ObjectId(user_id)})
        return profile
    except Exception:
        return None


async def get_profiles(skip: int = 0, limit: int = 100, filters: dict = None) -> list[dict]:
    """Get all profiles with pagination and optional filters."""
    collection = get_job_seeker_profiles_collection()

    query = filters or {}
    cursor = collection.find(query).skip(skip).limit(limit).sort("updated_at", -1)
    return await cursor.to_list(length=limit)


async def search_profiles(
    skills: list[str] = None,
    location: str = None,
    min_experience: int = None,
    max_experience: int = None,
    skip: int = 0,
    limit: int = 100
) -> list[dict]:
    """Search profiles with various criteria."""
    collection = get_job_seeker_profiles_collection()

    query = {}

    if skills:
        # Match any of the provided skills
        query["skills"] = {"$in": skills}

    if location:
        # Case-insensitive location search
        query["location"] = {"$regex": location, "$options": "i"}

    if min_experience is not None or max_experience is not None:
        query["experience_years"] = {}
        if min_experience is not None:
            query["experience_years"]["$gte"] = min_experience
        if max_experience is not None:
            query["experience_years"]["$lte"] = max_experience

    cursor = collection.find(query).skip(skip).limit(limit).sort("updated_at", -1)
    return await cursor.to_list(length=limit)


async def update_profile(profile_id: str, update_data: dict) -> dict | None:
    """Update profile."""
    collection = get_job_seeker_profiles_collection()

    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()

    try:
        result = await collection.find_one_and_update(
            {"_id": ObjectId(profile_id)},
            {"$set": update_data},
            return_document=True
        )
        return result
    except Exception:
        return None


async def increment_profile_views(profile_id: str) -> bool:
    """Increment profile view count."""
    collection = get_job_seeker_profiles_collection()

    try:
        result = await collection.update_one(
            {"_id": ObjectId(profile_id)},
            {"$inc": {"profile_views": 1}}
        )
        return result.modified_count > 0
    except Exception:
        return False


async def delete_profile(profile_id: str) -> bool:
    """Delete profile."""
    collection = get_job_seeker_profiles_collection()

    try:
        result = await collection.delete_one({"_id": ObjectId(profile_id)})
        return result.deleted_count > 0
    except Exception:
        return False

