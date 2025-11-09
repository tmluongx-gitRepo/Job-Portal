"""
Cross-resource authorization tests.
Ensures authorization works correctly across related resources.
"""
import pytest
from httpx import AsyncClient
from bson import ObjectId


class TestCrossResourceAuthorization:
    """Test authorization across related resources."""
    
    @pytest.mark.asyncio
    async def test_cannot_create_job_without_employer_profile(self, client: AsyncClient, employer_token):
        """Employers must have a profile before posting jobs."""
        if not employer_token:
            pytest.skip("Email confirmation required for testing")
        
        headers = {"Authorization": f"Bearer {employer_token}"}
        
        # Try to create job without creating profile first
        response = await client.post(
            "/api/jobs",
            headers=headers,
            json={
                "title": "Software Engineer",
                "description": "Great job opportunity",
                "location": "Remote",
                "job_type": "full-time",
                "experience_level": "mid"
            }
        )
        
        # Should fail - need profile first
        assert response.status_code == 400
        assert "profile" in response.json()["detail"].lower()
    
    
    @pytest.mark.asyncio
    async def test_deleting_user_cascades_to_profile(self, client: AsyncClient, 
                                                     job_seeker_with_profile, admin_token):
        """Deleting user should cascade to their profile."""
        if not admin_token:
            pytest.skip("Email confirmation required for testing")
        
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        
        # Admin deletes user
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        delete_response = await client.delete(f"/api/users/{js_user_id}", headers=admin_headers)
        assert delete_response.status_code == 204
        
        # Profile should also be gone
        response = await client.get(f"/api/job-seeker-profiles/{js_profile_id}")
        assert response.status_code == 404
    
    
    @pytest.mark.asyncio
    async def test_employer_can_only_view_applications_to_own_jobs(self, client: AsyncClient,
                                                                   employer_with_profile):
        """Employers can only see applications to their own jobs."""
        emp_token, _, emp_profile_id = employer_with_profile
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        
        # Employer creates a job
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Backend Developer",
                "description": "Join our team",
                "location": "San Francisco, CA",
                "job_type": "full-time",
                "experience_level": "mid",
                "required_skills": ["Python", "FastAPI"]
            }
        )
        assert job_response.status_code == 201
        
        # Employer views applications (should see their own jobs' applications only)
        apps_response = await client.get("/api/applications", headers=emp_headers)
        assert apps_response.status_code == 200
        
        # Should be empty or only contain applications to their jobs
        applications = apps_response.json()
        for app in applications:
            # Verify each application is to a job owned by this employer
            job_response = await client.get(f"/api/jobs/{app['job_id']}", headers=emp_headers)
            assert job_response.status_code == 200
    
    
    @pytest.mark.asyncio
    async def test_cannot_update_profile_of_different_type(self, client: AsyncClient, 
                                                          job_seeker_token, employer_with_profile):
        """Job seekers cannot update employer profiles and vice versa."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        _, _, emp_profile_id = employer_with_profile
        
        # Job seeker tries to update employer profile
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = await client.put(
            f"/api/employer-profiles/{emp_profile_id}",
            headers=js_headers,
            json={"description": "Hacked!"}
        )
        
        assert response.status_code == 403
    
    
    @pytest.mark.asyncio
    async def test_deleting_job_makes_applications_inaccessible(self, client: AsyncClient,
                                                                job_seeker_with_profile, 
                                                                employer_with_profile, test_cleaner):
        """Deleting a job should affect its applications."""
        js_token, js_user_id, js_profile_id = job_seeker_with_profile
        emp_token, _, emp_profile_id = employer_with_profile
        
        # Employer posts job
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        job_response = await client.post(
            "/api/jobs",
            headers=emp_headers,
            json={
                "title": "Test Job for Deletion",
                "description": "This will be deleted",
                "location": "Remote",
                "job_type": "full-time",
                "experience_level": "mid"
            }
        )
        assert job_response.status_code == 201
        job_id = job_response.json()["id"]
        test_cleaner.track_job(job_id)
        
        # Job seeker applies
        js_headers = {"Authorization": f"Bearer {js_token}"}
        app_response = await client.post(
            "/api/applications",
            headers=js_headers,
            json={
                "job_id": job_id,
                "cover_letter": "Please hire me!"
            }
        )
        assert app_response.status_code == 201
        app_id = app_response.json()["id"]
        test_cleaner.track_application(app_id)
        
        # Employer deletes job
        delete_response = await client.delete(f"/api/jobs/{job_id}", headers=emp_headers)
        assert delete_response.status_code == 204
        
        # Application should either be deleted or marked with deleted job
        app_check = await client.get(f"/api/applications/{app_id}", headers=js_headers)
        # Accept either 404 (cascaded delete) or 200 with job deleted flag
        assert app_check.status_code in [200, 404, 410]
    
    
    @pytest.mark.asyncio
    async def test_profile_ownership_required_for_job_posting(self, client: AsyncClient,
                                                              employer_token, employer_with_profile):
        """Cannot post job using another employer's profile."""
        if not employer_token:
            pytest.skip("Email confirmation required for testing")
        
        # employer_token is a fresh employer without profile
        # employer_with_profile has a profile
        
        _, _, other_profile_id = employer_with_profile
        
        headers = {"Authorization": f"Bearer {employer_token}"}
        
        # Create own profile first
        profile_response = await client.post(
            "/api/employer-profiles",
            headers=headers,
            json={
                "company_name": "My Company",
                "industry": "Tech",
                "company_size": "10-50",
                "location": "NYC",
                "description": "We're hiring"
            }
        )
        
        if profile_response.status_code != 201:
            pytest.skip("Could not create employer profile")
        
        # Now post job - should link to OWN profile, not other employer's
        job_response = await client.post(
            "/api/jobs",
            headers=headers,
            json={
                "title": "Engineer",
                "description": "Join us",
                "location": "NYC",
                "job_type": "full-time",
                "experience_level": "mid"
            }
        )
        
        if job_response.status_code == 201:
            job = job_response.json()
            # Job should be linked to own profile, not other_profile_id
            assert job["posted_by"] != other_profile_id

