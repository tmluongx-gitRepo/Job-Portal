"""Conversation summarisation helpers."""

from __future__ import annotations

import asyncio
import importlib
import logging
from typing import TYPE_CHECKING, Any, cast

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import SecretStr

from app.config import settings

logger = logging.getLogger(__name__)

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


SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You maintain a concise running summary of a chat between a user and an assistant."
            " Update the summary with the latest exchange whilst keeping key details "
            "relevant to future recommendations. Limit to about {summary_max_tokens} tokens.",
        ),
        (
            "human",
            "Current summary (may be empty):\n{current_summary}\n\n"
            "Recent user message: {user_message}\n"
            "Recent assistant reply: {assistant_message}",
        ),
    ]
)


async def summarise_conversation(
    *,
    current_summary: str | None,
    user_message: str,
    assistant_message: str,
) -> str:
    """Return an updated rolling summary for the conversation."""

    base_summary = current_summary or ""
    llm_cls = _CHAT_OPENAI_CLS
    if not settings.OPENAI_API_KEY or llm_cls is None:
        truncated = (
            base_summary + "\n" + f"User: {user_message}" + "\n" + f"Assistant: {assistant_message}"
        ).strip()
        return truncated[-settings.CHAT_SUMMARY_MAX_TOKENS * 5 :]

    llm = cast(
        Any,
        llm_cls(
            api_key=SecretStr(settings.OPENAI_API_KEY),
            model=settings.OPENAI_SUMMARY_MODEL or settings.OPENAI_CHAT_MODEL,
            temperature=0,
            streaming=False,
        ),
    )
    chain = (
        RunnableLambda(
            lambda _: {
                "current_summary": base_summary,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "summary_max_tokens": settings.CHAT_SUMMARY_MAX_TOKENS,
            }
        )
        | SUMMARY_PROMPT
        | llm
        | StrOutputParser()
    )

    attempts = max(1, settings.CHAT_SUMMARY_MAX_RETRIES)
    min_delay = max(0.1, settings.CHAT_SUMMARY_RETRY_MIN_DELAY)

    for attempt in range(attempts):
        try:
            result = await chain.ainvoke({})
            return str(result)
        except Exception as exc:  # pragma: no cover - upstream network flakiness
            logger.warning(
                "chat.summary.retry",
                extra={
                    "attempt": attempt + 1,
                    "max_attempts": attempts,
                    "error": str(exc),
                },
            )
            if attempt + 1 >= attempts:
                truncated = (
                    base_summary
                    + "\n"
                    + f"User: {user_message}"
                    + "\n"
                    + f"Assistant: {assistant_message}"
                ).strip()
                return truncated[-settings.CHAT_SUMMARY_MAX_TOKENS * 5 :]
            await asyncio.sleep(min_delay * (2**attempt))

    # Should never reach here
    return base_summary
