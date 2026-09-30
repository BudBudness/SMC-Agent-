"""FVG observations with chronological lifecycle and partial-fill state."""
def find_fvg(df):
    out=[]
    for i in range(2,len(df)):
        a,b,c=df.iloc[i-2],df.iloc[i-1],df.iloc[i]; formed=df.index[i]
        if float(a.high)<float(c.low):
            out.append({"kind":"BULLISH","low":float(a.high),"high":float(c.low),"time":df.index[i-1],"formed_at":formed,"status":"ACTIVE","fill_ratio":0.0})
        if float(a.low)>float(c.high):
            out.append({"kind":"BEARISH","low":float(c.high),"high":float(a.low),"time":df.index[i-1],"formed_at":formed,"status":"ACTIVE","fill_ratio":0.0})
    for g in out:
        after=df.loc[df.index>g["formed_at"]]
        if after.empty: continue
        touched=(after.low<=g["high"])&(after.high>=g["low"])
        if touched.any():
            first=after.index[touched.to_numpy().nonzero()[0][0]]
            g["mitigated_at"]=first; g["status"]="MITIGATED"
            lo=float(g["low"]); hi=float(g["high"]); width=max(hi-lo,1e-12)
            for _,r in after.loc[:first].iterrows():
                if g["kind"]=="BULLISH": depth=max(0,min(1,(hi-float(r.low))/width))
                else: depth=max(0,min(1,(float(r.high)-lo)/width))
                g["fill_ratio"]=max(float(g["fill_ratio"]),depth)
        invalid=(after.close<g["low"]) if g["kind"]=="BULLISH" else (after.close>g["high"])
        if invalid.any():
            g["status"]="INVALIDATED"; g["invalidated_at"]=after.index[invalid.to_numpy().nonzero()[0][0]]
        g["structural_significance"]="HIGH" if g["fill_ratio"]==0 and g["status"]=="ACTIVE" else "OBSERVED"
    return out
