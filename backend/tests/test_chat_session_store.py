"""Unit tests for ChatSessionStore using in-memory stubs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pytest

from app.ai.chat.sessions import ChatSession, ChatSessionStore


class StubHistoryService:
    """In-memory stand-in for ChatHistoryService."""

    def __init__(self) -> None:
        self.sessions: dict[str, ChatSession] = {}
        self.messages: dict[str, list[dict[str, Any]]] = {}

    async def ensure_session(self, *, user_id: str, role: str) -> dict[str, Any]:
        if user_id not in self.sessions:
            now = datetime.now(UTC)
            session = ChatSession(
                session_id=f"session-{user_id}",
                user_id=user_id,
                role=role,
                status="active",
                last_interaction_at=now,
                created_at=now,
                summary=None,
            )
            self.sessions[user_id] = session
            self.messages[session.session_id] = []
        session = self.sessions[user_id]
        return {
            "session_id": session.session_id,
            "user_id": user_id,
            "role": session.role,
            "status": session.status,
            "summary": session.summary,
            "last_interaction_at": session.last_interaction_at,
            "created_at": session.created_at,
            "updated_at": session.created_at,
        }

    async def get_latest_session(self, *, user_id: str) -> dict[str, Any] | None:
        session = self.sessions.get(user_id)
        if not session:
            return None
        return {
            "session_id": session.session_id,
            "user_id": user_id,
            "role": session.role,
            "status": session.status,
            "summary": session.summary,
            "last_interaction_at": session.last_interaction_at,
            "created_at": session.created_at,
            "updated_at": session.created_at,
        }

    async def append_message(self, *, session_id: str, message: dict[str, Any]) -> None:
        self.messages.setdefault(session_id, []).append(message)

    async def fetch_recent(self, *, session_id: str, limit: int) -> list[dict[str, Any]]:
        return self.messages.get(session_id, [])[-limit:]

    async def upsert_summary(self, *, session_id: str, summary: str) -> None:
        # Stored summary lives on ChatSession; caller handles assignment.
        pass


@dataclass
class StubCache:
    summaries: dict[str, str]
    recent: dict[str, list[str]]

    async def get_summary(self, *, session_id: str) -> str | None:
        return self.summaries.get(session_id)

    async def set_summary(self, *, session_id: str, summary: str) -> None:
        self.summaries[session_id] = summary

    async def get_recent_messages(self, *, session_id: str) -> list[str]:
        return self.recent.get(session_id, []).copy()

    async def push_recent_message(self, *, session_id: str, payload: str) -> None:
        self.recent.setdefault(session_id, []).append(payload)


@pytest.mark.asyncio
async def test_chat_session_store_round_trip() -> None:
    history = StubHistoryService()
    cache = StubCache(summaries={}, recent={})
    store = ChatSessionStore(history_service=history, cache=cache)  # type: ignore[arg-type]

    session = await store.get_or_create(user_id="user-1", role="job_seeker")
    assert session.session_id == "session-user-1"

    await store.save_message(session=session, message={"role": "user", "text": "Hi"})
    await store.save_message(
        session=session,
        message={"role": "assistant", "text": "Hello", "structured": {"foo": "bar"}},
    )

    summary, messages = await store.hydrate_context(session=session, limit=5)
    assert summary is None
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["structured"] == {"foo": "bar"}

    await store.update_summary(session=session, summary="Conversation summary")
    assert cache.summaries[session.session_id] == "Conversation summary"

    cached_summary, cached_messages = await store.hydrate_context(session=session, limit=5)
    assert cached_summary == "Conversation summary"
    assert len(cached_messages) == 2
