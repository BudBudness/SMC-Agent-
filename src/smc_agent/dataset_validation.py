"""OHLC integrity and timeframe validation."""
import pandas as pd
def validate_ohlc(df):
    errors=[]; warnings=[]; required={"open","high","low","close"}; missing=required-set(df.columns)
    if missing:errors.append(f"missing columns: {sorted(missing)}")
    if not isinstance(df.index,pd.DatetimeIndex):errors.append("index must be DatetimeIndex")
    if isinstance(df.index,pd.DatetimeIndex):
        if df.index.tz is None:warnings.append("timestamps are timezone-naive")
        if not df.index.is_monotonic_increasing:errors.append("timestamps are not sorted")
        if df.index.has_duplicates:errors.append("duplicate timestamps")
    if not missing:
        if df[list(required)].isna().any().any():errors.append("OHLC contains NaN")
        if (df.high<df.low).any():errors.append("high below low")
        if (df.open>df.high).any() or (df.open<df.low).any():errors.append("open outside range")
        if (df.close>df.high).any() or (df.close<df.low).any():errors.append("close outside range")
    return {"valid":not errors,"errors":errors,"warnings":warnings,"rows":len(df)}
def validate_alignment(frames):
    issues=[]
    for name,df in frames.items():
        r=validate_ohlc(df)
        if not r["valid"]:issues.append({"timeframe":name,"errors":r["errors"]})
    return {"valid":not issues,"issues":issues}
