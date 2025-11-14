"""LangChain v1 agent that handles employer conversations."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from app.ai.chat.chain import employer_response, employer_stream
from app.ai.chat.constants import ChatEventType


class EmployerAgent:
    """LangChain-backed agent for employer oriented conversations."""

    async def stream(
        self, message: str, context: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], str, AsyncIterator[str]]:
        matches, summary, factory = await employer_stream(message, context)
        return list(matches), summary, factory()

    async def generate(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Return structured data notes for the employer conversation."""

        payload = await employer_response(message, context)
        return {
            "type": ChatEventType.TOKEN.value,
            "data": payload,
        }
