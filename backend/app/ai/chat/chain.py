"""LangChain chains for role-aware chat agents."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Sequence
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

from app.ai.chat.instrumentation import logger, tracing_context
from app.ai.chat.tools.retrievers import (
    fetch_candidate_matches_for_employer,
    fetch_job_matches_for_user,
)
from app.ai.chat.utils import AUDIENCE_EMPLOYER, AUDIENCE_JOB_SEEKER, prepare_matches
from app.config import settings

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - optional dependency
    ChatOpenAI = None  # type: ignore[assignment]


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
    raw_matches = await fetch_job_matches_for_user(user_context=context)
    matches, summary = prepare_matches(raw_matches, audience=AUDIENCE_JOB_SEEKER)

    if not settings.OPENAI_API_KEY or ChatOpenAI is None:
        fallback_text = (
            f"Here are the latest matches:\n{summary}"
            if matches
            else "I don't see any relevant roles yet, but I'll keep checking."
        )
        logger.info(
            "chat.fallback_response",
            extra={
                "audience": AUDIENCE_JOB_SEEKER,
                "matches": len(matches),
            },
        )
        return matches, summary, lambda: _fallback_stream(fallback_text)

    def factory() -> AsyncIterator[str]:
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0,
            streaming=True,
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
            with tracing_context("job_seeker_stream"):
                async for chunk in chain.astream({}):
                    yield chunk

        return generator()

    return matches, summary, factory


async def employer_stream(
    message: str, context: dict[str, Any]
) -> tuple[Sequence[dict[str, Any]], str, Callable[[], AsyncIterator[str]]]:
    raw_matches = await fetch_candidate_matches_for_employer(user_context=context)
    matches, summary = prepare_matches(raw_matches, audience=AUDIENCE_EMPLOYER)

    if not settings.OPENAI_API_KEY or ChatOpenAI is None:
        fallback_text = (
            f"Here are some candidates:\n{summary}"
            if matches
            else "I don't have any great candidates just yet, let's gather more data."
        )
        logger.info(
            "chat.fallback_response",
            extra={
                "audience": AUDIENCE_EMPLOYER,
                "matches": len(matches),
            },
        )
        return matches, summary, lambda: _fallback_stream(fallback_text)

    def factory() -> AsyncIterator[str]:
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0,
            streaming=True,
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
            with tracing_context("employer_stream"):
                async for chunk in chain.astream({}):
                    yield chunk

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
