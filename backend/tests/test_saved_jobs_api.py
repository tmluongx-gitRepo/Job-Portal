"""
Tests for Saved Jobs API endpoints.
"""

import pytest
from httpx import AsyncClient

from tests.conftest import DataCleaner
from tests.constants import (
    HTTP_CONFLICT,
    HTTP_CREATED,
    HTTP_FORBIDDEN,
    HTTP_NO_CONTENT,
    HTTP_NOT_FOUND,
    HTTP_OK,
)


@pytest.mark.asyncio
class TestSavedJobsAPI:
    """Test suite for Saved Jobs API."""

    async def test_unauthenticated_cannot_save_job(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot save jobs."""
        response = await client.post(
            "/api/saved-jobs",
            json={"job_id": "507f1f77bcf86cd799439011", "job_seeker_id": "test"},
        )
        assert response.status_code == HTTP_FORBIDDEN

    async def test_unauthenticated_cannot_list_saved_jobs(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot list saved jobs."""
        response = await client.get("/api/saved-jobs")
        assert response.status_code == HTTP_FORBIDDEN

    async def test_employer_cannot_save_job(self, client: AsyncClient, employer_token: str) -> None:
        """Employers cannot save jobs."""
        response = await client.post(
            "/api/saved-jobs",
            json={"job_id": "507f1f77bcf86cd799439011", "job_seeker_id": "test"},
            headers={"Authorization": f"Bearer {employer_token}"},
        )
        assert response.status_code == HTTP_FORBIDDEN

    async def test_job_seeker_can_list_saved_jobs_empty(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Job seeker can list their saved jobs (initially empty)."""
        response = await client.get(
            "/api/saved-jobs", headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == HTTP_OK
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    async def test_job_seeker_can_check_if_job_saved(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Job seeker can check if a job is saved."""
        response = await client.get(
            "/api/saved-jobs/check/507f1f77bcf86cd799439011",
            headers={"Authorization": f"Bearer {job_seeker_token}"},
        )
        assert response.status_code == HTTP_OK
        data = response.json()
        assert "is_saved" in data
        assert data["is_saved"] is False

    async def test_job_seeker_can_count_saved_jobs(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Job seeker can count their saved jobs."""
        response = await client.get(
            "/api/saved-jobs/count", headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == HTTP_OK
        data = response.json()
        assert "count" in data
        assert data["count"] == 0

    async def test_cannot_save_nonexistent_job(
        self, client: AsyncClient, job_seeker_with_profile: tuple[str, str, str]
    ) -> None:
        """Cannot save a job that doesn't exist."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile

        response = await client.post(
            "/api/saved-jobs",
            json={
                "job_id": "507f1f77bcf86cd799439011",  # Non-existent job
                "job_seeker_id": js_user_id,
            },
            headers={"Authorization": f"Bearer {js_token}"},
        )
        assert response.status_code == HTTP_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    async def test_get_nonexistent_saved_job(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Getting a non-existent saved job returns 404."""
        response = await client.get(
            "/api/saved-jobs/507f1f77bcf86cd799439011",
            headers={"Authorization": f"Bearer {job_seeker_token}"},
        )
        assert response.status_code == HTTP_NOT_FOUND

    async def test_update_nonexistent_saved_job(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Updating a non-existent saved job returns 404."""
        response = await client.put(
            "/api/saved-jobs/507f1f77bcf86cd799439011",
            json={"notes": "Updated notes"},
            headers={"Authorization": f"Bearer {job_seeker_token}"},
        )
        assert response.status_code == HTTP_NOT_FOUND

    async def test_delete_nonexistent_saved_job(
        self, client: AsyncClient, job_seeker_token: str
    ) -> None:
        """Deleting a non-existent saved job returns 404."""
        response = await client.delete(
            "/api/saved-jobs/507f1f77bcf86cd799439011",
            headers={"Authorization": f"Bearer {job_seeker_token}"},
        )
        assert response.status_code == HTTP_NOT_FOUND


@pytest.mark.asyncio
class TestSavedJobsAPIIntegration:
    """Integration tests requiring actual data."""

    async def test_complete_saved_jobs_workflow(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
        test_cleaner: DataCleaner,
    ) -> None:
        """Test complete workflow: create job, save it, update notes, delete."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, emp_user_id, emp_profile_id = employer_with_profile

        # 1. Employer creates a job
        job_response = await client.post(
            "/api/jobs",
            json={
                "title": "Test Job for Saving",
                "company": "Test Company",
                "location": "Remote",
                "description": "A job to test saving functionality",
                "job_type": "Full-time",
            },
            headers={"Authorization": f"Bearer {emp_token}"},
        )
        assert job_response.status_code == HTTP_CREATED
        job = job_response.json()
        job_id = job["id"]
        test_cleaner.track_job(job_id)

        # 2. Job seeker saves the job
        save_response = await client.post(
            "/api/saved-jobs",
            json={
                "job_id": job_id,
                "job_seeker_id": js_user_id,
                "notes": "Looks interesting!",
            },
            headers={"Authorization": f"Bearer {js_token}"},
        )
        assert save_response.status_code == HTTP_CREATED
        saved_job = save_response.json()
        assert saved_job["job_id"] == job_id
        assert saved_job["notes"] == "Looks interesting!"
        saved_job_id = saved_job["id"]

        # 3. Check if job is saved
        check_response = await client.get(
            f"/api/saved-jobs/check/{job_id}",
            headers={"Authorization": f"Bearer {js_token}"},
        )
        assert check_response.status_code == HTTP_OK
        assert check_response.json()["is_saved"] is True

        # 4. Count saved jobs
        count_response = await client.get(
            "/api/saved-jobs/count", headers={"Authorization": f"Bearer {js_token}"}
        )
        assert count_response.status_code == HTTP_OK
        assert count_response.json()["count"] == 1

        # 5. List saved jobs
        list_response = await client.get(
            "/api/saved-jobs", headers={"Authorization": f"Bearer {js_token}"}
        )
        assert list_response.status_code == HTTP_OK
        saved_jobs = list_response.json()
        assert len(saved_jobs) == 1
        assert saved_jobs[0]["job_id"] == job_id

        # 6. Get specific saved job
        get_response = await client.get(
            f"/api/saved-jobs/{saved_job_id}",
            headers={"Authorization": f"Bearer {js_token}"},
        )
        assert get_response.status_code == HTTP_OK
        assert get_response.json()["id"] == saved_job_id

        # 7. Update notes
        update_response = await client.put(
            f"/api/saved-jobs/{saved_job_id}",
            json={"notes": "Updated: Will apply next week"},
            headers={"Authorization": f"Bearer {js_token}"},
        )
        assert update_response.status_code == HTTP_OK
        updated = update_response.json()
        assert updated["notes"] == "Updated: Will apply next week"

        # 8. Try to save the same job again (should fail with 409)
        duplicate_response = await client.post(
            "/api/saved-jobs",
            json={"job_id": job_id, "job_seeker_id": js_user_id},
            headers={"Authorization": f"Bearer {js_token}"},
        )
        assert duplicate_response.status_code == HTTP_CONFLICT

        # 9. Delete saved job
        delete_response = await client.delete(
            f"/api/saved-jobs/{saved_job_id}",
            headers={"Authorization": f"Bearer {js_token}"},
        )
        assert delete_response.status_code == HTTP_NO_CONTENT

        # 10. Verify it's deleted
        verify_response = await client.get(
            f"/api/saved-jobs/{saved_job_id}",
            headers={"Authorization": f"Bearer {js_token}"},
        )
        assert verify_response.status_code == HTTP_NOT_FOUND

        # 11. Count should be 0 again
        final_count = await client.get(
            "/api/saved-jobs/count", headers={"Authorization": f"Bearer {js_token}"}
        )
        assert final_count.json()["count"] == 0
