"""LangChain chains for role-aware chat agents."""

from __future__ import annotations

import asyncio
import importlib
import re
from collections.abc import AsyncIterator, Callable, Sequence
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from pydantic import SecretStr

from app.ai.chat.instrumentation import logger, tracing_context
from app.ai.chat.tools.retrievers import (
    fetch_candidate_matches_for_employer,
    fetch_job_matches_for_user,
)
from app.ai.chat.utils import AUDIENCE_EMPLOYER, AUDIENCE_JOB_SEEKER, prepare_matches
from app.config import settings
from app.crud import application as application_crud
from app.crud import job as job_crud
from app.crud import job_seeker_profile as job_seeker_profile_crud
from app.schemas.application import ApplicationCreate
from app.services.webhook_service import trigger_application_webhook

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from langchain_openai import ChatOpenAI as ChatOpenAIType
else:  # pragma: no cover - runtime fallback typing
    ChatOpenAIType = Any


def _resolve_chat_openai_cls() -> Any | None:
    try:
        module = importlib.import_module("langchain_openai")
    except ImportError:  # pragma: no cover - optional dependency
        return None
    return getattr(module, "ChatOpenAI", None)


_CHAT_OPENAI_CLS = _resolve_chat_openai_cls()


JOB_SEEKER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are helping a job seeker. Use the provided job matches to craft a helpful reply.\n\n"
            "Matches:\n{matches_summary}",
        ),
        ("human", "{message}"),
    ]
)

EMPLOYER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are helping an employer find candidates. Use the candidate shortlist to craft recommendations.\n\n"
            "Candidates:\n{matches_summary}",
        ),
        ("human", "{message}"),
    ]
)


async def _fallback_stream(text: str) -> AsyncIterator[str]:
    yield text


async def job_seeker_stream(
    message: str, context: dict[str, Any]
) -> tuple[Sequence[dict[str, Any]], str, Callable[[], AsyncIterator[str]]]:
    application_reply = await _maybe_handle_application(message, context)
    if application_reply is not None:
        text, summary = application_reply
        return [], summary, lambda: _fallback_stream(text)

    if _is_small_talk(message):
        return _small_talk_response(message)

    if _is_status_question(message):
        status_text = (
            "I haven't spotted any employer replies just yet. "
            "I'll keep an eye out and let you know as soon as someone responds."
        )
        return [], "No new employer replies yet.", lambda: _fallback_stream(status_text)

    raw_matches = await fetch_job_matches_for_user(user_context=context, query=message)
    matches, summary = prepare_matches(raw_matches, audience=AUDIENCE_JOB_SEEKER)

    llm_cls = _CHAT_OPENAI_CLS
    if not settings.OPENAI_API_KEY or llm_cls is None:
        fallback_text = _fallback_chat_response(
            matches=matches,
            summary=summary,
            audience=AUDIENCE_JOB_SEEKER,
            user_message=message,
        )
        logger.info(
            "chat.fallback_response",
            extra={
                "audience": AUDIENCE_JOB_SEEKER,
                "matches": len(matches),
            },
        )
        return matches, summary, lambda: _fallback_stream(fallback_text)

    retry_attempts = max(1, settings.CHAT_STREAM_MAX_RETRIES)
    min_delay = max(0.1, settings.CHAT_STREAM_RETRY_MIN_DELAY)

    def factory() -> AsyncIterator[str]:
        # LangChain's OpenAI wrapper accepts either SecretStr or plain strings; we
        # wrap once here to appease type checkers without mutating global settings.
        llm = cast(
            Any,
            llm_cls(
                api_key=SecretStr(settings.OPENAI_API_KEY),
                model=settings.OPENAI_JOB_SEEKER_MODEL or settings.OPENAI_CHAT_MODEL,
                temperature=0,
                streaming=True,
            ),
        )
        chain = (
            RunnableParallel(
                message=RunnableLambda(lambda _: message),
                matches_summary=RunnableLambda(lambda _: summary),
            )
            | JOB_SEEKER_PROMPT
            | llm
            | StrOutputParser()
        )

        async def generator() -> AsyncIterator[str]:
            for attempt in range(retry_attempts):
                try:
                    with tracing_context("job_seeker_stream"):
                        async for chunk in chain.astream({}):
                            yield chunk
                    return  # noqa: TRY300
                except Exception as exc:  # pragma: no cover - flakiness hard to simulate
                    logger.warning(
                        "chat.stream.retry",
                        extra={
                            "audience": AUDIENCE_JOB_SEEKER,
                            "attempt": attempt + 1,
                            "max_attempts": retry_attempts,
                            "error": str(exc),
                        },
                    )
                    if attempt + 1 >= retry_attempts:
                        fallback_text = _fallback_chat_response(
                            matches=matches,
                            summary=summary,
                            audience=AUDIENCE_JOB_SEEKER,
                            user_message=message,
                        )
                        yield fallback_text
                        return
                    await asyncio.sleep(min_delay * (2**attempt))

        return generator()

    return matches, summary, factory


