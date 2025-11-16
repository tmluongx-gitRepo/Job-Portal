"""CLI helper to seed job/candidate embeddings into Chroma."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from collections.abc import Sequence

from app.config import settings
from app.tasks.embedding_tasks import process_candidates, process_jobs

LOGGER = logging.getLogger("app.scripts.ingest_embeddings")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest job and/or candidate embeddings into Chroma using existing pipeline helpers.",
    )
    parser.add_argument(
        "--jobs",
        nargs="*",
        help="Optional list of job IDs to ingest. Omit to process all jobs.",
    )
    parser.add_argument(
        "--candidates",
        nargs="*",
        help="Optional list of candidate IDs to ingest. Omit to process all candidates.",
    )
    parser.add_argument(
        "--skip-jobs",
        action="store_true",
        help="Skip job embeddings even if --jobs is provided.",
    )
    parser.add_argument(
        "--skip-candidates",
        action="store_true",
        help="Skip candidate embeddings even if --candidates is provided.",
    )
    return parser


async def _run(args: argparse.Namespace) -> None:
    if not settings.OPENAI_API_KEY:
        LOGGER.warning(
            "OPENAI_API_KEY is not configured; embeddings will use deterministic fallback vectors."
        )

    jobs: Sequence[str] | None = None if args.jobs == [] else args.jobs
    candidates: Sequence[str] | None = None if args.candidates == [] else args.candidates

    if not args.skip_jobs:
        LOGGER.info(
            "Starting job embedding ingestion", extra={"job_count": len(jobs) if jobs else "all"}
        )
        await process_jobs(list(jobs) if jobs is not None else None)
        LOGGER.info("Job embedding ingestion completed")

    if not args.skip_candidates:
        LOGGER.info(
            "Starting candidate embedding ingestion",
            extra={"candidate_count": len(candidates) if candidates else "all"},
        )
        await process_candidates(list(candidates) if candidates is not None else None)
        LOGGER.info("Candidate embedding ingestion completed")


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO)
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.skip_jobs and args.skip_candidates:
        LOGGER.info("Nothing to do; both job and candidate ingestion skipped")
        return 0

    try:
        asyncio.run(_run(args))
    except KeyboardInterrupt:  # pragma: no cover - operator convenience
        LOGGER.warning("Embedding ingestion interrupted")
        return 130
    except Exception as exc:  # pragma: no cover - operational visibility
        LOGGER.exception("Embedding ingestion failed", exc_info=exc)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
