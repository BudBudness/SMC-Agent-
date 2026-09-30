"""Order-block observations linked to displacement and chronological lifecycle."""
def find_order_blocks(df, displacement_events=None):
    displacement_events=displacement_events or []
    out=[]
    disp_times=[e.get("time") for e in displacement_events]
    for i in range(1,len(df)):
        p,c=df.iloc[i-1],df.iloc[i]
        bullish=p.close<p.open and c.close>c.open and c.high>p.high
        bearish=p.close>p.open and c.close<c.open and c.low<p.low
        if not (bullish or bearish): continue
        kind="BULLISH" if bullish else "BEARISH"
        out.append({"kind":kind,"low":float(p.low),"high":float(p.open) if bullish else float(p.high),
                    "time":df.index[i-1],"formed_at":df.index[i],"status":"ACTIVE",
                    "origin_candle":df.index[i-1],"linked_displacement":any(t is not None and t>=df.index[i] and t<=df.index[min(i+3,len(df)-1)] for t in disp_times)})
    for ob in out:
        after=df.loc[df.index>ob["formed_at"]]
        if after.empty: continue
        touched=(after.low<=ob["high"])&(after.high>=ob["low"])
        if touched.any():
            ob["status"]="MITIGATED"; ob["mitigated_at"]=after.index[touched.to_numpy().nonzero()[0][0]]
        invalid=(after.close<ob["low"]) if ob["kind"]=="BULLISH" else (after.close>ob["high"])
        if invalid.any():
            ob["status"]="INVALIDATED"; ob["invalidated_at"]=after.index[invalid.to_numpy().nonzero()[0][0]]
        ob["structural_significance"]="HIGH" if ob["linked_displacement"] else "OBSERVED"
    return out