async def employer_stream(
    message: str, context: dict[str, Any]
) -> tuple[Sequence[dict[str, Any]], str, Callable[[], AsyncIterator[str]]]:
    review_response = await _maybe_handle_employer_review(message, context)
    if review_response is not None:
        return review_response

    if _is_small_talk(message):
        return _employer_small_talk_response(message)

    raw_matches = await fetch_candidate_matches_for_employer(user_context=context)
    matches, summary = prepare_matches(raw_matches, audience=AUDIENCE_EMPLOYER)

    llm_cls = _CHAT_OPENAI_CLS
    if not settings.OPENAI_API_KEY or llm_cls is None:
        fallback_text = _fallback_chat_response(
            matches=matches,
            summary=summary,
            audience=AUDIENCE_EMPLOYER,
            user_message=message,
        )
        logger.info(
            "chat.fallback_response",
            extra={
                "audience": AUDIENCE_EMPLOYER,
                "matches": len(matches),
            },
        )
        return matches, summary, lambda: _fallback_stream(fallback_text)

    retry_attempts = max(1, settings.CHAT_STREAM_MAX_RETRIES)
    min_delay = max(0.1, settings.CHAT_STREAM_RETRY_MIN_DELAY)

    def factory() -> AsyncIterator[str]:
        llm = cast(
            Any,
            llm_cls(
                api_key=SecretStr(settings.OPENAI_API_KEY),
                model=settings.OPENAI_EMPLOYER_MODEL or settings.OPENAI_CHAT_MODEL,
                temperature=0,
                streaming=True,
            ),
        )
        chain = (
            RunnableParallel(
                message=RunnableLambda(lambda _: message),
                matches_summary=RunnableLambda(lambda _: summary),
            )
            | EMPLOYER_PROMPT
            | llm
            | StrOutputParser()
        )

        async def generator() -> AsyncIterator[str]:
            for attempt in range(retry_attempts):
                try:
                    with tracing_context("employer_stream"):
                        async for chunk in chain.astream({}):
                            yield chunk
                    return  # noqa: TRY300
                except Exception as exc:  # pragma: no cover - flakiness hard to simulate
                    logger.warning(
                        "chat.stream.retry",
                        extra={
                            "audience": AUDIENCE_EMPLOYER,
                            "attempt": attempt + 1,
                            "max_attempts": retry_attempts,
                            "error": str(exc),
                        },
                    )
                    if attempt + 1 >= retry_attempts:
                        fallback_text = _fallback_chat_response(
                            matches=matches,
                            summary=summary,
                            audience=AUDIENCE_EMPLOYER,
                            user_message=message,
                        )
                        yield fallback_text
                        return
                    await asyncio.sleep(min_delay * (2**attempt))

        return generator()

    return matches, summary, factory


async def job_seeker_response(message: str, context: dict[str, Any]) -> dict[str, Any]:
    matches, summary, stream_factory = await job_seeker_stream(message, context)
    text_parts: list[str] = []
    async for chunk in stream_factory():
        text_parts.append(chunk)
    return {"text": "".join(text_parts), "matches": matches, "summary": summary}


async def employer_response(message: str, context: dict[str, Any]) -> dict[str, Any]:
    matches, summary, stream_factory = await employer_stream(message, context)
    text_parts: list[str] = []
    async for chunk in stream_factory():
        text_parts.append(chunk)
    return {"text": "".join(text_parts), "matches": matches, "summary": summary}


