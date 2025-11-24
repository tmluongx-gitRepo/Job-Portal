"""Retrieval helpers for chat agents."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Mapping, Sequence
from typing import Any

from app.ai.chat.instrumentation import logger
from app.ai.chat.tools.scoring import calculate_candidate_matches, calculate_job_matches
from app.config import settings
from app.database import get_collection, get_job_seeker_profiles_collection, get_jobs_collection

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
    except Exception as exc:  # pragma: no cover - rely on fallback
        log_payload = {
            "collection": collection_name,
            "operation": "get_collection",
        }
        if settings.DEBUG:
            logger.exception("chat.retriever.collection_failure", extra=log_payload)
        else:
            log_payload["error"] = str(exc)
            logger.warning("chat.retriever.collection_failure", extra=log_payload)
        return []

    def _query() -> list[dict[str, Any]]:
        result = collection.query(
            query_texts=[query_text],
            where=where,
            n_results=limit,
        )

        if not isinstance(result, dict):
            logger.warning(
                "chat.retriever.vector_malformed",
                extra={"collection": collection_name, "detail": "non-dict result"},
            )
            return []

        metadatas_raw = result.get("metadatas")
        distances_raw = result.get("distances")
        ids_raw = result.get("ids")

        if not isinstance(metadatas_raw, list) or not metadatas_raw:
            logger.warning(
                "chat.retriever.vector_malformed",
                extra={"collection": collection_name, "detail": "missing metadatas"},
            )
            return []

        metadatas_seq = metadatas_raw[0] if metadatas_raw else []
        if not isinstance(metadatas_seq, list):
            logger.warning(
                "chat.retriever.vector_malformed",
                extra={"collection": collection_name, "detail": "metadatas not list"},
            )
            return []

        distances_seq = (
            distances_raw[0] if isinstance(distances_raw, list) and distances_raw else []
        )
        ids_seq = ids_raw[0] if isinstance(ids_raw, list) and ids_raw else []

        matches: list[dict[str, Any]] = []
        for idx, metadata in enumerate(metadatas_seq):
            item: dict[str, Any] = dict(metadata) if isinstance(metadata, dict) else {}
            item.setdefault("id", ids_seq[idx] if idx < len(ids_seq) else None)
            item.setdefault("source", "vector")
            distance = distances_seq[idx] if idx < len(distances_seq) else None
            if distance is not None:
                try:
                    item["match_score"] = max(0.0, 1 - float(distance))
                except (TypeError, ValueError):
                    item["match_score"] = 0.0
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
    except Exception as exc:  # pragma: no cover - rely on fallback
        log_payload = {
            "collection": collection_name,
            "operation": "query",
        }
        if settings.DEBUG:
            logger.exception("chat.retriever.query_failure", extra=log_payload)
        else:
            log_payload["error"] = str(exc)
            logger.warning("chat.retriever.query_failure", extra=log_payload)
        return []


async def fetch_job_matches_for_user(
    *, user_context: dict, limit: int = 3, query: str | None = None
) -> Sequence[dict[str, Any]]:
    """Fetch candidate job matches for a job seeker."""

    resume_summary = _sanitize_query_text(
        user_context.get("resume_summary"), fallback="job recommendations"
    )
    if query:
        resume_summary = (f"{resume_summary} {query}").strip()
    resume_features = _extract_resume_features(user_context)
    resume_features = dict(resume_features)

    query_skill_hints = _extract_skill_hints(query)
    if query_skill_hints:
        existing_skills = _coerce_string_set(resume_features.get("skills"))
        merged = sorted(existing_skills | query_skill_hints)
        resume_features["skills"] = merged
    skill_filters = _coerce_string_set(resume_features.get("skills"))

    search_limit = max(limit * 2, limit)
    matches = await _query_chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        query_text=resume_summary,
        limit=search_limit,
        where={"kind": "job"},
    )
    if matches:
        if skill_filters:
            matches = [match for match in matches if _record_matches_keywords(match, skill_filters)]
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

    fallback = await _metadata_job_matches(
        features=resume_features,
        limit=limit,
        skill_filters=skill_filters,
    )
    if fallback:
        logger.info(
            "chat.retriever.job_matches",
            extra={"stage": "metadata", "count": len(fallback)},
        )
        return fallback

    catalog = await _catalog_job_matches(limit=limit)
    if catalog:
        logger.info(
            "chat.retriever.job_matches",
            extra={"stage": "catalog", "count": len(catalog)},
        )
        return catalog

    logger.info("chat.retriever.job_matches", extra={"stage": "empty", "count": 0})
    return []


async def fetch_candidate_matches_for_employer(
    *, user_context: dict, limit: int = 3
) -> Sequence[dict[str, Any]]:
    """Fetch candidate matches for an employer's current openings."""

    job_summary = _sanitize_query_text(
        user_context.get("job_summary"), fallback="candidate recommendations"
    )
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
    if fallback:
        logger.info(
            "chat.retriever.candidate_matches",
            extra={"stage": "metadata", "count": len(fallback)},
        )
        return fallback

    catalog = await _catalog_candidate_matches(limit=limit)
    if catalog:
        logger.info(
            "chat.retriever.candidate_matches",
            extra={"stage": "catalog", "count": len(catalog)},
        )
        return catalog

    logger.info("chat.retriever.candidate_matches", extra={"stage": "empty", "count": 0})
    return []


def _extract_resume_features(user_context: Mapping[str, Any]) -> dict[str, Any]:
    return _extract_features(user_context, _RESUME_FEATURE_KEYS)


def _extract_job_features(user_context: Mapping[str, Any]) -> dict[str, Any]:
    return _extract_features(user_context, _EMPLOYER_FEATURE_KEYS)


