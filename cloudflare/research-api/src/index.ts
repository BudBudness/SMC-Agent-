export interface ResearchJob {
  run_id: string;
  source_commit: string;
  parameters: Record<string, unknown>;
}

interface Env {
  DB: D1Database;
  RESEARCH_JOBS: Queue<ResearchJob>;
  RESULTS: R2Bucket;
  ACCESS_TEAM_DOMAIN: string;
  ACCESS_AUD: string;
  CALLBACK_SECRET: string;
  GITHUB_APP_ID: string;
  GITHUB_APP_INSTALLATION_ID: string;
  GITHUB_APP_PRIVATE_KEY: string;
  GITHUB_REPOSITORY: string;
  GITHUB_WORKFLOW_FILE: string;
  GITHUB_DEFAULT_REF: string;
}

const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });

const b64url = (value: string | ArrayBuffer) => {
  const bytes = typeof value === "string" ? new TextEncoder().encode(value) : new Uint8Array(value);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
};

function decodePart(value: string): Record<string, any> {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "=".repeat((4 - normalized.length % 4) % 4);
  return JSON.parse(atob(padded));
}

async function verifyAccess(request: Request, env: Env): Promise<boolean> {
  const token = request.headers.get("Cf-Access-Jwt-Assertion");
  if (!token) return false;
  try {
    const [encodedHeader, encodedPayload, encodedSignature] = token.split(".");
    const header = decodePart(encodedHeader);
    const payload = decodePart(encodedPayload);
    if (header.alg !== "RS256" || !header.kid || payload.iss !== `https://${env.ACCESS_TEAM_DOMAIN}`) return false;
    if (!Array.isArray(payload.aud) || !payload.aud.includes(env.ACCESS_AUD)) return false;
    const now = Math.floor(Date.now() / 1000);
    if (typeof payload.exp !== "number" || payload.exp <= now || (typeof payload.nbf === "number" && payload.nbf > now)) return false;

    const certsResponse = await fetch(`https://${env.ACCESS_TEAM_DOMAIN}/cdn-cgi/access/certs`);
    if (!certsResponse.ok) return false;
    const certs = await certsResponse.json() as { keys: JsonWebKey[] };
    const jwk = certs.keys.find((key: any) => key.kid === header.kid);
    if (!jwk) return false;

    const publicKey = await crypto.subtle.importKey(
      "jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]
    );
    const normalizedSignature = encodedSignature.replace(/-/g, "+").replace(/_/g, "/");
    const signature = Uint8Array.from(atob(normalizedSignature + "=".repeat((4 - normalizedSignature.length % 4) % 4)), c => c.charCodeAt(0));
    return crypto.subtle.verify(
      "RSASSA-PKCS1-v1_5", publicKey, signature,
      new TextEncoder().encode(`${encodedHeader}.${encodedPayload}`)
    );
  } catch {
    return false;
  }
}

function derLength(length: number): Uint8Array {
  if (length < 128) return new Uint8Array([length]);
  if (length < 256) return new Uint8Array([0x81, length]);
  return new Uint8Array([0x82, (length >> 8) & 0xff, length & 0xff]);
}

function wrapPkcs1AsPkcs8(pkcs1: Uint8Array): Uint8Array {
  const algorithm = new Uint8Array([0x30,0x0d,0x06,0x09,0x2a,0x86,0x48,0x86,0xf7,0x0d,0x01,0x01,0x01,0x05,0x00]);
  const version = new Uint8Array([0x02,0x01,0x00]);
  const octetLength = derLength(pkcs1.length);
  const octetHeader = new Uint8Array([0x04, ...octetLength]);
  const innerLength = version.length + algorithm.length + octetHeader.length + pkcs1.length;
  const sequenceHeader = new Uint8Array([0x30, ...derLength(innerLength)]);
  const result = new Uint8Array(sequenceHeader.length + innerLength);
  let offset = 0;
  for (const part of [sequenceHeader, version, algorithm, octetHeader, pkcs1]) {
    result.set(part, offset);
    offset += part.length;
  }
  return result;
}

