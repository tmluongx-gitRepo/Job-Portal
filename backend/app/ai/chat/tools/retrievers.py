"""Retrieval helpers for chat agents."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

from app.config import settings
from app.database import get_collection

FALLBACK_JOB_MATCHES: list[dict[str, Any]] = [
    {
        "job_id": "sample-job-1",
        "title": "AI Solutions Engineer",
        "match_score": 0.82,
    },
    {
        "job_id": "sample-job-2",
        "title": "Data Scientist",
        "match_score": 0.78,
    },
    {
        "job_id": "sample-job-3",
        "title": "Backend Developer",
        "match_score": 0.74,
    },
]

FALLBACK_CANDIDATE_MATCHES: list[dict[str, Any]] = [
    {
        "candidate_id": "sample-candidate-1",
        "name": "Jordan Lee",
        "match_score": 0.84,
    },
    {
        "candidate_id": "sample-candidate-2",
        "name": "Casey Morgan",
        "match_score": 0.8,
    },
    {
        "candidate_id": "sample-candidate-3",
        "name": "Taylor Kim",
        "match_score": 0.77,
    },
]


async def _query_chroma(
    *,
    collection_name: str,
    query_text: str,
    limit: int,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    try:
        collection = get_collection(collection_name)
    except Exception:  # pragma: no cover - rely on fallback
        return []

    def _query() -> list[dict[str, Any]]:
        result = collection.query(
            query_texts=[query_text],
            where=where,
            n_results=limit,
        )
        metadatas = result.get("metadatas", [[]])[0] or []
        distances = result.get("distances", [[]])[0] or []
        ids = result.get("ids", [[]])[0] or []

        matches: list[dict[str, Any]] = []
        for idx, metadata in enumerate(metadatas):
            item = dict(metadata or {})
            item.setdefault("id", ids[idx] if idx < len(ids) else None)
            distance = distances[idx] if idx < len(distances) else None
            if distance is not None:
                item["match_score"] = max(0.0, 1 - float(distance))
            matches.append(item)
        return matches

    try:
        return await asyncio.to_thread(_query)
    except Exception:  # pragma: no cover - rely on fallback
        return []


async def fetch_job_matches_for_user(
    *, user_context: dict, limit: int = 3
) -> Sequence[dict[str, Any]]:
    """Fetch candidate job matches for a job seeker."""

    resume_summary = user_context.get("resume_summary") or "job recommendations"
    matches = await _query_chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        query_text=resume_summary,
        limit=limit,
        where={"kind": "job"},
    )
    return matches[:limit] if matches else FALLBACK_JOB_MATCHES[:limit]


async def fetch_candidate_matches_for_employer(
    *, user_context: dict, limit: int = 3
) -> Sequence[dict[str, Any]]:
    """Fetch candidate matches for an employer's current openings."""

    job_summary = user_context.get("job_summary") or "candidate recommendations"
    matches = await _query_chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        query_text=job_summary,
        limit=limit,
        where={"kind": "candidate"},
    )
    return matches[:limit] if matches else FALLBACK_CANDIDATE_MATCHES[:limit]
