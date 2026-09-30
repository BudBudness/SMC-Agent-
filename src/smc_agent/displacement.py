"""Chronological displacement observations with robust local normalization."""
import pandas as pd

def detect_displacement(df, lookback=20):
    if len(df) <= lookback:
        return []
    x=df.copy()
    rng=(x["high"]-x["low"]).astype(float)
    body=(x["close"]-x["open"]).abs().astype(float)
    baseline=rng.shift(1).rolling(lookback,min_periods=lookback).median()
    body_base=body.shift(1).rolling(lookback,min_periods=lookback).median()
    out=[]
    for i in range(lookback,len(x)):
        r=x.iloc[i]; br=float(baseline.iloc[i] or 0); bb=float(body_base.iloc[i] or 0)
        if br<=0 or bb<=0: continue
        rr=float(rng.iloc[i]/br); rb=float(body.iloc[i]/bb)
        directional=float((r.close-r.open)/rng.iloc[i]) if rng.iloc[i]>0 else 0
        if rr<1.25 or rb<1.25 or abs(directional)<0.55: continue
        strength="EXTREME" if rr>=3 and rb>=3 else "STRONG" if rr>=2 and rb>=2 else "MODERATE"
        out.append({"time":x.index[i],"direction":"BULLISH" if r.close>r.open else "BEARISH",
                    "strength":strength,"range_ratio":round(rr,4),"body_ratio":round(rb,4),
                    "directional_body":round(abs(directional),4),"formed_at":x.index[i]})
    return out
