"""Matching score utilities for jobs and candidates."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

_NUMERIC_PATTERN = re.compile(r"(\d+(?:\.\d+)?)")


def calculate_job_matches(
    *, resume_features: Mapping[str, object], jobs: Sequence[Mapping[str, object]]
) -> list[dict[str, Any]]:
    """Return jobs ranked by relevance for a job seeker.

    The function blends the vector similarity score coming from Chroma (stored on
    the `match_score` field) with lightweight metadata heuristics. If no metadata
    is available we fall back to the vector score, and if no vector score exists
    we solely rely on the metadata heuristics. The output is sorted by the final
    `match_score` in descending order and includes a `score_breakdown` field so the
    caller can surface additional context to the UI if desired.
    """

    resume_skills = _normalise_skills(resume_features.get("skills"))
    resume_location = _normalise_text(resume_features.get("location"))
    resume_industry = _normalise_text(resume_features.get("industry"))
    resume_experience = _parse_years(resume_features.get("experience_years"))

    ranked: list[dict[str, Any]] = []
    for job in jobs:
        item = dict(job)

        vector_score = _clamp(_safe_float(item.get("match_score")) or 0.0)
        job_skills = _normalise_skills(item.get("skills") or item.get("skills_required"))
        job_location = _normalise_text(item.get("location"))
        job_industry = _normalise_text(item.get("industry"))
        job_experience = _parse_years(
            item.get("experience_required") or item.get("min_experience_years")
        )

        components = _collect_metadata_components(
            (
                "skills_overlap",
                _skill_overlap(resume_skills, job_skills),
                0.6,
            ),
            (
                "location_match",
                _location_score(resume_location, job_location),
                0.2,
            ),
            (
                "industry_match",
                _industry_score(resume_industry, job_industry),
                0.15,
            ),
            (
                "experience_alignment",
                _experience_alignment(resume_experience, job_experience),
                0.05,
            ),
        )

        metadata_score, breakdown = _combine_components(components)

        final_score = _blend_scores(vector_score, metadata_score, bool(components))

        item["vector_score"] = round(vector_score, 3)
        item["match_score"] = round(final_score, 3)
        if breakdown:
            item["score_breakdown"] = breakdown
        ranked.append(item)

    ranked.sort(key=lambda entry: entry.get("match_score", 0.0), reverse=True)
    return ranked


def calculate_candidate_matches(
    *, job_features: Mapping[str, object], candidates: Sequence[Mapping[str, object]]
) -> list[dict[str, Any]]:
    """Return candidates ranked by relevance for an employer."""

    job_skills = _normalise_skills(
        job_features.get("skills")
        or job_features.get("skills_required")
        or job_features.get("job_skills")
    )
    job_location = _normalise_text(job_features.get("location") or job_features.get("job_location"))
    job_industry = _normalise_text(job_features.get("industry") or job_features.get("job_industry"))
    job_experience = _parse_years(
        job_features.get("experience_years")
        or job_features.get("job_experience_years")
        or job_features.get("minimum_experience_years")
    )

    ranked: list[dict[str, Any]] = []
    for profile in candidates:
        item = dict(profile)
        vector_score = _clamp(_safe_float(item.get("match_score")) or 0.0)

        candidate_skills = _normalise_skills(item.get("skills"))
        candidate_location = _normalise_text(item.get("location"))
        candidate_industry = _normalise_text(item.get("industry"))
        candidate_experience = _parse_years(item.get("experience_years"))

        components = _collect_metadata_components(
            (
                "skills_overlap",
                _skill_overlap(job_skills, candidate_skills),
                0.6,
            ),
            (
                "location_match",
                _location_score(job_location, candidate_location),
                0.2,
            ),
            (
                "industry_match",
                _industry_score(job_industry, candidate_industry),
                0.15,
            ),
            (
                "experience_alignment",
                _experience_alignment(job_experience, candidate_experience, favour_surplus=True),
                0.05,
            ),
        )

        metadata_score, breakdown = _combine_components(components)
        final_score = _blend_scores(vector_score, metadata_score, bool(components))

        item["vector_score"] = round(vector_score, 3)
        item["match_score"] = round(final_score, 3)
        if breakdown:
            item["score_breakdown"] = breakdown
        ranked.append(item)

    ranked.sort(key=lambda entry: entry.get("match_score", 0.0), reverse=True)
    return ranked


def _collect_metadata_components(
    *components: tuple[str, float | None, float],
) -> list[tuple[str, float, float]]:
    """Return metadata scoring components after filtering zero-weight entries."""

    collected: list[tuple[str, float, float]] = []
    for name, score, weight in components:
        if weight <= 0 or score is None:
            continue
        collected.append((name, _clamp(score), weight))
    return collected


def _combine_components(
    components: list[tuple[str, float, float]],
) -> tuple[float, dict[str, float]]:
    """Return the combined metadata score and a readable breakdown."""

    if not components:
        return 0.0, {}

    total_weight = sum(weight for _, _, weight in components)
    if total_weight <= 0:
        return 0.0, {}

    weighted_score = sum(score * weight for _, score, weight in components) / total_weight
    breakdown = {name: round(score, 3) for name, score, _ in components}
    return _clamp(weighted_score), breakdown


def _blend_scores(vector_score: float, metadata_score: float, has_metadata: bool) -> float:
    """Blend vector and metadata scores with sensible defaults."""

    if vector_score <= 0 and not has_metadata:
        return 0.0
    if vector_score <= 0:
        return metadata_score
    if not has_metadata:
        return vector_score
    return _clamp(vector_score * 0.65 + metadata_score * 0.35)


def _skill_overlap(a: set[str], b: set[str]) -> float | None:
    if not a or not b:
        return None
    overlap = a & b
    if not overlap:
        return 0.0
    seeker_ratio = len(overlap) / max(len(a), 1)
    target_ratio = len(overlap) / max(len(b), 1)
    return _clamp((seeker_ratio + target_ratio) / 2)


def _location_score(reference: str, candidate: str) -> float | None:
    if not reference or not candidate:
        return None
    if candidate == reference:
        return 1.0
    if reference in candidate or candidate in reference:
        return 0.6
    return 0.0


def _industry_score(reference: str, candidate: str) -> float | None:
    if not reference or not candidate:
        return None
    if candidate == reference:
        return 1.0
    if reference in candidate or candidate in reference:
        return 0.5
    return 0.0


def _experience_alignment(
    baseline_years: float | None,
    comparison_years: float | None,
    *,
    favour_surplus: bool = False,
) -> float | None:
    if baseline_years is None or comparison_years is None:
        return None

    delta = comparison_years - baseline_years
    if delta >= 2:  # noqa: PLR2004
        return 1.0 if favour_surplus else 0.85
    if delta >= 0:
        return 0.85 if favour_surplus else 1.0
    if delta >= -1:
        return 0.6
    if delta >= -2:  # noqa: PLR2004
        return 0.4
    return 0.0


def _normalise_skills(value: Any) -> set[str]:
    skills: set[str] = set()
    if value is None:
        return skills
    if isinstance(value, str):
        parts = [part.strip() for part in value.replace(";", ",").split(",")]
        return {part.lower() for part in parts if part}
    try:
        for item in value:  # type: ignore[iteration-over-annotation]
            text = str(item).strip().lower()
            if text:
                skills.add(text)
    except TypeError:
        text = str(value).strip().lower()
        if text:
            skills.add(text)
    return skills


def _normalise_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _parse_years(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return number
    text = str(value)
    match = _NUMERIC_PATTERN.search(text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:  # pragma: no cover - defensive
            return None
    return None


def _safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
