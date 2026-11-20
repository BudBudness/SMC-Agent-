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
Do not merge the migration branch into main, drop legacy data, revoke credentials or change production DNS before the Cloudflare replacement is deployed, tested and a rollback path exists. The migration branch removes vercel.json and the Supabase-backed application route because those code paths have been replaced; main remains unchanged until the pull request is merged. Preserve any legacy database data until export, reconciliation and restore verification are complete.

## 6. Current migration state and blockers

### Completed in the migration branch
- app/api/research/route.ts now proxies run, report, hypothesis and evidence operations to the Cloudflare research Worker through a service binding. It no longer calls the Vercel Python route or Supabase REST API.
- app/page.tsx no longer identifies Supabase as the research-history provider and now polls asynchronous research jobs.
- The Python engine remains canonical and is executed by scripts/run_research_job.py from the dispatched GitHub Actions workflow.
- D1 schema, Worker API, Queue dispatch, GitHub App token minting, R2 result publishing, checksum metadata, callback lifecycle and dead-letter handling are implemented as code.
- Root OpenNext/Wrangler configuration and a Cloudflare service binding are present.
- GitHub Actions validation workflows are defined for the Worker, D1 SQL and OpenNext dashboard build.

### Outstanding blockers
- vercel.json has been removed from the isolated migration branch. The existing main branch remains unchanged until the pull request is merged.
- No Cloudflare D1 database, R2 bucket, Queues, Access application or Worker deployment has been provisioned or verified from this execution environment.
- wrangler.jsonc contains a D1 database ID placeholder and Access settings placeholders; runtime secrets still need secure provisioning.
- The GitHub App used by the Worker must be installed with Actions write and Contents read permissions; its private key and installation identifiers are not provisioned.
- GitHub Actions requires scoped R2 credentials and the Worker callback secret in repository secrets, plus the R2 bucket and callback URL as repository variables.
- The research-job workflow_dispatch file must exist on the default branch before the Worker can dispatch jobs; this migration branch must be merged only after the production rollout sequence is approved.
- No Supabase data export/import has been performed. Existing historical run, hypothesis, report and evidence records must be exported and reconciled before the legacy database is retired.
- The Cloudflare account connector is not available in this execution environment, preventing resource provisioning, migrations, deployment and live browser verification.

The provider migration is therefore implemented as an isolated code baseline but not deployed. Production certification remains withheld.
