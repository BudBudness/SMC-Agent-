"""Canonical multi-timeframe reconstruction from source candles."""

import pandas as pd

TIMEFRAME_RULES = {
    "12M": "12ME",
    "6M": "6ME",
    "3M": "3ME",
    "W": "W",
    "D": "D",
    "4H": "4h",
    "1H": "1h",
    "15M": "15min",
    "5M": "5min",
    "1M": "1min",
}

ANALYSIS_TIMEFRAMES = tuple(TIMEFRAME_RULES)


def resample(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Build one canonical OHLC timeframe without future-dated bin labels.

    Resampling libraries conventionally label a calendar bucket by its period
    boundary. That can place a monthly/weekly label after the last source
    candle (for example, a 12M bucket ending in 2027 while source data ends
    in 2026). Research states must instead be timestamped at the last observed
    source candle inside each bucket.
    """
    if timeframe not in TIMEFRAME_RULES:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    if df.empty:
        return df.copy()

    source = df.sort_index()
    rule = TIMEFRAME_RULES[timeframe]
    if timeframe == "1M":
        return source[["open", "high", "low", "close"]].copy()

    bars = source.resample(rule).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    ).dropna()
    if bars.empty:
        return bars

    # Use the final observed source timestamp in each bucket as the bar's
    # as-of timestamp. This preserves chronology and prevents future labels.
    last_observed = source.index.to_series().resample(rule).last().reindex(bars.index)
    valid = last_observed.notna()
    bars = bars.loc[valid].copy()
    bars.index = pd.DatetimeIndex(last_observed.loc[valid].to_numpy())
    bars = bars[~bars.index.duplicated(keep="last")]
    return bars


def reconstruct(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Reconstruct the complete SMC hierarchy from the source timeframe."""
    return {tf: resample(df, tf) for tf in ANALYSIS_TIMEFRAMES}


def coverage(frames: dict[str, pd.DataFrame]) -> dict[str, int]:
    return {tf: int(len(frame)) for tf, frame in frames.items()}
