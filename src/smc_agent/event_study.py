"""Fixed-horizon historical event study; no execution semantics."""
import pandas as pd
def event_reactions(df,events,horizons=(1,3,5,10,20)):
    close=df["close"]; out=[]
    for e in events or []:
        ts=pd.Timestamp(e["time"]); prior=close.loc[:ts]
        if prior.empty: continue
        base=float(prior.iloc[-1]); row={"event":e.get("name"),"time":ts.isoformat(),"base":base}
        for h in horizons:
            future=close.loc[close.index>ts].head(h); row[f"h{h}"]=None if future.empty else float(future.iloc[-1]/base-1)
        out.append(row)
    return pd.DataFrame(out)
def summarize(reactions):
    if reactions is None or reactions.empty:return {"samples":0}
    out={"samples":len(reactions)}
    for c in reactions.columns:
        if c.startswith("h"):
            s=pd.to_numeric(reactions[c],errors="coerce").dropna()
            if len(s):out[c]={"mean":float(s.mean()),"median":float(s.median()),"positive_rate":float((s>0).mean())}
    return out
