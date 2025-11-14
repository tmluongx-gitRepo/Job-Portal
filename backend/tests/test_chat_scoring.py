"""Unit tests for chat scoring helpers."""

from __future__ import annotations

from app.ai.chat.tools.scoring import calculate_candidate_matches, calculate_job_matches


def test_calculate_job_matches_blends_vector_and_metadata() -> None:
    resume_features = {
        "skills": ["Python", "FastAPI", "MongoDB"],
        "location": "Austin, TX",
        "industry": "Software",
        "experience_years": 5,
    }

    jobs = [
        {
            "job_id": "j1",
            "title": "Senior Backend Engineer",
            "skills_required": ["Python", "FastAPI", "MongoDB"],
            "location": "Austin, TX",
            "industry": "Software",
            "experience_required": "5+ years",
            "match_score": 0.55,  # Vector similarity from Chroma
        },
        {
            "job_id": "j2",
            "title": "Data Analyst",
            "skills_required": ["SQL", "Tableau"],
            "location": "Dallas, TX",
            "industry": "Analytics",
            "match_score": 0.85,
        },
    ]

    ranked = calculate_job_matches(resume_features=resume_features, jobs=jobs)

    assert ranked[0]["job_id"] == "j1"
    assert ranked[0]["match_score"] > ranked[1]["match_score"]
    assert ranked[0]["vector_score"] == 0.55
    assert "skills_overlap" in ranked[0]["score_breakdown"]
    # Metadata should contribute enough that j1 outranks the higher vector-only score
    assert ranked[0]["match_score"] >= 0.65


def test_calculate_job_matches_handles_metadata_only() -> None:
    resume_features = {"skills": ["Python"], "location": "Remote"}
    jobs = [
        {
            "job_id": "j3",
            "title": "Remote Python Developer",
            "skills_required": ["Python", "APIs"],
            "location": "Remote",
        }
    ]

    ranked = calculate_job_matches(resume_features=resume_features, jobs=jobs)
    assert ranked[0]["match_score"] > 0.5
    assert ranked[0]["vector_score"] == 0.0


def test_calculate_candidate_matches_prioritises_contextual_fit() -> None:
    job_features = {
        "skills": ["Python", "FastAPI"],
        "location": "Remote",
        "industry": "Software",
        "experience_years": 3,
    }

    candidates = [
        {
            "candidate_id": "c1",
            "name": "Jordan Lee",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "location": "Remote",
            "industry": "Software",
            "experience_years": 5,
            "match_score": 0.5,
        },
        {
            "candidate_id": "c2",
            "name": "Casey Morgan",
            "skills": ["SQL", "Tableau"],
            "location": "Chicago",
            "industry": "Analytics",
            "experience_years": 2,
            "match_score": 0.8,
        },
    ]

    ranked = calculate_candidate_matches(job_features=job_features, candidates=candidates)

    assert ranked[0]["candidate_id"] == "c1"
    assert ranked[0]["match_score"] > ranked[1]["match_score"]
    assert "skills_overlap" in ranked[0]["score_breakdown"]
    breakdown = ranked[1]["score_breakdown"]
    assert breakdown.get("skills_overlap", 0.0) == 0.0
    assert breakdown.get("location_match", 0.0) == 0.0
