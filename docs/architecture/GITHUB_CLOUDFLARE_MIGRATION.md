# GitHub + Cloudflare Migration Specification

Status: DESIGN BASELINE — implementation and deployment not yet verified
Target repository: BudBudness/SMC-Agent-
Canonical branch: main
Migration branch: migration/github-cloudflare-control-plane

## 1. Non-negotiable platform boundary
- GitHub is the source-of-truth control plane: source, pull requests, Actions, tests, benchmark artifacts and release provenance.
- Cloudflare is the production platform: Workers, D1, R2, Queues, Pages/Workers delivery, DNS, Access and runtime observability as required.
- Vercel and Supabase are not target dependencies and must not appear in the final runtime, deployment, persistence or CI configuration.
- No live trading, broker connectivity, order placement or financial execution is in scope.

## 2. Runtime decomposition
The existing application combines a Next.js dashboard, a Python research engine, release-hosted research artifacts and Supabase persistence. These concerns must be separated before legacy configuration is removed.

### Dashboard and API
Deploy the dashboard as a Cloudflare-compatible Next.js application using the supported OpenNext Cloudflare adapter and Wrangler. Confirm compatibility against the actual Next.js version and Node APIs used by the application before selecting the final deployment mode. The Worker API is the only public application API.

### Research execution
The research engine is Python and must not be moved into a JavaScript Worker by translation-by-assumption. Run the canonical Python package on GitHub-hosted Actions runners. A Worker accepts and validates research requests, persists request state in D1, and places work on a Cloudflare Queue. A queue consumer dispatches a repository event to GitHub Actions using a narrowly scoped GitHub App installation token stored as a Worker secret. The workflow executes the Python engine, validates outputs, writes immutable artifacts to R2, and calls an authenticated Worker callback to finalize run state. All callbacks must be authenticated, idempotent and bound to a run ID plus source commit.

### Persistence
- D1 replaces Supabase tables for research runs, reports, hypotheses and evidence.
- R2 stores versioned, immutable research outputs, replay slices and benchmark artifacts.
- D1 records artifact keys, content hashes, dataset lineage, engine version, source commit and timestamps.
- R2 writes use temporary/staging keys followed by validated promotion or immutable versioned keys; never overwrite the only known-good artifact.
- Define and test D1 migrations, R2 retention, backup/export and restore before cutover.

### Delivery and CI
- GitHub Actions performs Python tests, TypeScript checks, Next.js/Cloudflare build validation, benchmark gates and deployment orchestration.
- Wrangler deploys the Cloudflare Worker and required resources from reviewed configuration.
- Production secrets are provisioned only in Cloudflare/GitHub secret stores; never committed.
- A release is identified by one Git commit SHA and a manifest of artifact hashes.

## 3. Required implementation sequence
1. Inventory current runtime routes, data models, engine entry points and deployment assumptions.
2. Define D1 schema and migrations matching current Supabase read/write behavior.
3. Implement Worker API contracts and D1 persistence, with integration tests.
4. Implement Queue dispatch, GitHub Actions execution, authenticated callback and idempotent retry handling.
5. Implement R2 artifact publishing/reading and verify checksums and lineage.
6. Adapt and build the dashboard for Cloudflare; replace same-origin Python function calls with the Worker/queue API contract.
7. Add Cloudflare preview deployment and end-to-end smoke tests.
8. Verify backup and restore, then perform a controlled production cutover.
9. Only after the replacement passes, remove Vercel configuration and all Supabase references/dependencies.
10. Verify the old providers are no longer used by workflows, runtime code, repository settings or deployed infrastructure.

## 4. Certification gates
### Gate A — Chronological benchmark
- Data sorted strictly by event time; deterministic replay.
- No future bars, future labels, revised candles or future macro data leak into features.
- Confirmed swing events become available only at their actual confirmation timestamp.
- Walk-forward evaluation uses chronological train/validation/test partitions.
- Freeze dataset version, code commit, parameters and artifact hashes.
- Report sample counts, coverage, exclusions and failure cases.

### Gate B — Human-verified benchmark
- Independent human annotations using a versioned annotation protocol.
- Annotators blinded to model output and future outcomes.
- Adjudication and inter-annotator agreement reported.
- Precision, recall, F1, confusion matrix and per-event-class results reported against the human reference set.
- Rule-generated labels must never be described as human ground truth.

### Gate C — Cloudflare production deployment
- Successful reviewed GitHub Actions deployment for the certified commit.
- Worker/Pages URL, resource bindings and runtime health verified.
- D1 migration and R2 artifact read/write checks pass.
- Queue dispatch, workflow execution and callback lifecycle pass.
- Backup/restore evidence and runtime error checks recorded.
- No Vercel or Supabase dependency remains in the deployed path.

### Gate D — Live browser verification
- Open the deployed Cloudflare URL in a real browser.
- Verify primary dashboard views, data loading, API requests, research run lifecycle and report/artifact access.
- Inspect browser console and network failures.
- Confirm responsive layout and research-only boundary.
- Record tested URL, commit SHA, UTC timestamp and evidence.

## 5. Cutover safety
Do not delete vercel.json, remove Supabase-backed code, drop tables, revoke credentials or change DNS before the replacement implementation is tested and a rollback path exists. These are migration/cutover operations, not preparatory cleanup. The final state must remove both providers; the intermediate migration branch may retain compatibility code until the replacement is ready.

## 6. Current known blockers
- app/api/research/route.ts still invokes /api/research_engine, relying on the Vercel Python-function route.
- The same route still reads/writes Supabase REST resources (smc_research_runs, smc_reports, smc_hypotheses, smc_evidence).
- vercel.json still defines the Python function deployment.
- .github/workflows/long-history-mtf.yml still watches vercel.json.
- app/page.tsx still labels research history as Supabase-persisted.
- No Cloudflare Wrangler/OpenNext configuration or D1 schema was present in the inspected repository files.
- No Cloudflare account/resource access was available to this execution environment at inspection time.

These blockers mean the provider migration is not complete and production certification remains withheld.