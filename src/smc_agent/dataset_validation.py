"""OHLC integrity, gap, timezone and multi-timeframe alignment validation."""
import pandas as pd

def validate_ohlc(df, expected_frequency=None):
    errors=[]; warnings=[]; required={"open","high","low","close"}
    missing=required-set(df.columns)
    if missing: errors.append(f"missing columns: {sorted(missing)}")
    if not isinstance(df.index,pd.DatetimeIndex):
        errors.append("index must be DatetimeIndex")
    if isinstance(df.index,pd.DatetimeIndex):
        if df.index.tz is None: warnings.append("timestamps are timezone-naive")
        if not df.index.is_monotonic_increasing: errors.append("timestamps are not sorted")
        if df.index.has_duplicates: errors.append("duplicate timestamps")
        if expected_frequency:
            inferred=pd.infer_freq(df.index)
            if inferred and inferred != expected_frequency:
                warnings.append(f"inferred frequency {inferred} differs from expected {expected_frequency}")
    if not missing:
        if df[list(required)].isna().any().any(): errors.append("OHLC contains NaN")
        if (df.high<df.low).any(): errors.append("high below low")
        if (df.open>df.high).any() or (df.open<df.low).any(): errors.append("open outside range")
        if (df.close>df.high).any() or (df.close<df.low).any(): errors.append("close outside range")
    return {"valid":not errors,"errors":errors,"warnings":warnings,"rows":len(df)}

def validate_alignment(frames):
    issues=[]; checked=[]
    for name,df in frames.items():
        r=validate_ohlc(df)
        checked.append(name)
        if not r["valid"]: issues.append({"timeframe":name,"errors":r["errors"]})
    ordered=[(name,df.index) for name,df in frames.items() if isinstance(df.index,pd.DatetimeIndex)]
    for i,(a,ai) in enumerate(ordered):
        for b,bi in ordered[i+1:]:
            if len(ai) and len(bi) and ai[0] < bi[-1] and bi[0] < ai[-1]:
                continue
            if len(ai) and len(bi): issues.append({"timeframe_pair":[a,b],"errors":["non-overlapping ranges"]})
    return {"valid":not issues,"issues":issues,"checked":checked}
