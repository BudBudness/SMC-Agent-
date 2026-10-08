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

def mtf_structure_alignment(htf_df, ltf_df, htf_direction, tolerance_atr=0.35):
    """Research-only HTF zone -> LTF CHoCH/BOS -> HTF target relationship."""
    if htf_direction not in {"LONG", "SHORT"} or htf_df.empty or ltf_df.empty:
        return {"status":"NOT_ESTABLISHED","reason":"insufficient_direction_or_data"}
    hs=swings(htf_df)
    if len(hs)<2 or len(ltf_df)<20:
        return {"status":"NOT_ESTABLISHED","reason":"insufficient_confirmed_swings"}
    recent=hs[-6:]
    price=float(ltf_df.close.iloc[-1])
    tr=(ltf_df.high-ltf_df.low).rolling(20).median().iloc[-1]
    tolerance=float(tr*tolerance_atr) if pd.notna(tr) and tr>0 else 0.0
    dist,zone=min(((abs(price-float(x[2])),x) for x in recent),key=lambda z:z[0])
    arrived=dist<=tolerance if tolerance else False
    shift=choch_bos(ltf_df,htf_direction)
    target_kind="LOW" if htf_direction=="SHORT" else "HIGH"
    targets=[x for x in hs if x[0]==target_kind and x[2] != zone[2]]
    target=min(targets,key=lambda x:abs(float(x[2])-price)) if targets else None
    status="ALIGNED" if arrived and (shift.get("choch") or shift.get("bos")) else "ZONE_ARRIVAL" if arrived else "NOT_ESTABLISHED"
    return {"status":status,"htf_direction":htf_direction,
            "zone":{"kind":zone[0],"price":float(zone[2]),"formed_at":zone[1],"confirmed_at":zone[3]},
            "zone_distance":float(dist),"zone_tolerance":tolerance,
            "arrival_time":ltf_df.index[-1] if arrived else None,
            "choch":bool(shift.get("choch")),"bos":bool(shift.get("bos")),
            "confirmation_time":shift.get("confirmation_time") if (shift.get("choch") or shift.get("bos")) else None,
            "htf_target":{"kind":target[0],"price":float(target[2]),"formed_at":target[1],"confirmed_at":target[3]} if target else None,
            "interpretation":"LTF CHoCH/BOS is evidence of structural alignment; it cannot override HTF authority or constitute an execution signal."}

def choch_bos(df,direction):
    """Close-confirmed structural break against/with the prior confirmed sequence."""
    s=swings(df); highs=[x for x in s if x[0]=="HIGH"]; lows=[x for x in s if x[0]=="LOW"]
    if len(highs)<2 or len(lows)<2:return {"choch":False,"bos":False,"reference":None}
    close=float(df.close.iloc[-1])
    if direction=="LONG":
        ref=highs[-1]; continuation=close>ref[2]
        prior_down=highs[-1][2]<highs[-2][2]
        return {"choch":bool(continuation and prior_down),"bos":bool(continuation and not prior_down),"reference":ref,"confirmation_time":df.index[-1]}
    if direction=="SHORT":
        ref=lows[-1]; continuation=close<ref[2]
        prior_up=lows[-1][2]>lows[-2][2]
        return {"choch":bool(continuation and prior_up),"bos":bool(continuation and not prior_up),"reference":ref,"confirmation_time":df.index[-1]}
    return {"choch":False,"bos":False,"reference":None}
