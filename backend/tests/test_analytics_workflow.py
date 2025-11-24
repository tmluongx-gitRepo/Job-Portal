"""
E2E Workflow tests for Analytics endpoints.

Tests that analytics endpoints accurately reflect the actual state of:
- Jobs, applications, and interviews
- Status breakdowns and counts
- Recent activity calculations
- Interview metrics and ratings

This ensures the aggregation logic is correct and analytics match reality.
"""

import pytest
from httpx import AsyncClient

from tests.constants import HTTP_CREATED, HTTP_OK


class TestAnalyticsWorkflow:
    """Test analytics accuracy through complete workflows."""

    @pytest.mark.asyncio
    async def test_job_analytics_accuracy(  # noqa: PLR0915
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """Test that job analytics accurately reflect applications and interviews."""
        emp_token, emp_user_id, _ = employer_with_profile
        js1_token, _, js1_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js1_headers = {"Authorization": f"Bearer {js1_token}"}

        # Step 1: Employer creates a job
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Senior Python Developer",
                "company": "Analytics Test Co",
                "description": "Build analytics features",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Step 2: Get initial analytics (should be empty)
        analytics_response = await client.get(
            f"/api/jobs/{job_id}/analytics", headers=emp_headers
        )
        assert analytics_response.status_code == HTTP_OK
        analytics = analytics_response.json()
        assert analytics["total_applications"] == 0
        assert analytics["interviews_scheduled"] == 0
        assert analytics["interviews_completed"] == 0
        assert analytics["last_application_date"] is None

        # Step 3: Job seeker 1 applies
        app1_response = await client.post(
            "/api/applications",
            headers=js1_headers,
            json={
                "job_id": job_id,
                "job_seeker_id": js1_profile_id,
                "notes": "Very interested",
            },
        )
        assert app1_response.status_code == HTTP_CREATED
        app1_id = app1_response.json()["id"]

        # Step 4: Verify analytics updated (1 application)
        analytics_response = await client.get(
            f"/api/jobs/{job_id}/analytics", headers=emp_headers
        )
        assert analytics_response.status_code == HTTP_OK
        analytics = analytics_response.json()
        assert analytics["total_applications"] == 1
        assert analytics["applications_by_status"]["Application Submitted"] == 1
        assert analytics["recent_applications_count"] == 1
        assert analytics["last_application_date"] is not None

        # Step 5: Employer updates application 1 status to "Under Review"
        await client.put(
            f"/api/applications/{app1_id}",
            headers=emp_headers,
            json={"status": "Under Review"},
        )

        # Step 6: Verify analytics reflect status change
        analytics_response = await client.get(
            f"/api/jobs/{job_id}/analytics", headers=emp_headers
        )
        assert analytics_response.status_code == HTTP_OK
        analytics = analytics_response.json()
        assert analytics["total_applications"] == 1
        assert analytics["applications_by_status"]["Under Review"] == 1

        # Step 7: Schedule interview for application 1
        interview_response = await client.post(
            "/api/interviews",
            headers=emp_headers,
            json={
                "application_id": app1_id,
                "scheduled_date": "2025-12-01T10:00:00Z",
                "interview_type": "video",
                "duration_minutes": 60,
                "timezone": "UTC",
                "interviewer_email": "interviewer@test.com",
            },
        )
        assert interview_response.status_code == HTTP_CREATED
        interview_id = interview_response.json()["id"]

        # Step 8: Verify analytics include interview
        analytics_response = await client.get(
            f"/api/jobs/{job_id}/analytics", headers=emp_headers
        )
        assert analytics_response.status_code == HTTP_OK
        analytics = analytics_response.json()
        assert analytics["interviews_scheduled"] == 1
        assert analytics["interviews_completed"] == 0
        assert analytics["avg_interview_rating"] is None

        # Step 9: Complete interview with rating
        await client.post(
            f"/api/interviews/{interview_id}/complete",
            headers=emp_headers,
            json={"feedback": "Great candidate", "rating": 5},
        )

        # Step 10: Verify analytics reflect completed interview
        analytics_response = await client.get(
            f"/api/jobs/{job_id}/analytics", headers=emp_headers
        )
        assert analytics_response.status_code == HTTP_OK
        analytics = analytics_response.json()
        assert analytics["interviews_scheduled"] == 0  # No longer scheduled
        assert analytics["interviews_completed"] == 1
        assert analytics["avg_interview_rating"] == 5.0  # noqa: PLR2004

    @pytest.mark.asyncio
    async def test_employer_job_stats_accuracy(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """Test that employer job stats accurately reflect their job portfolio."""
        emp_token, emp_user_id, _ = employer_with_profile
        js_token, _, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # Step 1: Get initial stats (may have jobs from other tests)
        initial_stats_response = await client.get(
            f"/api/employer-profiles/user/{emp_user_id}/job-stats", headers=emp_headers
        )
        assert initial_stats_response.status_code == HTTP_OK
        initial_stats = initial_stats_response.json()
        initial_total_jobs = initial_stats["total_jobs"]
        initial_active_jobs = initial_stats["active_jobs"]
        initial_total_apps = initial_stats["total_applications_received"]

        # Step 2: Create 2 active jobs
        job1_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Backend Engineer",
                "company": "Test Co",
                "description": "Build APIs",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job1_response.status_code == HTTP_CREATED
        job1_id = job1_response.json()["id"]

        job2_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Frontend Engineer",
                "company": "Test Co",
                "description": "Build UIs",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job2_response.status_code == HTTP_CREATED
        job2_id = job2_response.json()["id"]

        # Step 3: Verify stats updated (2 more jobs)
        stats_response = await client.get(
            f"/api/employer-profiles/user/{emp_user_id}/job-stats", headers=emp_headers
        )
        assert stats_response.status_code == HTTP_OK
        stats = stats_response.json()
        assert stats["total_jobs"] == initial_total_jobs + 2
        assert stats["active_jobs"] == initial_active_jobs + 2
        assert stats["inactive_jobs"] == stats["total_jobs"] - stats["active_jobs"]

        # Step 4: Job seeker applies to both jobs
        await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job1_id,
                "job_seeker_id": js_profile_id,
                "notes": "Backend expert",
            },
        )
        await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job2_id,
                "job_seeker_id": js_profile_id,
                "notes": "Frontend expert",
            },
        )

        # Step 5: Verify application counts updated
        stats_response = await client.get(
            f"/api/employer-profiles/user/{emp_user_id}/job-stats", headers=emp_headers
        )
        assert stats_response.status_code == HTTP_OK
        stats = stats_response.json()
        assert stats["total_applications_received"] == initial_total_apps + 2
        assert stats["applications_this_week"] >= 2  # noqa: PLR2004

        # Step 6: Verify top jobs list structure
        assert isinstance(stats["top_jobs"], list)
        assert len(stats["top_jobs"]) <= 5  # noqa: PLR2004
        # Verify each top job has the expected structure
        for job in stats["top_jobs"]:
            assert "job_id" in job
            assert "title" in job
            assert "applications" in job
            assert "is_active" in job

        # Step 7: Deactivate job1
        await client.put(
            f"/api/jobs/{job1_id}", headers=emp_headers, json={"is_active": False}
        )

        # Step 8: Verify inactive job count increased
        stats_response = await client.get(
            f"/api/employer-profiles/user/{emp_user_id}/job-stats", headers=emp_headers
        )
        assert stats_response.status_code == HTTP_OK
        stats = stats_response.json()
        assert stats["active_jobs"] == initial_active_jobs + 1
        assert stats["inactive_jobs"] >= 1

    @pytest.mark.asyncio
    async def test_job_seeker_application_stats_accuracy(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """Test that job seeker application stats accurately reflect their application history."""
        emp_token, _, _ = employer_with_profile
        js_token, js_user_id, js_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js_headers = {"Authorization": f"Bearer {js_token}"}

        # Step 1: Get initial stats (may have applications from other tests)
        initial_stats_response = await client.get(
            f"/api/job-seeker-profiles/user/{js_user_id}/application-stats",
            headers=js_headers,
        )
        assert initial_stats_response.status_code == HTTP_OK
        initial_stats = initial_stats_response.json()
        initial_total_apps = initial_stats["total_applications"]

        # Step 2: Employer creates 2 jobs
        job1_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Data Scientist",
                "company": "Analytics Co",
                "description": "Analyze data",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job1_response.status_code == HTTP_CREATED
        job1_id = job1_response.json()["id"]

        job2_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "ML Engineer",
                "company": "AI Co",
                "description": "Build models",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job2_response.status_code == HTTP_CREATED
        job2_id = job2_response.json()["id"]

        # Step 3: Job seeker applies to both
        app1_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job1_id,
                "job_seeker_id": js_profile_id,
                "notes": "Data science expert",
            },
        )
        assert app1_response.status_code == HTTP_CREATED
        app1_id = app1_response.json()["id"]

        app2_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job2_id,
                "job_seeker_id": js_profile_id,
                "notes": "ML expert",
            },
        )
        assert app2_response.status_code == HTTP_CREATED

        # Step 4: Verify stats updated (2 more applications)
        stats_response = await client.get(
            f"/api/job-seeker-profiles/user/{js_user_id}/application-stats",
            headers=js_headers,
        )
        assert stats_response.status_code == HTTP_OK
        stats = stats_response.json()
        assert stats["total_applications"] == initial_total_apps + 2
        assert stats["applications_by_status"]["Application Submitted"] >= 2  # noqa: PLR2004
        assert stats["applications_this_week"] >= 2  # noqa: PLR2004

        # Step 5: Schedule interview for application 1
        interview_response = await client.post(
            "/api/interviews",
            headers=emp_headers,
            json={
                "application_id": app1_id,
                "scheduled_date": "2025-12-15T14:00:00Z",
                "interview_type": "technical",
                "duration_minutes": 90,
                "timezone": "UTC",
                "interviewer_email": "tech@test.com",
            },
        )
        assert interview_response.status_code == HTTP_CREATED
        interview_id = interview_response.json()["id"]

        # Step 6: Verify interview stats updated
        stats_response = await client.get(
            f"/api/job-seeker-profiles/user/{js_user_id}/application-stats",
            headers=js_headers,
        )
        assert stats_response.status_code == HTTP_OK
        stats = stats_response.json()
        assert stats["interviews_scheduled"] >= 1
        assert stats["interviews_completed"] >= 0

        # Step 7: Complete interview with rating
        await client.post(
            f"/api/interviews/{interview_id}/complete",
            headers=emp_headers,
            json={"feedback": "Strong technical skills", "rating": 4},
        )

        # Step 8: Verify completed interview stats
        stats_response = await client.get(
            f"/api/job-seeker-profiles/user/{js_user_id}/application-stats",
            headers=js_headers,
        )
        assert stats_response.status_code == HTTP_OK
        stats = stats_response.json()
        assert stats["interviews_completed"] >= 1
        # Job seeker can see their own rating
        assert stats["avg_interview_rating"] is not None
        assert stats["avg_interview_rating"] > 0

    @pytest.mark.asyncio
    async def test_analytics_with_status_changes(
        self,
        client: AsyncClient,
        employer_with_profile: tuple[str, str, str],
        job_seeker_with_profile: tuple[str, str, str],
    ) -> None:
        """Test analytics correctly reflect application status changes."""
        emp_token, _, _ = employer_with_profile
        js1_token, _, js1_profile_id = job_seeker_with_profile

        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        js1_headers = {"Authorization": f"Bearer {js1_token}"}

        # Create a job
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Full Stack Developer",
                "company": "Status Test",
                "description": "Test status changes",
                "location": "Remote",
                "job_type": "Full-time",
            },
        )
        assert job_response.status_code == HTTP_CREATED
        job_id = job_response.json()["id"]

        # Create application
        app1_response = await client.post(
            "/api/applications",
            headers=js1_headers,
            json={"job_id": job_id, "job_seeker_id": js1_profile_id, "notes": "App 1"},
        )
        assert app1_response.status_code == HTTP_CREATED
        app1_id = app1_response.json()["id"]

        # Update to "Under Review"
        await client.put(
            f"/api/applications/{app1_id}",
            headers=emp_headers,
            json={"status": "Under Review"},
        )

        # Verify analytics show correct status
        analytics_response = await client.get(
            f"/api/jobs/{job_id}/analytics", headers=emp_headers
        )
        assert analytics_response.status_code == HTTP_OK
        analytics = analytics_response.json()
        assert analytics["total_applications"] == 1
        assert analytics["applications_by_status"]["Under Review"] == 1
        assert "Application Submitted" not in analytics["applications_by_status"]

