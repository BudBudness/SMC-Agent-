"""Source-data integrity checks for research artifacts.

These checks describe dataset quality only; they do not infer market direction.
Gap handling follows the source semantics: missing M1 bars can occur during
normal FX trading pauses, so gaps are retained as provenance rather than
treated as corruption.
"""

import pandas as pd


def validate_source(df: pd.DataFrame, expected_minutes: int = 1) -> dict:
    required = {"open", "high", "low", "close"}
    missing = sorted(required - set(df.columns))
    if missing:
        return {"status": "FAIL", "errors": [f"missing columns: {', '.join(missing)}"]}

    idx = pd.DatetimeIndex(df.index)
    errors = []
    warnings = []

    if not idx.is_monotonic_increasing:
        errors.append("timestamp index is not monotonic increasing")
    duplicate_count = int(idx.duplicated().sum())
    if duplicate_count:
        errors.append(f"duplicate timestamps: {duplicate_count}")

    numeric = df[list(required)].apply(pd.to_numeric, errors="coerce")
    null_counts = {k: int(v) for k, v in numeric.isna().sum().items() if int(v)}
    if null_counts:
        errors.append(f"non-numeric/null OHLC values: {null_counts}")

    bad_ohlc = (
        (numeric["high"] < numeric[["open", "close"]].max(axis=1))
        | (numeric["low"] > numeric[["open", "close"]].min(axis=1))
        | (numeric["high"] < numeric["low"])
    )
    bad_ohlc_count = int(bad_ohlc.fillna(False).sum())
    if bad_ohlc_count:
        errors.append(f"invalid OHLC rows: {bad_ohlc_count}")

    gaps = pd.Series(idx).diff().dropna().dt.total_seconds().div(60)
    expected = float(expected_minutes)
    gap_threshold = expected * 2
    large_gaps = gaps[gaps > gap_threshold]
    gap_info = {
        "large_gap_count": int(len(large_gaps)),
        "max_gap_minutes": float(large_gaps.max()) if not large_gaps.empty else 0.0,
        "threshold_minutes": gap_threshold,
        "treatment": "informational; normal FX trading pauses and low-liquidity gaps are retained as provenance",
    }
    if not large_gaps.empty:
        warnings.append(gap_info)

    if len(idx):
        start = idx.min().isoformat()
        end = idx.max().isoformat()
    else:
        start = end = None

    return {
        "status": "FAIL" if errors else "PASS",
        "rows": int(len(df)),
        "start": start,
        "end": end,
        "duplicate_timestamps": duplicate_count,
        "invalid_ohlc_rows": bad_ohlc_count,
        "large_gaps": gap_info,
        "errors": errors,
        "warnings": warnings,
        "expected_source_cadence_minutes": expected_minutes,
    }
