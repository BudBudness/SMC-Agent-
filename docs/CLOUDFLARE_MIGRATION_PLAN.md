# Cloudflare Migration Plan — Henryz SMC Intelligence

Status: architecture and execution specification; no production deployment or database migration claimed. This remains a research/intelligence system, not a trading or execution system.

## Target platform
- Next.js research dashboard deployed to Cloudflare Workers through OpenNext, subject to compatibility validation for the current app.
- D1 for research-run metadata, reports, hypotheses, evidence and audit history.
- R2 for versioned research artifacts and large replay payloads; immutable release artifacts remain content-addressed/versioned.
- Cloudflare Queues for asynchronous research-run requests and durable status transitions.
- A separately deployed Python research runtime for the canonical pandas/numpy pipeline. The Python engine must not be rewritten in JavaScript or moved into a latency-sensitive Worker request without benchmark evidence.
- Cloudflare Containers is the preferred candidate for the Python runtime if available in the target account/region and proven to support the repository's Python 3.12, pandas 2.3 and numpy 2.2 dependencies. Otherwise, use a separately approved Cloudflare-compatible compute target; do not silently fall back to Vercel.
- GitHub Actions for deterministic validation, dataset publishing and release gates.

## Provider retirement
- Remove the hard-coded Supabase REST endpoint and publishable key from `app/api/research/route.ts`.
- Replace direct Supabase REST calls with a typed repository layer backed by D1.
- Replace Vercel-specific config and 300-second function assumptions with explicit Cloudflare runtime, queue, timeout and job-status design.
- Preserve the GitHub Release dataset artifacts only as a transitional source; evaluate R2 artifact mirroring with checksums, lineage and immutable version identifiers.
- Never place GitHub tokens, API keys or provider secrets in source code.

## Research execution lifecycle
1. Authenticated research request is validated and assigned an idempotency key.
2. Worker records a queued run in D1 and enqueues a job.
3. Python runtime fetches a pinned dataset artifact, validates source lineage and executes the canonical pipeline.
4. Large report/replay payloads are stored in R2; D1 stores metadata, status, checksums and bounded queryable summaries.
5. Worker exposes authorized run status and report endpoints.
6. Failed jobs are retryable without duplicate completed runs; each state transition is auditable.

## Security and data integrity
- This is not a live-trading system; no broker/exchange order endpoints or transaction capability are introduced.
- Require authenticated access for research execution and private run history; enforce owner/team authorization server-side.
- Pin artifact versions and verify checksums before processing.
- Apply request bounds, concurrency controls and job timeouts. Do not trust client-supplied result objects.
- No existing Supabase data export or verified run-history backup is established by this plan. Do not claim data recovery or import.

## Acceptance gates
1. Remove Supabase endpoint/key and Vercel-specific configuration from runtime and docs.
2. D1 migrations and repository-layer tests pass.
3. Python runtime compatibility benchmark demonstrates successful canonical EURUSD pipeline execution with measured memory, CPU and wall time.
4. Queue retry, idempotency, failure, cancellation and status-transition tests pass.
5. Dataset checksum, lineage, report schema and replay integrity tests pass.
6. Worker build/dry-run and dashboard browser E2E pass.
7. D1 backup restore and R2 artifact recovery are demonstrated before production cutover.

## Critical compatibility gate
The existing Python engine imports pandas and numpy, downloads and decompresses a long-history gzip CSV, and runs a parameterized pipeline. Cloudflare Workers' request runtime is not an assumed fit for this workload. The compute target must pass the benchmark gate before implementation is selected or production is enabled. Cloudflare account provisioning and production deployment require an authorized Cloudflare control-plane session.
