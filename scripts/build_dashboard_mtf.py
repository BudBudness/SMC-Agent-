#!/usr/bin/env python3
"""Build a compact, full-history MTF artifact for the research dashboard.

The artifact keeps structural state derived from the complete source history while
shipping only a bounded recent OHLC tail per timeframe for visualization.
"""
import argparse, gzip, hashlib, json
from pathlib import Path
import pandas as pd

from smc_agent.providers import HistDataProvider
from smc_agent.timeframes import reconstruct, ANALYSIS_TIMEFRAMES
from smc_agent.structure import swings
from smc_agent.contradictions import compare

TAIL_BARS = {
    "12M": 25, "6M": 50, "3M": 100, "W": 260, "D": 520,
    "4H": 1000, "1H": 2000, "15M": 4000, "5M": 5000, "1M": 10000,
}

def asof_state(frame):
    points = swings(frame)
    highs, lows = [], []
    by_confirmation = {}
    for kind, _pivot, value, confirmation in points:
        by_confirmation.setdefault(confirmation, []).append((kind, value))
    state = "NEUTRAL"
    for ts in frame.index:
        for kind, value in by_confirmation.get(ts, ()):
            target = highs if kind == "HIGH" else lows
            target.append(value)
            if len(target) > 2:
                target.pop(0)
        if len(highs) >= 2 and len(lows) >= 2:
            if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
                state = "LONG"
            elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                state = "SHORT"
            else:
                state = "NEUTRAL"
    return state, points

def serial_frame(frame, tail):
    x = frame.tail(tail)
    return [
        [ts.isoformat(), float(r.open), float(r.high), float(r.low), float(r.close)]
        for ts, r in x.iterrows()
    ]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--out", default="data/long_history/EURUSD_MTF_dashboard.json.gz")
    a = p.parse_args()

    source = HistDataProvider(a.csv).candles()
    frames = reconstruct(source)
    states = {}
    payload = {
        "schema_version": "2.0",
        "symbol": "EURUSD",
        "source_rows": int(len(source)),
        "source_start": source.index[0].isoformat(),
        "source_end": source.index[-1].isoformat(),
        "source_frequency": "1M",
        "method": "full-history MTF structural state with bounded visualization tails",
        "lookahead_control": "States are computed only from swings after their right-side confirmation timestamp.",
        "timeframes": {},
    }
    for tf in ANALYSIS_TIMEFRAMES:
        frame = frames[tf]
        state, points = asof_state(frame)
        states[tf] = state
        payload["timeframes"][tf] = {
            "bars": int(len(frame)),
            "start": frame.index[0].isoformat(),
            "end": frame.index[-1].isoformat(),
            "state": state,
            "confirmed_highs": int(sum(p[0] == "HIGH" for p in points)),
            "confirmed_lows": int(sum(p[0] == "LOW" for p in points)),
            "ohlc_tail": serial_frame(frame, TAIL_BARS[tf]),
        }
    payload["contradictions"] = compare(states)["contradictions"]
    raw = json.dumps(payload, separators=(",", ":")).encode()
    payload["artifact_sha256"] = hashlib.sha256(raw).hexdigest()
    final = json.dumps(payload, separators=(",", ":")).encode()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(a.out, "wb") as f:
        f.write(final)
    print(json.dumps({
        "source_rows": payload["source_rows"],
        "source_start": payload["source_start"],
        "source_end": payload["source_end"],
        "timeframes": {k: v["bars"] for k, v in payload["timeframes"].items()},
        "states": states,
        "contradictions": len(payload["contradictions"]),
        "artifact": a.out,
        "sha256": payload["artifact_sha256"],
    }, indent=2))

if __name__ == "__main__":
    main()
