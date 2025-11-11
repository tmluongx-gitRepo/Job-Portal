"""
Integration workflow tests.

Tests that verify complete user workflows work correctly.
These tests use working test fixtures (not auth registration endpoints).

Note: E2E tests requiring auth registration are not possible here due to
email confirmation requirements. Those should be in a separate E2E test
suite (Cypress/Playwright) with email confirmation disabled.
"""

import pytest
from httpx import AsyncClient

from tests.constants import EXTENDED_SKILLS_COUNT, HTTP_OK


class TestIntegrationWorkflows:
    """Integration tests for complete user workflows."""

    @pytest.mark.asyncio
    async def test_profile_update_workflow(
        self, client: AsyncClient, job_seeker_with_profile: tuple[str, str, str]
    ) -> None:
        """Test updating profile and viewing changes."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # Get initial profile
        initial_response = await client.get(f"/api/job-seeker-profiles/{js_profile_id}")
        assert initial_response.status_code == HTTP_OK
        initial_response.json()

        # Update profile
        update_response = await client.put(
            f"/api/job-seeker-profiles/{js_profile_id}",
            headers=js_headers,
            json={
                "bio": "Updated bio for workflow test",
                "skills": ["Python", "FastAPI", "MongoDB", "React", "TypeScript"],
            },
        )
        assert update_response.status_code == HTTP_OK
        updated_profile = update_response.json()

        # Verify changes
        assert updated_profile["bio"] == "Updated bio for workflow test"
        assert len(updated_profile["skills"]) == EXTENDED_SKILLS_COUNT
        assert "TypeScript" in updated_profile["skills"]

        # Verify changes persist
        verify_response = await client.get(f"/api/job-seeker-profiles/{js_profile_id}")
        assert verify_response.status_code == HTTP_OK
        assert verify_response.json()["bio"] == "Updated bio for workflow test"
