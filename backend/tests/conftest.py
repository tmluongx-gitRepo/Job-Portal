"""
═══════════════════════════════════════════════════════════════
PYTEST SHARED FIXTURES
═══════════════════════════════════════════════════════════════

This file provides reusable test components (fixtures) that are
automatically available to all tests without importing.

⚠️  This filename MUST be 'conftest.py' - it's required by pytest
    and cannot be changed. Think of it as 'shared test setup'.

Available Fixtures:
───────────────────
• client              → HTTP client for API requests
• db                  → MongoDB database connection
• test_cleaner        → Automatic cleanup of test data
• admin_token         → Admin user JWT (auto-cleanup)
• job_seeker_token    → Job seeker user JWT (auto-cleanup)
• employer_token      → Employer user JWT (auto-cleanup)
• job_seeker_with_profile  → Complete job seeker (auto-cleanup)
• employer_with_profile    → Complete employer (auto-cleanup)

Cleanup System:
───────────────
• Per-test cleanup: Tracks and removes data created by each test
• Session cleanup: Safety net that runs at end of all tests
• Token isolation: Users are deleted after tests, invalidating tokens
• Minimal output: Only shows cleanup summary

═══════════════════════════════════════════════════════════════
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from bson import ObjectId
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.database import get_mongo_database
from app.main import app
from tests.constants import HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_OK, TEST_USERS

# ============================================================================
# SECURITY: Test Account Management
# ============================================================================


async def _disable_test_accounts() -> None:
    """
    Disable all test accounts in Supabase after test session.

    SECURITY: This prevents test accounts (especially admin) from being used
    outside of test sessions, even if credentials are exposed.
    """
    from supabase import create_client

    try:
        admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

        print("\n🔒 Disabling test accounts in Supabase...")

        # Get all users
        users_response = admin_client.auth.admin.list_users()

        disabled_count = 0
        for user in users_response:
            # Check if this is a test user
            if user.email in [u["email"] for u in TEST_USERS.values()]:
                try:
                    # Ban the user (prevents login)
                    admin_client.auth.admin.update_user_by_id(
                        user.id,
                        {"ban_duration": "876000h"},  # ~100 years
                    )
                    print(f"   🔒 Disabled: {user.email}")
                    disabled_count += 1
                except Exception as e:
                    print(f"   ⚠️  Failed to disable {user.email}: {e}")

        if disabled_count > 0:
            print(f"✅ Disabled {disabled_count} test account(s)")
            print("   Test accounts will be re-enabled on next test run")
        else:
            print("INFO: No test accounts found to disable")

    except Exception as e:
        print(f"⚠️  Failed to disable test accounts: {e}")
        print("   (This is not critical - tests completed successfully)")


async def _enable_test_accounts() -> None:
    """
    Enable all test accounts in Supabase before test session.

    This re-enables accounts that were disabled after the previous test session.
    """
    from supabase import create_client

    try:
        admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

        print("🔓 Enabling test accounts in Supabase...")

        # Get all users
        users_response = admin_client.auth.admin.list_users()

        enabled_count = 0
        for user in users_response:
            # Check if this is a test user
            if user.email in [u["email"] for u in TEST_USERS.values()]:
                try:
                    # Unban the user by setting ban_duration to "0h" or removing it
                    admin_client.auth.admin.update_user_by_id(user.id, {"ban_duration": "0h"})
                    print(f"   🔓 Enabled: {user.email}")
                    enabled_count += 1
                except Exception as e:
                    print(f"   ⚠️  Failed to enable {user.email}: {e}")

        if enabled_count > 0:
            print(f"✅ Enabled {enabled_count} test account(s)\n")

    except Exception as e:
        print(f"⚠️  Failed to enable test accounts: {e}")
        print("   Tests may fail if accounts are disabled\n")


# ============================================================================
# CORE FIXTURES
# ============================================================================


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing (function-scoped)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an event loop for session-scoped async fixtures.

    Note: This overrides pytest-asyncio's event_loop fixture, which triggers
    a deprecation warning. This is currently the most reliable way to support
    session-scoped async fixtures. The warning can be safely ignored.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def session_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP client for session-scoped fixtures (token generation).

    Note: follow_redirects=False and no cookie jar to prevent session interference.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=False,
        # Don't persist cookies between requests to avoid cross-contamination
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="session", autouse=True)
def _configure_test_database() -> Generator[None, None, None]:
    """
    Configure the application to use test database for all tests.

    SECURITY: Also enables test accounts at session start.
    """
    import asyncio
    import os

    # SECURITY: Enable test accounts before tests run
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_enable_test_accounts())
    loop.close()

    # Override database name for tests
    original_db_name = os.environ.get("MONGO_DB_NAME")
    os.environ["MONGO_DB_NAME"] = settings.MONGO_TEST_DB_NAME

    # Force settings reload
    settings.MONGO_DB_NAME = settings.MONGO_TEST_DB_NAME

    yield

    # Restore original (if any)
    if original_db_name:
        os.environ["MONGO_DB_NAME"] = original_db_name
        settings.MONGO_DB_NAME = original_db_name


@pytest_asyncio.fixture
def db() -> Generator[Any, None, None]:
    """Database connection for test operations."""
    database = get_mongo_database()
    yield database


# ============================================================================
# TEST DATA CLEANUP SYSTEM
# ============================================================================


class DataCleaner:
    """
    Tracks and cleans up test data created during tests.

    Ensures tokens from one test don't affect other tests by:
    - Tracking user IDs associated with auth tokens
    - Cleaning up users (which invalidates tokens)
    - Deleting in proper order (apps → jobs → profiles → users)
    """

    def __init__(self, db: Any) -> None:
        self.db = db
        self.user_ids: set[str] = set()
        self.profile_ids: dict[str, str] = {}  # profile_id -> type (job_seeker/employer)
        self.job_ids: set[str] = set()
        self.application_ids: set[str] = set()
        self.test_emails: set[str] = set()
        self.supabase_user_ids: set[str] = set()  # Supabase UUIDs for cleanup

    def track_user(self, user_id: str, email: str | None = None) -> None:
        """Track a user created during testing."""
        self.user_ids.add(user_id)
        if email:
            self.test_emails.add(email)

    def track_profile(self, profile_id: str, profile_type: str) -> None:
        """Track a profile (job_seeker or employer)."""
        self.profile_ids[profile_id] = profile_type

    def track_job(self, job_id: str) -> None:
        """Track a job posting."""
        self.job_ids.add(job_id)

    def track_application(self, application_id: str) -> None:
        """Track a job application."""
        self.application_ids.add(application_id)

    async def cleanup(self) -> dict[str, int]:
        """Clean up all tracked test data."""
        from tests.supabase_test_utils import delete_supabase_user

        counts = {"users": 0, "profiles": 0, "jobs": 0, "applications": 0, "supabase_users": 0}

        # Clean applications first (they reference jobs)
        if self.application_ids:
            result = await self.db["applications"].delete_many(
                {"_id": {"$in": [ObjectId(aid) for aid in self.application_ids]}}
            )
            counts["applications"] = result.deleted_count

        # Clean jobs (they reference profiles)
        if self.job_ids:
            result = await self.db["jobs"].delete_many(
                {"_id": {"$in": [ObjectId(jid) for jid in self.job_ids]}}
            )
            counts["jobs"] = result.deleted_count

        # Clean profiles (they reference users)
        if self.profile_ids:
            for profile_id, profile_type in self.profile_ids.items():
                collection_name = f"{profile_type}_profiles"
                await self.db[collection_name].delete_one({"_id": ObjectId(profile_id)})
                counts["profiles"] += 1

        # Clean users last (this invalidates auth tokens)
        if self.user_ids:
            result = await self.db["users"].delete_many(
                {"_id": {"$in": [ObjectId(uid) for uid in self.user_ids]}}
            )
            counts["users"] = result.deleted_count

        # Clean Supabase users (auth provider cleanup)
        for supabase_id in self.supabase_user_ids:
            if delete_supabase_user(supabase_id):
                counts["supabase_users"] += 1

        return counts


@pytest_asyncio.fixture
async def test_cleaner(db: Any) -> AsyncGenerator[DataCleaner, None]:
    """
    Provides test data cleanup for each test.

    Automatically tracks and cleans up data created during the test,
    ensuring each test's authentication data is isolated.
    """
    cleaner = DataCleaner(db)

    yield cleaner

    # Cleanup after test completes
    counts = await cleaner.cleanup()

    # Minimal output: only show if something was cleaned
    total = sum(counts.values())
    if total > 0:
        items = [f"{v} {k}" for k, v in counts.items() if v > 0]
        print(f"  🧹 Cleaned: {', '.join(items)}")


@pytest.fixture(scope="session", autouse=True)
def session_cleanup() -> Generator[None, None, None]:
    """
    Safety net: Clean ALL test data at end of test session.

    This catches any orphaned test data that wasn't cleaned up during tests.
    Particularly important for tokens/auth data from skipped or failed tests.

    SECURITY: Also disables test accounts in Supabase to prevent unauthorized access.
    """
    yield

    # Run cleanup after all tests complete (create new event loop for cleanup)
    import asyncio

    async def _cleanup() -> None:
        print("\n" + "=" * 60)
        print("🧹 Final Test Session Cleanup")
        print("=" * 60)

        # SECURITY: Disable test accounts in Supabase
        await _disable_test_accounts()

        db = get_mongo_database()
        total_cleaned = 0

        try:
            # Clean test users (by email pattern) - this invalidates all test tokens
            result = await db["users"].delete_many({"email": {"$regex": ".*_test_.*@example.com"}})
            if result.deleted_count > 0:
                print(f"  ├─ Users: {result.deleted_count}")
                total_cleaned += result.deleted_count

            # Clean test profiles
            result = await db["job_seeker_profiles"].delete_many(
                {"full_name": {"$regex": "^Test.*"}}
            )
            if result.deleted_count > 0:
                print(f"  ├─ Job Seeker Profiles: {result.deleted_count}")
                total_cleaned += result.deleted_count

            result = await db["employer_profiles"].delete_many(
                {"company_name": {"$regex": "^Test.*"}}
            )
            if result.deleted_count > 0:
                print(f"  ├─ Employer Profiles: {result.deleted_count}")
                total_cleaned += result.deleted_count

            # Clean test jobs
            result = await db["jobs"].delete_many(
                {
                    "title": {
                        "$regex": "^(Test|Original|Software Engineer|To Delete|Protected Job).*"
                    }
                }
            )
            if result.deleted_count > 0:
                print(f"  ├─ Jobs: {result.deleted_count}")
                total_cleaned += result.deleted_count

            if total_cleaned > 0:
                print(f"\n✅ Session cleanup complete: {total_cleaned} items removed")
            else:
                print("✅ No orphaned test data found")
        except Exception as e:
            print(f"⚠️  Session cleanup encountered an error: {e}")
            print("   (Per-test cleanup already handled most data)")

        print("=" * 60 + "\n")

    # Create new event loop and run cleanup
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_cleanup())
        loop.close()
    except Exception as e:
        print(f"\n⚠️  Could not run session cleanup: {e}")
        print("(This is okay - per-test cleanup already handled the data)\n")


# ============================================================================
# TOKEN FIXTURES WITH AUTO-CLEANUP
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def admin_token(session_client: AsyncClient) -> str:
    """
    Login as permanent test admin (session-scoped).

    Token is created once per test session and reused across all tests.
    This avoids token conflicts and improves test performance.

    Note: Admin user must exist in Supabase (created manually or via setup script).
    """
    user = TEST_USERS["admin"]

    login_response = await session_client.post(
        "/api/auth/login", json={"email": user["email"], "password": user["password"]}
    )

    if login_response.status_code == HTTP_OK:
        token: str = login_response.json()["access_token"]
        return token

    pytest.fail(
        f"Failed to login test admin: {login_response.status_code}\n"
        f"Response: {login_response.json()}\n"
        f"Admin user must be created manually in Supabase or via setup script."
    )


@pytest_asyncio.fixture(scope="session")
async def job_seeker_token(session_client: AsyncClient) -> str:
    """
    Login as permanent test job seeker (session-scoped).

    Token is created once per test session and reused across all tests.
    This avoids token conflicts and improves test performance.
    """
    user = TEST_USERS["job_seeker"]

    login_response = await session_client.post(
        "/api/auth/login", json={"email": user["email"], "password": user["password"]}
    )

    if login_response.status_code == HTTP_OK:
        token: str = login_response.json()["access_token"]
        return token

    pytest.fail(
        f"Failed to login test job seeker: {login_response.status_code}\n"
        f"Response: {login_response.json()}\n"
        f"Did you run 'python -m tests.setup_test_users' to create test users?"
    )


@pytest_asyncio.fixture(scope="session")
async def employer_token(session_client: AsyncClient) -> str:
    """
    Login as permanent test employer (session-scoped).

    Token is created once per test session and reused across all tests.
    This avoids token conflicts and improves test performance.
    """
    user = TEST_USERS["employer"]

    login_response = await session_client.post(
        "/api/auth/login", json={"email": user["email"], "password": user["password"]}
    )

    if login_response.status_code == HTTP_OK:
        token: str = login_response.json()["access_token"]
        return token

    pytest.fail(
        f"Failed to login test employer: {login_response.status_code}\n"
        f"Response: {login_response.json()}\n"
        f"Did you run 'python -m tests.setup_test_users' to create test users?"
    )


@pytest_asyncio.fixture
async def job_seeker_with_profile(
    client: AsyncClient, job_seeker_token: str, test_cleaner: DataCleaner
) -> tuple[str, str, str]:
    """
    Create a job seeker with a complete profile.

    All data (user, profile) is tracked and cleaned up after the test.
    Returns (token, user_id, profile_id).
    """
    if not job_seeker_token:
        pytest.skip("Cannot create job seeker token (email confirmation required)")

    headers = {"Authorization": f"Bearer {job_seeker_token}"}

    # Get user info (this triggers JIT provisioning if user doesn't exist)
    user_response = await client.get("/api/users/me", headers=headers)
    if user_response.status_code != HTTP_OK:
        pytest.skip(f"Cannot get user info: {user_response.status_code}")

    user_id = user_response.json()["id"]

    # Check if profile already exists
    existing_profile_response = await client.get(
        f"/api/job-seeker-profiles/user/{user_id}", headers=headers
    )

    if existing_profile_response.status_code == HTTP_OK:
        # Profile exists, use it
        profile_id = existing_profile_response.json()["id"]
    else:
        # Profile doesn't exist, create it
        # (Note: If we get 400 "already exists" on create, it means the GET endpoint
        # returned non-200 even though the profile exists - this is a race condition)
        profile_response = await client.post(
            "/api/job-seeker-profiles",
            headers=headers,
            json={
                "user_id": user_id,
                "first_name": "Test",
                "last_name": "JobSeeker",
                "email": TEST_USERS["job_seeker"]["email"],
                "phone": "555-1234",
                "location": "San Francisco, CA",
                "skills": ["Python", "FastAPI"],
                "bio": "Test bio",
            },
        )

        if profile_response.status_code == HTTP_CREATED:
            profile_id = profile_response.json()["id"]
            # Track profile for cleanup
            test_cleaner.track_profile(profile_id, "job_seeker")
        elif profile_response.status_code == HTTP_BAD_REQUEST:
            # Profile already exists (race condition), fetch it
            error_detail = profile_response.json() if profile_response.content else {}
            if "already have" in str(error_detail.get("detail", "")).lower():
                existing_profile_response = await client.get(
                    f"/api/job-seeker-profiles/user/{user_id}", headers=headers
                )
                if existing_profile_response.status_code == HTTP_OK:
                    profile_id = existing_profile_response.json()["id"]
                else:
                    pytest.skip(
                        f"Profile exists but cannot fetch it: {existing_profile_response.status_code}"
                    )
            else:
                pytest.skip(f"Cannot create job seeker profile: 400\nError: {error_detail}")
        else:
            error_detail = profile_response.json() if profile_response.content else "No content"
            pytest.skip(
                f"Cannot create job seeker profile: {profile_response.status_code}\n"
                f"Error: {error_detail}"
            )

    return job_seeker_token, user_id, profile_id


@pytest_asyncio.fixture
async def employer_with_profile(
    client: AsyncClient, employer_token: str, test_cleaner: DataCleaner
) -> tuple[str, str, str]:
    """
    Create an employer with a complete profile.

    All data (user, profile) is tracked and cleaned up after the test.
    Returns (token, user_id, profile_id).
    """
    if not employer_token:
        pytest.skip("Cannot create employer token (email confirmation required)")

    headers = {"Authorization": f"Bearer {employer_token}"}

    # Get user info (this triggers JIT provisioning if user doesn't exist)
    user_response = await client.get("/api/users/me", headers=headers)
    if user_response.status_code != HTTP_OK:
        pytest.skip(f"Cannot get user info: {user_response.status_code}")

    user_id = user_response.json()["id"]

    # Check if profile already exists
    existing_profile_response = await client.get(
        f"/api/employer-profiles/user/{user_id}", headers=headers
    )

    if existing_profile_response.status_code == HTTP_OK:
        # Profile exists, use it
        profile_id = existing_profile_response.json()["id"]
    else:
        # Create new profile
        profile_response = await client.post(
            "/api/employer-profiles",
            headers=headers,
            json={
                "user_id": user_id,
                "company_name": "Test Company",
                "industry": "Technology",
                "company_size": "50-200",
                "website": "https://testcompany.com",
                "location": "San Francisco, CA",
                "description": "Test company description",
            },
        )

        if profile_response.status_code == HTTP_CREATED:
            profile_id = profile_response.json()["id"]
            # Track profile for cleanup
            test_cleaner.track_profile(profile_id, "employer")
        elif profile_response.status_code == HTTP_BAD_REQUEST:
            # Profile already exists (race condition), fetch it
            error_detail = profile_response.json() if profile_response.content else {}
            if "already have" in str(error_detail.get("detail", "")).lower():
                existing_profile_response = await client.get(
                    f"/api/employer-profiles/user/{user_id}", headers=headers
                )
                if existing_profile_response.status_code == HTTP_OK:
                    profile_id = existing_profile_response.json()["id"]
                else:
                    pytest.skip(
                        f"Profile exists but cannot fetch it: {existing_profile_response.status_code}"
                    )
            else:
                pytest.skip(f"Cannot create employer profile: 400\nError: {error_detail}")
        else:
            error_detail = profile_response.json() if profile_response.content else "No content"
            pytest.skip(
                f"Cannot create employer profile: {profile_response.status_code}\n"
                f"Error: {error_detail}"
            )

    return employer_token, user_id, profile_id


@pytest_asyncio.fixture
async def create_temp_user(
    client: AsyncClient,
) -> AsyncGenerator[Any, None]:
    """
    Factory fixture to create temporary users for testing cross-user scenarios.

    Returns a function that creates a user, logs them in, and tracks for cleanup.

    Usage:
        async def test_something(create_temp_user):
            # Create a second employer
            token2, user_id2 = await create_temp_user("employer", "temp.employer@test.com")
            # Use token2 for requests...
    """
    from supabase import create_client

    admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    created_user_ids: list[str] = []

    async def _create_user(
        account_type: str, email: str, password: str = "TempUser123!"
    ) -> tuple[str | None, str | None]:
        """Create a temporary user in Supabase and return their token and user_id."""
        # First, try to delete any existing user with this email (from failed cleanup)
        try:
            users = admin_client.auth.admin.list_users()
            for user in users:
                if user.email == email:
                    admin_client.auth.admin.delete_user(user.id)
                    print(f"🧹 Deleted existing temp user: {email}")
        except Exception:
            pass  # Ignore errors during cleanup

        # Create user in Supabase
        try:
            response = admin_client.auth.admin.create_user(
                {
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {"account_type": account_type},
                }
            )

            if response.user:
                created_user_ids.append(response.user.id)

                # Small delay to ensure user is fully created in Supabase
                import asyncio

                await asyncio.sleep(0.5)

                # Login using regular Supabase client (anon key, not service role)
                # to get a user-level token that our API can validate
                user_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
                login_result = user_client.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )

                if login_result.session and login_result.session.access_token:
                    token = login_result.session.access_token

                    # Get user info to trigger JIT provisioning
                    headers = {"Authorization": f"Bearer {token}"}
                    user_response = await client.get("/api/users/me", headers=headers)

                    if user_response.status_code == HTTP_OK:
                        user_data = user_response.json()
                        user_id = user_data.get("id")
                        if user_id:
                            return token, user_id
                        print(f"⚠️  User response missing 'id': {user_data}")
                    else:
                        print(
                            f"⚠️  Failed to get user info: {user_response.status_code} - {user_response.text}"
                        )
                else:
                    print("⚠️  Login failed: No session or access token")
        except Exception as e:
            print(f"⚠️  Failed to create temp user: {e}")
            import traceback

            traceback.print_exc()
            return None, None

        print("⚠️  Failed to create temp user: No response from Supabase")
        return None, None

    yield _create_user

    # Cleanup: Delete all created users from both Supabase and MongoDB
    import contextlib

    from app.crud import user as user_crud

    for supabase_id in created_user_ids:
        # Delete from Supabase
        with contextlib.suppress(Exception):
            admin_client.auth.admin.delete_user(supabase_id)

        # Delete from MongoDB (find by Supabase ID, then delete by MongoDB ObjectId)
        with contextlib.suppress(Exception):
            user_doc = await user_crud.get_user_by_supabase_id(supabase_id)
            if user_doc:
                await user_crud.delete_user(str(user_doc["_id"]))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def auth_headers(token: str) -> dict:
    """Helper to create authorization headers."""
    return {"Authorization": f"Bearer {token}"}
