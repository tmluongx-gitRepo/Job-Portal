"""
Token security tests.
Ensures JWT tokens are properly validated and cannot be tampered with.
"""

import jwt
import pytest
from httpx import AsyncClient


class TestTokenSecurity:
    """Test JWT token security and validation."""

    @pytest.mark.asyncio
    async def test_malformed_token_rejected(self, client: AsyncClient) -> None:
        """Malformed tokens should return 401 Unauthorized."""
        test_cases = [
            "not-a-jwt-token",
            "Bearer.malformed.token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "",
            "null",
        ]

        for malformed_token in test_cases:
            headers = {"Authorization": f"Bearer {malformed_token}"}
            response = await client.get("/api/users/me", headers=headers)
            assert response.status_code in [401, 403], f"Failed for token: {malformed_token}"

    @pytest.mark.asyncio
    async def test_tampered_payload_rejected(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Tokens with modified payloads should be rejected."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        # Decode token without verification to get payload
        payload = jwt.decode(job_seeker_token, options={"verify_signature": False})

        # Tamper with payload - try to make user an admin
        payload["account_type"] = "admin"
        payload["role"] = "admin"

        # Re-encode with wrong secret (attacker doesn't have real secret)
        tampered_token = jwt.encode(payload, "wrong-secret-key-attack", algorithm="HS256")

        # Try to use tampered token to access admin endpoint
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = await client.get("/api/users", headers=headers)

        # Should be rejected
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_token_without_bearer_prefix_rejected(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Tokens without 'Bearer' prefix should be rejected."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        # Try without Bearer prefix
        headers = {"Authorization": job_seeker_token}
        response = await client.get("/api/users/me", headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_empty_authorization_header_rejected(self, client: AsyncClient) -> None:
        """Empty Authorization header should be rejected."""
        headers = {"Authorization": ""}
        response = await client.get("/api/users/me", headers=headers)
        assert response.status_code in [401, 403]

        # No Authorization header at all
        response = await client.get("/api/users/me")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_double_bearer_prefix_rejected(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Token with double 'Bearer' prefix should be rejected."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer Bearer {job_seeker_token}"}
        response = await client.get("/api/users/me", headers=headers)

        assert response.status_code in [401, 403]
