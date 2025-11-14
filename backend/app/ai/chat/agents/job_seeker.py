"""LangChain v1 agent that handles job seeker conversations (scaffold)."""

from __future__ import annotations

from typing import Any


class JobSeekerAgent:
    """Placeholder implementation for the job seeker focused agent."""

    def __init__(self) -> None:
        self._ready = False

    async def generate(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Return a structured response for the job seeker.

        The real implementation will query ChromaDB, perform matching and invoke
        LangChain runtimes. For now we raise to make the stub explicit.
        """
        raise NotImplementedError("JobSeekerAgent.generate is not yet implemented")
