"""
CRUD operations for User model.
"""
from datetime import datetime

from bson import ObjectId

from app.database import get_users_collection



async def create_user(email: str, account_type: str = "job_seeker") -> dict:
    """Create a new user."""
    collection = get_users_collection()

    # Check if user already exists
    existing_user = await collection.find_one({"email": email})
    if existing_user:
        raise ValueError(f"User with email {email} already exists")

    user_doc = {
        "email": email,
        "account_type": account_type,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc


async def get_user_by_id(user_id: str) -> dict | None:
    """Get user by ID."""
    collection = get_users_collection()

    try:
        user = await collection.find_one({"_id": ObjectId(user_id)})
        return user
    except Exception:
        return None


async def get_user_by_email(email: str) -> dict | None:
    """Get user by email."""
    collection = get_users_collection()
    return await collection.find_one({"email": email})


async def get_users(skip: int = 0, limit: int = 100) -> list[dict]:
    """Get all users with pagination."""
    collection = get_users_collection()
    cursor = collection.find().skip(skip).limit(limit)
    return await cursor.to_list(length=limit)


async def update_user(user_id: str, update_data: dict) -> dict | None:
    """Update user."""
    collection = get_users_collection()

    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()

    try:
        result = await collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )
        return result
    except Exception:
        return None


async def delete_user(user_id: str) -> bool:
    """Delete user."""
    collection = get_users_collection()

    try:
        result = await collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    except Exception:
        return False

