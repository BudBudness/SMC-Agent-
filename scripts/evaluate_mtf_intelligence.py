#!/usr/bin/env python3
"""Evaluate substantive multi-timeframe structure and chronological OOS behavior."""
import argparse
import json
from pathlib import Path

import pandas as pd

from smc_agent.providers import HistDataProvider
from smc_agent.timeframes import reconstruct, ANALYSIS_TIMEFRAMES
from smc_agent.structure import swings

MIN_BARS = {
    "12M": 20, "6M": 40, "3M": 80, "W": 100, "D": 200,
    "4H": 500, "1H": 1000, "15M": 2000, "5M": 5000, "1M": 10000,
}


def asof_states(frame, swing_points=None):
    """Build chronological states in O(n + s), where s is confirmed swings."""
    points = swings(frame) if swing_points is None else swing_points
    confirmed_by_index = {}
    for kind, _pivot_time, value, confirmation_time in points:
        confirmed_by_index.setdefault(confirmation_time, []).append((kind, value))

    index = frame.index
    out = []
    last_highs = []
    last_lows = []

    for ts in index:
        for kind, value in confirmed_by_index.get(ts, ()):
            if kind == "HIGH":
                last_highs.append(value)
                if len(last_highs) > 2:
                    last_highs.pop(0)
            else:
                last_lows.append(value)
                if len(last_lows) > 2:
                    last_lows.pop(0)

        if len(last_highs) < 2 or len(last_lows) < 2:
            out.append("NEUTRAL")
        elif last_highs[-1] > last_highs[-2] and last_lows[-1] > last_lows[-2]:
            out.append("LONG")
        elif last_highs[-1] < last_highs[-2] and last_lows[-1] < last_lows[-2]:
            out.append("SHORT")
        else:
            out.append("NEUTRAL")

    return pd.Series(out, index=index)


def summarize(tf, frame, states, swing_points):
    counts = states.value_counts().to_dict()
    transitions = int((states != states.shift()).sum() - 1) if len(states) else 0
    highs = sum(x[0] == "HIGH" for x in swing_points)
    lows = sum(x[0] == "LOW" for x in swing_points)
    non_neutral = int((states != "NEUTRAL").sum())

    return {
        "bars": int(len(frame)),
        "start": frame.index[0].isoformat() if len(frame) else None,
        "end": frame.index[-1].isoformat() if len(frame) else None,
        "state_counts": {k: int(counts.get(k, 0)) for k in ("LONG", "SHORT", "NEUTRAL")},
        "state_coverage": non_neutral / len(frame) if len(frame) else 0.0,
        "state_transitions": transitions,
        "confirmed_highs": highs,
        "confirmed_lows": lows,
        "dynamic": bool(transitions > 0 and highs > 0 and lows > 0),
        "depth_ok": len(frame) >= MIN_BARS.get(tf, 0),
    }


def evaluate_frame(tf, frame):
    points = swings(frame)
    states = asof_states(frame, points)
    return summarize(tf, frame, states, points), states


def oos_summary(tf, frame, states, split=0.7):
    n = len(frame)
    cut = max(1, int(n * split))
    test = frame.iloc[cut:]
    test_states = states.iloc[cut:]
    # Swing confirmation timestamps make the full-frame as-of state series
    # safe to slice chronologically: no pivot is visible before confirmation.
    test_points = [p for p in swings(frame) if p[3] >= frame.index[cut]]
    return {
        "split_index": cut,
        "train": summarize(tf, frame.iloc[:cut], states.iloc[:cut],
                           [p for p in swings(frame) if p[3] < frame.index[cut]]),
        "test": summarize(tf, test, test_states, test_points),
        "chronological": True,
        "future_leakage_control": "Each as-of state only uses swings after their right-side confirmation timestamp.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--out", default="benchmark-results/mtf_substantive_evaluation.json")
    a = p.parse_args()

    df = HistDataProvider(a.csv).candles()
    frames = reconstruct(df)

    evaluation = {}
    oos_eval = {}
    for tf in ANALYSIS_TIMEFRAMES:
        frame = frames[tf]
        points = swings(frame)
        states = asof_states(frame, points)
        evaluation[tf] = summarize(tf, frame, states, points)

        n = len(frame)
        cut = max(1, int(n * 0.7))
        split_time = frame.index[cut]
        train_points = [p for p in points if p[3] < split_time]
        test_points = [p for p in points if p[3] >= split_time]
        oos_eval[tf] = {
            "split_index": cut,
            "train": summarize(tf, frame.iloc[:cut], states.iloc[:cut], train_points),
            "test": summarize(tf, frame.iloc[cut:], states.iloc[cut:], test_points),
            "chronological": True,
            "future_leakage_control": "Each as-of state only uses swings after their right-side confirmation timestamp.",
        }

    result = {
        "symbol": "EURUSD",
        "source_rows": len(df),
        "source_start": df.index[0].isoformat(),
        "source_end": df.index[-1].isoformat(),
        "method": "chronological descriptive structural evaluation",
        "purpose": "Determine whether 3M/6M/12M produce substantive changing structural information rather than merely reconstructed bars.",
        "timeframes": evaluation,
        "oos": oos_eval,
        "substantive_test": {
            tf: {
                "passes_technical_depth": evaluation[tf]["depth_ok"],
                "passes_dynamic_structure": evaluation[tf]["dynamic"],
                "passes_oos_dynamic_structure": oos_eval[tf]["test"]["dynamic"],
                "interpretation": "Substantive structure requires depth, confirmed swings, and time-varying states in chronological/OOS segments; this is not a predictive or profitability test.",
            }
            for tf in ("12M", "6M", "3M")
        },
    }

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(result, indent=2))
    print(json.dumps(result["substantive_test"], indent=2))


if __name__ == "__main__":
    main()
