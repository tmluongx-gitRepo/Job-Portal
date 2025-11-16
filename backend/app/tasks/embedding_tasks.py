"""Celery tasks and async helpers for embedding ingestion."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from typing import Any

from bson import ObjectId

from app.ai.indexers import (
    build_candidate_document,
    build_job_document,
    delete_candidate_embedding,
    delete_job_embedding,
    upsert_candidate_embedding,
    upsert_job_embedding,
)
from app.database import get_job_seeker_profiles_collection, get_jobs_collection

LOGGER = logging.getLogger("app.tasks.embedding")

try:
    from celery import shared_task  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency

    def shared_task(*_args, **_kwargs):  # type: ignore[misc,no-untyped-def]
        if _args and callable(_args[0]):
            return _args[0]

        def decorator(func):  # type: ignore[no-untyped-def]
            return func

        return decorator


async def process_jobs(job_ids: Sequence[str] | None = None) -> None:
    collection = get_jobs_collection()
    object_ids = _coerce_object_ids(job_ids)
    cursor = collection.find({"_id": {"$in": object_ids}} if object_ids else {})
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


async def process_candidates(candidate_ids: Sequence[str] | None = None) -> None:
    collection = get_job_seeker_profiles_collection()
    object_ids = _coerce_object_ids(candidate_ids)
    cursor = collection.find({"_id": {"$in": object_ids}} if object_ids else {})
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
    asyncio.run(process_jobs(job_ids))


@shared_task(name="ingest_candidate_embeddings")  # type: ignore[misc]
def ingest_candidate_embeddings(candidate_ids: list[str] | None = None) -> None:
    asyncio.run(process_candidates(candidate_ids))


def _coerce_object_ids(values: Sequence[str] | None) -> list[ObjectId]:
    object_ids: list[ObjectId] = []
    if not values:
        return object_ids
    for value in values:
        try:
            object_ids.append(ObjectId(value))
        except Exception:  # pragma: no cover - defensive logging
            LOGGER.warning("embedding.invalid_object_id", extra={"value": value})
    return object_ids


async def remove_jobs(job_ids: Sequence[str]) -> None:
    for job_id in job_ids:
        await delete_job_embedding(job_id)


async def remove_candidates(candidate_ids: Sequence[str]) -> None:
    for candidate_id in candidate_ids:
        await delete_candidate_embedding(candidate_id)


def register_embedding_periodic_tasks(celery_app: Any) -> None:
    """Configure Celery beat schedules for embedding backfills."""

    try:
        from celery.schedules import crontab  # type: ignore[import-not-found]
    except ImportError:  # pragma: no cover - optional dependency
        LOGGER.warning(
            "embedding.periodic_schedule_skipped",
            extra={"reason": "celery not installed"},
        )
        return

    celery_app.add_periodic_task(
        crontab(hour=2, minute=0),
        ingest_job_embeddings.s(),
        name="ingest-job-embeddings-daily",
    )
    celery_app.add_periodic_task(
        crontab(hour=2, minute=30),
        ingest_candidate_embeddings.s(),
        name="ingest-candidate-embeddings-daily",
    )
