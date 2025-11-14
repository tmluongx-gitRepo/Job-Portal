"""LangChain chains for role-aware chat agents."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Sequence
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

from app.ai.chat.tools.retrievers import (
    fetch_candidate_matches_for_employer,
    fetch_job_matches_for_user,
)
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


def _format_matches(matches: Sequence[dict[str, Any]]) -> str:
    return "\n".join(f"- {item}" for item in matches)


async def _fallback_stream(text: str) -> AsyncIterator[str]:
    yield text


async def job_seeker_stream(
    message: str, context: dict[str, Any]
) -> tuple[Sequence[dict[str, Any]], Callable[[], AsyncIterator[str]]]:
    matches = await fetch_job_matches_for_user(user_context=context)

    if not settings.OPENAI_API_KEY or ChatOpenAI is None:
        fallback_text = (
            f"Stub: showing example roles relevant to {message.strip() or 'your latest request'}."
        )
        return matches, lambda: _fallback_stream(fallback_text)

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
                matches_summary=RunnableLambda(lambda _: _format_matches(matches)),
            )
            | JOB_SEEKER_PROMPT
            | llm
            | StrOutputParser()
        )

        async def generator() -> AsyncIterator[str]:
            async for chunk in chain.astream({}):
                yield chunk

        return generator()

    return matches, factory


async def employer_stream(
    message: str, context: dict[str, Any]
) -> tuple[Sequence[dict[str, Any]], Callable[[], AsyncIterator[str]]]:
    matches = await fetch_candidate_matches_for_employer(user_context=context)

    if not settings.OPENAI_API_KEY or ChatOpenAI is None:
        fallback_text = f"Stub: returning example candidates relevant to {message.strip() or 'your open roles'}."
        return matches, lambda: _fallback_stream(fallback_text)

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
                matches_summary=RunnableLambda(lambda _: _format_matches(matches)),
            )
            | EMPLOYER_PROMPT
            | llm
            | StrOutputParser()
        )

        async def generator() -> AsyncIterator[str]:
            async for chunk in chain.astream({}):
                yield chunk

        return generator()

    return matches, factory


async def job_seeker_response(message: str, context: dict[str, Any]) -> dict[str, Any]:
    matches, stream_factory = await job_seeker_stream(message, context)
    text_parts: list[str] = []
    async for chunk in stream_factory():
        text_parts.append(chunk)
    return {"text": "".join(text_parts), "matches": matches}


async def employer_response(message: str, context: dict[str, Any]) -> dict[str, Any]:
    matches, stream_factory = await employer_stream(message, context)
    text_parts: list[str] = []
    async for chunk in stream_factory():
        text_parts.append(chunk)
    return {"text": "".join(text_parts), "matches": matches}
