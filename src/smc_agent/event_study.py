"""Fixed-horizon historical event study; no execution semantics."""
import pandas as pd


def event_reactions(df, events, horizons=(1, 3, 5, 10, 20)):
    """Measure descriptive post-event returns using bars strictly after each event."""
    close = pd.to_numeric(df["close"], errors="coerce").dropna()
    out = []
    for e in events or []:
        try:
            ts = pd.Timestamp(e["time"])
        except Exception:
            continue
        prior = close.loc[:ts]
        if prior.empty:
            continue
        base = float(prior.iloc[-1])
        row = {
            "event": e.get("name"),
            "time": ts.isoformat(),
            "base": base,
            "timeframe": e.get("timeframe"),
        }
        for h in horizons:
            future = close.loc[close.index > ts].head(h)
            row[f"h{h}"] = None if len(future) < h else float(future.iloc[-1] / base - 1)
        out.append(row)
    return pd.DataFrame(out)


def summarize(reactions):
    if reactions is None or reactions.empty:
        return {"samples": 0, "complete_samples": {}, "status": "INSUFFICIENT_SAMPLE"}

    out = {"samples": len(reactions), "complete_samples": {}}
    for c in reactions.columns:
        if not c.startswith("h"):
            continue
        s = pd.to_numeric(reactions[c], errors="coerce").dropna()
        out["complete_samples"][c] = int(len(s))
        if len(s):
            out[c] = {
                "mean": float(s.mean()),
                "median": float(s.median()),
                "positive_rate": float((s > 0).mean()),
            }
    out["status"] = "DESCRIPTIVE_ONLY"
    out["method"] = "bar-count forward return; incomplete horizons excluded"
    return out
