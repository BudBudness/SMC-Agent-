import gzip
import io
import json
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from http.server import BaseHTTPRequestHandler

import pandas as pd

from src.smc_agent.pipeline import run as run_pipeline

RELEASE_BASE = "https://github.com/BudBudness/SMC-Agent-/releases/download/research-data/"
DATASETS = {
    "EURUSD": "EURUSD_M1_dashboard.csv.gz",
}

def _json_safe(value):
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except (TypeError, ValueError):
            pass
    return value

def _read_source(symbol, artifact):
    if artifact not in DATASETS.values():
        raise ValueError("dataset artifact is not allowed")
    if DATASETS.get(symbol) != artifact:
        raise ValueError("dataset artifact does not match instrument")
    url = RELEASE_BASE + artifact
    req = Request(url, headers={"User-Agent": "Henryz-SMC-Research/1.0"})
    with urlopen(req, timeout=120) as response:
        raw = response.read()
    payload = gzip.decompress(raw)
    frame = pd.read_csv(io.BytesIO(payload))
    col = "timestamp" if "timestamp" in frame.columns else "time"
    if col not in frame.columns:
        raise ValueError("dataset has no timestamp column")
    frame[col] = pd.to_datetime(frame[col], utc=True)
    frame = frame.set_index(col).sort_index()
    return frame, url

def _params(body):
    symbol = str(body.get("instrument") or body.get("symbol") or "EURUSD").upper()
    artifact = str(body.get("dataset_artifact") or DATASETS.get(symbol, ""))
    if symbol not in DATASETS:
        raise ValueError("unsupported instrument")
    replay_bars = int(body.get("replay_bars", 2000))
    if replay_bars < 100 or replay_bars > 10000:
        raise ValueError("replay_bars must be between 100 and 10000")
    return {
        "symbol": symbol,
        "artifact": artifact,
        "replay_bars": replay_bars,
        "start": body.get("start"),
        "end": body.get("end"),
        "now": body.get("now"),
        "news_events": body.get("news_events") or [],
        "historical_episodes": body.get("historical_episodes") or [],
    }

def execute(body):
    p = _params(body)
    df, source_url = _read_source(p["symbol"], p["artifact"])

    if p["start"]:
        start = pd.Timestamp(p["start"])
        if start.tzinfo is None:
            start = start.tz_localize("UTC")
        df = df[df.index >= start]
    if p["end"]:
        end = pd.Timestamp(p["end"])
        if end.tzinfo is None:
            end = end.tz_localize("UTC")
        df = df[df.index <= end]
    if df.empty:
        raise ValueError("parameterized window contains no source rows")

    effective_now = p["now"]
    if effective_now:
        effective_now = pd.Timestamp(effective_now)
        if effective_now.tzinfo is None:
            effective_now = effective_now.tz_localize("UTC")
    else:
        effective_now = df.index[-1]

    pipeline = run_pipeline(
        df,
        symbol=p["symbol"],
        news_events=p["news_events"],
        historical_episodes=p["historical_episodes"],
        now=effective_now,
    )

    replay = df.tail(p["replay_bars"])[["open", "high", "low", "close"]].reset_index()
    replay_records = _json_safe(replay.to_dict(orient="records"))
    report = _json_safe(pipeline["report"])
    validation = _json_safe(pipeline["dataset_validation"])
    mtf_validation = _json_safe(pipeline["mtf_validation"])
    lineage = _json_safe(pipeline["lineage"])

    closes = [float(x["close"]) for x in replay_records if x.get("close") is not None]
    events = report.get("events", [])
    name = lambda e: str(e.get("name") or e.get("type") or "").lower()
    benchmarks = {
        "definitions": {
            "event_count": "Count of events emitted by the canonical research engine.",
            "liquidity_event_count": "Count of liquidity formation, sweep, and liquidity observations.",
            "displacement_event_count": "Count of displacement observations.",
            "fvg_event_count": "Count of fair-value-gap observations.",
            "order_block_event_count": "Count of order-block observations.",
            "window_return": "Descriptive close-to-close change across the requested replay window.",
        },
        "results": {
            "event_count": len(events),
            "liquidity_event_count": sum("liquidity" in name(e) or "sweep" in name(e) for e in events),
            "displacement_event_count": sum("displacement" in name(e) for e in events),
            "fvg_event_count": sum("fvg" in name(e) for e in events),
            "order_block_event_count": sum("order_block" in name(e) or "orderblock" in name(e) for e in events),
            "replay_bars": len(replay_records),
            "window_return": (closes[-1] / closes[0] - 1) if len(closes) > 1 else 0.0,
        },
        "limitations": [
            "Descriptive research output only.",
            "No predictive interpretation or execution semantics.",
            "Historical analogue results are descriptive and depend on the supplied episode set.",
        ],
    }

    return {
        "engine_version": "0.3.0",
        "execution": "CANONICAL_PIPELINE",
        "parameters": {
            "instrument": p["symbol"],
            "dataset_artifact": p["artifact"],
            "start": p["start"],
            "end": p["end"],
            "now": _json_safe(effective_now),
            "replay_bars": p["replay_bars"],
            "news_event_count": len(p["news_events"]),
            "historical_episode_count": len(p["historical_episodes"]),
        },
        "source": {
            "artifact": p["artifact"],
            "url": source_url,
            "rows_after_window": len(df),
            "start": df.index.min().isoformat(),
            "end": df.index.max().isoformat(),
        },
        "dataset_validation": validation,
        "mtf_validation": mtf_validation,
        "report": report,
        "replay": replay_records,
        "benchmarks": benchmarks,
        "lineage": lineage,
    }

class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(_json_safe(payload), separators=(",", ":"), allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(200, {"service": "henryz-smc-research-engine", "execution": "CANONICAL_PIPELINE", "status": "READY"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            self._send(200, execute(body))
        except Exception as exc:
            self._send(500, {"status": "FAILED", "error": str(exc)})

