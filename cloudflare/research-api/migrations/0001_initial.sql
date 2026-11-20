PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS research_runs (
  id TEXT PRIMARY KEY,
  instrument TEXT NOT NULL,
  dataset TEXT,
  status TEXT NOT NULL CHECK (status IN ('QUEUED','RUNNING','COMPLETED','FAILED')),
  parameters_json TEXT NOT NULL,
  result_key TEXT,
  result_sha256 TEXT,
  error TEXT,
  source_commit TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  started_at TEXT,
  completed_at TEXT,
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_research_runs_created
  ON research_runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_runs_status
  ON research_runs(status, created_at DESC);

CREATE TABLE IF NOT EXISTS research_reports (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  artifact_key TEXT NOT NULL,
  artifact_sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(run_id)
);
CREATE INDEX IF NOT EXISTS idx_research_reports_run ON research_reports(run_id);

CREATE TABLE IF NOT EXISTS research_hypotheses (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  statement TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'OPEN',
  data_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_research_hypotheses_created
  ON research_hypotheses(created_at DESC);

CREATE TABLE IF NOT EXISTS research_evidence (
  id TEXT PRIMARY KEY,
  claim TEXT NOT NULL,
  evidence_type TEXT NOT NULL DEFAULT 'UNCLASSIFIED',
  provenance_json TEXT NOT NULL DEFAULT '{}',
  data_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_research_evidence_created
  ON research_evidence(created_at DESC);

CREATE TABLE IF NOT EXISTS research_job_events (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  detail_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_research_job_events_run
  ON research_job_events(run_id, created_at);
