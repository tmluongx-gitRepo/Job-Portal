"""Retrieval helpers for chat agents."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

from app.config import settings
from app.database import get_collection, get_job_seeker_profiles_collection, get_jobs_collection

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
    if matches:
        return matches[:limit]

    # Metadata fallback: rank jobs by simple heuristics (skills overlap, location)
    weights = _extract_weights_from_user_context(user_context)
    fallback = await _metadata_job_matches(weights=weights, limit=limit)
    return fallback if fallback else FALLBACK_JOB_MATCHES[:limit]


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
    if matches:
        return matches[:limit]

    weights = _extract_weights_from_user_context(user_context)
    fallback = await _metadata_candidate_matches(weights=weights, limit=limit)
    return fallback if fallback else FALLBACK_CANDIDATE_MATCHES[:limit]


def _extract_weights_from_user_context(user_context: dict) -> dict[str, Any]:
    return {
        "skills": set(map(str.lower, user_context.get("skills", []))),
        "location": str(user_context.get("location", "")).lower(),
        "industry": str(user_context.get("industry", "")).lower(),
    }


async def _metadata_job_matches(*, weights: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    collection = get_jobs_collection()

    def _score_job(job: dict[str, Any]) -> dict[str, Any] | None:
        skills = set(map(str.lower, job.get("skills_required", [])))
        score = 0.0
        if weights["skills"] and skills:
            score += len(weights["skills"] & skills) / max(len(skills), 1)
        if weights["location"] and str(job.get("location", "")).lower().startswith(
            weights["location"]
        ):
            score += 0.25
        if weights["industry"] and str(job.get("industry", "")).lower() == weights["industry"]:
            score += 0.15

        if score == 0:
            return None

        return {
            "job_id": str(job.get("_id")),
            "title": job.get("title"),
            "match_score": round(min(score, 0.95), 2),
        }

    def _query() -> list[dict[str, Any]]:
        cursor = collection.find({"is_active": True}).limit(100)
        matches = []
        for doc in cursor:  # type: ignore[attr-defined]
            scored = _score_job(doc)
            if scored:
                matches.append(scored)
        matches.sort(key=lambda item: item["match_score"], reverse=True)
        return matches[:limit]

    try:
        return await asyncio.to_thread(_query)
    except Exception:  # pragma: no cover
        return []


async def _metadata_candidate_matches(
    *, weights: dict[str, Any], limit: int
) -> list[dict[str, Any]]:
    collection = get_job_seeker_profiles_collection()

    def _score_candidate(profile: dict[str, Any]) -> dict[str, Any] | None:
        skills = set(map(str.lower, profile.get("skills", [])))
        score = 0.0
        if weights["skills"] and skills:
            score += len(weights["skills"] & skills) / max(len(weights["skills"]), 1)
        if weights["location"] and str(profile.get("location", "")).lower().startswith(
            weights["location"]
        ):
            score += 0.25
        if weights["industry"]:
            experience = profile.get("work_history", [])
            if any(weights["industry"] in str(entry).lower() for entry in experience):
                score += 0.15

        if score == 0:
            return None

        return {
            "candidate_id": str(profile.get("_id")),
            "name": " ".join(filter(None, [profile.get("first_name"), profile.get("last_name")])),
            "match_score": round(min(score, 0.95), 2),
        }

    def _query() -> list[dict[str, Any]]:
        cursor = collection.find({}).limit(100)
        matches = []
        for doc in cursor:  # type: ignore[attr-defined]
            scored = _score_candidate(doc)
            if scored:
                matches.append(scored)
        matches.sort(key=lambda item: item["match_score"], reverse=True)
        return matches[:limit]

    try:
        return await asyncio.to_thread(_query)
    except Exception:  # pragma: no cover
        return []
