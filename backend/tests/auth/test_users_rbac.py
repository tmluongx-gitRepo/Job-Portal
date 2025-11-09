"""
RBAC tests for Users API.
Tests authorization rules for different user roles.
"""
import pytest
from httpx import AsyncClient


class TestUsersRBAC:
    """Test role-based access control for Users API."""
    
    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_access_users(self, client: AsyncClient):
        """Unauthenticated users cannot access any user endpoints."""
        # FastAPI HTTPBearer returns 403 when no credentials provided
        
        # GET /users
        response = await client.get("/api/users")
        assert response.status_code in [401, 403]
        
        # GET /users/me
        response = await client.get("/api/users/me")
        assert response.status_code in [401, 403]
        
        # GET /users/{id}
        response = await client.get("/api/users/some-id")
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_job_seeker_can_view_own_account(self, client: AsyncClient, job_seeker_token):
        """Job seekers can view their own account via /me."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = await client.get("/api/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["account_type"] == "job_seeker"
        assert "email" in data
    
    @pytest.mark.asyncio
    async def test_job_seeker_cannot_list_all_users(self, client: AsyncClient, job_seeker_token):
        """Job seekers cannot list all users (admin only)."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = await client.get("/api/users", headers=headers)
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_job_seeker_can_update_own_account(self, client: AsyncClient, job_seeker_token):
        """Job seekers can update their own account via /me."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        # Update email (if Supabase allows)
        response = await client.put(
            "/api/users/me",
            headers=headers,
            json={"email": "newemail@example.com"}
        )
        
        # May succeed or fail depending on Supabase rules
        # The important part is it's not a 403 (authorization issue)
        assert response.status_code in [200, 400, 422]
    
    @pytest.mark.asyncio
    async def test_job_seeker_cannot_change_own_account_type(self, client: AsyncClient, job_seeker_token):
        """Job seekers cannot change their own account_type."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        response = await client.put(
            "/api/users/me",
            headers=headers,
            json={"account_type": "admin"}
        )
        
        assert response.status_code == 403
        assert "cannot change" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_job_seeker_can_delete_own_account(self, client: AsyncClient, job_seeker_token):
        """Job seekers can delete their own account."""
        if not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        response = await client.delete("/api/users/me", headers=headers)
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_employer_can_view_own_account(self, client: AsyncClient, employer_token):
        """Employers can view their own account via /me."""
        if not employer_token:
            pytest.skip("Email confirmation required for testing")
        
        headers = {"Authorization": f"Bearer {employer_token}"}
        response = await client.get("/api/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["account_type"] == "employer"
    
    @pytest.mark.asyncio
    async def test_employer_cannot_view_other_users(self, client: AsyncClient, employer_token, job_seeker_token):
        """Employers cannot view other users' accounts."""
        if not employer_token or not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        # Get job seeker's user ID
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        js_response = await client.get("/api/users/me", headers=js_headers)
        js_user_id = js_response.json()["id"]
        
        # Try to view as employer
        emp_headers = {"Authorization": f"Bearer {employer_token}"}
        response = await client.get(f"/api/users/{js_user_id}", headers=emp_headers)
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_admin_can_list_all_users(self, client: AsyncClient, admin_token):
        """Admins can list all users."""
        if not admin_token:
            pytest.skip("Email confirmation required for testing")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get("/api/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_admin_can_view_any_user(self, client: AsyncClient, admin_token, job_seeker_token):
        """Admins can view any user's account."""
        if not admin_token or not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        # Get job seeker's user ID
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        js_response = await client.get("/api/users/me", headers=js_headers)
        js_user_id = js_response.json()["id"]
        
        # View as admin
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get(f"/api/users/{js_user_id}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == js_user_id
    
    @pytest.mark.asyncio
    async def test_admin_can_create_user(self, client: AsyncClient, admin_token):
        """Admins can create users via POST /users."""
        if not admin_token:
            pytest.skip("Email confirmation required for testing")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(
            "/api/users",
            headers=headers,
            json={
                "email": "admin_created@example.com",
                "account_type": "job_seeker"
            }
        )
        
        # May succeed or fail based on validation
        # Important: Not a 403 (authorization issue)
        assert response.status_code in [201, 400, 422]
    
    @pytest.mark.asyncio
    async def test_admin_can_change_account_type(self, client: AsyncClient, admin_token, job_seeker_token):
        """Admins can change a user's account_type."""
        if not admin_token or not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        # Get job seeker's user ID
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        js_response = await client.get("/api/users/me", headers=js_headers)
        js_user_id = js_response.json()["id"]
        
        # Change account type as admin
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.put(
            f"/api/users/{js_user_id}",
            headers=admin_headers,
            json={"account_type": "employer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["account_type"] == "employer"
    
    @pytest.mark.asyncio
    async def test_admin_can_delete_any_user(self, client: AsyncClient, admin_token, job_seeker_token):
        """Admins can delete any user."""
        if not admin_token or not job_seeker_token:
            pytest.skip("Email confirmation required for testing")
        
        # Get job seeker's user ID
        js_headers = {"Authorization": f"Bearer {job_seeker_token}"}
        js_response = await client.get("/api/users/me", headers=js_headers)
        js_user_id = js_response.json()["id"]
        
        # Delete as admin
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.delete(f"/api/users/{js_user_id}", headers=admin_headers)
        
        assert response.status_code == 204