async function githubInstallationToken(env: Env): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  const header = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const payload = b64url(JSON.stringify({
    iat: now - 30, exp: now + 540, iss: env.GITHUB_APP_ID
  }));
  const unsigned = `${header}.${payload}`;
  const pem = env.GITHUB_APP_PRIVATE_KEY.replace(/\\n/g, "\n").trim();
  const isPkcs1 = pem.includes("BEGIN RSA PRIVATE KEY");
  const encodedKey = pem.replace(/-----BEGIN [A-Z ]+PRIVATE KEY-----|-----END [A-Z ]+PRIVATE KEY-----|\s/g, "");
  const rawKey = Uint8Array.from(atob(encodedKey), c => c.charCodeAt(0));
  const binary = isPkcs1 ? wrapPkcs1AsPkcs8(rawKey) : rawKey;
  const key = await crypto.subtle.importKey(
    "pkcs8", binary, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]
  );
  const signature = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(unsigned));
  const appJwt = `${unsigned}.${b64url(signature)}`;
  const response = await fetch(
    `https://api.github.com/app/installations/${env.GITHUB_APP_INSTALLATION_ID}/access_tokens`,
    { method: "POST", headers: { authorization: `Bearer ${appJwt}`, accept: "application/vnd.github+json", "x-github-api-version": "2022-11-28", "user-agent": "henryz-smc-cloudflare-worker" } }
  );
  if (!response.ok) throw new Error(`GitHub App token exchange failed: ${response.status}`);
  const body = await response.json() as { token: string };
  return body.token;
}

async function dispatchResearch(job: ResearchJob, env: Env): Promise<void> {
  const token = await githubInstallationToken(env);
  const response = await fetch(
    `https://api.github.com/repos/${env.GITHUB_REPOSITORY}/actions/workflows/${env.GITHUB_WORKFLOW_FILE}/dispatches`,
    {
      method: "POST",
      headers: { authorization: `Bearer ${token}`, accept: "application/vnd.github+json", "content-type": "application/json", "x-github-api-version": "2022-11-28", "user-agent": "henryz-smc-cloudflare-worker" },
      body: JSON.stringify({
        ref: env.GITHUB_DEFAULT_REF,
        inputs: {
          run_id: job.run_id,
          source_commit: job.source_commit,
          parameters_json: JSON.stringify(job.parameters),
        },
      }),
    }
  );
  if (!response.ok) throw new Error(`GitHub workflow dispatch failed: ${response.status} ${await response.text()}`);
}

async function recordEvent(env: Env, runId: string, type: string, detail: unknown = {}) {
  await env.DB.prepare(
    "INSERT INTO research_job_events (id, run_id, event_type, detail_json) VALUES (?, ?, ?, ?)"
  ).bind(crypto.randomUUID(), runId, type, JSON.stringify(detail)).run();
}

