"""Conversation session management scaffolding."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.ai.chat.cache import RedisChatCache, get_chat_cache
from app.services.chat_history import ChatHistoryService
from app.type_definitions import ChatSessionDocument


@dataclass
class ChatSession:
    session_id: str
    user_id: str
    role: str
    status: str
    last_interaction_at: datetime
    created_at: datetime
    summary: str | None = None


class ChatSessionStore:
    """Manage chat sessions using Mongo persistence and Redis caching."""

    def __init__(
        self,
        *,
        history_service: ChatHistoryService | None = None,
        cache: RedisChatCache | None = None,
    ) -> None:
        self._history = history_service or ChatHistoryService()
        self._cache = cache or get_chat_cache()

    async def load(self, *, user_id: str) -> ChatSession | None:
        """Return the latest active session for the user if it exists."""

        document = await self._history.get_latest_session(user_id=user_id)
        if document is None:
            return None
        return self._document_to_session(document)

    async def get_or_create(self, *, user_id: str, role: str) -> ChatSession:
        """Return a chat session, creating one if necessary."""

        document = await self._history.ensure_session(user_id=user_id, role=role)
        return self._document_to_session(document)

    async def save_message(self, *, session: ChatSession, message: dict[str, Any]) -> None:
        """Persist a chat message and push it to the Redis recent cache."""

        await self._history.append_message(session_id=session.session_id, message=message)

        now = datetime.now(UTC)
        session.last_interaction_at = now

        payload = {
            "role": message.get("role"),
            "payload_type": message.get("payload_type", "text"),
            "text": message.get("text"),
            "structured": message.get("structured"),
            "tokens_used": message.get("tokens_used"),
            "created_at": now.isoformat(),
        }
        await self._cache.push_recent_message(
            session_id=session.session_id,
            payload=json.dumps(payload, ensure_ascii=False),
        )

    async def hydrate_context(
        self, *, session: ChatSession, limit: int
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Return cached summary and recent messages, warming cache if required."""

        summary = await self._cache.get_summary(session_id=session.session_id)
        if summary is None and session.summary:
            summary = session.summary
            await self._cache.set_summary(session_id=session.session_id, summary=summary)

        cached_messages = await self._cache.get_recent_messages(session_id=session.session_id)
        messages: list[dict[str, Any]] = []
        for entry in cached_messages:
            try:
                messages.append(json.loads(entry))
            except json.JSONDecodeError:  # pragma: no cover - cache drift
                continue

        if not messages:
            docs = await self._history.fetch_recent(session_id=session.session_id, limit=limit)
            for doc in docs:
                created_at = doc.get("created_at")
                msg = {
                    "role": doc.get("role"),
                    "payload_type": doc.get("payload_type"),
                    "text": doc.get("text"),
                    "structured": doc.get("structured"),
                    "created_at": created_at.isoformat() if created_at else None,
                }
                messages.append(msg)
                await self._cache.push_recent_message(
                    session_id=session.session_id,
                    payload=json.dumps(msg, ensure_ascii=False),
                )

        return summary, messages

    async def update_summary(self, *, session: ChatSession, summary: str) -> None:
        """Persist and cache the rolling summary for the session."""

        session.summary = summary
        await self._history.upsert_summary(session_id=session.session_id, summary=summary)
        await self._cache.set_summary(session_id=session.session_id, summary=summary)

    @staticmethod
    def _document_to_session(document: ChatSessionDocument) -> ChatSession:
        return ChatSession(
            session_id=document["session_id"],
            user_id=str(document["user_id"]),
            role=document["role"],
            status=document["status"],
            last_interaction_at=document["last_interaction_at"],
            created_at=document["created_at"],
            summary=document.get("summary"),
        )
