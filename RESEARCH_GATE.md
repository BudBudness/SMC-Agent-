# Research Gate — Henryz SMC Intelligence

## Certification status
**NOT CERTIFIED.** The four certification gates below are independent and must all pass against the same release commit and immutable dataset/artifact manifest.

The product is a research and intelligence system only. No broker integration, order placement, live trading, paper trading or position management is in scope.

## Gate 1 — Chronological benchmark
- [ ] Chronological replay is deterministic and strictly ordered by event time.
- [ ] No look-ahead leakage, including confirmed-swing right-side confirmation timing.
- [ ] Walk-forward train/validation/test partitions are chronological.
- [ ] Dataset, parameters, source commit and output hashes are versioned.
- [ ] Sample counts, exclusions, coverage and failure cases are reported.

## Gate 2 — Human-verified benchmark
- [ ] Versioned annotation protocol and event definitions.
- [ ] Independent annotations blinded to model output and future outcomes.
- [ ] Adjudication and inter-annotator agreement reported.
- [ ] Precision, recall, F1, confusion matrix and per-class metrics reported.
- [ ] Rule-generated labels are explicitly distinguished from human ground truth.

## Gate 3 — Cloudflare production deployment
- [ ] GitHub Actions deployment succeeds for the certified commit.
- [ ] Cloudflare Worker/dashboard health and runtime bindings verified.
- [ ] D1 migrations and persistence integration tests pass.
- [ ] R2 artifact integrity and lineage checks pass.
- [ ] Queue-to-GitHub-Actions research execution and callback lifecycle pass.
- [ ] Backup/restore and rollback evidence recorded.
- [ ] No Vercel or Supabase dependency remains in the production path.

## Gate 4 — Live browser verification
- [ ] Deployed Cloudflare URL opened in a real browser.
- [ ] Dashboard views, API calls, research lifecycle and artifact access verified.
- [ ] Browser console and network errors inspected.
- [ ] Responsive layout and research-only boundary verified.
- [ ] URL, commit SHA, UTC timestamp and evidence recorded.

## Migration architecture
The canonical target is GitHub + Cloudflare. See docs/architecture/GITHUB_CLOUDFLARE_MIGRATION.md for the runtime decomposition, execution model, persistence mapping, cutover sequence and safety controls.

GitHub Actions runs the Python research engine. Cloudflare Workers provide the public API and orchestration; Queues dispatch work; D1 stores transactional research metadata; R2 stores immutable research artifacts. The dashboard is configured for Cloudflare Workers using OpenNext and Wrangler; production build, deployment and live browser verification remain open.

## Migration safety
Vercel and Supabase are not target providers. The migration branch removes Supabase from the application API and removes the dashboard's Vercel Python-function dependency. vercel.json remains temporarily as migration residue until Cloudflare deployment and rollback verification pass. Do not remove the existing runtime path until the Cloudflare replacement has passed integration tests and a rollback path is verified. Remove all Vercel/Supabase files, code, secrets, workflows and infrastructure references as part of the completed cutover—not as an unverified partial deletion.

## Research limitations
Historical analogue similarity is descriptive and does not establish causality or future direction. No profitability, predictive-accuracy, recommendation or live-readiness claim is made without the corresponding independently validated evidence.

## Current release artifacts
The long-history workflow currently publishes:
- EURUSD_M1_normalized.csv.gz
- EURUSD_M1_dashboard.csv.gz
- EURUSD_MTF_dashboard.json.gz
- EURUSD_research_report.json
- mtf_coverage.json
- mtf_substantive_evaluation.json
- labelled-eurusd.json

Artifact publication to GitHub Releases is not a substitute for the planned Cloudflare R2 production artifact store.