"""
Test application status transition workflows and side effects.
"""

import pytest
from httpx import AsyncClient

from tests.constants import HTTP_CREATED, HTTP_OK


class TestApplicationAcceptanceWorkflow:
    """Test complete acceptance workflow with side effects."""

    @pytest.mark.asyncio
    async def test_accepting_application_cancels_interviews(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """When application accepted, all interviews are cancelled."""
        emp_token, _, _ = employer_with_profile
        js_token, _, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # 1. Create job
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Software Engineer",
                "company": "Test Co",
                "description": "Great opportunity",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # 2. Job seeker applies
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={"job_id": job_id, "job_seeker_id": js_profile_id, "notes": "Interested"},
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # 3. Employer schedules interview
        interview_response = await client.post(
            "/api/interviews",
            headers=emp_headers,
            json={
                "application_id": app_id,
                "scheduled_date": "2025-12-01T10:00:00Z",
                "interview_type": "video",
                "duration_minutes": 60,
                "timezone": "UTC",
                "interviewer_email": "interviewer@test.com",
            },
        )
        assert interview_response.status_code == HTTP_CREATED
        interview_id = interview_response.json()["id"]

        # 4. Employer extends offer
        await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Offer Extended"},
        )

        # 5. Employer accepts application
        await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Accepted"},
        )

        # 6. Verify interview is cancelled
        interview_check = await client.get(f"/api/interviews/{interview_id}", headers=emp_headers)
        assert interview_check.status_code == HTTP_OK
        assert interview_check.json()["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_accepting_application_marks_job_filled(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """When application accepted, job is marked as inactive."""
        emp_token, _, _ = employer_with_profile
        js_token, _, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # 1. Create job (is_active=True by default)
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Data Scientist",
                "company": "Test Co",
                "description": "ML role",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]
        assert job_response.json()["is_active"] is True

        # 2. Job seeker applies
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={"job_id": job_id, "job_seeker_id": js_profile_id, "notes": "Interested"},
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # 3. Employer extends offer
        await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Offer Extended"},
        )

        # 4. Employer accepts
        await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Accepted"},
        )

        # 5. Verify job.is_active = False
        job_check = await client.get(f"/api/jobs/{job_id}")
        assert job_check.status_code == HTTP_OK
        assert job_check.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_accepting_application_rejects_others(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
        job_seeker_2_with_profile: tuple[str, str, str],
    ) -> None:
        """When one application accepted, others are auto-rejected."""
        emp_token, _, _ = employer_with_profile
        js1_token, _, js1_profile_id = job_seeker_with_profile
        js2_token, _, js2_profile_id = job_seeker_2_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js1_headers = {"Authorization": f"Bearer {js1_token}"}
        js2_headers = {"Authorization": f"Bearer {js2_token}"}

        # 1. Create job
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Product Manager",
                "company": "Test Co",
                "description": "PM role",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # 2. First job seeker applies
        app1_response = await client.post(
            "/api/applications",
            headers=js1_headers,
            json={"job_id": job_id, "job_seeker_id": js1_profile_id, "notes": "Interested"},
        )
        assert app1_response.status_code == HTTP_CREATED
        app1_id = app1_response.json()["id"]

        # 3. Second job seeker applies (using permanent test user)
        app2_response = await client.post(
            "/api/applications",
            headers=js2_headers,
            json={"job_id": job_id, "job_seeker_id": js2_profile_id, "notes": "Also interested"},
        )
        assert app2_response.status_code == HTTP_CREATED
        app2_id = app2_response.json()["id"]

        # 4. Employer extends offer to first applicant
        await client.put(
            f"/api/applications/{app1_id}",
            headers=emp_headers,
            json={"status": "Offer Extended"},
        )

        # 5. Employer accepts first application
        await client.put(
            f"/api/applications/{app1_id}",
            headers=emp_headers,
            json={"status": "Accepted"},
        )

        # 6. Verify second application is auto-rejected
        app2_check = await client.get(f"/api/applications/{app2_id}", headers=js2_headers)
        assert app2_check.status_code == HTTP_OK
        assert app2_check.json()["status"] == "Rejected"
        assert app2_check.json()["rejection_reason"] == "Position filled"


class TestApplicationRejectionWorkflow:
    """Test rejection workflow."""

    @pytest.mark.asyncio
    async def test_rejecting_application_cancels_interviews(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """When application rejected, interviews are cancelled."""
        emp_token, _, _ = employer_with_profile
        js_token, _, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # 1. Create job
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Backend Engineer",
                "company": "Test Co",
                "description": "API development",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # 2. Job seeker applies
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={"job_id": job_id, "job_seeker_id": js_profile_id, "notes": "Interested"},
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # 3. Employer schedules interview
        interview_response = await client.post(
            "/api/interviews",
            headers=emp_headers,
            json={
                "application_id": app_id,
                "scheduled_date": "2025-12-01T14:00:00Z",
                "interview_type": "phone",
                "duration_minutes": 30,
                "timezone": "UTC",
                "interviewer_email": "interviewer@test.com",
            },
        )
        assert interview_response.status_code == HTTP_CREATED
        interview_id = interview_response.json()["id"]

        # 4. Employer rejects application
        await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Rejected", "rejection_reason": "Not a fit"},
        )

        # 5. Verify interview is cancelled
        interview_check = await client.get(f"/api/interviews/{interview_id}", headers=emp_headers)
        assert interview_check.status_code == HTTP_OK
        assert interview_check.json()["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_rejection_with_reason(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """Rejection stores reason properly."""
        emp_token, _, _ = employer_with_profile
        js_token, _, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # Create job
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Frontend Engineer",
                "company": "Test Co",
                "description": "React development",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Apply
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={"job_id": job_id, "job_seeker_id": js_profile_id, "notes": "Interested"},
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Reject with reason
        reject_response = await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={
                "status": "Rejected",
                "rejection_reason": "Insufficient experience with React",
            },
        )
        assert reject_response.status_code == HTTP_OK
        assert reject_response.json()["status"] == "Rejected"
        assert reject_response.json()["rejection_reason"] == "Insufficient experience with React"

    @pytest.mark.asyncio
    async def test_rejection_does_not_affect_job(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """Rejecting one application doesn't affect job status."""
        emp_token, _, _ = employer_with_profile
        js_token, _, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # Create job
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "DevOps Engineer",
                "company": "Test Co",
                "description": "Infrastructure",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Apply
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={"job_id": job_id, "job_seeker_id": js_profile_id, "notes": "Interested"},
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Reject
        await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Rejected", "rejection_reason": "Not a fit"},
        )

        # Verify job is still active
        job_check = await client.get(f"/api/jobs/{job_id}")
        assert job_check.status_code == HTTP_OK
        assert job_check.json()["is_active"] is True


