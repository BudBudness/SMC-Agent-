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
    """Build one canonical OHLC timeframe without look-ahead."""
    if timeframe not in TIMEFRAME_RULES:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    if df.empty:
        return df.copy()
    return df.sort_index().resample(TIMEFRAME_RULES[timeframe]).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    ).dropna()


def reconstruct(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Reconstruct the complete SMC hierarchy from the source timeframe."""
    return {tf: resample(df, tf) for tf in ANALYSIS_TIMEFRAMES}


def coverage(frames: dict[str, pd.DataFrame]) -> dict[str, int]:
    return {tf: int(len(frame)) for tf, frame in frames.items()}
