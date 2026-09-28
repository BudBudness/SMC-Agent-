def map_liquidity(swings):
    return [{"kind":"BSL" if s[0]=="HIGH" else "SSL","price":s[2],"time":s[1]} for s in swings]

def sweep(df,zones):
    if df.empty:return None
    r=df.iloc[-1]
    for z in sorted(zones,key=lambda x:abs(r.close-x["price"])):
        if z["kind"]=="BSL" and r.high>z["price"] and r.close<z["price"]:
            return {"kind":"BSL","price":z["price"],"time":df.index[-1]}
        if z["kind"]=="SSL" and r.low<z["price"] and r.close>z["price"]:
            return {"kind":"SSL","price":z["price"],"time":df.index[-1]}
    return None
