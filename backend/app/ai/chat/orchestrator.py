"""LangChain v1 orchestrator for the role-aware chat experience."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Protocol


class StreamEvent(Protocol):
    """Protocol describing a streaming event payload."""

    type: str
    data: dict


class ChatOrchestrator:
    """Placeholder orchestrator coordinating sub-agents.

    This scaffolding will be extended in subsequent phases. For now it outlines
    the interfaces we expect to expose to the streaming endpoint.
    """

    async def stream_response(
        self, *, message: str, user_context: dict
    ) -> AsyncIterator[StreamEvent]:
        """Yield streaming events for the caller.

        Args:
            message: Latest end-user message.
            user_context: Authenticated user metadata (role, ids, etc.).
        """
        raise NotImplementedError("Chat orchestrator streaming not yet implemented")


StreamFactory = Callable[[], ChatOrchestrator]


def get_chat_orchestrator() -> ChatOrchestrator:
    """Factory hook for dependency injection.

    Later phases will likely add caching/singleton behaviour here. Keeping the
    function now helps downstream code reference a stable import path.
    """

    return ChatOrchestrator()
