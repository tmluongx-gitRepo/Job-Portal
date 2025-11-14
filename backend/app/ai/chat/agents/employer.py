"""LangChain v1 agent that handles employer conversations (scaffold)."""

from __future__ import annotations

from typing import Any


class EmployerAgent:
    """Placeholder implementation for the employer focused agent."""

    def __init__(self) -> None:
        self._ready = False

    async def generate(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Return a structured response for the employer.

        The real implementation will query ChromaDB, perform candidate matching
        and stream LangChain outputs. For now we raise to make the stub explicit.
        """
        raise NotImplementedError("EmployerAgent.generate is not yet implemented")
