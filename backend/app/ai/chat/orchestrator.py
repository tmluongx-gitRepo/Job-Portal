"""LangChain v1 orchestrator for the role-aware chat experience."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Protocol

from app.ai.chat.sessions import ChatSession, ChatSessionStore
from app.ai.chat.utils import emit_text
from app.services.chat_history import ChatHistoryService


class StreamEvent(Protocol):
    """Protocol describing a streaming event payload."""

    type: str
    data: dict


class ChatOrchestrator:
    """Stubbed orchestrator that will later call LangChain agents."""

    def __init__(
        self,
        *,
        session_store: ChatSessionStore | None = None,
        history_service: ChatHistoryService | None = None,
    ) -> None:
        self._session_store = session_store or ChatSessionStore()
        self._history_service = history_service or ChatHistoryService()

    async def stream_response(
        self, *, message: str, user_context: dict, session: ChatSession
    ) -> AsyncIterator[StreamEvent]:
        """Yield streaming events for the caller.

        This stub simply echoes the request until LangChain chains are wired.
        """

        # Persist user message for history
        await self._history_service.append_message(
            session_id=session.session_id,
            message={"role": user_context.get("account_type", "user"), "text": message},
        )

        text = f"Echoing '{message}' for role {user_context.get('account_type')}"
        async for event in emit_text(text):
            yield event  # type: ignore[misc]


StreamFactory = Callable[[], ChatOrchestrator]


def get_chat_orchestrator() -> ChatOrchestrator:
    """Factory hook for dependency injection.

    Later phases will likely add caching/singleton behaviour here. Keeping the
    function now helps downstream code reference a stable import path.
    """

    return ChatOrchestrator()
