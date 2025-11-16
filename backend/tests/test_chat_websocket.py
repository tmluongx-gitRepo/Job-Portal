"""Integration-style test for the chat websocket using dependency overrides."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.ai.chat.constants import ChatEventType
from app.ai.chat.sessions import ChatSession
from app.api.routes import chat as chat_route
from app.main import app


@dataclass
class StubSessionStore:
    summary: str | None = "Earlier summary"
    history: list[dict[str, Any]] | None = None
    messages: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        if self.history is None:
            self.history = []
        if self.messages is None:
            self.messages = []  # Ensure messages is never None

    async def get_or_create(self, *, user_id: str, role: str) -> ChatSession:
        now = datetime.now(UTC)
        return ChatSession(
            session_id="session-123",
            user_id=user_id,
            role=role,
            status="active",
            last_interaction_at=now,
            created_at=now,
            summary=self.summary,
        )

    async def save_message(
        self,
        *,
        session: ChatSession,  # noqa: ARG002
        message: dict[str, Any],
    ) -> None:
        if self.messages is not None:
            self.messages.append(message)

    async def hydrate_context(
        self,
        *,
        session: ChatSession,  # noqa: ARG002
        limit: int,  # noqa: ARG002
    ) -> tuple[str | None, list[dict[str, Any]]]:
        return self.summary, list(self.history or [])

    async def update_summary(self, *, session: ChatSession, summary: str) -> None:  # noqa: ARG002
        self.summary = summary


class StubOrchestrator:
    async def stream_response(
        self,
        *,
        message: str,  # noqa: ARG002
        user_context: dict,  # noqa: ARG002
        session: ChatSession,  # noqa: ARG002
    ) -> AsyncIterator[dict[str, Any]]:
        yield {
            "type": ChatEventType.MATCHES.value,
            "data": {
                "matches": [
                    {
                        "id": "job-1",
                        "label": "Backend Engineer",
                        "subtitle": "Initech | Austin, TX",
                        "match_score": 0.82,
                        "vector_score": 0.76,
                        "score_breakdown": {"skills_overlap": 0.9},
                        "reasons": ["skills overlap 90%"],
                        "source": "vector",
                        "metadata": {"company": "Initech"},
                    }
                ],
                "summary": "1. Backend Engineer — Initech | Austin, TX — match 82%",
            },
        }
        yield {"type": ChatEventType.TOKEN.value, "data": {"text": "Hello"}}
        yield {"type": ChatEventType.COMPLETE.value, "data": {}}


@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[misc]
    app.dependency_overrides[chat_route.get_current_user] = lambda: {  # type: ignore[attr-defined]
        "id": "user-1",
        "account_type": "job_seeker",
    }

    stub_store = StubSessionStore(history=[{"role": "assistant", "text": "Welcome back"}])

    monkeypatch.setattr(chat_route, "ChatSessionStore", lambda: stub_store)
    monkeypatch.setattr(chat_route, "get_chat_orchestrator", lambda: StubOrchestrator())

    yield

    app.dependency_overrides.pop(chat_route.get_current_user, None)  # type: ignore[attr-defined]


def test_websocket_streams_matches_and_tokens() -> None:
    client = TestClient(app)
    with client.websocket_connect("/api/chat/ws") as websocket:
        initial = websocket.receive_json()
        assert initial["type"] == ChatEventType.INFO.value

        summary_event = websocket.receive_json()
        assert summary_event["type"] == ChatEventType.SUMMARY.value

        history_event = websocket.receive_json()
        assert history_event["type"] == ChatEventType.HISTORY.value

        websocket.send_json({"message": "Hello"})

        match_event = websocket.receive_json()
        assert match_event["type"] == ChatEventType.MATCHES.value
        assert match_event["data"]["matches"][0]["label"] == "Backend Engineer"

        token_event = websocket.receive_json()
        assert token_event["type"] == ChatEventType.TOKEN.value
        assert token_event["data"]["text"] == "Hello"

        complete_event = websocket.receive_json()
        assert complete_event["type"] == ChatEventType.COMPLETE.value
