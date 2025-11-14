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
        query = _message.strip() or "your open roles"
        return {
            "type": ChatEventType.TOKEN.value,
            "data": {
                "text": f"Stub: returning example candidates relevant to {query}.",
                "matches": [
                    {
                        "candidate_id": "sample-candidate-1",
                        "name": "Jordan Lee",
                        "match_score": 0.84,
                    },
                    {
                        "candidate_id": "sample-candidate-2",
                        "name": "Casey Morgan",
                        "match_score": 0.8,
                    },
                ],
            },
        }
