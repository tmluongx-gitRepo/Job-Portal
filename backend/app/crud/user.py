"""
CRUD operations for User model.
"""

from datetime import UTC, datetime
from typing import cast

from bson import ObjectId

from app.database import get_users_collection
from app.type_definitions import UserDocument


async def create_user(
    email: str, account_type: str = "job_seeker", supabase_id: str | None = None
) -> UserDocument:
    """
    Create a new user.

    Args:
        email: User's email address
        account_type: Type of account (job_seeker, employer, admin)
        supabase_id: Optional Supabase user ID for auth integration

    Returns:
        Created user document

    Raises:
        ValueError: If user with email already exists
    """
    collection = get_users_collection()

    # Check if user already exists by email or Supabase ID
    query = {"$or": [{"email": email}]}
    if supabase_id:
        query["$or"].append({"supabase_id": supabase_id})

    existing_user = await collection.find_one(query)
    if existing_user:
        raise ValueError(f"User with email {email} already exists")

    user_doc = {
        "email": email,
        "account_type": account_type,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    # Add Supabase ID if provided
    if supabase_id:
        user_doc["supabase_id"] = supabase_id

    result = await collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return cast(UserDocument, user_doc)


async def get_user_by_id(user_id: str) -> UserDocument | None:
    """Get user by ID."""
    collection = get_users_collection()

    try:
        result = await collection.find_one({"_id": ObjectId(user_id)})
        return cast(UserDocument, result) if result else None
    except Exception:
        return None


async def get_user_by_email(email: str) -> UserDocument | None:
    """Get user by email."""
    collection = get_users_collection()
    result = await collection.find_one({"email": email})
    return cast(UserDocument, result) if result else None


async def get_user_by_supabase_id(supabase_id: str) -> UserDocument | None:
    """Get user by Supabase ID."""
    collection = get_users_collection()
    result = await collection.find_one({"supabase_id": supabase_id})
    return cast(UserDocument, result) if result else None


async def get_users(skip: int = 0, limit: int = 100) -> list[UserDocument]:
    """Get all users with pagination."""
    collection = get_users_collection()
    cursor = collection.find().skip(skip).limit(limit)
    results = await cursor.to_list(length=limit)
    return cast(list[UserDocument], results)


async def update_user(user_id: str, update_data: dict[str, object]) -> UserDocument | None:
    """Update user."""
    collection = get_users_collection()

    # Add updated_at timestamp
    update_data["updated_at"] = datetime.now(UTC)

    try:
        result = await collection.find_one_and_update(
            {"_id": ObjectId(user_id)}, {"$set": update_data}, return_document=True
        )
        return cast(UserDocument, result) if result else None
    except Exception:
        return None


async def delete_user(user_id: str) -> bool:
    """Delete user."""
    collection = get_users_collection()

    try:
        result = await collection.delete_one({"_id": ObjectId(user_id)})
    except Exception:
        return False
    else:
        return bool(result.deleted_count > 0)
