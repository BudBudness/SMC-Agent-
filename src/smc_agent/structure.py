import pandas as pd

def swings(df,left=2,right=2):
    """Return confirmed swing points with exact right-side confirmation timestamp."""
    if len(df)<=left+right:return []
    high=pd.to_numeric(df["high"],errors="coerce"); low=pd.to_numeric(df["low"],errors="coerce")
    ph=high.shift(1).rolling(left,min_periods=left).max(); fh=high.shift(-1).rolling(right,min_periods=right).max()
    pl=low.shift(1).rolling(left,min_periods=left).min(); fl=low.shift(-1).rolling(right,min_periods=right).min()
    hm=high.gt(ph)&high.ge(fh); lm=low.lt(pl)&low.le(fl); idx=df.index.to_numpy(); out=[]
    for i in hm.to_numpy().nonzero()[0]:
        if i+right<len(idx):out.append(("HIGH",idx[i],float(high.iloc[i]),idx[i+right]))
    for i in lm.to_numpy().nonzero()[0]:
        if i+right<len(idx):out.append(("LOW",idx[i],float(low.iloc[i]),idx[i+right]))
    return sorted(out,key=lambda x:x[1])

def protected_swings(df): return swings(df,3,3)

def structure_state(df):
    s=swings(df); highs=[x for x in s if x[0]=="HIGH"]; lows=[x for x in s if x[0]=="LOW"]
    if len(highs)<2 or len(lows)<2:return "NEUTRAL"
    if highs[-1][2]>highs[-2][2] and lows[-1][2]>lows[-2][2]:return "LONG"
    if highs[-1][2]<highs[-2][2] and lows[-1][2]<lows[-2][2]:return "SHORT"
    return "NEUTRAL"

def weekly_bias(df): return structure_state(df)

def choch_bos(df,direction):
    """Close-confirmed structural break against/with the prior confirmed sequence."""
    s=swings(df); highs=[x for x in s if x[0]=="HIGH"]; lows=[x for x in s if x[0]=="LOW"]
    if len(highs)<2 or len(lows)<2:return {"choch":False,"bos":False,"reference":None}
    close=float(df.close.iloc[-1])
    if direction=="LONG":
        ref=highs[-1]; continuation=close>ref[2]
        prior_down=highs[-1][2]<highs[-2][2]
        return {"choch":bool(continuation and prior_down),"bos":bool(continuation and not prior_down),"reference":ref}
    if direction=="SHORT":
        ref=lows[-1]; continuation=close<ref[2]
        prior_up=lows[-1][2]>lows[-2][2]
        return {"choch":bool(continuation and prior_up),"bos":bool(continuation and not prior_up),"reference":ref}
    return {"choch":False,"bos":False,"reference":None}