def _fallback_chat_response(
    *,
    matches: Sequence[dict[str, Any]],
    summary: str,  # noqa: ARG001
    audience: str,
    user_message: str,
) -> str:
    if not matches:
        if audience == AUDIENCE_JOB_SEEKER:
            return "I don't have any strong matches just yet. If you share a preferred role, location, or skill focus I can refine the search."
        return "I couldn't spot any candidates that line up right now. Try narrowing by a role, location, or seniority so I can hunt again."

    bullets: list[str] = []
    for match in matches[:3]:
        label = match.get("label") or "Opportunity"
        subtitle = match.get("subtitle")
        bullet = f"• {label}"
        if subtitle:
            bullet = f"{bullet} — {subtitle}"
        bullets.append(bullet)

    bullet_block = "\n".join(bullets)
    heard_line = f"I heard: \u201c{user_message}\u201d."

    if audience == AUDIENCE_JOB_SEEKER:
        closing = "Want me to narrow things by skills, location, or salary?"
        return (
            f"{heard_line}\nHere\u2019s what I\u2019m seeing right now:\n{bullet_block}\n{closing}"
        )

    closing = "Need me to dig into different skills or seniority?"
    return f"{heard_line}\nThese candidates look promising:\n{bullet_block}\n{closing}"


_APPLY_TRIGGER = re.compile(r"\bapply\b", re.IGNORECASE)
_APPLY_CAPTURE = re.compile(
    r"apply(?:\s+(?:for|to))?(?:\s+the)?\s+(?P<target>[\w\s\-:&'/.#]+)",
    re.IGNORECASE,
)
_JOB_ID_PATTERN = re.compile(r"(?:job::)?([0-9a-f]{24})", re.IGNORECASE)
_ORDINAL_MAP: dict[str, int] = {
    "first": 0,
    "1": 0,
    "1st": 0,
    "second": 1,
    "2": 1,
    "2nd": 1,
    "third": 2,
    "3": 2,
    "3rd": 2,
}


async def _maybe_handle_application(  # noqa: PLR0911
    message: str, context: dict[str, Any]
) -> tuple[str, str] | None:
    job_hint = _parse_apply_target(message)
    if job_hint is None:
        return None

    if not job_hint:
        return (
            "Happy to help with applications—let me know which role you'd like me to submit to.",
            "Awaiting role selection for application.",
        )

    if context.get("account_type") != AUDIENCE_JOB_SEEKER:
        return (
            "I can only submit applications when you're signed in as a job seeker.",
            "Cannot apply from non job seeker account.",
        )

    user_id = context.get("id")
    if not isinstance(user_id, str) or not user_id:
        return (
            "I couldn't confirm your account details to submit the application. Please sign in again and try once more.",
            "Missing user context for application submission.",
        )

    profile = await job_seeker_profile_crud.get_profile_by_user_id(user_id)
    if not profile:
        return (
            "I need your job seeker profile before I can submit applications. Once it's set up, I can apply for you automatically.",
            "Job seeker profile missing for application submission.",
        )

    profile_id = str(profile["_id"])
    recent_matches = context.get("recent_matches")
    if not isinstance(recent_matches, Sequence):
        recent_matches = []

    job = await _resolve_job_from_context(job_hint, recent_matches)
    if not job:
        return (
            "I couldn't find a role that matches that description. Try referencing the job title exactly as it appears in the matches, or ask me to show them again.",
            "Job not found for requested application.",
        )

    job_id = str(job["_id"])
    title = job.get("title") or "this role"
    company = job.get("company") or "the employer"

    duplicate = await application_crud.check_duplicate_application(profile_id, job_id)
    if duplicate:
        return (
            f"It looks like you've already applied to {title} at {company}. I'll keep watching for any updates from them.",
            f"Already applied to {title} at {company}.",
        )

    application_data = ApplicationCreate(job_id=job_id, job_seeker_id=profile_id)
    application_doc = await application_crud.create_application(
        application_data.model_dump(), job_seeker_id=profile_id
    )
    await job_crud.increment_application_count(job_id)

    try:
        asyncio.create_task(  # noqa: RUF006
            trigger_application_webhook(application_doc, job, profile)  # type: ignore[arg-type]
        )
    except Exception as exc:  # pragma: no cover - webhook best effort
        logger.warning(
            "chat.application.webhook_failed",
            extra={"job_id": job_id, "profile_id": profile_id, "error": str(exc)},
        )

    confirmation = f"All set! I've submitted your application to {title} at {company}. I'll let you know when there's news."
    summary = f"Applied to {title} at {company}."
    return confirmation, summary


def _parse_apply_target(message: str) -> str | None:
    if not message or not _APPLY_TRIGGER.search(message):
        return None

    match = _APPLY_CAPTURE.search(message)
    if not match:
        return ""

    target = match.group("target") or ""
    target = target.strip(" .!?\n\r")
    lowered = target.lower()
    if any(keyword in lowered for keyword in ("filter", "filters", "filtering")):
        return None
    return target


