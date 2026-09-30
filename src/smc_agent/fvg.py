"""Fair-value-gap observations with chronological lifecycle state."""
def find_fvg(df):
    out=[]
    for i in range(2,len(df)):
        a,b,c=df.iloc[i-2],df.iloc[i-1],df.iloc[i]; ts=df.index[i-1]
        if float(a.high)<float(c.low):
            out.append({"kind":"BULLISH","low":float(a.high),"high":float(c.low),"time":ts,"formed_at":df.index[i],"status":"ACTIVE"})
        if float(a.low)>float(c.high):
            out.append({"kind":"BEARISH","low":float(c.high),"high":float(a.low),"time":ts,"formed_at":df.index[i],"status":"ACTIVE"})
    for gap in out:
        after=df.loc[df.index>gap["formed_at"]]
        if after.empty: continue
        touched=(after.low<=gap["high"])&(after.high>=gap["low"])
        if touched.any():
            gap["status"]="MITIGATED"; gap["mitigated_at"]=after.index[touched.to_numpy().nonzero()[0][0]]
        if gap["kind"]=="BULLISH" and (after.close<gap["low"]).any(): gap["status"]="INVALIDATED"
        if gap["kind"]=="BEARISH" and (after.close>gap["high"]).any(): gap["status"]="INVALIDATED"
    return out
