"""ChromaDB + Redis-backed retriever utilities (scaffold)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


async def fetch_resume_chunks(*, resume_id: str) -> Sequence[dict[str, Any]]:
    """Return vector chunks associated with a resume.

    Real implementation will query ChromaDB using LangChain v1 retrievers.
    """
    raise NotImplementedError("fetch_resume_chunks is not yet implemented")


async def fetch_job_chunks(*, job_ids: Sequence[str]) -> Sequence[dict[str, Any]]:
    """Return vector chunks associated with jobs."""
    raise NotImplementedError("fetch_job_chunks is not yet implemented")