async def _resolve_job_from_context(
    job_hint: str, recent_matches: Sequence[dict[str, Any]]
) -> dict[str, Any] | None:
    job_id = _extract_job_id(job_hint)
    if job_id:
        job = await job_crud.get_job_by_id(job_id)
        if job:
            return job  # type: ignore[return-value]

    match_job = await _job_from_recent_matches(job_hint, recent_matches)
    if match_job:
        return match_job  # type: ignore[return-value]

    jobs = await job_crud.search_jobs(query=job_hint, limit=5)
    if jobs:
        return jobs[0]  # type: ignore[return-value]

    return None


async def _job_from_recent_matches(
    job_hint: str, recent_matches: Sequence[dict[str, Any]]
) -> dict[str, Any] | None:
    if not recent_matches:
        return None

    job_hint_lower = job_hint.lower()
    ordinal_index = _infer_match_index(job_hint_lower)
    if ordinal_index is not None and 0 <= ordinal_index < len(recent_matches):
        job = await _job_from_match_dict(recent_matches[ordinal_index])
        if job:
            return job

    for match in recent_matches:
        label = str(match.get("label", "")).lower()
        subtitle = str(match.get("subtitle", "")).lower()
        metadata = match.get("metadata") if isinstance(match.get("metadata"), dict) else {}
        company = str(metadata.get("company", "")).lower()  # type: ignore[union-attr]

        if (
            job_hint_lower in label
            or label in job_hint_lower
            or job_hint_lower in company
            or company in job_hint_lower
            or job_hint_lower in subtitle
        ):
            job = await _job_from_match_dict(match)
            if job:
                return job

    return None


def _infer_match_index(job_hint_lower: str) -> int | None:
    for key, index in _ORDINAL_MAP.items():
        if key in job_hint_lower:
            return index
    return None


async def _job_from_match_dict(match: dict[str, Any]) -> dict[str, Any] | None:
    candidates: list[str] = []
    for key in ("id", "job_id"):
        value = match.get(key)
        if isinstance(value, str):
            candidates.append(value)
    metadata = match.get("metadata")
    if isinstance(metadata, dict):
        meta_job_id = metadata.get("job_id") or metadata.get("id")
        if isinstance(meta_job_id, str):
            candidates.append(meta_job_id)

    for candidate in candidates:
        job_id = _normalise_job_id(candidate)
        if not job_id:
            continue
        job = await job_crud.get_job_by_id(job_id)
        if job:
            return job  # type: ignore[return-value]

    return None


def _extract_job_id(text: str) -> str | None:
    match = _JOB_ID_PATTERN.search(text)
    if not match:
        return None
    return match.group(1)


