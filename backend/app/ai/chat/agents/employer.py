"""LangChain v1 agent that handles employer conversations (scaffold)."""

from __future__ import annotations

from typing import Any

from app.ai.chat.constants import ChatEventType


class EmployerAgent:
    """Placeholder implementation for the employer focused agent."""

    def __init__(self) -> None:
        self._ready = False

    async def generate(self, _message: str, _context: dict[str, Any]) -> dict[str, Any]:
        """Return a stubbed structured response for the employer."""
        return {
            "type": ChatEventType.TOKEN.value,
            "data": {
                "text": "Employer agent not yet implemented",
                "matches": [],
            },
        }
