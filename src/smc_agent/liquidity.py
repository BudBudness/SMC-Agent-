"""Liquidity mapping and chronological sweep observation."""

def map_liquidity(swing_points, scope="external"):
    return [
        {
            "kind": "BSL" if point[0] == "HIGH" else "SSL",
            "price": float(point[2]),
            "time": point[1],
            "scope": scope,
            "strength": "structural",
        }
        for point in swing_points
    ]

def sweep(df, zones, lookback=96):
    """Find the latest confirmed liquidity raid in the available window.

    This is deliberately an observation: without a subsequent candle it is not
    upgraded to a confirmed structural reversal.
    """
    if df.empty or not zones:
        return None
    start=max(0,len(df)-lookback)
    for i in range(len(df)-1,start-1,-1):
        r=df.iloc[i]
        ts=df.index[i]
        candidates=sorted(zones,key=lambda z:abs(float(r.close)-float(z["price"])))
        for z in candidates:
            price=float(z["price"])
            if z["kind"]=="BSL" and float(r.high)>price and float(r.close)<price:
                return {"kind":"BSL","price":price,"time":ts,"scope":z.get("scope","unknown"),"confirmation":"rejection_close"}
            if z["kind"]=="SSL" and float(r.low)<price and float(r.close)>price:
                return {"kind":"SSL","price":price,"time":ts,"scope":z.get("scope","unknown"),"confirmation":"rejection_close"}
    return None