def _normalise_job_id(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if "::" in cleaned:
        cleaned = cleaned.split("::", 1)[-1]
    if _JOB_ID_PATTERN.fullmatch(cleaned):
        return cleaned
    return None


_STATUS_PATTERN = re.compile(
    r"(have i (got|received)|any (replies|responses)|application status|heard back|respond(?:ed)?|message me)",
    re.IGNORECASE,
)


def _is_status_question(message: str) -> bool:
    return bool(_STATUS_PATTERN.search(message))


_SMALL_TALK_PATTERN = re.compile(
    r"\b(hi|hello|hey|how are you|what's up|thanks|thank you|good (morning|afternoon|evening)|great job|nice work)\b",
    re.IGNORECASE,
)


_REVIEW_PATTERN = re.compile(
    r"(review|show|see|get|list)\s+(my\s+)?(applications|applicants|candidates)",
    re.IGNORECASE,
)


def _is_small_talk(message: str) -> bool:
    return bool(_SMALL_TALK_PATTERN.search(message))


def _small_talk_response(
    message: str,
) -> tuple[Sequence[dict[str, Any]], str, Callable[[], AsyncIterator[str]]]:
    normalised = message.strip().lower()
    if "thank" in normalised:
        text = "You got it! I'm here whenever you need help exploring roles or next steps."
    elif "how are" in normalised or "what's up" in normalised:
        text = "I'm doing great—always ready to help you find a path forward. How can I support you today?"
    elif any(greeting in normalised for greeting in ("hi", "hello", "hey")):
        text = "Hi there! Ready whenever you are to look at roles, resumes, or next actions."
    else:
        text = "Happy to chat! Let me know if you want matches, application tips, or anything else."

    return [], "Small talk acknowledged.", lambda: _fallback_stream(text)


def _employer_small_talk_response(
    message: str,
) -> tuple[Sequence[dict[str, Any]], str, Callable[[], AsyncIterator[str]]]:
    normalised = message.strip().lower()
    if "thank" in normalised:
        text = "Anytime! I'm here to surface candidates or hiring updates whenever you need them."
    elif "how are" in normalised or "what's up" in normalised:
        text = "Doing well—ready to help review applicants, shortlist talent, or check interview status."
    elif any(greeting in normalised for greeting in ("hi", "hello", "hey")):
        text = "Hello! Let me know if you want a fresh shortlist, pipeline insights, or candidate details."
    else:
        text = "Standing by whenever you want to look at candidates or next hiring steps."

    return [], "Small talk acknowledged.", lambda: _fallback_stream(text)


async def _maybe_handle_employer_review(
    message: str, context: dict[str, Any]
) -> tuple[Sequence[dict[str, Any]], str, Callable[[], AsyncIterator[str]]] | None:
    if not _REVIEW_PATTERN.search(message):
        return None

    user_id = context.get("id")
    if not isinstance(user_id, str) or not user_id:
        text = (
            "I couldn't confirm your employer account. Please sign in again to review applications."
        )
        return [], text, lambda: _fallback_stream(text)

    jobs = await job_crud.get_jobs(posted_by=user_id)
    if not jobs:
        text = "I don't see any job postings yet. Once you publish a role, I'll bring the applications here."
        return [], text, lambda: _fallback_stream(text)

    paired_applications: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for job in jobs:
        job_id = str(job.get("_id"))
        if not job_id:
            continue
        job_apps = await application_crud.get_applications(limit=50, job_id=job_id)
        for application in job_apps:
            paired_applications.append((application, job))  # type: ignore[arg-type]

    if not paired_applications:
        text = "No one has applied yet. I'll let you know as soon as a new application comes in."
        return [], text, lambda: _fallback_stream(text)

    paired_applications.sort(key=_application_sort_key, reverse=True)
    paired_applications = paired_applications[:6]

    matches: list[dict[str, Any]] = []
    for application, job in paired_applications:  # type: ignore[assignment]
        profile = await job_seeker_profile_crud.get_profile_by_id(application["job_seeker_id"])
        full_name = _build_candidate_name(profile, application["job_seeker_id"])  # type: ignore[arg-type]
        job_title = job.get("title") or "Role"
        job_location = job.get("location") or "Location not provided"
        subtitle = f"{job_title} — {job_location}"
        applied_at = _format_datetime(application.get("applied_date"))
        status = application.get("status") or "Application Submitted"
        profile_skills = list(profile.get("skills", [])) if isinstance(profile, dict) else []
        experience_years = profile.get("experience_years") if isinstance(profile, dict) else None

        matches.append(
            {
                "id": application.get("job_seeker_id"),
                "label": full_name,
                "subtitle": subtitle,
                "match_score": 0.35,
                "score_breakdown": {"recent_application": 1.0},
                "source": "applications",
                "metadata": {
                    "application_id": str(application.get("_id")),
                    "job_id": application.get("job_id"),
                    "job_title": job_title,
                    "job_location": job_location,
                    "status": status,
                    "applied_at": applied_at,
                    "candidate_email": (profile or {}).get("email"),  # type: ignore[call-overload]
                    "candidate_phone": (profile or {}).get("phone"),  # type: ignore[call-overload]
                    "candidate_profile_id": (
                        str(profile.get("_id")) if isinstance(profile, dict) else None
                    ),
                    "skills": profile_skills,
                    "experience_years": experience_years,
                },
            }
        )

    context["navigate_to"] = "/employer-dashboard#applications"

    summary = f"{len(matches)} applications ready for review."
    text = "I pulled the latest applications across your open roles and opened the applications dashboard for you."
    return matches, summary, lambda: _fallback_stream(text)


def _application_sort_key(item: tuple[dict[str, Any], dict[str, Any]]) -> datetime:
    application, _ = item
    applied = application.get("applied_date")
    if isinstance(applied, datetime):
        try:
            return applied.astimezone(UTC)
        except Exception:
            return applied
    return datetime.min.replace(tzinfo=UTC)


def _format_datetime(value: Any) -> str | None:
    if isinstance(value, datetime):
        try:  # noqa: SIM105
            value = value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
        except Exception:
            pass
        return value.isoformat()
    if isinstance(value, str):
        return value
    return None


def _build_candidate_name(profile: dict[str, Any] | None, fallback_id: str) -> str:
    if isinstance(profile, dict):
        first = str(profile.get("first_name") or "").strip()
        last = str(profile.get("last_name") or "").strip()
        full = " ".join(part for part in (first, last) if part)
        if full:
            return full
    return f"Candidate {fallback_id[:8]}"
