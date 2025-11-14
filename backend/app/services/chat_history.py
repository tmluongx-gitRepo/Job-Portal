"""Mongo-backed chat history services."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

from bson import ObjectId

from app.database import (
    get_chat_messages_collection,
    get_chat_sessions_collection,
)
from app.type_definitions import ChatMessageDocument, ChatSessionDocument


class ChatHistoryService:
    """High-level abstraction for storing and retrieving chat transcripts."""

    def __init__(self) -> None:
        self._sessions = get_chat_sessions_collection()
        self._messages = get_chat_messages_collection()

    async def get_latest_session(self, *, user_id: str) -> ChatSessionDocument | None:
        """Return the most recent active session for the user, if any."""

        user_object_id = ObjectId(user_id)
        doc = await self._sessions.find_one(
            {"user_id": user_object_id, "status": "active"},
            sort=[("last_interaction_at", -1)],
        )
        return cast(ChatSessionDocument | None, doc)

    async def ensure_session(self, *, user_id: str, role: str) -> ChatSessionDocument:
        """Return an active session for the user, creating one if necessary."""

        user_object_id = ObjectId(user_id)
        existing = await self._sessions.find_one(
            {"user_id": user_object_id, "status": "active"},
            sort=[("last_interaction_at", -1)],
        )

        if existing:
            return cast(ChatSessionDocument, existing)

        now = datetime.now(UTC)
        session_doc: ChatSessionDocument = {
            "_id": ObjectId(),
            "session_id": str(uuid4()),
            "user_id": user_object_id,
            "role": role,
            "status": "active",
            "summary": None,
            "last_interaction_at": now,
            "created_at": now,
            "updated_at": now,
        }
        await self._sessions.insert_one(session_doc)
        return session_doc

    async def append_message(self, *, session_id: str, message: dict[str, Any]) -> None:
        """Persist a chat message and bump session timestamps."""

        now = datetime.now(UTC)
        document: ChatMessageDocument = {
            "_id": ObjectId(),
            "session_id": session_id,
            "role": cast(str, message.get("role", "assistant")),
            "payload_type": cast(str, message.get("payload_type", "text")),
            "text": cast(str | None, message.get("text")),
            "structured": message.get("structured"),
            "tokens_used": cast(int | None, message.get("tokens_used")),
            "created_at": now,
        }
        await self._messages.insert_one(document)

        await self._sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {"last_interaction_at": now, "updated_at": now},
            },
        )

    async def fetch_recent(self, *, session_id: str, limit: int) -> Sequence[dict[str, Any]]:
        """Return the latest `limit` chat messages for the session."""

        cursor = self._messages.find({"session_id": session_id}).sort("created_at", -1).limit(limit)
        results = await cursor.to_list(length=limit)
        return list(reversed(results))

    async def upsert_summary(self, *, session_id: str, summary: str) -> None:
        """Attach/replace the rolling summary for the session."""

        now = datetime.now(UTC)
        await self._sessions.update_one(
            {"session_id": session_id},
            {"$set": {"summary": summary, "updated_at": now}},
        )
