"""Order-block observations with chronological mitigation/invalidation state."""
def find_order_blocks(df):
    out=[]
    for i in range(1,len(df)):
        p,c=df.iloc[i-1],df.iloc[i]
        if p.close<p.open and c.close>c.open and c.high>p.high:
            out.append({"kind":"BULLISH","low":float(p.low),"high":float(p.open),"time":df.index[i-1],"formed_at":df.index[i],"status":"ACTIVE"})
        if p.close>p.open and c.close<c.open and c.low<p.low:
            out.append({"kind":"BEARISH","low":float(p.open),"high":float(p.high),"time":df.index[i-1],"formed_at":df.index[i],"status":"ACTIVE"})
    for ob in out:
        after=df.loc[df.index>ob["formed_at"]]
        if after.empty: continue
        touched=(after.low<=ob["high"])&(after.high>=ob["low"])
        if touched.any():
            ob["status"]="MITIGATED"; ob["mitigated_at"]=after.index[touched.to_numpy().nonzero()[0][0]]
        if ob["kind"]=="BULLISH" and (after.close<ob["low"]).any(): ob["status"]="INVALIDATED"
        if ob["kind"]=="BEARISH" and (after.close>ob["high"]).any(): ob["status"]="INVALIDATED"
    return out
