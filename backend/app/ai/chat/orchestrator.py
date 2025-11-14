"""LangChain v1 orchestrator for the role-aware chat experience."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Protocol

from app.ai.chat.agents import EmployerAgent, JobSeekerAgent
from app.ai.chat.constants import ChatEventType, ChatRole
from app.ai.chat.sessions import ChatSession, ChatSessionStore
from app.ai.chat.summarizer import summarise_conversation
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

        matches, chunk_iterator = await agent.stream(message, user_context)

        if matches:
            yield {"type": ChatEventType.MATCHES.value, "data": {"matches": matches}}  # type: ignore[misc]

        accumulated: list[str] = []
        async for chunk in chunk_iterator:
            accumulated.append(chunk)
            yield {
                "type": ChatEventType.TOKEN.value,
                "data": {"text": chunk},
            }  # type: ignore[misc]

        text = "".join(accumulated)

        await self._session_store.save_message(
            session=session,
            message={
                "role": ChatRole.ASSISTANT.value,
                "text": text,
                "structured": {"matches": matches, "text": text},
            },
        )

        new_summary = await summarise_conversation(
            current_summary=session.summary,
            user_message=message,
            assistant_message=text,
        )
        await self._session_store.update_summary(session=session, summary=new_summary)
        yield {
            "type": ChatEventType.SUMMARY.value,
            "data": {"summary": new_summary},
        }  # type: ignore[misc]

        yield {"type": ChatEventType.COMPLETE.value, "data": {}}  # type: ignore[misc]


StreamFactory = Callable[[], ChatOrchestrator]


def get_chat_orchestrator() -> ChatOrchestrator:
    """Factory hook for dependency injection.

    Later phases will likely add caching/singleton behaviour here. Keeping the
    function now helps downstream code reference a stable import path.
    """

    return ChatOrchestrator()
