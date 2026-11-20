# Cloudflare Research API

This service is the Cloudflare control plane for Henryz SMC research jobs.

## Components

- Worker: authenticated HTTP API, GitHub App dispatch, queue consumer and callback.
- D1: research run state, reports, hypotheses, evidence and job events.
- Queue: durable dispatch buffer between request acceptance and GitHub Actions.
- R2: immutable JSON result artifacts.
- GitHub Actions: runs the canonical Python research engine at the exact source commit.

## Provision resources

Create these resources in the target Cloudflare account before deployment:

- D1 database: `henryz-smc-research`
- R2 bucket: `henryz-smc-research-results`
- Queue: `henryz-smc-research-jobs`
- Dead-letter Queue: `henryz-smc-research-jobs-dlq`

Update `wrangler.jsonc` with the real D1 database ID, Cloudflare Access team domain/application AUD, and the exact 40-character Git commit SHA deployed to this Worker as `GITHUB_SOURCE_COMMIT`. `GITHUB_DEFAULT_REF` remains the branch containing the workflow_dispatch definition (normally `main`). This separates the workflow-dispatch ref from the pinned engine source commit so every run is reproducible. The queue names and R2 bucket names are fixed by the configuration.

Apply the migration only after the D1 database exists:

```sh
cd cloudflare/research-api
npm install
npx wrangler d1 migrations apply henryz-smc-research --remote
```

Deploy after setting secrets:

```sh
npx wrangler secret put CALLBACK_SECRET
npx wrangler secret put GITHUB_APP_ID
npx wrangler secret put GITHUB_APP_INSTALLATION_ID
npx wrangler secret put GITHUB_APP_PRIVATE_KEY
npx wrangler deploy
```

The GitHub App installation must have access to this repository and the minimum required permissions: Actions (write) and Contents (read). Its private key is stored only as the Worker secret. The Worker mints short-lived installation tokens; no long-lived GitHub token is stored.

The GitHub Actions workflow also requires repository secrets `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `CLOUDFLARE_ACCOUNT_ID`, and `RESEARCH_WORKER_CALLBACK_SECRET`; repository variables `CLOUDFLARE_R2_BUCKET` and `RESEARCH_WORKER_CALLBACK_URL`. Use an R2-scoped access key, not an account-wide API token. The callback URL is the Worker URL plus `/internal/research-complete`.

Protect the Worker route with a Cloudflare Access application. Set `ACCESS_TEAM_DOMAIN` to the Access team hostname (without scheme) and `ACCESS_AUD` to the Access application AUD. The Worker verifies the Access JWT signature, issuer, audience and expiry. The internal callback uses a separate shared secret and bypasses the interactive Access JWT.

## Dispatch and result lifecycle

1. Authenticated client submits `POST /api/research` with `{ "action": "run", "instrument": "EURUSD", "parameters": { ... } }`.
2. Worker inserts a QUEUED D1 run and sends a queue message.
3. Queue consumer mints a short-lived GitHub App installation token and dispatches `.github/workflows/research-job.yml`.
4. Workflow checks out the requested commit and executes `scripts/run_research_job.py`.
5. Workflow writes `research/<run_id>/<workflow_run_id>-<attempt>/result.json` to R2 and sends the checksum to the Worker callback.
6. Worker verifies the object exists and its SHA-256 checksum, then marks the D1 run COMPLETED.
7. Client polls `GET /api/research?resource=run&run_id=<id>`; the result is included after completion.

## Operational constraints

- The workflow_dispatch workflow must exist on the repository's default branch before the Worker can dispatch it. Merge the migration PR before enabling queue dispatch.
- The first implementation supports EURUSD only, matching the current Python engine's allowed dataset.
- No Vercel or Supabase service is used by this new service.
- No existing production data is migrated or deleted by these files.
- Do not remove the legacy Next.js route until the dashboard is switched to this API and end-to-end verification passes.
- Provisioning, migrations, secrets and deployment are intentionally not run by CI. They require the real Cloudflare account resources and scoped credentials.
