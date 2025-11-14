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
        query = _message.strip() or "your recent request"
        return {
            "type": ChatEventType.TOKEN.value,
            "data": {
                "text": f"Stub: showing example roles relevant to {query}.",
                "matches": [
                    {
                        "job_id": "sample-job-1",
                        "title": "AI Solutions Engineer",
                        "match_score": 0.82,
                    },
                    {
                        "job_id": "sample-job-2",
                        "title": "Data Scientist",
                        "match_score": 0.78,
                    },
                ],
            },
        }
