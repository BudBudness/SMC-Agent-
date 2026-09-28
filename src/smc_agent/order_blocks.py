def find_order_blocks(df):
    out=[]
    for i in range(1,len(df)):
        p,c=df.iloc[i-1],df.iloc[i]
        if p.close<p.open and c.close>c.open and c.high>p.high:
            out.append({"kind":"BULLISH","low":p.low,"high":p.open,"time":df.index[i-1]})
        if p.close>p.open and c.close<c.open and c.low<p.low:
            out.append({"kind":"BEARISH","low":p.open,"high":p.high,"time":df.index[i-1]})
    return out
