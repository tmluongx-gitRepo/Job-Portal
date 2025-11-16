"""Chroma indexing helpers for chat agents."""

from __future__ import annotations

from app.ai.chat.instrumentation import logger
from app.ai.embeddings import generate_embedding
from app.config import settings
from app.database import get_collection


async def upsert_job_embedding(*, job_id: str, text: str, metadata: dict[str, object]) -> None:
    # Chroma's Python client is sync-only today; revisit if async APIs are added upstream.
    collection = get_collection(settings.CHROMA_COLLECTION_NAME)
    vector = await generate_embedding(text)
    if not vector:
        logger.warning(
            "embeddings.vector_missing",
            extra={"kind": "job", "job_id": job_id},
        )
    collection.upsert(
        ids=[f"job::{job_id}"],
        documents=[text],
        metadatas=[{"kind": "job", "job_id": job_id, **metadata}],
        embeddings=[vector] if vector else None,
    )


async def upsert_candidate_embedding(
    *, candidate_id: str, text: str, metadata: dict[str, object]
) -> None:
    # Chroma's Python client is sync-only today; revisit if async APIs are added upstream.
    collection = get_collection(settings.CHROMA_COLLECTION_NAME)
    vector = await generate_embedding(text)
    if not vector:
        logger.warning(
            "embeddings.vector_missing",
            extra={"kind": "candidate", "candidate_id": candidate_id},
        )
    collection.upsert(
        ids=[f"candidate::{candidate_id}"],
        documents=[text],
        metadatas=[{"kind": "candidate", "candidate_id": candidate_id, **metadata}],
        embeddings=[vector] if vector else None,
    )


def build_job_document(job: dict[str, object]) -> str:
    parts: list[str] = []
    for key in ["title", "company", "location", "description", "responsibilities", "requirements"]:
        value = job.get(key)
        if not value:
            continue
        if isinstance(value, list):
            parts.append("\n".join(map(str, value)))
        else:
            parts.append(str(value))
    return "\n\n".join(parts)


async def delete_job_embedding(job_id: str) -> None:
    """Remove a job embedding from Chroma if it exists."""

    collection = get_collection(settings.CHROMA_COLLECTION_NAME)
    collection.delete(ids=[f"job::{job_id}"])


async def delete_candidate_embedding(candidate_id: str) -> None:
    """Remove a candidate embedding from Chroma if it exists."""

    collection = get_collection(settings.CHROMA_COLLECTION_NAME)
    collection.delete(ids=[f"candidate::{candidate_id}"])


def build_candidate_document(profile: dict[str, object]) -> str:
    parts: list[str] = []
    for key in [
        "first_name",
        "last_name",
        "location",
        "bio",
        "skills",
        "experience_years",
        "work_history",
    ]:
        value = profile.get(key)
        if not value:
            continue
        if isinstance(value, list):
            parts.append("\n".join(map(str, value)))
        else:
            parts.append(str(value))
    return "\n\n".join(parts)
