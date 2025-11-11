"""
Supabase utilities for testing with service role key.

Provides admin-level operations for test setup and cleanup:
- Auto-confirm user emails
- Delete Supabase users
"""

from supabase import Client, create_client

from app.config import settings


def get_admin_supabase_client() -> Client:
    """
    Get Supabase client with service role key (admin privileges).

    This client can:
    - Bypass Row Level Security (RLS)
    - Confirm user emails without verification
    - Delete users without authentication
    - Perform admin operations

    Returns:
        Supabase client with service role key

    Raises:
        ValueError: If service role key not configured
    """
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError(
            "SUPABASE_SERVICE_ROLE_KEY not configured. "
            "Get it from: Supabase Dashboard > Settings > API > service_role key"
        )

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def confirm_user_email(user_id: str) -> bool:
    """
    Auto-confirm a user's email using admin privileges.

    This bypasses the email verification flow for testing.

    Args:
        user_id: Supabase user UUID

    Returns:
        True if successful, False otherwise
    """
    try:
        admin_client = get_admin_supabase_client()
        admin_client.auth.admin.update_user_by_id(user_id, {"email_confirm": True})
    except Exception as e:
        print(f"⚠️  Failed to confirm email for user {user_id}: {e}")
        return False
    else:
        return True


def delete_supabase_user(user_id: str) -> bool:
    """
    Delete a user from Supabase (for test cleanup).

    Args:
        user_id: Supabase user UUID

    Returns:
        True if successful, False otherwise
    """
    try:
        admin_client = get_admin_supabase_client()
        admin_client.auth.admin.delete_user(user_id)
    except Exception as e:
        print(f"⚠️  Failed to delete Supabase user {user_id}: {e}")
        return False
    else:
        return True
