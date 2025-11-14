"""LangChain v1 agent that handles job seeker conversations (scaffold)."""

from __future__ import annotations

from typing import Any

from app.ai.chat.constants import ChatEventType


class JobSeekerAgent:
    """Placeholder implementation for the job seeker focused agent."""

    def __init__(self) -> None:
        self._ready = False

    async def generate(self, _message: str, _context: dict[str, Any]) -> dict[str, Any]:
        """Return a stubbed structured response for the job seeker."""
        return {
            "type": ChatEventType.TOKEN.value,
            "data": {
                "text": "Job seeker agent not yet implemented",
                "matches": [],
            },
        }