class TestStatusTransitionValidation:
    """Test status transition validation rules."""

    @pytest.mark.asyncio
    async def test_cannot_accept_from_submitted(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """Cannot go directly from Submitted to Accepted."""
        emp_token, _, _ = employer_with_profile
        js_token, _, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # Create job and apply
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Test Job",
                "company": "Test Co",
                "description": "Test",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={"job_id": job_id, "job_seeker_id": js_profile_id, "notes": "Test"},
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Try to accept without offer
        accept_response = await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Accepted"},
        )
        assert accept_response.status_code == 400  # noqa: PLR2004

    @pytest.mark.asyncio
    async def test_can_accept_from_offer_extended(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """Can accept when offer is extended."""
        emp_token, _, _ = employer_with_profile
        js_token, _, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # Create job and apply
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Test Job",
                "company": "Test Co",
                "description": "Test",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={"job_id": job_id, "job_seeker_id": js_profile_id, "notes": "Test"},
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Extend offer
        await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Offer Extended"},
        )

        # Accept
        accept_response = await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Accepted"},
        )
        assert accept_response.status_code == HTTP_OK
        assert accept_response.json()["status"] == "Accepted"

    @pytest.mark.asyncio
    async def test_accepted_is_final(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """Accepted status cannot be changed."""
        emp_token, _, _ = employer_with_profile
        js_token, _, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # Create job and apply
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Test Job",
                "company": "Test Co",
                "description": "Test",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={"job_id": job_id, "job_seeker_id": js_profile_id, "notes": "Test"},
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Extend offer and accept
        await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Offer Extended"},
        )
        await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Accepted"},
        )

        # Try to reject after acceptance
        reject_response = await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Rejected"},
        )
        assert reject_response.status_code == 400  # noqa: PLR2004

