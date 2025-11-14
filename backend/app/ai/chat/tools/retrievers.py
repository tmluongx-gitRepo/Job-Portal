"""Retrieval helpers for chat agents."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from typing import Any

from app.ai.chat.instrumentation import logger
from app.ai.chat.tools.scoring import calculate_candidate_matches, calculate_job_matches
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

_RESUME_FEATURE_KEYS: dict[str, Sequence[str]] = {
    "skills": ("skills", "resume_skills", "top_skills"),
    "location": ("location", "resume_location", "city"),
    "industry": ("industry", "target_industry"),
    "experience_years": ("experience_years", "years_experience"),
}

_EMPLOYER_FEATURE_KEYS: dict[str, Sequence[str]] = {
    "skills": ("job_skills", "skills_required", "skills"),
    "location": ("job_location", "location"),
    "industry": ("job_industry", "industry"),
    "experience_years": (
        "job_experience_years",
        "experience_years",
        "minimum_experience_years",
    ),
}


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
            item.setdefault("source", "vector")
            distance = distances[idx] if idx < len(distances) else None
            if distance is not None:
                item["match_score"] = max(0.0, 1 - float(distance))
            matches.append(item)
        logger.info(
            "chat.retriever.vector_results",
            extra={
                "collection": collection_name,
                "result_count": len(matches),
            },
        )
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
    resume_features = _extract_resume_features(user_context)

    search_limit = max(limit * 2, limit)
    matches = await _query_chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        query_text=resume_summary,
        limit=search_limit,
        where={"kind": "job"},
    )
    if matches:
        logger.info(
            "chat.retriever.job_matches",
            extra={
                "stage": "vector",
                "count": len(matches),
            },
        )
        ranked = calculate_job_matches(
            resume_features=resume_features,
            jobs=[dict(match) for match in matches],
        )
        meaningful = [item for item in ranked if item.get("match_score", 0) > 0]
        if meaningful:
            return meaningful[:limit]
        if ranked:
            return ranked[:limit]

    fallback = await _metadata_job_matches(features=resume_features, limit=limit)
    logger.info(
        "chat.retriever.job_matches",
        extra={
            "stage": "metadata" if fallback else "fallback",
            "count": len(fallback) if fallback else len(FALLBACK_JOB_MATCHES[:limit]),
        },
    )
    return fallback if fallback else FALLBACK_JOB_MATCHES[:limit]


async def fetch_candidate_matches_for_employer(
    *, user_context: dict, limit: int = 3
) -> Sequence[dict[str, Any]]:
    """Fetch candidate matches for an employer's current openings."""

    job_summary = user_context.get("job_summary") or "candidate recommendations"
    job_features = _extract_job_features(user_context)

    search_limit = max(limit * 2, limit)
    matches = await _query_chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        query_text=job_summary,
        limit=search_limit,
        where={"kind": "candidate"},
    )
    if matches:
        logger.info(
            "chat.retriever.candidate_matches",
            extra={
                "stage": "vector",
                "count": len(matches),
            },
        )
        ranked = calculate_candidate_matches(
            job_features=job_features,
            candidates=[dict(match) for match in matches],
        )
        meaningful = [item for item in ranked if item.get("match_score", 0) > 0]
        if meaningful:
            return meaningful[:limit]
        if ranked:
            return ranked[:limit]

    fallback = await _metadata_candidate_matches(features=job_features, limit=limit)
    logger.info(
        "chat.retriever.candidate_matches",
        extra={
            "stage": "metadata" if fallback else "fallback",
            "count": len(fallback) if fallback else len(FALLBACK_CANDIDATE_MATCHES[:limit]),
        },
    )
    return fallback if fallback else FALLBACK_CANDIDATE_MATCHES[:limit]


def _extract_resume_features(user_context: Mapping[str, Any]) -> dict[str, Any]:
    return _extract_features(user_context, _RESUME_FEATURE_KEYS)


def _extract_job_features(user_context: Mapping[str, Any]) -> dict[str, Any]:
    return _extract_features(user_context, _EMPLOYER_FEATURE_KEYS)


def _extract_features(
    user_context: Mapping[str, Any], keys_map: Mapping[str, Sequence[str]]
) -> dict[str, Any]:
    features: dict[str, Any] = {}
    sources: list[Mapping[str, Any]] = []

    if isinstance(user_context, Mapping):
        sources.append(user_context)
        metadata = user_context.get("metadata")
        if isinstance(metadata, Mapping):
            sources.append(metadata)
            for metadata_value in metadata.values():
                if isinstance(metadata_value, Mapping):
                    sources.append(metadata_value)

    for feature_name, candidate_keys in keys_map.items():
        value: Any | None = None
        for source in sources:
            for key in candidate_keys:
                if key not in source:
                    continue
                candidate = source[key]
                if candidate in (None, "", [], {}):
                    continue
                value = candidate
                break
            if value is not None:
                break
        features[feature_name] = value

    return features


async def _metadata_job_matches(*, features: Mapping[str, Any], limit: int) -> list[dict[str, Any]]:
    collection = get_jobs_collection()

    def _query() -> list[dict[str, Any]]:
        cursor = collection.find({"is_active": True}).limit(120)
        results: list[dict[str, Any]] = []
        for doc in cursor:  # type: ignore[attr-defined]
            results.append(
                {
                    "job_id": str(doc.get("_id")),
                    "title": doc.get("title"),
                    "company": doc.get("company"),
                    "location": doc.get("location"),
                    "industry": doc.get("industry"),
                    "job_type": doc.get("job_type"),
                    "skills_required": doc.get("skills_required", []),
                    "experience_required": doc.get("experience_required"),
                    "source": "metadata",
                }
            )
        return results

    try:
        jobs = await asyncio.to_thread(_query)
    except Exception:  # pragma: no cover
        return []

    ranked = calculate_job_matches(resume_features=features, jobs=jobs)
    return ranked[:limit]


async def _metadata_candidate_matches(
    *, features: Mapping[str, Any], limit: int
) -> list[dict[str, Any]]:
    collection = get_job_seeker_profiles_collection()

    def _query() -> list[dict[str, Any]]:
        cursor = collection.find({}).limit(120)
        results: list[dict[str, Any]] = []
        for doc in cursor:  # type: ignore[attr-defined]
            full_name = " ".join(
                filter(None, [doc.get("first_name"), doc.get("last_name")])
            ).strip()
            results.append(
                {
                    "candidate_id": str(doc.get("_id")),
                    "name": full_name or None,
                    "skills": doc.get("skills", []),
                    "location": doc.get("location"),
                    "industry": doc.get("industry"),
                    "experience_years": doc.get("experience_years"),
                    "work_history": doc.get("work_history"),
                    "source": "metadata",
                }
            )
        return results

    try:
        candidates = await asyncio.to_thread(_query)
    except Exception:  # pragma: no cover
        return []

    ranked = calculate_candidate_matches(job_features=features, candidates=candidates)
    return ranked[:limit]