async function handleApi(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  if (url.pathname === "/health") return json({ ok: true, service: "henryz-smc-research-api" });

  if (request.method === "GET") {
    const resource = url.searchParams.get("resource") || "runs";
    if (resource === "run") {
      const runId = url.searchParams.get("run_id");
      if (!runId) return json({ error: "run_id is required" }, 400);
      const row = await env.DB.prepare("SELECT * FROM research_runs WHERE id = ?").bind(runId).first<any>();
      if (!row) return json({ error: "Run not found" }, 404);
      let result = null;
      if (row.result_key) { const object = await env.RESULTS.get(row.result_key); if (object) result = await object.json(); }
      return json({ run: { ...row, parameters: JSON.parse(row.parameters_json) }, result });
    }
    if (resource === "runs") {
      const result = await env.DB.prepare(
        "SELECT id, instrument, dataset, status, parameters_json, result_key, result_sha256, error, source_commit, created_at, started_at, completed_at, updated_at FROM research_runs ORDER BY created_at DESC LIMIT 100"
      ).all();
      return json(result.results);
    }
    if (resource === "hypotheses") {
      const result = await env.DB.prepare("SELECT * FROM research_hypotheses ORDER BY created_at DESC LIMIT 500").all();
      return json(result.results);
    }
    if (resource === "evidence") {
      const result = await env.DB.prepare("SELECT * FROM research_evidence ORDER BY created_at DESC LIMIT 500").all();
      return json(result.results);
    }
    if (resource === "report") {
      const runId = url.searchParams.get("run_id");
      if (!runId) return json({ error: "run_id is required" }, 400);
      const row = await env.DB.prepare("SELECT result_key, result_sha256 FROM research_runs WHERE id = ?").bind(runId).first<any>();
      if (!row?.result_key) return json({ error: "Research result is not ready" }, 404);
      const object = await env.RESULTS.get(row.result_key);
      if (!object) return json({ error: "Research artifact is missing" }, 404);
      return new Response(object.body, { headers: { "content-type": "application/json", "cache-control": "no-store", "etag": row.result_sha256 || "" } });
    }
    return json({ error: "Unknown resource" }, 400);
  }

  if (request.method !== "POST") return json({ error: "Method not allowed" }, 405);
  const body = await request.json() as Record<string, any>;

  if (body.action === "run") {
    const parameters = body.parameters && typeof body.parameters === "object" ? body.parameters : {};
    const instrument = String(body.instrument || parameters.instrument || "EURUSD").toUpperCase();
    if (instrument !== "EURUSD") return json({ error: "Unsupported instrument" }, 400);
    const replayBars = Number(parameters.replay_bars ?? 2000);
    if (!Number.isInteger(replayBars) || replayBars < 100 || replayBars > 10000) return json({ error: "replay_bars must be between 100 and 10000" }, 400);
    const runId = crypto.randomUUID();
    const sourceCommit = String(body.source_commit || env.GITHUB_DEFAULT_REF);
    const job: ResearchJob = { run_id: runId, source_commit: sourceCommit, parameters: { ...parameters, instrument } };
    await env.DB.prepare(
      "INSERT INTO research_runs (id, instrument, dataset, status, parameters_json, source_commit) VALUES (?, ?, ?, 'QUEUED', ?, ?)"
    ).bind(runId, instrument, String(parameters.dataset_artifact || "EURUSD_M1_dashboard.csv.gz"), JSON.stringify(job.parameters), sourceCommit).run();
    await recordEvent(env, runId, "QUEUED", { source_commit: sourceCommit });
    await env.RESEARCH_JOBS.send(job);
    return json({ run: { id: runId, instrument, status: "QUEUED", parameters: job.parameters, source_commit: sourceCommit }, status: "QUEUED" }, 202);
  }

  if (body.action === "hypothesis") {
    const data = body.data || {};
    const title = String(data.title || data.statement || "").trim();
    const statement = String(data.statement || title).trim();
    if (!title || !statement) return json({ error: "title and statement are required" }, 400);
    const id = crypto.randomUUID();
    await env.DB.prepare("INSERT INTO research_hypotheses (id, title, statement, status, data_json) VALUES (?, ?, ?, ?, ?)")
      .bind(id, title, statement, String(data.status || "OPEN"), JSON.stringify(data)).run();
    return json({ id, title, statement, status: String(data.status || "OPEN"), created_at: new Date().toISOString() }, 201);
  }

  if (body.action === "evidence") {
    const data = body.data || {};
    const claim = String(data.claim || "").trim();
    if (!claim) return json({ error: "claim is required" }, 400);
    const id = crypto.randomUUID();
    await env.DB.prepare("INSERT INTO research_evidence (id, claim, evidence_type, provenance_json, data_json) VALUES (?, ?, ?, ?, ?)")
      .bind(id, claim, String(data.evidence_type || "UNCLASSIFIED"), JSON.stringify(data.provenance || {}), JSON.stringify(data)).run();
    return json({ id, claim, evidence_type: String(data.evidence_type || "UNCLASSIFIED"), provenance: data.provenance || {}, created_at: new Date().toISOString() }, 201);
  }

  if (body.action === "report") {
    const runId = String(body.run_id || "");
    if (!runId) return json({ error: "run_id is required" }, 400);
    const row = await env.DB.prepare("SELECT result_key FROM research_runs WHERE id = ?").bind(runId).first<any>();
    if (!row?.result_key) return json({ error: "Research result is not ready" }, 404);
    const object = await env.RESULTS.get(row.result_key);
    if (!object) return json({ error: "Research artifact is missing" }, 404);
    return new Response(object.body, { headers: { "content-type": "application/json", "cache-control": "no-store" } });
  }
  return json({ error: "Unknown action" }, 400);
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (new URL(request.url).pathname === "/health") return json({ ok: true, service: "henryz-smc-research-api" });
    if (new URL(request.url).pathname === "/internal/research-complete") {
      if (request.method !== "POST" || request.headers.get("authorization") !== `Bearer ${env.CALLBACK_SECRET}`) {
        return json({ error: "Unauthorized" }, 401);
      }
      const body = await request.json() as Record<string, any>;
      const runId = String(body.run_id || "");
      const status = String(body.status || "");
      if (!runId || !["COMPLETED", "FAILED"].includes(status)) return json({ error: "Invalid callback" }, 400);
      const row = await env.DB.prepare("SELECT id, status FROM research_runs WHERE id = ?").bind(runId).first<any>();
      if (!row) return json({ error: "Run not found" }, 404);
      if (row.status === "COMPLETED" || row.status === "FAILED") return json({ ok: true, idempotent: true });
      if (status === "COMPLETED") {
        const key = String(body.result_key || "");
        const hash = String(body.result_sha256 || "");
        if (!key.startsWith(`research/${runId}/`) || !/^[a-f0-9]{64}$/.test(hash)) return json({ error: "Invalid artifact reference" }, 400);
        const object = await env.RESULTS.head(key);
        if (!object || object.customMetadata?.sha256 !== hash) return json({ error: "Artifact integrity check failed" }, 409);
        await env.DB.prepare("UPDATE research_runs SET status='COMPLETED', result_key=?, result_sha256=?, completed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'), updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?")
          .bind(key, hash, runId).run();
        await env.DB.prepare("INSERT OR IGNORE INTO research_reports (id, run_id, artifact_key, artifact_sha256) VALUES (?, ?, ?, ?)")
          .bind(crypto.randomUUID(), runId, key, hash).run();
      } else {
        await env.DB.prepare("UPDATE research_runs SET status='FAILED', error=?, completed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'), updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?")
          .bind(String(body.error || "Research job failed").slice(0, 2000), runId).run();
      }
      await recordEvent(env, runId, status, { result_key: body.result_key || null, error: body.error || null });
      return json({ ok: true });
    }

    if (!await verifyAccess(request, env)) return json({ error: "Cloudflare Access authentication required" }, 401);
    try {
      return await handleApi(request, env);
    } catch (error) {
      return json({ error: error instanceof Error ? error.message : "Internal error" }, 500);
    }
  },

  async queue(batch: MessageBatch<ResearchJob>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      if (batch.queue === "henryz-smc-research-jobs-dlq") {
        await env.DB.prepare("UPDATE research_runs SET status='FAILED', error='Queue dispatch exceeded retry limit', completed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'), updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=? AND status IN ('QUEUED','RUNNING')")
          .bind(message.body.run_id).run();
        await recordEvent(env, message.body.run_id, "FAILED", { reason: "dead_letter_queue" });
        message.ack();
        continue;
      }
      try {
        await dispatchResearch(message.body, env);
        await env.DB.prepare("UPDATE research_runs SET status='RUNNING', started_at=COALESCE(started_at, strftime('%Y-%m-%dT%H:%M:%fZ','now')), updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=? AND status='QUEUED'")
          .bind(message.body.run_id).run();
        await recordEvent(env, message.body.run_id, "DISPATCHED", { source_commit: message.body.source_commit });
        message.ack();
      } catch {
        message.retry();
      }
    }
  },
};
