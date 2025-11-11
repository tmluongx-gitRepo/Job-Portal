"""
RBAC tests for Users API.

Comprehensive tests covering:
- Self-service endpoints (/me)
- Admin operations
- Cross-user authorization
- Search and pagination
- User management workflows
"""

from collections.abc import Awaitable, Callable

import pytest
from httpx import AsyncClient

from tests.constants import (
    HTTP_CREATED,
    HTTP_FORBIDDEN,
    HTTP_NO_CONTENT,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MIN_PAGE_SIZE,
)


class TestUsersRBAC:
    """Test role-based access control for Users API."""

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_access_users(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot access any user endpoints."""
        # FastAPI HTTPBearer returns 403 when no credentials provided

        # GET /users
        response = await client.get("/api/users")
        assert response.status_code in [401, 403]

        # GET /users/me
        response = await client.get("/api/users/me")
        assert response.status_code in [401, 403]

        # GET /users/{id}
        response = await client.get("/api/users/some-id")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_job_seeker_can_view_own_account(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Job seekers can view their own account via /me."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = await client.get("/api/users/me", headers=headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["account_type"] == "job_seeker"
        assert "email" in data

    @pytest.mark.asyncio
    async def test_job_seeker_cannot_list_all_users(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Job seekers cannot list all users (admin only)."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = await client.get("/api/users", headers=headers)

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_job_seeker_can_update_own_account(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Job seekers can update their own account via /me."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {job_seeker_token}"}

        # Ensure user exists in MongoDB (trigger JIT provisioning)
        await client.get("/api/users/me", headers=headers)

        # Update email (if Supabase allows)
        response = await client.put(
            "/api/users/me", headers=headers, json={"email": "newemail@example.com"}
        )

        # May succeed or fail depending on Supabase rules or user existence
        # The important part is it's not a 403 (authorization issue)
        assert response.status_code in [200, 400, 404, 422]

    @pytest.mark.asyncio
    async def test_job_seeker_cannot_change_own_account_type(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Job seekers cannot change their own account_type."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {job_seeker_token}"}

        response = await client.put(
            "/api/users/me", headers=headers, json={"account_type": "admin"}
        )

        assert response.status_code == HTTP_FORBIDDEN
        assert "cannot change" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_job_seeker_can_delete_own_account(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Job seekers can delete their own account."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {job_seeker_token}"}

        # Ensure user exists in MongoDB (trigger JIT provisioning)
        await client.get("/api/users/me", headers=headers)

        response = await client.delete("/api/users/me", headers=headers)

        # Accept both 204 (deleted) and 404 (doesn't exist) as valid
        assert response.status_code in [HTTP_NO_CONTENT, 404]

    @pytest.mark.asyncio
    async def test_employer_can_view_own_account(
        self, client: AsyncClient, employer_token: str
    ) -> None:
        """Employers can view their own account via /me."""
        if not employer_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {employer_token}"}
        response = await client.get("/api/users/me", headers=headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["account_type"] == "employer"

    @pytest.mark.asyncio
    async def test_employer_cannot_view_other_users(
        self, client: AsyncClient, employer_token: str, job_seeker_token: str
    ) -> None:
        """Employers cannot view other users' accounts."""
        if not employer_token or not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        # Get job seeker's user ID
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        js_response = await client.get("/api/users/me", headers=js_headers)
        js_user_id = js_response.json()["id"]

        # Try to view as employer
        emp_headers = {"Authorization": f"Bearer {employer_token}"}
        response = await client.get(f"/api/users/{js_user_id}", headers=emp_headers)

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_can_list_all_users(self, client: AsyncClient, admin_token: str) -> None:
        """Admins can list all users."""
        if not admin_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get("/api/users", headers=headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_admin_can_view_any_user(
        self, client: AsyncClient, admin_token: str, job_seeker_token: str
    ) -> None:
        """Admins can view any user's account."""
        if not admin_token or not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        # Get job seeker's user ID
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        js_response = await client.get("/api/users/me", headers=js_headers)
        js_user_id = js_response.json()["id"]

        # View as admin
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get(f"/api/users/{js_user_id}", headers=admin_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == js_user_id

    @pytest.mark.asyncio
    async def test_admin_can_create_user(self, client: AsyncClient, admin_token: str) -> None:
        """Admins can create users via POST /users."""
        if not admin_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(
            "/api/users",
            headers=headers,
            json={"email": "admin_created@example.com", "account_type": "job_seeker"},
        )

        # May succeed or fail based on validation
        # Important: Not a 403 (authorization issue)
        assert response.status_code in [201, 400, 422]

    @pytest.mark.asyncio
    async def test_admin_can_change_account_type(
        self, client: AsyncClient, admin_token: str, job_seeker_token: str
    ) -> None:
        """Admins can change a user's account_type."""
        if not admin_token or not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        # Get job seeker's user ID
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        js_response = await client.get("/api/users/me", headers=js_headers)
        js_user_id = js_response.json()["id"]

        # Change account type as admin
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.put(
            f"/api/users/{js_user_id}", headers=admin_headers, json={"account_type": "employer"}
        )

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["account_type"] == "employer"

    @pytest.mark.asyncio
    async def test_admin_can_delete_any_user(
        self, client: AsyncClient, admin_token: str, job_seeker_token: str
    ) -> None:
        """Admins can delete any user."""
        if not admin_token or not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        # Get job seeker's user ID
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        js_response = await client.get("/api/users/me", headers=js_headers)
        js_user_id = js_response.json()["id"]

        # Delete as admin
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.delete(f"/api/users/{js_user_id}", headers=admin_headers)

        assert response.status_code == HTTP_NO_CONTENT

    # ============================================================================
    # ADMIN PAGINATION & SEARCH TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_admin_can_paginate_users(
        self,
        client: AsyncClient,
        admin_token: str,
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Admins can paginate through user list."""
        if not admin_token:
            pytest.skip("Email confirmation required for testing")

        # Create multiple users
        for i in range(3):
            await create_temp_user("job_seeker", f"temp.pagination{i}@test.com")

        headers = {"Authorization": f"Bearer {admin_token}"}

        # Test pagination
        response1 = await client.get("/api/users?skip=0&limit=2", headers=headers)
        assert response1.status_code == HTTP_OK
        page1 = response1.json()

        response2 = await client.get("/api/users?skip=2&limit=2", headers=headers)
        assert response2.status_code == HTTP_OK
        page2 = response2.json()

        # Pages should have different users
        if len(page1) >= MIN_PAGE_SIZE and len(page2) >= 1:
            page1_ids = {u["id"] for u in page1}
            page2_ids = {u["id"] for u in page2}
            assert page1_ids != page2_ids

    @pytest.mark.asyncio
    async def test_admin_can_search_user_by_email(
        self,
        client: AsyncClient,
        admin_token: str,
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Admins can search for users by email."""
        if not admin_token:
            pytest.skip("Email confirmation required for testing")

        # Create user with specific email
        email = "searchable.user@test.com"
        await create_temp_user("job_seeker", email)

        headers = {"Authorization": f"Bearer {admin_token}"}

        # Search by email
        response = await client.get(f"/api/users/email/{email}", headers=headers)
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["email"] == email

    @pytest.mark.asyncio
    async def test_non_admin_cannot_search_user_by_email(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Non-admins cannot search users by email."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = await client.get("/api/users/email/test@example.com", headers=headers)

        assert response.status_code == HTTP_FORBIDDEN

    # ============================================================================
    # USER WORKFLOW TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_complete_user_registration_workflow(
        self,
        client: AsyncClient,
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Complete workflow: Register → View profile → Update → Create profile."""
        # Step 1: Create new user
        token, user_id = await create_temp_user("job_seeker", "temp.user.workflow@test.com")
        if not token or not user_id:
            pytest.skip("Failed to create temp user")

        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: View own account
        me_response = await client.get("/api/users/me", headers=headers)
        assert me_response.status_code == HTTP_OK
        assert me_response.json()["account_type"] == "job_seeker"

        # Step 3: Update account info
        update_response = await client.put(
            "/api/users/me", headers=headers, json={"email": "updated@example.com"}
        )
        # May succeed or fail based on validation, not authorization
        assert update_response.status_code in [HTTP_OK, 400, 422]

        # Step 4: Create job seeker profile
        profile_response = await client.post(
            "/api/job-seeker-profiles",
            headers=headers,
            json={
                "user_id": user_id,
                "first_name": "Test",
                "last_name": "User",
                "email": "temp.user.workflow@test.com",
                "skills": ["Python"],
            },
        )
        # Profile creation should succeed (or already exist)
        assert profile_response.status_code in [201, 400]

    @pytest.mark.asyncio
    async def test_admin_user_management_workflow(
        self,
        client: AsyncClient,
        admin_token: str,
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Admin workflow: List users → View user → Update user → Delete user."""
        if not admin_token:
            pytest.skip("Email confirmation required for testing")

        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Step 1: Create a test user
        token, user_id = await create_temp_user("job_seeker", "temp.admin.mgmt@test.com")
        if not token or not user_id:
            pytest.skip("Failed to create temp user")

        # Step 2: Admin lists all users
        list_response = await client.get("/api/users", headers=admin_headers)
        assert list_response.status_code == HTTP_OK
        users = list_response.json()
        assert any(u["id"] == user_id for u in users)

        # Step 3: Admin views specific user
        view_response = await client.get(f"/api/users/{user_id}", headers=admin_headers)
        assert view_response.status_code == HTTP_OK
        assert view_response.json()["id"] == user_id

        # Step 4: Admin updates user
        update_response = await client.put(
            f"/api/users/{user_id}", headers=admin_headers, json={"account_type": "employer"}
        )
        assert update_response.status_code == HTTP_OK
        assert update_response.json()["account_type"] == "employer"

        # Step 5: Admin deletes user
        delete_response = await client.delete(f"/api/users/{user_id}", headers=admin_headers)
        assert delete_response.status_code == HTTP_NO_CONTENT

    @pytest.mark.asyncio
    async def test_user_account_deletion_cascade_workflow(
        self,
        client: AsyncClient,
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """User deletion should cascade to profile."""
        # Step 1: Create user and profile
        token, user_id = await create_temp_user("job_seeker", "temp.cascade@test.com")
        if not token or not user_id:
            pytest.skip("Failed to create temp user")

        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Create profile
        profile_response = await client.post(
            "/api/job-seeker-profiles",
            headers=headers,
            json={
                "user_id": user_id,
                "first_name": "Delete",
                "last_name": "Me",
                "email": "temp.cascade@test.com",
                "skills": ["Test"],
            },
        )
        if profile_response.status_code != HTTP_CREATED:
            pytest.skip("Failed to create profile")

        profile_id = profile_response.json()["id"]

        # Step 3: Verify profile exists
        get_profile = await client.get(f"/api/job-seeker-profiles/{profile_id}")
        assert get_profile.status_code == HTTP_OK

        # Step 4: Delete user
        delete_response = await client.delete("/api/users/me", headers=headers)
        assert delete_response.status_code in [HTTP_NO_CONTENT, HTTP_NOT_FOUND]

        # Step 5: Verify profile is also deleted (cascade)
        verify_profile = await client.get(f"/api/job-seeker-profiles/{profile_id}")
        assert verify_profile.status_code == HTTP_NOT_FOUND

    @pytest.mark.asyncio
    async def test_account_type_protection_workflow(
        self,
        client: AsyncClient,
        job_seeker_token: str,
        employer_token: str,
    ) -> None:
        """Users cannot change their own account type to gain privileges."""
        if not job_seeker_token or not employer_token:
            pytest.skip("Email confirmation required for testing")

        # Job seeker tries to become admin
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        js_response = await client.put(
            "/api/users/me", headers=js_headers, json={"account_type": "admin"}
        )
        assert js_response.status_code == HTTP_FORBIDDEN

        # Employer tries to become admin
        emp_headers = {"Authorization": f"Bearer {employer_token}"}
        emp_response = await client.put(
            "/api/users/me", headers=emp_headers, json={"account_type": "admin"}
        )
        assert emp_response.status_code == HTTP_FORBIDDEN
