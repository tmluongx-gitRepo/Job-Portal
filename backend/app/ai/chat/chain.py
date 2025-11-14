"""LangChain v1 runnable scaffolding for chat agents."""

from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda

JOB_SEEKER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful agent assisting job seekers."),
        ("human", "{message}"),
    ]
)

EMPLOYER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful agent assisting employers."),
        ("human", "{message}"),
    ]
)


def _job_seeker_stub(prompt_value: Any) -> dict[str, Any]:
    messages = prompt_value.to_messages()
    user_message = messages[-1].content.strip()
    query = user_message or "your latest request"
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


def _employer_stub(prompt_value: Any) -> dict[str, Any]:
    messages = prompt_value.to_messages()
    user_message = messages[-1].content.strip()
    query = user_message or "your open roles"
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


def build_job_seeker_chain() -> Runnable[dict[str, Any], dict[str, Any]]:
    """Return a LangChain runnable for job seeker queries (stub)."""

    return JOB_SEEKER_PROMPT | RunnableLambda(_job_seeker_stub)


def build_employer_chain() -> Runnable[dict[str, Any], dict[str, Any]]:
    """Return a LangChain runnable for employer queries (stub)."""

    return EMPLOYER_PROMPT | RunnableLambda(_employer_stub)
