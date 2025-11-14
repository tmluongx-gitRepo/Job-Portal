"""Helper utilities for chat orchestrator scaffolding."""

from __future__ import annotations

import math
from collections.abc import AsyncIterator, Mapping, Sequence
from typing import Any

from app.ai.chat.constants import ChatEventType

AUDIENCE_JOB_SEEKER = "job_seeker"
AUDIENCE_EMPLOYER = "employer"


async def emit_text(message: str) -> AsyncIterator[dict]:
    """Yield a single text event (non-streaming placeholder)."""
    yield {"type": ChatEventType.TOKEN.value, "data": {"text": message}}
    yield {"type": ChatEventType.COMPLETE.value, "data": {}}


def prepare_matches(
    matches: Sequence[Mapping[str, Any]] | Sequence[dict[str, Any]],
    *,
    audience: str,
) -> tuple[list[dict[str, Any]], str]:
    """Return normalised matches and a summary string for LLM prompts/UI."""

    normalised: list[dict[str, Any]] = []
    for index, match in enumerate(matches, start=1):
        normalised.append(_normalise_match(match, audience=audience, fallback_index=index))

    normalised.sort(key=lambda item: item.get("match_score", 0.0), reverse=True)

    summary = _render_summary(normalised)
    return normalised, summary


def _normalise_match(
    match: Mapping[str, Any], *, audience: str, fallback_index: int
) -> dict[str, Any]:
    identifier = _extract_identifier(match, fallback_index=fallback_index)
    label = _extract_label(match)

    subtitle = _build_subtitle(match, audience=audience)

    vector_score = _safe_float(match.get("vector_score"))
    score = _safe_float(match.get("match_score"))
    if score is None and vector_score is not None:
        score = vector_score
    score = _clamp(score) if score is not None else 0.0

    vector_score = _clamp(vector_score)

    breakdown = _normalise_breakdown(match.get("score_breakdown"))
    reasons = _top_reasons(breakdown)

    source = match.get("source")
    if not isinstance(source, str) or not source.strip():
        source = "vector" if vector_score is not None else "metadata"

    metadata = _extract_metadata(match, audience=audience)

    return {
        "id": identifier,
        "label": label or "Result",
        "subtitle": subtitle,
        "match_score": score,
        "vector_score": vector_score,
        "score_breakdown": breakdown,
        "reasons": reasons,
        "source": source,
        "metadata": metadata,
    }


def _extract_identifier(match: Mapping[str, Any], *, fallback_index: int) -> str:
    for key in ("id", "job_id", "candidate_id", "document_id"):
        value = match.get(key)
        if value is not None and value != "":
            return str(value)
    return f"match-{fallback_index}"


def _extract_label(match: Mapping[str, Any]) -> str:
    for key in ("title", "name", "job_title", "candidate_name"):
        value = match.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _build_subtitle(match: Mapping[str, Any], *, audience: str) -> str | None:
    parts: list[str] = []

    if audience == AUDIENCE_JOB_SEEKER:
        for key in ("company", "location"):
            value = match.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
    else:
        location = match.get("location") or match.get("city")
        if isinstance(location, str) and location.strip():
            parts.append(location.strip())
        experience = match.get("experience_years")
        if isinstance(experience, int | float):
            experience_value = float(experience)
            if experience_value.is_integer():
                parts.append(f"{int(experience_value)} yrs exp")
            else:
                parts.append(f"{experience_value:.1f} yrs exp")

    return " | ".join(parts) if parts else None


def _normalise_breakdown(breakdown: Any) -> dict[str, float]:
    if not isinstance(breakdown, Mapping):
        return {}
    result: dict[str, float] = {}
    for key, value in breakdown.items():
        score = _safe_float(value)
        if score is None:
            continue
        clamped_score = _clamp(score)
        if clamped_score is not None:
            result[key] = round(clamped_score, 3)
    return result


def _top_reasons(breakdown: Mapping[str, float]) -> list[str]:
    if not breakdown:
        return []
    items = sorted(breakdown.items(), key=lambda item: item[1], reverse=True)
    reasons: list[str] = []
    for name, value in items[:3]:
        label = name.replace("_", " ")
        percentage = int(round(value * 100))
        reasons.append(f"{label} {percentage}%")
    return reasons


def _extract_metadata(match: Mapping[str, Any], *, audience: str) -> dict[str, Any] | None:
    keys: tuple[str, ...]
    if audience == AUDIENCE_JOB_SEEKER:
        keys = (
            "job_id",
            "company",
            "location",
            "industry",
            "job_type",
            "skills",
            "skills_required",
        )
    else:
        keys = (
            "candidate_id",
            "location",
            "experience_years",
            "skills",
            "industry",
        )

    metadata: dict[str, Any] = {}
    for key in keys:
        if key in match:
            value = match[key]
            if value not in (None, "", [], {}):
                metadata[key] = value

    return metadata or None


def _render_summary(matches: Sequence[Mapping[str, Any]]) -> str:
    if not matches:
        return "No matches available yet."

    lines: list[str] = []
    for index, match in enumerate(matches, start=1):
        label = match.get("label") or "Result"
        subtitle = match.get("subtitle")
        score = match.get("match_score", 0.0)
        percentage = int(round(float(score) * 100))

        segments = [f"{index}. {label}"]
        if subtitle:
            segments.append(str(subtitle))
        segments.append(f"match {percentage}%")

        reasons = match.get("reasons") or []
        if reasons:
            segments.append(f"reasons: {', '.join(reasons)}")

        lines.append(" — ".join(segments))

    return "\n".join(lines)


def _safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _clamp(value: float | None) -> float | None:
    if value is None:
        return None
    return max(0.0, min(1.0, float(value)))
