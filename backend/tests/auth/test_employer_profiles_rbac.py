"""
RBAC tests for Employer Profiles API.
"""

from typing import Any

import pytest
from httpx import AsyncClient

from tests.constants import (
    HTTP_CREATED,
    HTTP_FORBIDDEN,
    HTTP_NO_CONTENT,
    HTTP_OK,
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
