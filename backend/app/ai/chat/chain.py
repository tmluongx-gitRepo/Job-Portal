"""LangChain v1 runnable scaffolding for chat agents."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableLambda


def _job_seeker_stub(inputs: dict[str, Any]) -> dict[str, Any]:
    message = str(inputs.get("message", "")).strip()
    query = message or "your latest request"
    return {
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
    }


def _employer_stub(inputs: dict[str, Any]) -> dict[str, Any]:
    message = str(inputs.get("message", "")).strip()
    query = message or "your open roles"
    return {
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
    }


def build_job_seeker_chain() -> RunnableLambda:
    """Return a LangChain runnable for job seeker queries (stub)."""

    return RunnableLambda(_job_seeker_stub)


def build_employer_chain() -> RunnableLambda:
    """Return a LangChain runnable for employer queries (stub)."""

    return RunnableLambda(_employer_stub)
