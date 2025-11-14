"""Chroma indexing helpers for chat agents."""

from __future__ import annotations

from app.ai.embeddings import generate_embedding
from app.config import settings
from app.database import get_collection


async def upsert_job_embedding(*, job_id: str, text: str, metadata: dict[str, object]) -> None:
    collection = get_collection(settings.CHROMA_COLLECTION_NAME)
    vector = await generate_embedding(text)
    collection.upsert(
        ids=[f"job::{job_id}"],
        documents=[text],
        metadatas=[{"kind": "job", "job_id": job_id, **metadata}],
        embeddings=[vector] if vector else None,
    )


async def upsert_candidate_embedding(
    *, candidate_id: str, text: str, metadata: dict[str, object]
) -> None:
    collection = get_collection(settings.CHROMA_COLLECTION_NAME)
    vector = await generate_embedding(text)
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
