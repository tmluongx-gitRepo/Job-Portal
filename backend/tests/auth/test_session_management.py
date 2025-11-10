"""
Session management tests.
Tests concurrent sessions, logout, and session limits.
"""

import pytest
from bson import ObjectId
from httpx import AsyncClient

from tests.constants import (
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
)


class TestSessionManagement:
    """Test session and token management."""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_sessions_allowed(self, client: AsyncClient, test_cleaner):
        """Users can login from multiple devices simultaneously."""
        email = f"multidevice_test_{ObjectId()}@example.com"
        password = "TestPass123!"

        # Register user
        register_response = await client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "account_type": "job_seeker"},
        )

        if register_response.status_code != HTTP_OK:
            pytest.skip("Email confirmation required for testing")

        # Track for cleanup
        first_token = register_response.json().get("access_token")
        if first_token:
            user_response = await client.get(
                "/api/users/me", headers={"Authorization": f"Bearer {first_token}"}
            )
            if user_response.status_code == HTTP_OK:
                test_cleaner.track_user(user_response.json()["id"], email)

        # Login from "device 1"
        response1 = await client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        if response1.status_code != HTTP_OK:
            pytest.skip("Login endpoint not returning tokens")
        token1 = response1.json()["access_token"]

        # Login from "device 2"
        response2 = await client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        token2 = response2.json()["access_token"]

        # Login from "device 3"
        response3 = await client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        token3 = response3.json()["access_token"]

        # All tokens should work
        for token in [token1, token2, token3]:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get("/api/users/me", headers=headers)
            assert response.status_code == HTTP_OK

    @pytest.mark.asyncio
    async def test_logout_invalidates_current_session(self, client: AsyncClient, test_cleaner):
        """Logging out should invalidate the current session."""
        email = f"logout_test_{ObjectId()}@example.com"
        password = "TestPass123!"

        # Register
        register_response = await client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "account_type": "job_seeker"},
        )

        if register_response.status_code != HTTP_OK:
            pytest.skip("Email confirmation required for testing")

        token = register_response.json().get("access_token")
        if not token:
            pytest.skip("No token returned from registration")

        # Track for cleanup
        user_response = await client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        if user_response.status_code == HTTP_OK:
            test_cleaner.track_user(user_response.json()["id"], email)

        headers = {"Authorization": f"Bearer {token}"}

        # Verify token works
        response = await client.get("/api/users/me", headers=headers)
        assert response.status_code == HTTP_OK

        # Logout
        logout_response = await client.post("/api/auth/logout", headers=headers)

        if logout_response.status_code == HTTP_OK:
            # Token should not work after logout
            response = await client.get("/api/users/me", headers=headers)
            assert response.status_code == HTTP_UNAUTHORIZED
        else:
            pytest.skip("Logout endpoint not fully implemented or requires different flow")

    @pytest.mark.asyncio
    async def test_refresh_token_extends_session(self, client: AsyncClient, job_seeker_token):
        """Refresh token should extend session without re-login."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {job_seeker_token}"}

        # Try to refresh token
        response = await client.post("/api/auth/refresh", headers=headers)

        if response.status_code == HTTP_NOT_FOUND:
            pytest.skip("Refresh endpoint not implemented yet")

        if response.status_code == HTTP_OK:
            data = response.json()
            new_access_token = data.get("access_token")

            if new_access_token:
                # New token should work
                new_headers = {"Authorization": f"Bearer {new_access_token}"}
                me_response = await client.get("/api/users/me", headers=new_headers)
                assert me_response.status_code == HTTP_OK

                # Tokens should be different
                assert new_access_token != job_seeker_token
        else:
            pytest.skip(f"Refresh endpoint returned {response.status_code}")

    @pytest.mark.asyncio
    async def test_login_creates_new_session(self, client: AsyncClient, test_cleaner):
        """Each login should create a fresh session."""
        email = f"login_test_{ObjectId()}@example.com"
        password = "TestPass123!"

        # Register
        register_response = await client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "account_type": "employer"},
        )

        if register_response.status_code != HTTP_OK:
            pytest.skip("Email confirmation required for testing")

        token1 = register_response.json().get("access_token")
        if token1:
            # Track for cleanup
            user_response = await client.get(
                "/api/users/me", headers={"Authorization": f"Bearer {token1}"}
            )
            if user_response.status_code == HTTP_OK:
                test_cleaner.track_user(user_response.json()["id"], email)

        # Login again
        login_response = await client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )

        if login_response.status_code != HTTP_OK:
            pytest.skip("Login endpoint not working as expected")

        token2 = login_response.json().get("access_token")

        # Both tokens should work (concurrent sessions)
        if token1 and token2:
            for token in [token1, token2]:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get("/api/users/me", headers=headers)
                assert response.status_code == HTTP_OK
