"""Integration-style tests ensuring embedding hooks are scheduled."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import Any

import pytest
from httpx import AsyncClient

from app.api.routes import resumes as resumes_route
from app.auth.dependencies import get_current_user, require_employer, require_job_seeker
from app.crud import employer_profile as employer_profile_crud
from app.crud import job as job_crud
from app.crud import resume as resume_crud
from app.main import app


@pytest.mark.asyncio
async def test_job_creation_triggers_embedding(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    employer_id = "employer-test"
    jobs_store: dict[str, dict[str, Any]] = {}

    async def fake_create_job(
        job_data: dict[str, object], posted_by: str | None = None
    ) -> dict[str, Any]:
        job_id = f"job-{len(jobs_store) + 1}" if posted_by else "job-unknown"
        doc = {
            "_id": job_id,
            "title": job_data.get("title", "Untitled"),
            "company": job_data.get("company", "Company"),
            "description": job_data.get("description", ""),
            "location": job_data.get("location", "Remote"),
            "job_type": job_data.get("job_type", ""),
            "experience_required": job_data.get("experience_required"),
            "is_active": True,
            "posted_by": posted_by,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        jobs_store[job_id] = doc
        return doc

    async def fake_get_profile_by_user_id(_user_id: str) -> dict[str, str]:
        return {"_id": "profile"}

    async def fake_require_employer() -> dict[str, str]:
        return {"id": employer_id}

    monkeypatch.setattr(job_crud, "create_job", fake_create_job)
    monkeypatch.setattr(
        employer_profile_crud, "get_profile_by_user_id", fake_get_profile_by_user_id
    )
    app.dependency_overrides[require_employer] = fake_require_employer

    scheduled_ids: list[list[str] | None] = []
    created_tasks: list[asyncio.Task[Any]] = []

    async def fake_process_jobs(job_ids: list[str] | None) -> None:
        scheduled_ids.append(job_ids)

    original_create_task = asyncio.create_task

    def fake_create_task(coro: Awaitable[Any]) -> asyncio.Task[Any]:
        task: asyncio.Task[Any] = original_create_task(coro)  # type: ignore[arg-type]
        created_tasks.append(task)
        return task

    monkeypatch.setattr("app.api.routes.jobs.process_jobs", fake_process_jobs)
    monkeypatch.setattr("app.api.routes.jobs.asyncio.create_task", fake_create_task)

    response = await client.post(
        "/api/jobs",
        json={
            "title": "Streaming Engineer",
            "company": "Test Co",
            "description": "Work on realtime systems",
            "location": "Remote",
            "job_type": "Full-time",
            "experience_required": "5+ years",
        },
    )

    assert response.status_code == 201

    if created_tasks:
        await asyncio.gather(*created_tasks)

    created_job_id = response.json()["id"]
    assert any(job_ids and created_job_id in job_ids for job_ids in scheduled_ids)

    app.dependency_overrides.pop(require_employer, None)


@pytest.mark.asyncio
async def test_job_update_triggers_embedding(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    employer_id = "employer-test"
    jobs_store: dict[str, dict[str, Any]] = {}

    async def fake_create_job(
        job_data: dict[str, object], posted_by: str | None = None
    ) -> dict[str, Any]:
        job_id = f"job-{len(jobs_store) + 1}"
        doc = {
            "_id": job_id,
            "title": job_data.get("title", "Untitled"),
            "company": job_data.get("company", "Company"),
            "description": job_data.get("description", ""),
            "location": job_data.get("location", "Remote"),
            "job_type": job_data.get("job_type", ""),
            "experience_required": job_data.get("experience_required"),
            "is_active": True,
            "posted_by": posted_by,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        jobs_store[job_id] = doc
        return doc

    async def fake_get_job_by_id(job_id: str) -> dict[str, Any] | None:
        doc = jobs_store.get(job_id)
        if doc is None:
            return None
        return {**doc}

    async def fake_update_job(job_id: str, update_data: dict[str, Any]) -> dict[str, Any] | None:
        doc = jobs_store.get(job_id)
        if doc is None:
            return None
        doc.update(update_data)
        doc["updated_at"] = "2024-01-02T00:00:00Z"
        return {**doc}

    async def fake_get_profile_by_user_id(_user_id: str) -> dict[str, str]:
        return {"_id": "profile"}

    async def fake_require_employer() -> dict[str, str]:
        return {"id": employer_id}

    async def fake_current_user() -> dict[str, str]:
        return {"id": employer_id, "account_type": "employer"}

    monkeypatch.setattr(job_crud, "create_job", fake_create_job)
    monkeypatch.setattr(job_crud, "get_job_by_id", fake_get_job_by_id)
    monkeypatch.setattr(job_crud, "update_job", fake_update_job)
    monkeypatch.setattr(
        employer_profile_crud, "get_profile_by_user_id", fake_get_profile_by_user_id
    )
    app.dependency_overrides[require_employer] = fake_require_employer
    app.dependency_overrides[get_current_user] = fake_current_user

    create_response = await client.post(
        "/api/jobs",
        json={
            "title": "Original",
            "company": "Test Co",
            "description": "Original",
            "location": "Remote",
            "job_type": "Full-time",
            "experience_required": "3 years",
        },
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["id"]

    scheduled_ids: list[list[str] | None] = []
    created_tasks: list[asyncio.Task[Any]] = []

    async def fake_process_jobs(job_ids: list[str] | None) -> None:
        scheduled_ids.append(job_ids)

    original_create_task = asyncio.create_task

    def fake_create_task(coro: Awaitable[Any]) -> asyncio.Task[Any]:
        task: asyncio.Task[Any] = original_create_task(coro)  # type: ignore[arg-type]
        created_tasks.append(task)
        return task

    monkeypatch.setattr("app.api.routes.jobs.process_jobs", fake_process_jobs)
    monkeypatch.setattr("app.api.routes.jobs.asyncio.create_task", fake_create_task)

    update_response = await client.put(
        f"/api/jobs/{job_id}",
        json={"description": "Updated description"},
    )

    assert update_response.status_code == 200

    if created_tasks:
        await asyncio.gather(*created_tasks)

    assert any(job_ids and job_id in job_ids for job_ids in scheduled_ids)

    app.dependency_overrides.pop(require_employer, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_job_delete_triggers_cleanup(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    employer_id = "employer-test"
    jobs_store: dict[str, dict[str, Any]] = {}

    async def fake_create_job(
        job_data: dict[str, object], posted_by: str | None = None
    ) -> dict[str, Any]:
        job_id = f"job-{len(jobs_store) + 1}"
        doc = {
            "_id": job_id,
            "title": job_data.get("title", "Untitled"),
            "company": job_data.get("company", "Company"),
            "description": job_data.get("description", ""),
            "location": job_data.get("location", "Remote"),
            "job_type": job_data.get("job_type", ""),
            "is_active": True,
            "posted_by": posted_by,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        jobs_store[job_id] = doc
        return doc

    async def fake_get_job_by_id(job_id: str) -> dict[str, Any] | None:
        doc = jobs_store.get(job_id)
        if doc is None:
            return None
        return {**doc}

    async def fake_delete_job(job_id: str) -> bool:
        return jobs_store.pop(job_id, None) is not None

    async def fake_get_profile_by_user_id(_user_id: str) -> dict[str, str]:
        return {"_id": "profile"}

    async def fake_require_employer() -> dict[str, str]:
        return {"id": employer_id}

    async def fake_current_user() -> dict[str, str]:
        return {"id": employer_id, "account_type": "employer"}

    monkeypatch.setattr(job_crud, "create_job", fake_create_job)
    monkeypatch.setattr(job_crud, "get_job_by_id", fake_get_job_by_id)
    monkeypatch.setattr(job_crud, "delete_job", fake_delete_job)
    monkeypatch.setattr(
        employer_profile_crud, "get_profile_by_user_id", fake_get_profile_by_user_id
    )
    app.dependency_overrides[require_employer] = fake_require_employer
    app.dependency_overrides[get_current_user] = fake_current_user

    create_response = await client.post(
        "/api/jobs",
        json={
            "title": "Temp",
            "company": "Test",
            "description": "Delete me",
            "location": "Remote",
            "job_type": "Contract",
        },
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["id"]

    removed_ids: list[list[str] | None] = []
    created_tasks: list[asyncio.Task[Any]] = []

    async def fake_remove_jobs(job_ids: list[str] | None) -> None:
        removed_ids.append(job_ids)

    original_create_task = asyncio.create_task

    def fake_create_task(coro: Awaitable[Any]) -> asyncio.Task[Any]:
        task: asyncio.Task[Any] = original_create_task(coro)  # type: ignore[arg-type]
        created_tasks.append(task)
        return task

    monkeypatch.setattr("app.api.routes.jobs.remove_jobs", fake_remove_jobs)
    monkeypatch.setattr("app.api.routes.jobs.asyncio.create_task", fake_create_task)

    delete_response = await client.delete(f"/api/jobs/{job_id}")
    assert delete_response.status_code == 204

    if created_tasks:
        await asyncio.gather(*created_tasks)

    assert any(job_ids and job_id in job_ids for job_ids in removed_ids)

    app.dependency_overrides.pop(require_employer, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_resume_upload_triggers_candidate_embedding(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate_id = "candidate-test"

    async def fake_require_job_seeker() -> dict[str, str]:
        return {"id": candidate_id}

    app.dependency_overrides[require_job_seeker] = fake_require_job_seeker

    class FakeDropboxService:
        def upload_file(self, file_content: bytes, user_id: str) -> str:  # noqa: ARG002
            return f"/resumes/{user_id}.pdf"

        def delete_file(self, dropbox_path: str) -> bool:  # noqa: ARG002
            return True

    async def fake_create_or_update_resume(**kwargs: Any) -> dict[str, Any]:
        return {
            "_id": "resume-1",
            "job_seeker_id": kwargs["job_seeker_id"],
            "original_filename": kwargs["original_filename"],
            "dropbox_path": kwargs["dropbox_path"],
            "content_type": kwargs["content_type"],
            "uploaded_at": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

    scheduled_ids: list[list[str] | None] = []
    created_tasks: list[asyncio.Task[Any]] = []

    async def fake_process_candidates(candidate_ids: list[str] | None) -> None:
        scheduled_ids.append(candidate_ids)

    original_create_task = asyncio.create_task

    def fake_create_task(coro: Awaitable[Any]) -> asyncio.Task[Any]:
        task: asyncio.Task[Any] = original_create_task(coro)  # type: ignore[arg-type]
        created_tasks.append(task)
        return task

    monkeypatch.setattr("app.api.routes.resumes.get_dropbox_service", lambda: FakeDropboxService())
    monkeypatch.setattr(
        "app.api.routes.resumes.resume_crud.create_or_update_resume", fake_create_or_update_resume
    )
    monkeypatch.setattr("app.api.routes.resumes.process_candidates", fake_process_candidates)
    monkeypatch.setattr("app.api.routes.resumes.asyncio.create_task", fake_create_task)

    files = {"file": ("resume.pdf", b"dummy content", "application/pdf")}

    response = await client.post("/api/resumes", files=files)
    assert response.status_code == 201

    if created_tasks:
        await asyncio.gather(*created_tasks)

    assert any(c_ids and candidate_id in c_ids for c_ids in scheduled_ids)

    app.dependency_overrides.pop(require_job_seeker, None)


@pytest.mark.asyncio
async def test_resume_delete_triggers_candidate_cleanup(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate_id = "candidate-delete"
    app.dependency_overrides[require_job_seeker] = lambda: {"id": candidate_id}

    class FakeDropboxService:
        def delete_file(self, dropbox_path: str) -> bool:  # noqa: ARG002
            return True

    async def fake_get_resume_by_job_seeker(_user_id: str) -> dict[str, Any] | None:
        return {
            "_id": "resume-1",
            "job_seeker_id": candidate_id,
            "dropbox_path": "/resumes/candidate-delete.pdf",
        }

    async def fake_delete_resume(_user_id: str) -> bool:
        return True

    removed_ids: list[list[str] | None] = []
    created_tasks: list[asyncio.Task[Any]] = []

    async def fake_remove_candidates(candidate_ids: list[str] | None) -> None:
        removed_ids.append(candidate_ids)

    original_create_task = asyncio.create_task

    def fake_create_task(coro: Awaitable[Any]) -> asyncio.Task[Any]:
        task: asyncio.Task[Any] = original_create_task(coro)  # type: ignore[arg-type]
        created_tasks.append(task)
        return task

    monkeypatch.setattr(resume_crud, "get_resume_by_job_seeker", fake_get_resume_by_job_seeker)
    monkeypatch.setattr(resume_crud, "delete_resume", fake_delete_resume)
    monkeypatch.setattr(resumes_route, "get_dropbox_service", lambda: FakeDropboxService())
    monkeypatch.setattr(resumes_route, "remove_candidates", fake_remove_candidates)
    monkeypatch.setattr("app.api.routes.resumes.asyncio.create_task", fake_create_task)

    response = await client.delete("/api/resumes/me")
    assert response.status_code == 204

    if created_tasks:
        await asyncio.gather(*created_tasks)

    assert any(candidate_id in ids for ids in removed_ids if ids)

    app.dependency_overrides.pop(require_job_seeker, None)
