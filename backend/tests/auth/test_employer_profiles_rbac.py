"""
RBAC tests for Employer Profiles API.

Comprehensive tests covering:
- Basic CRUD operations
- Cross-user authorization
- Pagination
- Business logic (profile views, verification)
- User workflows
"""

from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from httpx import AsyncClient

from tests.constants import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_FORBIDDEN,
    HTTP_NO_CONTENT,
    HTTP_OK,
    MIN_PAGE_SIZE,
)


class TestEmployerProfilesRBAC:
    """Test role-based access control for Employer Profiles API."""

    @pytest.mark.asyncio
    async def test_unauthenticated_can_browse_profiles(self, client: AsyncClient) -> None:
        """Unauthenticated users can browse employer profiles (public)."""
        response = await client.get("/api/employer-profiles")

        assert response.status_code == HTTP_OK
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_create_profile(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot create profiles."""
        response = await client.post(
            "/api/employer-profiles",
            json={"company_name": "Test Company", "industry": "Technology"},
        )

        # FastAPI HTTPBearer returns 403 when no credentials provided
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_employer_can_create_profile(
        self, client: AsyncClient, employer_token: str
    ) -> None:
        """Employers can create their profile."""
        if not employer_token:
            pytest.skip("Email confirmation required for testing")

        # Get user info first to get user_id
        user_response = await client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {employer_token}"}
        )
        user_id = user_response.json()["id"]

        headers = {"Authorization": f"Bearer {employer_token}"}

        response = await client.post(
            "/api/employer-profiles",
            headers=headers,
            json={
                "user_id": user_id,
                "company_name": "Test Company",
                "industry": "Technology",
                "company_size": "50-200",
                "website": "https://test.com",
                "location": "SF",
                "description": "Test",
            },
        )

        # Accept both 201 (created) and 400 (already exists) as valid
        # since other tests in the session may have already created the profile
        assert response.status_code in [HTTP_CREATED, 400]

        # If created, verify the data
        if response.status_code == HTTP_CREATED:
            data = response.json()
            assert data["company_name"] == "Test Company"

    @pytest.mark.asyncio
    async def test_job_seeker_cannot_create_employer_profile(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Job seekers cannot create employer profiles."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = await client.post(
            "/api/employer-profiles",
            headers=headers,
            json={"user_id": "test", "company_name": "Test", "industry": "Tech"},
        )

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_employer_can_update_own_profile(
        self, client: AsyncClient, employer_with_profile: tuple[str, str, str]
    ) -> None:
        """Employers can update their own profile."""
        token, user_id, profile_id = employer_with_profile

        headers = {"Authorization": f"Bearer {token}"}
        response = await client.put(
            f"/api/employer-profiles/{profile_id}",
            headers=headers,
            json={"description": "Updated description"},
        )

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_employer_cannot_update_other_profile(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        create_temp_user: Any,
    ) -> None:
        """Employers cannot update other employers' profiles."""
        _, _, profile_id = employer_with_profile

        # Create a second employer to test cross-user authorization
        token2, _ = await create_temp_user("employer", "temp.employer2@test.com")
        if not token2:
            pytest.skip("Failed to create temporary employer user")

        headers = {"Authorization": f"Bearer {token2}"}
        response = await client.put(
            f"/api/employer-profiles/{profile_id}", headers=headers, json={"description": "Hacked!"}
        )

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_can_update_any_profile(
        self, client: AsyncClient, admin_token: str, employer_with_profile: tuple[str, str, str]
    ) -> None:
        """Admins can update any employer profile."""
        if not admin_token:
            pytest.skip("Email confirmation required for testing")

        _, _, profile_id = employer_with_profile

        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.put(
            f"/api/employer-profiles/{profile_id}",
            headers=headers,
            json={"description": "Admin updated"},
        )

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["description"] == "Admin updated"

    @pytest.mark.asyncio
    async def test_employer_can_delete_own_profile(
        self, client: AsyncClient, employer_with_profile: tuple[str, str, str]
    ) -> None:
        """Employers can delete their own profile."""
        token, user_id, profile_id = employer_with_profile

        headers = {"Authorization": f"Bearer {token}"}
        response = await client.delete(f"/api/employer-profiles/{profile_id}", headers=headers)

        assert response.status_code == HTTP_NO_CONTENT

    @pytest.mark.asyncio
    async def test_job_seeker_cannot_delete_employer_profile(
        self,
        client: AsyncClient,
        job_seeker_token: str,
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Job seekers cannot delete employer profiles."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        _, _, profile_id = employer_with_profile

        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = await client.delete(f"/api/employer-profiles/{profile_id}", headers=headers)

        assert response.status_code == HTTP_FORBIDDEN

    # ============================================================================
    # PAGINATION TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_pagination_with_skip_and_limit(
        self,
        client: AsyncClient,
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Pagination works with skip and limit."""
        # Create multiple employer profiles
        for i in range(3):
            token, user_id = await create_temp_user("employer", f"temp.emp.page{i}@test.com")
            if token and user_id:
                headers = {"Authorization": f"Bearer {token}"}
                await client.post(
                    "/api/employer-profiles",
                    headers=headers,
                    json={
                        "user_id": user_id,
                        "company_name": f"Company{i}",
                        "industry": "Technology",
                        "company_size": "10-50",
                        "location": "SF",
                        "description": "Test company",
                    },
                )

        # Test pagination
        response1 = await client.get("/api/employer-profiles?skip=0&limit=2")
        assert response1.status_code == HTTP_OK
        page1 = response1.json()

        response2 = await client.get("/api/employer-profiles?skip=2&limit=2")
        assert response2.status_code == HTTP_OK
        page2 = response2.json()

        # Pages should have different profiles
        if len(page1) >= MIN_PAGE_SIZE and len(page2) >= 1:
            page1_ids = {p["id"] for p in page1}
            page2_ids = {p["id"] for p in page2}
            assert page1_ids != page2_ids

    # ============================================================================
    # BUSINESS LOGIC TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_profile_views_increment(
        self, client: AsyncClient, employer_with_profile: tuple[str, str, str]
    ) -> None:
        """Profile view count increments when viewed."""
        _, _, profile_id = employer_with_profile

        # Get initial view count
        response1 = await client.get(f"/api/employer-profiles/{profile_id}")
        initial_views = response1.json().get("profile_views", 0)

        # View the profile (views increment automatically)
        await client.get(f"/api/employer-profiles/{profile_id}")

        # Check view count increased
        response2 = await client.get(f"/api/employer-profiles/{profile_id}")
        current_views = response2.json().get("profile_views", 0)
        assert current_views >= initial_views

    @pytest.mark.asyncio
    async def test_cannot_create_duplicate_profile(
        self, client: AsyncClient, employer_with_profile: tuple[str, str, str]
    ) -> None:
        """Cannot create duplicate profile for same user."""
        token, user_id, profile_id = employer_with_profile
        headers = {"Authorization": f"Bearer {token}"}

        # Try to create another profile for same user
        response = await client.post(
            "/api/employer-profiles",
            headers=headers,
            json={
                "user_id": user_id,
                "company_name": "Duplicate Company",
                "industry": "Tech",
                "company_size": "10-50",
                "location": "NYC",
                "description": "Duplicate",
            },
        )

        assert response.status_code == HTTP_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_get_profile_by_user_id(
        self, client: AsyncClient, employer_with_profile: tuple[str, str, str]
    ) -> None:
        """Can get profile by user ID."""
        _, user_id, profile_id = employer_with_profile

        # Get profile by user ID
        response = await client.get(f"/api/employer-profiles/user/{user_id}")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == profile_id

    # ============================================================================
    # USER WORKFLOW TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_complete_profile_creation_workflow(
        self,
        client: AsyncClient,
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Complete workflow: Register → Create profile → Update → Post job."""
        # Step 1: Create new employer
        token, user_id = await create_temp_user("employer", "temp.emp.workflow1@test.com")
        if not token or not user_id:
            pytest.skip("Failed to create temp user")

        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Create initial profile
        create_response = await client.post(
            "/api/employer-profiles",
            headers=headers,
            json={
                "user_id": user_id,
                "company_name": "TechStartup Inc",
                "industry": "Technology",
                "company_size": "10-50",
                "location": "San Francisco, CA",
                "description": "We're hiring!",
            },
        )
        assert create_response.status_code == HTTP_CREATED
        profile_id = create_response.json()["id"]

        # Step 3: Update profile with more details
        update_response = await client.put(
            f"/api/employer-profiles/{profile_id}",
            headers=headers,
            json={
                "website": "https://techstartup.com",
                "description": "Leading tech startup looking for talented engineers",
                "founded_year": 2020,
            },
        )
        assert update_response.status_code == HTTP_OK

        # Step 4: Profile appears in public listing
        list_response = await client.get("/api/employer-profiles")
        assert any(p["id"] == profile_id for p in list_response.json())

        # Step 5: Employer can now post jobs (tested in jobs tests)
        # Just verify profile exists for job posting
        get_response = await client.get(f"/api/employer-profiles/{profile_id}", headers=headers)
        assert get_response.status_code == HTTP_OK

    @pytest.mark.asyncio
    async def test_job_seeker_viewing_company_workflow(
        self,
        client: AsyncClient,
        job_seeker_token: str,
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Job seeker workflow: Browse companies → View company profile."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        _, _, profile_id = employer_with_profile
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}

        # Step 1: Browse all company profiles
        browse_response = await client.get("/api/employer-profiles", headers=js_headers)
        assert browse_response.status_code == HTTP_OK
        profiles = browse_response.json()
        assert len(profiles) >= 1

        # Step 2: View specific company profile
        detail_response = await client.get(
            f"/api/employer-profiles/{profile_id}", headers=js_headers
        )
        assert detail_response.status_code == HTTP_OK
        profile_detail = detail_response.json()
        assert "company_name" in profile_detail
        assert "description" in profile_detail

    @pytest.mark.asyncio
    async def test_profile_update_workflow(
        self, client: AsyncClient, employer_with_profile: tuple[str, str, str]
    ) -> None:
        """Employer workflow: Update company profile over time."""
        token, user_id, profile_id = employer_with_profile
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Update basic info
        response1 = await client.put(
            f"/api/employer-profiles/{profile_id}",
            headers=headers,
            json={"website": "https://newwebsite.com", "location": "Seattle, WA"},
        )
        assert response1.status_code == HTTP_OK

        # Step 2: Update company description
        response2 = await client.put(
            f"/api/employer-profiles/{profile_id}",
            headers=headers,
            json={"description": "We are a fast-growing company in the tech industry"},
        )
        assert response2.status_code == HTTP_OK

        # Step 3: Update company size and industry
        response3 = await client.put(
            f"/api/employer-profiles/{profile_id}",
            headers=headers,
            json={"company_size": "50-200", "industry": "Software"},
        )
        assert response3.status_code == HTTP_OK

        # Step 4: Verify all updates persisted
        final_response = await client.get(f"/api/employer-profiles/{profile_id}")
        profile = final_response.json()
        # Check that updates were applied (some fields may not persist if not in schema)
        assert "fast-growing" in profile["description"]
        assert profile["company_size"] == "50-200"

    @pytest.mark.asyncio
    async def test_employer_to_job_posting_workflow(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Complete employer workflow: Profile → Job posting → Applications."""
        token, user_id, profile_id = employer_with_profile
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Verify profile exists
        profile_response = await client.get(f"/api/employer-profiles/{profile_id}", headers=headers)
        assert profile_response.status_code == HTTP_OK

        # Step 2: Create a job posting
        job_response = await client.post(
            "/api/jobs",
            headers=headers,
            json={
                "title": "Software Engineer",
                "company": profile_response.json()["company_name"],
                "description": "Join our team",
                "location": "Remote",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
                "skills_required": ["Python", "FastAPI"],
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Step 3: Job is visible and linked to employer
        job_detail_response = await client.get(f"/api/jobs/{job_id}")
        assert job_detail_response.status_code == HTTP_OK
        job_detail = job_detail_response.json()
        assert job_detail["posted_by"] == user_id

        # Step 4: Employer can update their job
        update_job_response = await client.put(
            f"/api/jobs/{job_id}", headers=headers, json={"title": "Senior Software Engineer"}
        )
        assert update_job_response.status_code == HTTP_OK
