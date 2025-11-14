# Chat Agent Roadmap (Backend)

This note captures outstanding work before the conversational agent can be production-ready.

## Embedding Ingestion & Scoring
- [ ] Build a background job (Celery or FastAPI task) that generates embeddings for resumes and jobs using `OPENAI_EMBEDDING_MODEL` and upserts them into Chroma.
- [ ] Store denormalised metadata (skills, location, industry, seniority) alongside each embedding.
- [ ] Replace fallback scoring with actual similarity fusion: `score = alpha * (1 - distance) + beta * metadata_score(rows)`.
- [ ] Add data refresh triggers: when a resume/job is updated, regenerate embeddings.
- [ ] Provide seed/backfill script to ingest existing data into Chroma.

## OpenAI Streaming & Reliability
- [ ] Switch chains to use streaming ChatOpenAI by default when `OPENAI_API_KEY` present.
- [ ] Add retry/backoff around streaming calls; surface `error` events to clients on failure.
- [ ] Support configurable temperature and response length (config + chain inputs).
- [ ] Add tracing via LangSmith when `LANGCHAIN_TRACING_ENABLED` is true.

## Frontend Contract
- [ ] Document event schema in `README.md` or dedicated `docs/chat_protocol.md` for frontend consumers.
- [ ] Provide sample payloads and sequencing diagrams for typical flows (initial connect, job seeker query, employer query).
- [ ] Coordinate with frontend to ensure messages from UI map to backend expectations (`message`, optional filters, etc.).

## Quality & Observability
- [ ] Unit tests for metadata scoring helpers once Mongo collections available.
- [ ] Integration test that exercises the websocket (mocking LangChain/Redis) to verify event sequencing.
- [ ] Add structured logging around orchestrator decisions and summary updates.
