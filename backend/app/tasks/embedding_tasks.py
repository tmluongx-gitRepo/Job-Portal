"""Celery tasks for embedding ingestion."""

from __future__ import annotations

import asyncio

from app.ai.indexers import (
    build_candidate_document,
    build_job_document,
    upsert_candidate_embedding,
    upsert_job_embedding,
)
from app.database import get_job_seeker_profiles_collection, get_jobs_collection

try:
    from celery import shared_task  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency

    def shared_task(func):  # type: ignore[misc,no-untyped-def]
        return func


async def _process_jobs(job_ids: list[str] | None = None) -> None:
    collection = get_jobs_collection()
    cursor = collection.find({"_id": {"$in": job_ids}} if job_ids else {})
    async for job in cursor:  # type: ignore[async-for]
        job_id = str(job["_id"])
        document = build_job_document(job)
        metadata = {
            "title": job.get("title"),
            "location": job.get("location"),
            "industry": job.get("industry"),
            "skills": job.get("skills_required", []),
        }
        await upsert_job_embedding(job_id=job_id, text=document, metadata=metadata)


async def _process_candidates(candidate_ids: list[str] | None = None) -> None:
    collection = get_job_seeker_profiles_collection()
    cursor = collection.find({"_id": {"$in": candidate_ids}} if candidate_ids else {})
    async for profile in cursor:  # type: ignore[async-for]
        candidate_id = str(profile["_id"])
        document = build_candidate_document(profile)
        metadata = {
            "location": profile.get("location"),
            "skills": profile.get("skills", []),
            "experience_years": profile.get("experience_years"),
        }
        await upsert_candidate_embedding(
            candidate_id=candidate_id, text=document, metadata=metadata
        )


@shared_task(name="ingest_job_embeddings")  # type: ignore[misc]
def ingest_job_embeddings(job_ids: list[str] | None = None) -> None:
    asyncio.run(_process_jobs(job_ids))


@shared_task(name="ingest_candidate_embeddings")  # type: ignore[misc]
def ingest_candidate_embeddings(candidate_ids: list[str] | None = None) -> None:
    asyncio.run(_process_candidates(candidate_ids))
