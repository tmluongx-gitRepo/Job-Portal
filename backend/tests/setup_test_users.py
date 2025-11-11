"""
One-time setup: Create permanent test users in Supabase.

Run this script once to create test users that will be reused across all tests:
    cd backend
    python -m tests.setup_test_users

These users are permanent fixtures and should NOT be deleted by test cleanup.
"""

import asyncio

from supabase import create_client

from app.config import settings
from tests.constants import TEST_USERS


async def setup_test_users() -> None:
    """
    Create permanent test users in Supabase.

    Uses service role key to create users with email already confirmed.
    These users will be reused across all test runs.
    """
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Error: SUPABASE_SERVICE_ROLE_KEY not configured")
        print("   Add it to your .env file from Supabase Dashboard > Settings > API")
        return

    admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

    print("=" * 60)
    print("🔧 Creating Permanent Test Users in Supabase")
    print("=" * 60)
    print()

    for user_data in TEST_USERS.values():
        try:
            admin_client.auth.admin.create_user(
                {
                    "email": user_data["email"],
                    "password": user_data["password"],
                    "email_confirm": True,  # Auto-confirm email
                    "user_metadata": {"account_type": user_data["account_type"]},
                }
            )
            print(f"✅ Created {user_data['account_type']:12} | {user_data['email']}")
        except Exception as e:
            error_str = str(e).lower()
            if "already registered" in error_str or "already exists" in error_str:
                print(f"ℹ  Already exists:  {user_data['account_type']:12} | {user_data['email']}")  # noqa: RUF001
            else:
                print(f"❌ Error: {user_data['email']}")
                print(f"   {e}")

    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Test users are ready. Run tests with:")
    print("  cd backend")
    print("  uv run pytest tests/test_users_me_rbac.py -v")
    print()


if __name__ == "__main__":
    asyncio.run(setup_test_users())