def _extract_features(  # noqa: PLR0912
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
                cleaned = _normalise_feature_value(candidate)
                if cleaned is None:
                    continue
                value = cleaned
                break
            if value is not None:
                break
        if isinstance(value, list):
            features[feature_name] = value
        elif value is None:
            features[feature_name] = []
        else:
            features[feature_name] = value

    return features


def _sanitize_query_text(value: Any, *, fallback: str, max_length: int = 1024) -> str:
    """Ensure query text is a safe, bounded string."""

    if isinstance(value, str):
        text = value.strip()
        if text:
            return text[:max_length]
    return fallback


def _normalise_feature_value(
    value: Any, *, max_items: int = 20, max_length: int = 256
) -> Any | None:
    """Restrict feature values to safe primitives the scoring layer expects."""

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        return text[:max_length]
    if isinstance(value, int | float | bool):
        return value
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        cleaned_list: list[Any] = []
        for item in value[:max_items]:
            normalised = _normalise_feature_value(item, max_items=max_items, max_length=max_length)
            if normalised is not None:
                cleaned_list.append(normalised)
        return cleaned_list if cleaned_list else None
    return None


_SKILL_TRIGGER_PATTERN = re.compile(r"skills?\s*[:=-]?\s*(.+)", re.IGNORECASE)
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "for",
    "with",
    "please",
    "filter",
    "skills",
    "skill",
    "by",
    "show",
    "me",
    "can",
    "you",
    "find",
}


def _extract_skill_hints(query: str | None) -> set[str]:
    if not query:
        return set()
    match = _SKILL_TRIGGER_PATTERN.search(query)
    candidate_text = match.group(1) if match else query
    return {
        token
        for token in _TOKEN_PATTERN.findall(candidate_text.lower())
        if token and token not in _STOPWORDS
    }


def _coerce_string_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        cleaned = value.strip()
        return {cleaned.lower()} if cleaned else set()
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray | str):
        result: set[str] = set()
        for item in value:
            if isinstance(item, str) and item.strip():
                result.add(item.strip().lower())
        return result
    return set()


def _record_matches_keywords(record: Mapping[str, Any], keywords: set[str]) -> bool:
    if not keywords:
        return True
    haystack_parts: list[str] = []
    for key in (
        "label",
        "title",
        "company",
        "subtitle",
        "industry",
        "job_type",
    ):
        value = record.get(key)
        if isinstance(value, str):
            haystack_parts.append(value.lower())
    for key in ("skills", "skills_required"):
        value = record.get(key)
        if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray | str):
            haystack_parts.extend(str(item).lower() for item in value if item)
        elif isinstance(value, str):
            haystack_parts.append(value.lower())
    haystack = " ".join(haystack_parts)
    return all(keyword in haystack for keyword in keywords)


async def _metadata_job_matches(
    *,
    features: Mapping[str, Any],
    limit: int,
    skill_filters: set[str] | None,
) -> list[dict[str, Any]]:
    collection = get_jobs_collection()

    cursor = collection.find({"is_active": True}).limit(120)
    jobs: list[dict[str, Any]] = []

    try:
        async for doc in cursor:  # type: ignore[async-for]
            jobs.append(
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
    except Exception:  # pragma: no cover - defensive fallback
        return []

    if skill_filters:
        jobs = [job for job in jobs if _record_matches_keywords(job, skill_filters)]

    ranked = calculate_job_matches(resume_features=features, jobs=jobs)
    return ranked[:limit]


async def _metadata_candidate_matches(
    *, features: Mapping[str, Any], limit: int
) -> list[dict[str, Any]]:
    collection = get_job_seeker_profiles_collection()

    cursor = collection.find({}).limit(120)
    candidates: list[dict[str, Any]] = []

    try:
        async for doc in cursor:  # type: ignore[async-for]
            full_name = " ".join(
                filter(None, [doc.get("first_name"), doc.get("last_name")])
            ).strip()
            candidates.append(
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
    except Exception:  # pragma: no cover
        return []

    ranked = calculate_candidate_matches(job_features=features, candidates=candidates)
    return ranked[:limit]


async def _catalog_job_matches(limit: int) -> list[dict[str, Any]]:
    collection = get_jobs_collection()
    cursor = collection.find({"is_active": True}).sort("created_at", -1).limit(max(limit, 5))

    catalog: list[dict[str, Any]] = []
    try:
        async for doc in cursor:  # type: ignore[async-for]
            catalog.append(
                {
                    "job_id": str(doc.get("_id")),
                    "title": doc.get("title"),
                    "company": doc.get("company"),
                    "location": doc.get("location"),
                    "job_type": doc.get("job_type"),
                    "skills_required": doc.get("skills_required", []),
                    "experience_required": doc.get("experience_required"),
                    "match_score": 0.35,
                    "source": "catalog",
                }
            )
    except Exception:  # pragma: no cover - catalog fallback best effort
        return []

    return catalog[:limit]


async def _catalog_candidate_matches(limit: int) -> list[dict[str, Any]]:
    collection = get_job_seeker_profiles_collection()
    cursor = collection.find({}).sort("created_at", -1).limit(max(limit, 5))

    catalog: list[dict[str, Any]] = []
    try:
        async for doc in cursor:  # type: ignore[async-for]
            full_name = " ".join(
                filter(None, [doc.get("first_name"), doc.get("last_name")])
            ).strip()
            catalog.append(
                {
                    "candidate_id": str(doc.get("_id")),
                    "name": full_name or "Candidate",
                    "location": doc.get("location"),
                    "skills": doc.get("skills", []),
                    "experience_years": doc.get("experience_years"),
                    "industry": doc.get("industry"),
                    "match_score": 0.35,
                    "source": "catalog",
                }
            )
    except Exception:  # pragma: no cover - catalog fallback best effort
        return []

    return catalog[:limit]
