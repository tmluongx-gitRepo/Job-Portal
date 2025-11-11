"""
Auth service layer for user operations.

This service layer sits between authentication/API routes and CRUD operations.
It handles the conversion from Supabase UUID (used in JWT tokens) to MongoDB ObjectId
(used throughout the application).

Key principle: MongoDB ObjectId is the primary ID. Supabase UUID is only used
for initial authentication lookup.
"""

from app.crud import user as user_crud
from app.type_definitions import UserDocument


async def get_or_create_user_by_supabase_id(
    supabase_id: str, email: str, account_type: str
) -> UserDocument:
    """
    Get or create user by Supabase ID (JIT provisioning).

    This is called during authentication to ensure a MongoDB user record exists
    for the authenticated Supabase user.

    SECURITY: For new users, only job_seeker and employer roles are allowed.
    Admin/service roles can only be assigned server-side after the user exists.

    Args:
        supabase_id: Supabase UUID from JWT token
        email: User's email address
        account_type: Type of account from JWT (untrusted for new users)

    Returns:
        UserDocument with MongoDB ObjectId as primary ID

    Flow:
        1. Try to find user by supabase_id
        2. If not found, try to find by email (handles recreated Supabase users)
        3. If found by email, update the supabase_id
        4. If not found at all, create new user with SAFE role only
    """
    # Try to find by Supabase ID first
    existing_user = await user_crud.get_user_by_supabase_id(supabase_id)
    if existing_user:
        # User exists - trust the stored account_type
        return existing_user

    # Try to find by email (handles case where Supabase user was deleted and recreated)
    existing_user = await user_crud.get_user_by_email(email)
    if existing_user:
        # User exists - trust the stored account_type, just update Supabase ID
        updated_user = await user_crud.update_user(
            str(existing_user["_id"]), {"supabase_id": supabase_id}
        )
        if updated_user:
            return updated_user

    # User doesn't exist - create new one with SAFE role only
    # SECURITY: Only allow job_seeker or employer for new users
    # Admin/service roles must be assigned server-side by existing admins
    safe_account_types = {"job_seeker", "employer"}
    safe_account_type = account_type if account_type in safe_account_types else "job_seeker"

    return await user_crud.create_user(
        email=email, account_type=safe_account_type, supabase_id=supabase_id
    )


async def get_user(user_id: str) -> UserDocument | None:
    """
    Get user by MongoDB ObjectId.

    Args:
        user_id: MongoDB ObjectId as string

    Returns:
        User document if found, None otherwise
    """
    return await user_crud.get_user_by_id(user_id)


async def update_user(user_id: str, update_data: dict[str, object]) -> UserDocument | None:
    """
    Update user by MongoDB ObjectId.

    Args:
        user_id: MongoDB ObjectId as string
        update_data: Dictionary of fields to update

    Returns:
        Updated user document if found, None otherwise
    """
    return await user_crud.update_user(user_id, update_data)


async def delete_user(user_id: str) -> bool:
    """
    Delete user by MongoDB ObjectId with cascade deletion.

    This will also delete:
    - Job seeker profile (if user is a job seeker)
    - Employer profile (if user is an employer)

    Args:
        user_id: MongoDB ObjectId as string

    Returns:
        True if deleted, False if not found
    """
    from app.crud import employer_profile as employer_profile_crud
    from app.crud import job_seeker_profile as job_seeker_profile_crud

    # Get user to check account type
    user = await user_crud.get_user_by_id(user_id)
    if not user:
        return False

    # Delete associated profile based on account type
    account_type = user.get("account_type")
    if account_type == "job_seeker":
        # Delete job seeker profile
        js_profile = await job_seeker_profile_crud.get_profile_by_user_id(user_id)
        if js_profile:
            await job_seeker_profile_crud.delete_profile(str(js_profile["_id"]))
    elif account_type == "employer":
        # Delete employer profile
        emp_profile = await employer_profile_crud.get_profile_by_user_id(user_id)
        if emp_profile:
            await employer_profile_crud.delete_profile(str(emp_profile["_id"]))

    # Delete the user
    return await user_crud.delete_user(user_id)
