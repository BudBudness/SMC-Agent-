def find_fvg(df):
    out=[]
    for i in range(2,len(df)):
        a,b,c=df.iloc[i-2],df.iloc[i-1],df.iloc[i]
        if a.high<c.low: out.append({"kind":"BULLISH","low":a.high,"high":c.low,"time":df.index[i-1]})
        if a.low>c.high: out.append({"kind":"BEARISH","low":c.high,"high":a.low,"time":df.index[i-1]})
    return out
