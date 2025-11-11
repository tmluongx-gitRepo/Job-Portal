"""
Tests for Health Check API.

Simple tests to verify the health endpoint is working correctly.
"""

import pytest
from httpx import AsyncClient

from tests.constants import HTTP_OK


@pytest.mark.asyncio
class TestHealthCheck:
    """Test suite for Health Check API."""

    async def test_health_check_returns_ok(self, client: AsyncClient) -> None:
        """Health check endpoint returns 200 OK."""
        response = await client.get("/health")
        assert response.status_code == HTTP_OK

    async def test_health_check_response_format(self, client: AsyncClient) -> None:
        """Health check returns proper JSON response."""
        response = await client.get("/health")
        assert response.status_code == HTTP_OK

        data = response.json()
        assert "status" in data
        # Status can be "healthy" or "degraded" depending on services
        assert data["status"] in ["healthy", "degraded"]

    async def test_health_check_no_auth_required(self, client: AsyncClient) -> None:
        """Health check is accessible without authentication."""
        # No auth headers
        response = await client.get("/health")
        assert response.status_code == HTTP_OK
        # Status can be "healthy" or "degraded"
        assert response.json()["status"] in ["healthy", "degraded"]

    async def test_health_check_always_available(self, client: AsyncClient) -> None:
        """Health check should always be available (idempotent)."""
        # Call it multiple times
        for _ in range(5):
            response = await client.get("/health")
            assert response.status_code == HTTP_OK
            # Status can be "healthy" or "degraded"
            assert response.json()["status"] in ["healthy", "degraded"]
