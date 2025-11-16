"""Tests for chat match normalisation and summaries."""

from __future__ import annotations

from app.ai.chat.utils import AUDIENCE_EMPLOYER, AUDIENCE_JOB_SEEKER, prepare_matches


def test_prepare_matches_job_seeker_includes_metadata_and_reasons() -> None:
    matches = [
        {
            "job_id": "j1",
            "title": "Senior Backend Engineer",
            "company": "Initech",
            "location": "Austin, TX",
            "match_score": 0.82,
            "vector_score": 0.76,
            "skills_required": ["Python", "FastAPI"],
            "score_breakdown": {
                "skills_overlap": 0.92,
                "location_match": 1.0,
            },
            "source": "vector",
        }
    ]

    normalised, summary = prepare_matches(matches, audience=AUDIENCE_JOB_SEEKER)

    assert len(normalised) == 1
    item = normalised[0]
    assert item["id"] == "j1"
    assert item["label"] == "Senior Backend Engineer"
    assert item["subtitle"] == "Initech | Austin, TX"
    assert item["match_score"] == 0.82
    assert item["vector_score"] == 0.76
    assert "skills overlap 92%" in item["reasons"]
    assert item["metadata"]["skills_required"] == ["Python", "FastAPI"]
    assert "match 82%" in summary
    assert "skills overlap" in summary


def test_prepare_matches_employer_surfaces_experience() -> None:
    matches = [
        {
            "candidate_id": "c1",
            "name": "Jordan Lee",
            "location": "Remote",
            "experience_years": 5,
            "match_score": 0.71,
            "score_breakdown": {
                "skills_overlap": 0.8,
                "experience_alignment": 0.9,
            },
        }
    ]

    normalised, summary = prepare_matches(matches, audience=AUDIENCE_EMPLOYER)

    assert normalised[0]["subtitle"] == "Remote | 5 yrs exp"
    assert "match 71%" in summary
    assert "experience alignment" in summary


def test_prepare_matches_handles_empty_list() -> None:
    normalised, summary = prepare_matches([], audience=AUDIENCE_JOB_SEEKER)

    assert normalised == []
    assert summary == "No matches available yet."
