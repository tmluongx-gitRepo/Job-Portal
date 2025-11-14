"""LangChain v1 agent that handles employer conversations."""

from __future__ import annotations

from typing import Any

from app.ai.chat.chain import employer_response
from app.ai.chat.constants import ChatEventType


class EmployerAgent:
    """LangChain-backed agent for employer oriented conversations."""

    async def generate(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Return structured data notes for the employer conversation."""

        payload = await employer_response(message, context)
        return {
            "type": ChatEventType.TOKEN.value,
            "data": payload,
        }
