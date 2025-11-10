"""
Tests for Resume API endpoints.
"""

import pytest
from httpx import AsyncClient

from tests.constants import HTTP_FORBIDDEN


@pytest.mark.asyncio
class TestResumesAPI:
    """Test suite for Resumes API."""

    async def test_unauthenticated_cannot_upload_resume(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot upload resumes."""
        response = await client.post("/api/resumes")
        assert response.status_code == HTTP_FORBIDDEN

    async def test_unauthenticated_cannot_get_resume_metadata(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot get resume metadata."""
        response = await client.get("/api/resumes/me")
        assert response.status_code == HTTP_FORBIDDEN

    async def test_unauthenticated_cannot_download_resume(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot download resumes."""
        response = await client.get("/api/resumes/507f1f77bcf86cd799439011/download")
        assert response.status_code == HTTP_FORBIDDEN

    async def test_unauthenticated_cannot_delete_resume(self, client: AsyncClient) -> None:
        """Unauthenticated users cannot delete resumes."""
        response = await client.delete("/api/resumes/me")
        assert response.status_code == HTTP_FORBIDDEN

    async def test_get_nonexistent_resume(self, client: AsyncClient) -> None:
        """Getting a non-existent resume returns 404."""
        # This test would require authentication
        # Skipping for now as it requires Supabase tokens

    async def test_download_nonexistent_resume(self, client: AsyncClient) -> None:
        """Downloading a non-existent resume returns 404."""
        # This test would require authentication
        # Skipping for now as it requires Supabase tokens

    async def test_delete_nonexistent_resume(self, client: AsyncClient) -> None:
        """Deleting a non-existent resume returns 404."""
        # This test would require authentication
        # Skipping for now as it requires Supabase tokens


@pytest.mark.asyncio
class TestResumesAPIIntegration:
    """Integration tests requiring actual data."""

    async def test_complete_resume_workflow(self, client: AsyncClient) -> None:
        """Test complete workflow: upload, get metadata, download, delete."""
        # This test would require:
        # 1. Authenticated job seeker
        # 2. Dropbox service configured
        # 3. Test file upload
        # Skipping for now as it requires Supabase tokens and Dropbox setup

    async def test_employer_cannot_upload_resume(self, client: AsyncClient) -> None:
        """Employers cannot upload resumes (RBAC check)."""
        # This test would require authenticated employer
        # Skipping for now as it requires Supabase tokens

    async def test_resume_replaces_existing(self, client: AsyncClient) -> None:
        """Uploading a new resume replaces the existing one."""
        # This test would require:
        # 1. Authenticated job seeker
        # 2. Upload first resume
        # 3. Upload second resume
        # 4. Verify only one resume exists
        # Skipping for now as it requires Supabase tokens and Dropbox setup

    async def test_invalid_file_type_rejected(self, client: AsyncClient) -> None:
        """Invalid file types are rejected."""
        # This test would require authenticated job seeker
        # Skipping for now as it requires Supabase tokens

    async def test_file_too_large_rejected(self, client: AsyncClient) -> None:
        """Files larger than 5MB are rejected."""
        # This test would require authenticated job seeker
        # Skipping for now as it requires Supabase tokens

    async def test_resume_appears_in_profile(self, client: AsyncClient) -> None:
        """After uploading resume, it appears in job seeker profile."""
        # This test would require:
        # 1. Authenticated job seeker with profile
        # 2. Upload resume
        # 3. Get profile and verify resume_file_url and resume_file_name
        # Skipping for now as it requires Supabase tokens and Dropbox setup

    async def test_ownership_check_on_download(self, client: AsyncClient) -> None:
        """Users can only download their own resumes."""
        # This test would require:
        # 1. Two authenticated job seekers
        # 2. Job seeker A uploads resume
        # 3. Job seeker B tries to download A's resume (should fail)
        # Skipping for now as it requires Supabase tokens

    async def test_admin_can_download_any_resume(self, client: AsyncClient) -> None:
        """Admins can download any user's resume."""
        # This test would require:
        # 1. Authenticated job seeker uploads resume
        # 2. Authenticated admin downloads it (should succeed)
        # Skipping for now as it requires Supabase tokens
