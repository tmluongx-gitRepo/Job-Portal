"""
RBAC tests for Applications API.

Tests authorization for:
- Creating applications (job seeker only)
- Viewing applications (role-based filtering)
- Updating applications (different rules for job seekers vs employers)
- Deleting applications (applicant or admin only)
"""

from collections.abc import Awaitable, Callable

import pytest
from httpx import AsyncClient

from tests.constants import (
    HTTP_BAD_REQUEST,
    HTTP_CONFLICT,
    HTTP_CREATED,
    HTTP_FORBIDDEN,
    HTTP_NO_CONTENT,
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
)


class TestApplicationsRBAC:
    """Test authorization for Applications API endpoints."""

    # ============================================================================
    # CREATE APPLICATION TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_job_seeker_can_create_application(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Job seekers can create applications to jobs."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Employer creates a job first
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Software Engineer",
                "company": "Test Company",
                "description": "Great opportunity",
                "location": "Remote",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Job seeker applies
        js_headers = {"Authorization": f"Bearer {js_token}"}
        response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "I'm very interested in this position",
            },
        )

        assert response.status_code == HTTP_CREATED
        data = response.json()
        assert data["job_id"] == job_id
        assert data["job_seeker_id"] == js_profile_id
        assert data["status"] == "Application Submitted"

    @pytest.mark.asyncio
    async def test_employer_cannot_create_application(
        self, client: AsyncClient, employer_token: str
    ) -> None:
        """Employers cannot create applications (not job seekers)."""
        if not employer_token:
            pytest.skip("Email confirmation required for testing")

        headers = {"Authorization": f"Bearer {employer_token}"}
        response = await client.post(
            "/api/applications",
            headers=headers,
            json={
                "job_id": "fake_job_id",
                "job_seeker_id": "fake_profile_id",
                "notes": "Test",
            },
        )

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_public_cannot_create_application(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot create applications."""
        response = await client.post(
            "/api/applications",
            json={
                "job_id": "fake_job_id",
                "job_seeker_id": "fake_profile_id",
                "notes": "Test",
            },
        )

        assert response.status_code in [HTTP_UNAUTHORIZED, HTTP_FORBIDDEN]

    @pytest.mark.asyncio
    async def test_cannot_apply_with_other_profile(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Job seekers cannot create applications using another user's profile."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create a job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Backend Developer",
                "company": "Test Company",
                "description": "Join our team",
                "location": "San Francisco, CA",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Create another job seeker
        token2, user_id2 = await create_temp_user("job_seeker", "temp.jobseeker.app@test.com")
        if not token2:
            pytest.skip("Failed to create temporary job seeker user")

        # Create profile for second job seeker
        headers2 = {"Authorization": f"Bearer {token2}"}
        profile_response = await client.post(
            "/api/job-seeker-profiles",
            headers=headers2,
            json={
                "user_id": user_id2,
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "temp.jobseeker.app@test.com",
                "skills": ["Python"],
            },
        )
        if profile_response.status_code not in [HTTP_CREATED, HTTP_BAD_REQUEST]:
            pytest.skip(
                f"Failed to create temp profile: {profile_response.status_code} - {profile_response.text}"
            )

        # If profile already exists, get it
        if profile_response.status_code == HTTP_BAD_REQUEST:
            # Profile exists, fetch it
            get_response = await client.get(
                f"/api/job-seeker-profiles/user/{user_id2}", headers=headers2
            )
            if get_response.status_code != HTTP_OK:
                pytest.skip(f"Failed to fetch existing profile: {get_response.status_code}")
            profile_id2 = get_response.json()["id"]
        else:
            profile_id2 = profile_response.json()["id"]

        # First job seeker tries to apply using second job seeker's profile
        js_headers = {"Authorization": f"Bearer {js_token}"}
        response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": profile_id2,  # Using someone else's profile
                "notes": "Trying to use another profile",
            },
        )

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_cannot_apply_to_inactive_job(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Cannot apply to inactive jobs."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Employer creates an inactive job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Old Position",
                "company": "Test Company",
                "description": "This position is closed",
                "location": "Remote",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
                "is_active": False,
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Update the job to set is_active to False (since create hardcodes it to True)
        update_response = await client.put(
            f"/api/jobs/{job_id}",
            headers=emp_headers,
            json={"is_active": False},
        )
        assert update_response.status_code == HTTP_OK

        # Try to apply
        js_headers = {"Authorization": f"Bearer {js_token}"}
        response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Trying to apply to inactive job",
            },
        )

        assert response.status_code == HTTP_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_cannot_apply_twice(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Cannot create duplicate applications to the same job."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create a job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Data Scientist",
                "company": "Test Company",
                "description": "AI/ML position",
                "location": "Remote",
                "job_type": "Full-time",
                "experience_required": "5+ years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Apply once
        js_headers = {"Authorization": f"Bearer {js_token}"}
        response1 = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "First application",
            },
        )
        assert response1.status_code == HTTP_CREATED

        # Try to apply again
        response2 = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Second application",
            },
        )

        assert response2.status_code == HTTP_CONFLICT

    # ============================================================================
    # LIST APPLICATIONS TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_job_seeker_sees_own_applications(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Job seekers see only their own applications."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create a job and apply
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Product Manager",
                "company": "Test Company",
                "description": "Lead product",
                "location": "New York, NY",
                "job_type": "Full-time",
                "experience_required": "5+ years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Interested in PM role",
            },
        )

        # List applications
        response = await client.get("/api/applications", headers=js_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert isinstance(data, list)
        # All applications should belong to this job seeker
        for app in data:
            assert app["job_seeker_id"] == js_profile_id

    @pytest.mark.asyncio
    async def test_employer_sees_applications_to_own_jobs(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Employers see only applications to their jobs."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, emp_user_id, _ = employer_with_profile

        # Create a job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Marketing Manager",
                "company": "Test Company",
                "description": "Lead marketing",
                "location": "Los Angeles, CA",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Job seeker applies
        js_headers = {"Authorization": f"Bearer {js_token}"}
        await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Marketing experience",
            },
        )

        # Employer lists applications
        response = await client.get("/api/applications", headers=emp_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert isinstance(data, list)
        # Should see the application
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_admin_sees_all_applications(
        self,
        client: AsyncClient,
        admin_token: str,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Admins can see all applications."""
        if not admin_token:
            pytest.skip("Admin token required for testing")

        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job and application
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "DevOps Engineer",
                "company": "Test Company",
                "description": "Infrastructure",
                "location": "Seattle, WA",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "DevOps experience",
            },
        )

        # Admin lists all applications
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get("/api/applications", headers=admin_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_public_cannot_list_applications(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot list applications."""
        response = await client.get("/api/applications")

        assert response.status_code in [HTTP_UNAUTHORIZED, HTTP_FORBIDDEN]

    @pytest.mark.asyncio
    async def test_employer_cannot_see_other_jobs_applications(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Employers cannot see applications to other employers' jobs."""
        emp_token, _, _ = employer_with_profile

        # Create another employer
        token2, user_id2 = await create_temp_user("employer", "temp.employer.app@test.com")
        if not token2:
            pytest.skip("Failed to create temporary employer user")

        # Create profile for second employer
        headers2 = {"Authorization": f"Bearer {token2}"}
        profile_response = await client.post(
            "/api/employer-profiles",
            headers=headers2,
            json={
                "user_id": user_id2,
                "company_name": "Other Company",
                "industry": "Technology",
                "location": "Austin, TX",
            },
        )
        if profile_response.status_code not in [HTTP_CREATED, HTTP_BAD_REQUEST]:
            pytest.skip(f"Failed to create temp employer profile: {profile_response.status_code}")

        # If profile already exists, get it
        if profile_response.status_code == HTTP_BAD_REQUEST:
            get_response = await client.get(
                f"/api/employer-profiles/user/{user_id2}", headers=headers2
            )
            if get_response.status_code != HTTP_OK:
                pytest.skip(
                    f"Failed to fetch existing employer profile: {get_response.status_code}"
                )

        # Second employer creates a job
        job_response = await client.post(
            "/api/jobs",
            headers=headers2,
            json={
                "title": "Sales Rep",
                "company": "Other Company",
                "description": "Sales position",
                "location": "Austin, TX",
                "job_type": "Full-time",
                "experience_required": "2+ years",
            },
        )
        if job_response.status_code != HTTP_CREATED:
            pytest.skip("Failed to create job")
        job_id = job_response.json()["id"]

        # First employer tries to filter by second employer's job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        response = await client.get(f"/api/applications?job_id={job_id}", headers=emp_headers)

        # Should either get 403 or empty list (depending on implementation)
        if response.status_code == HTTP_OK:
            data = response.json()
            assert len(data) == 0  # Should not see other employer's applications
        else:
            assert response.status_code == HTTP_FORBIDDEN

    # ============================================================================
    # GET SPECIFIC APPLICATION TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_job_seeker_can_view_own_application(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Job seekers can view their own applications."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job and apply
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "QA Engineer",
                "company": "Test Company",
                "description": "Quality assurance",
                "location": "Remote",
                "job_type": "Full-time",
                "experience_required": "2-4 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "QA experience",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # View the application
        response = await client.get(f"/api/applications/{app_id}", headers=js_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == app_id
        assert data["job_seeker_id"] == js_profile_id

    @pytest.mark.asyncio
    async def test_employer_can_view_application_to_own_job(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Employers can view applications to their jobs."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "UX Designer",
                "company": "Test Company",
                "description": "Design position",
                "location": "San Diego, CA",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Job seeker applies
        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Design portfolio attached",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Employer views the application
        response = await client.get(f"/api/applications/{app_id}", headers=emp_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == app_id

    @pytest.mark.asyncio
    async def test_admin_can_view_any_application(
        self,
        client: AsyncClient,
        admin_token: str,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Admins can view any application."""
        if not admin_token:
            pytest.skip("Admin token required for testing")

        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job and application
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Security Analyst",
                "company": "Test Company",
                "description": "Cybersecurity",
                "location": "Washington, DC",
                "job_type": "Full-time",
                "experience_required": "5+ years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Security certifications",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Admin views the application
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get(f"/api/applications/{app_id}", headers=admin_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == app_id

    @pytest.mark.asyncio
    async def test_cannot_view_other_application(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Job seekers cannot view other job seekers' applications."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create another job seeker
        token2, user_id2 = await create_temp_user("job_seeker", "temp.jobseeker.view@test.com")
        if not token2:
            pytest.skip("Failed to create temporary job seeker user")

        # Create profile for second job seeker
        headers2 = {"Authorization": f"Bearer {token2}"}
        profile_response = await client.post(
            "/api/job-seeker-profiles",
            headers=headers2,
            json={
                "user_id": user_id2,
                "first_name": "Bob",
                "last_name": "Wilson",
                "email": "temp.jobseeker.view@test.com",
                "skills": ["Java"],
            },
        )
        if profile_response.status_code not in [HTTP_CREATED, HTTP_BAD_REQUEST]:
            pytest.skip(f"Failed to create temp profile: {profile_response.status_code}")

        # If profile already exists, get it
        if profile_response.status_code == HTTP_BAD_REQUEST:
            get_response = await client.get(
                f"/api/job-seeker-profiles/user/{user_id2}", headers=headers2
            )
            if get_response.status_code != HTTP_OK:
                pytest.skip(f"Failed to fetch existing profile: {get_response.status_code}")
            profile_id2 = get_response.json()["id"]
        else:
            profile_id2 = profile_response.json()["id"]

        # Create job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Java Developer",
                "company": "Test Company",
                "description": "Java position",
                "location": "Boston, MA",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Second job seeker applies
        app_response = await client.post(
            "/api/applications",
            headers=headers2,
            json={
                "job_id": job_id,
                "job_seeker_id": profile_id2,
                "notes": "Java expert",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # First job seeker tries to view second job seeker's application
        js_headers = {"Authorization": f"Bearer {js_token}"}
        response = await client.get(f"/api/applications/{app_id}", headers=js_headers)

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_public_cannot_view_application(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot view applications."""
        response = await client.get("/api/applications/fake_id")

        assert response.status_code in [HTTP_UNAUTHORIZED, HTTP_FORBIDDEN]

    # ============================================================================
    # UPDATE APPLICATION TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_job_seeker_can_update_own_application_notes(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Job seekers can update notes on their applications."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job and apply
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Content Writer",
                "company": "Test Company",
                "description": "Writing position",
                "location": "Remote",
                "job_type": "Full-time",
                "experience_required": "2-4 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Initial note",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Update notes
        response = await client.put(
            f"/api/applications/{app_id}",
            headers=js_headers,
            json={"notes": "Updated note with more details"},
        )

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["notes"] == "Updated note with more details"

    @pytest.mark.asyncio
    async def test_job_seeker_cannot_update_status(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Job seekers cannot update application status."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job and apply
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "HR Manager",
                "company": "Test Company",
                "description": "HR position",
                "location": "Chicago, IL",
                "job_type": "Full-time",
                "experience_required": "5+ years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "HR experience",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Try to update status
        response = await client.put(
            f"/api/applications/{app_id}",
            headers=js_headers,
            json={"status": "Interview Scheduled"},
        )

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_employer_can_update_application_status(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Employers can update status of applications to their jobs."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Business Analyst",
                "company": "Test Company",
                "description": "BA position",
                "location": "Atlanta, GA",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Job seeker applies
        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "BA certification",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Employer updates status
        response = await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Under Review"},
        )

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["status"] == "Under Review"

    @pytest.mark.asyncio
    async def test_employer_cannot_update_other_jobs_applications(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Employers cannot update applications to other employers' jobs."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create another employer
        token2, user_id2 = await create_temp_user("employer", "temp.employer.update@test.com")
        if not token2:
            pytest.skip("Failed to create temporary employer user")

        # Create profile for second employer
        headers2 = {"Authorization": f"Bearer {token2}"}
        profile_response = await client.post(
            "/api/employer-profiles",
            headers=headers2,
            json={
                "user_id": user_id2,
                "company_name": "Another Company",
                "industry": "Finance",
                "location": "Miami, FL",
            },
        )
        if profile_response.status_code not in [HTTP_CREATED, HTTP_BAD_REQUEST]:
            pytest.skip(f"Failed to create temp employer profile: {profile_response.status_code}")

        # If profile already exists, get it
        if profile_response.status_code == HTTP_BAD_REQUEST:
            get_response = await client.get(
                f"/api/employer-profiles/user/{user_id2}", headers=headers2
            )
            if get_response.status_code != HTTP_OK:
                pytest.skip(
                    f"Failed to fetch existing employer profile: {get_response.status_code}"
                )

        # Second employer creates a job
        job_response = await client.post(
            "/api/jobs",
            headers=headers2,
            json={
                "title": "Financial Analyst",
                "company": "Another Company",
                "description": "Finance role",
                "location": "Miami, FL",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        if job_response.status_code != HTTP_CREATED:
            pytest.skip("Failed to create job")
        job_id = job_response.json()["id"]

        # Job seeker applies
        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Finance background",
            },
        )
        if app_response.status_code != HTTP_CREATED:
            pytest.skip("Failed to create application")
        app_id = app_response.json()["id"]

        # First employer tries to update second employer's application
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        response = await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Rejected"},
        )

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_can_update_any_application(
        self,
        client: AsyncClient,
        admin_token: str,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Admins can update any application."""
        if not admin_token:
            pytest.skip("Admin token required for testing")

        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job and application
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Project Manager",
                "company": "Test Company",
                "description": "PM role",
                "location": "Denver, CO",
                "job_type": "Full-time",
                "experience_required": "5+ years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "PM experience",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Admin updates the application
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.put(
            f"/api/applications/{app_id}",
            headers=admin_headers,
            json={"status": "Interview Scheduled", "notes": "Admin update"},
        )

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["status"] == "Interview Scheduled"

    @pytest.mark.asyncio
    async def test_public_cannot_update_application(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot update applications."""
        response = await client.put(
            "/api/applications/fake_id",
            json={"notes": "Test"},
        )

        assert response.status_code in [HTTP_UNAUTHORIZED, HTTP_FORBIDDEN]

    # ============================================================================
    # DELETE APPLICATION TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_job_seeker_can_withdraw_own_application(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Job seekers can withdraw their own applications."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job and apply
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Data Engineer",
                "company": "Test Company",
                "description": "Data pipelines",
                "location": "Austin, TX",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Data engineering skills",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Withdraw application
        response = await client.delete(f"/api/applications/{app_id}", headers=js_headers)

        assert response.status_code == HTTP_NO_CONTENT

        # Verify it's gone
        get_response = await client.get(f"/api/applications/{app_id}", headers=js_headers)
        assert get_response.status_code == HTTP_NOT_FOUND

    @pytest.mark.asyncio
    async def test_employer_cannot_delete_application(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Employers cannot delete applications (only applicant can withdraw)."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job and apply
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Mobile Developer",
                "company": "Test Company",
                "description": "iOS/Android",
                "location": "Portland, OR",
                "job_type": "Full-time",
                "experience_required": "2-4 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Mobile app portfolio",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Employer tries to delete
        response = await client.delete(f"/api/applications/{app_id}", headers=emp_headers)

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_can_delete_any_application(
        self,
        client: AsyncClient,
        admin_token: str,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Admins can delete any application."""
        if not admin_token:
            pytest.skip("Admin token required for testing")

        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job and application
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Network Engineer",
                "company": "Test Company",
                "description": "Networking",
                "location": "Phoenix, AZ",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Network certifications",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Admin deletes the application
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.delete(f"/api/applications/{app_id}", headers=admin_headers)

        assert response.status_code == HTTP_NO_CONTENT

    @pytest.mark.asyncio
    async def test_cannot_withdraw_other_application(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
        create_temp_user: Callable[[str, str], Awaitable[tuple[str | None, str | None]]],
    ) -> None:
        """Job seekers cannot withdraw other job seekers' applications."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create another job seeker
        token2, user_id2 = await create_temp_user("job_seeker", "temp.jobseeker.delete@test.com")
        if not token2:
            pytest.skip("Failed to create temporary job seeker user")

        # Create profile for second job seeker
        headers2 = {"Authorization": f"Bearer {token2}"}
        profile_response = await client.post(
            "/api/job-seeker-profiles",
            headers=headers2,
            json={
                "user_id": user_id2,
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "temp.jobseeker.delete@test.com",
                "skills": ["C++"],
            },
        )
        if profile_response.status_code not in [HTTP_CREATED, HTTP_BAD_REQUEST]:
            pytest.skip(f"Failed to create temp profile: {profile_response.status_code}")

        # If profile already exists, get it
        if profile_response.status_code == HTTP_BAD_REQUEST:
            get_response = await client.get(
                f"/api/job-seeker-profiles/user/{user_id2}", headers=headers2
            )
            if get_response.status_code != HTTP_OK:
                pytest.skip(f"Failed to fetch existing profile: {get_response.status_code}")
            profile_id2 = get_response.json()["id"]
        else:
            profile_id2 = profile_response.json()["id"]

        # Create job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "C++ Developer",
                "company": "Test Company",
                "description": "Systems programming",
                "location": "San Jose, CA",
                "job_type": "Full-time",
                "experience_required": "5+ years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Second job seeker applies
        app_response = await client.post(
            "/api/applications",
            headers=headers2,
            json={
                "job_id": job_id,
                "job_seeker_id": profile_id2,
                "notes": "C++ expert",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # First job seeker tries to delete second job seeker's application
        js_headers = {"Authorization": f"Bearer {js_token}"}
        response = await client.delete(f"/api/applications/{app_id}", headers=js_headers)

        assert response.status_code == HTTP_FORBIDDEN

    @pytest.mark.asyncio
    async def test_public_cannot_delete_application(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot delete applications."""
        response = await client.delete("/api/applications/fake_id")

        assert response.status_code in [HTTP_UNAUTHORIZED, HTTP_FORBIDDEN]

    # ============================================================================
    # USER WORKFLOW TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_complete_application_lifecycle(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Complete workflow: Create → View → Update → Delete."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Employer creates job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Full Stack Developer",
                "company": "Test Company",
                "description": "Full stack role",
                "location": "Remote",
                "job_type": "Full-time",
                "experience_required": "3-5 years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Job seeker applies
        js_headers = {"Authorization": f"Bearer {js_token}"}
        create_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Full stack experience",
            },
        )
        assert create_response.status_code == HTTP_CREATED
        app_id = create_response.json()["id"]

        # View the application
        view_response = await client.get(f"/api/applications/{app_id}", headers=js_headers)
        assert view_response.status_code == HTTP_OK
        assert view_response.json()["status"] == "Application Submitted"

        # Update notes
        update_response = await client.put(
            f"/api/applications/{app_id}",
            headers=js_headers,
            json={"notes": "Updated: Added portfolio link"},
        )
        assert update_response.status_code == HTTP_OK
        assert "Updated: Added portfolio link" in update_response.json()["notes"]

        # Withdraw application
        delete_response = await client.delete(f"/api/applications/{app_id}", headers=js_headers)
        assert delete_response.status_code == HTTP_NO_CONTENT

    @pytest.mark.asyncio
    async def test_employer_application_management_workflow(
        self,
        client: AsyncClient,
        job_seeker_with_profile: tuple[str, str, str],
        employer_with_profile: tuple[str, str, str],
    ) -> None:
        """Employer workflow: View applications → Update status."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, _ = employer_with_profile

        # Create job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Senior Engineer",
                "company": "Test Company",
                "description": "Lead engineer role",
                "location": "San Francisco, CA",
                "job_type": "Full-time",
                "experience_required": "7+ years",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Job seeker applies
        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js_profile_id,
                "notes": "Senior level experience",
            },
        )
        assert app_response.status_code == HTTP_CREATED
        app_id = app_response.json()["id"]

        # Employer views applications to their jobs
        list_response = await client.get("/api/applications", headers=emp_headers)
        assert list_response.status_code == HTTP_OK
        applications = list_response.json()
        assert len(applications) >= 1

        # Employer views specific application
        view_response = await client.get(f"/api/applications/{app_id}", headers=emp_headers)
        assert view_response.status_code == HTTP_OK

        # Employer updates status: Under Review
        update1 = await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Under Review", "next_step": "Technical interview"},
        )
        assert update1.status_code == HTTP_OK
        assert update1.json()["status"] == "Under Review"

        # Employer updates status: Interview Scheduled
        update2 = await client.put(
            f"/api/applications/{app_id}",
            headers=emp_headers,
            json={"status": "Interview Scheduled"},
        )
        assert update2.status_code == HTTP_OK
        assert update2.json()["status"] == "Interview Scheduled"
