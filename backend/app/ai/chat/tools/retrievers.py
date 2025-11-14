"""Retrieval helpers for chat agents."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


async def fetch_job_matches_for_user(
    *, _user_context: dict, limit: int = 3
) -> Sequence[dict[str, Any]]:
    """Fetch candidate job matches for a job seeker.

    Current implementation emits placeholder matches. When resume embeddings are
    ready, this function will query ChromaDB using the parsed resume vector and
    return ranked jobs.
    """

    # TODO: integrate resume-based retrieval from ChromaDB
    return [
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
        {
            "job_id": "sample-job-3",
            "title": "Backend Developer",
            "match_score": 0.74,
        },
    ][:limit]


async def fetch_candidate_matches_for_employer(
    *, _user_context: dict, limit: int = 3
) -> Sequence[dict[str, Any]]:
    """Fetch candidate matches for an employer's current openings."""

    # TODO: integrate job-based retrieval from ChromaDB
    return [
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
        {
            "candidate_id": "sample-candidate-3",
            "name": "Taylor Kim",
            "match_score": 0.77,
        },
    ][:limit]
