"""
Test /api/users/me endpoint with all user roles.

This validates the Supabase token testing infrastructure works correctly
before scaling to all endpoints.

Tests cover:
- Public (unauthenticated)
- Job Seeker
- Employer
- Invalid token
"""

import pytest
from httpx import AsyncClient

from tests.constants import HTTP_FORBIDDEN, HTTP_OK, HTTP_UNAUTHORIZED


class TestUsersMeEndpoint:
    """Test /api/users/me with different authentication levels."""

    @pytest.mark.asyncio
    async def test_get_me_as_public_user(self, client: AsyncClient) -> None:
        """Public (unauthenticated) users cannot access /api/users/me."""
        response = await client.get("/api/users/me")
        # API returns 403 for missing auth, which is acceptable
        assert response.status_code in [HTTP_UNAUTHORIZED, HTTP_FORBIDDEN]

    @pytest.mark.asyncio
    async def test_get_me_as_job_seeker(self, client: AsyncClient, job_seeker_token: str) -> None:
        """Job seekers can access their own user info."""
        response = await client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == HTTP_OK

        data = response.json()
        assert data["account_type"] == "job_seeker"
        assert "id" in data
        assert "email" in data
        print(f"✅ Job Seeker user created: {data['email']}")

    @pytest.mark.asyncio
    async def test_get_me_as_employer(self, client: AsyncClient, employer_token: str) -> None:
        """Employers can access their own user info."""
        response = await client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {employer_token}"}
        )
        assert response.status_code == HTTP_OK

        data = response.json()
        assert data["account_type"] == "employer"
        assert "id" in data
        assert "email" in data
        print(f"✅ Employer user created: {data['email']}")

    @pytest.mark.asyncio
    async def test_get_me_with_invalid_token(self, client: AsyncClient) -> None:
        """Invalid tokens are rejected."""
        response = await client.get(
            "/api/users/me", headers={"Authorization": "Bearer invalid_token_12345"}
        )
        # Should be 401 or 403 depending on how auth is handled
        assert response.status_code in [HTTP_UNAUTHORIZED, HTTP_FORBIDDEN]
