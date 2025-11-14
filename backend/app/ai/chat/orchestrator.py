"""LangChain v1 orchestrator for the role-aware chat experience."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Protocol

from app.ai.chat.agents import EmployerAgent, JobSeekerAgent
from app.ai.chat.constants import ChatEventType, ChatRole
from app.ai.chat.sessions import ChatSession, ChatSessionStore
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
        self._job_seeker_agent = JobSeekerAgent()
        self._employer_agent = EmployerAgent()

    async def stream_response(
        self, *, message: str, user_context: dict, session: ChatSession
    ) -> AsyncIterator[StreamEvent]:
        """Yield streaming events for the caller.

        This stub simply echoes the request until LangChain chains are wired.
        """

        await self._session_store.save_message(
            session=session,
            message={
                "role": ChatRole.USER.value,
                "text": message,
            },
        )

        account_type = user_context.get("account_type", "job_seeker")
        agent: JobSeekerAgent | EmployerAgent = self._job_seeker_agent
        if account_type == "employer":
            agent = self._employer_agent

        response_event = await agent.generate(message, user_context)
        assistant_payload = response_event.get("data", {})
        if "text" not in assistant_payload or assistant_payload.get("text") is None:
            assistant_payload["text"] = ""

        await self._session_store.save_message(
            session=session,
            message={
                "role": ChatRole.ASSISTANT.value,
                "text": assistant_payload.get("text"),
                "structured": assistant_payload,
            },
        )

        yield response_event  # type: ignore[misc]
        yield {"type": ChatEventType.COMPLETE.value, "data": {}}  # type: ignore[misc]


StreamFactory = Callable[[], ChatOrchestrator]


def get_chat_orchestrator() -> ChatOrchestrator:
    """Factory hook for dependency injection.

    Later phases will likely add caching/singleton behaviour here. Keeping the
    function now helps downstream code reference a stable import path.
    """

    return ChatOrchestrator()
