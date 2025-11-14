"""Matching score utilities for jobs and candidates (scaffold)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def calculate_job_matches(
    *, resume_features: Mapping[str, object], jobs: Sequence[Mapping[str, object]]
) -> Sequence[Mapping[str, object]]:
    """Return jobs ranked by relevance for a job seeker."""
    raise NotImplementedError("calculate_job_matches is not yet implemented")


def calculate_candidate_matches(
    *, job_features: Mapping[str, object], candidates: Sequence[Mapping[str, object]]
) -> Sequence[Mapping[str, object]]:
    """Return candidates ranked by relevance for an employer."""
    raise NotImplementedError("calculate_candidate_matches is not yet implemented")
