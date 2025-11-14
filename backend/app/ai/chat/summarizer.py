"""Conversation summarisation helpers."""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from app.config import settings

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - optional dependency
    ChatOpenAI = None  # type: ignore[assignment]


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
    if not settings.OPENAI_API_KEY or ChatOpenAI is None:
        truncated = (
            base_summary + "\n" + f"User: {user_message}" + "\n" + f"Assistant: {assistant_message}"
        ).strip()
        return truncated[-settings.CHAT_SUMMARY_MAX_TOKENS * 5 :]

    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_SUMMARY_MODEL or settings.OPENAI_CHAT_MODEL,
        temperature=0,
        streaming=False,
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
    result = await chain.ainvoke({})
    return str(result)
