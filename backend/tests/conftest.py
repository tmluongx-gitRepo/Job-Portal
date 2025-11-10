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
from tests.constants import HTTP_CREATED, HTTP_OK

# ============================================================================
# PERMANENT TEST USERS (created once, reused across all tests)
# ============================================================================

TEST_USERS = {
    "job_seeker": {
        "email": "test.jobseeker@yourapp.com",
        "password": "TestJobSeeker123!",
        "account_type": "job_seeker",
    },
    "employer": {
        "email": "test.employer@yourapp.com",
        "password": "TestEmployer123!",
        "account_type": "employer",
    },
}

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
    """Async HTTP client for session-scoped fixtures (token generation)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session", autouse=True)
def _configure_test_database() -> Generator[None, None, None]:
    """Configure the application to use test database for all tests."""
    import os

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


class TestDataCleaner:
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
async def test_cleaner(db: Any) -> AsyncGenerator[TestDataCleaner, None]:
    """
    Provides test data cleanup for each test.

    Automatically tracks and cleans up data created during the test,
    ensuring each test's authentication data is isolated.
    """
    cleaner = TestDataCleaner(db)

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
    """
    yield

    # Run cleanup after all tests complete (create new event loop for cleanup)
    import asyncio

    async def _cleanup() -> None:
        print("\n" + "=" * 60)
        print("🧹 Final Test Session Cleanup")
        print("=" * 60)

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


@pytest_asyncio.fixture
async def admin_token(_client: Any = None) -> str:
    """
    Login as permanent test admin user.

    Note: Admin users cannot be created via /api/auth/register.
    This fixture is kept for compatibility but will fail until
    an admin user is manually created in Supabase.
    """
    pytest.skip("Admin users must be created manually in Supabase dashboard")


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
    client: AsyncClient, job_seeker_token: str, test_cleaner: TestDataCleaner
) -> tuple[str, str, str]:
    """
    Create a job seeker with a complete profile.

    All data (user, profile) is tracked and cleaned up after the test.
    Returns (token, user_id, profile_id).
    """
    if not job_seeker_token:
        pytest.skip("Cannot create job seeker token (email confirmation required)")

    headers = {"Authorization": f"Bearer {job_seeker_token}"}

    # Get user info
    user_response = await client.get("/api/users/me", headers=headers)
    if user_response.status_code != HTTP_OK:
        pytest.skip("Cannot get user info")

    user_id = user_response.json()["id"]

    # Create profile
    profile_response = await client.post(
        "/api/job-seeker-profiles",
        headers=headers,
        json={
            "full_name": "Test Job Seeker",
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "skills": ["Python", "FastAPI"],
            "experience_level": "mid",
            "desired_job_title": "Software Engineer",
            "bio": "Test bio",
        },
    )

    if profile_response.status_code != HTTP_CREATED:
        pytest.skip("Cannot create job seeker profile")

    profile_id = profile_response.json()["id"]

    # Track profile for cleanup
    test_cleaner.track_profile(profile_id, "job_seeker")

    return job_seeker_token, user_id, profile_id


@pytest_asyncio.fixture
async def employer_with_profile(
    client: AsyncClient, employer_token: str, test_cleaner: TestDataCleaner
) -> tuple[str, str, str]:
    """
    Create an employer with a complete profile.

    All data (user, profile) is tracked and cleaned up after the test.
    Returns (token, user_id, profile_id).
    """
    if not employer_token:
        pytest.skip("Cannot create employer token (email confirmation required)")

    headers = {"Authorization": f"Bearer {employer_token}"}

    # Get user info
    user_response = await client.get("/api/users/me", headers=headers)
    if user_response.status_code != HTTP_OK:
        pytest.skip("Cannot get user info")

    user_id = user_response.json()["id"]

    # Create profile
    profile_response = await client.post(
        "/api/employer-profiles",
        headers=headers,
        json={
            "company_name": "Test Company",
            "industry": "Technology",
            "company_size": "50-200",
            "website": "https://testcompany.com",
            "location": "San Francisco, CA",
            "description": "Test company description",
        },
    )

    if profile_response.status_code != HTTP_CREATED:
        pytest.skip("Cannot create employer profile")

    profile_id = profile_response.json()["id"]

    # Track profile for cleanup
    test_cleaner.track_profile(profile_id, "employer")

    return employer_token, user_id, profile_id


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def auth_headers(token: str) -> dict:
    """Helper to create authorization headers."""
    return {"Authorization": f"Bearer {token}"}
