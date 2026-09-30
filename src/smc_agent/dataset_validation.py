"""OHLC integrity and multi-timeframe validation."""
import pandas as pd

def validate_ohlc(df,expected_frequency=None):
    errors=[]; warnings=[]; required={"open","high","low","close"}
    missing=required-set(df.columns)
    if missing: errors.append(f"missing columns: {sorted(missing)}")
    if not isinstance(df.index,pd.DatetimeIndex): errors.append("index must be DatetimeIndex")
    if isinstance(df.index,pd.DatetimeIndex):
        if df.index.tz is None: warnings.append("timestamps are timezone-naive")
        if not df.index.is_monotonic_increasing: errors.append("timestamps are not sorted")
        if df.index.has_duplicates: errors.append("duplicate timestamps")
        if expected_frequency:
            inferred=pd.infer_freq(df.index)
            if inferred and inferred!=expected_frequency: warnings.append(f"inferred frequency {inferred} differs from expected {expected_frequency}")
    if not missing:
        if df[list(required)].isna().any().any(): errors.append("OHLC contains NaN")
        if (df.high<df.low).any(): errors.append("high below low")
        if (df.open>df.high).any() or (df.open<df.low).any(): errors.append("open outside range")
        if (df.close>df.high).any() or (df.close<df.low).any(): errors.append("close outside range")
    return {"valid":not errors,"errors":errors,"warnings":warnings,"rows":len(df)}

def validate_alignment(frames):
    """Validate every reconstructed frame independently.

    Different resampling frequencies naturally have different timestamp ranges
    when a source window is short; non-overlap is not itself a data-integrity error.
    """
    issues=[]; checked=[]; coverage={}
    for name,df in frames.items():
        r=validate_ohlc(df); checked.append(name)
        coverage[name]={"rows":len(df),"start":df.index.min().isoformat() if len(df) else None,"end":df.index.max().isoformat() if len(df) else None}
        if not r["valid"]: issues.append({"timeframe":name,"errors":r["errors"]})
    return {"valid":not issues,"issues":issues,"checked":checked,"coverage":coverage}
