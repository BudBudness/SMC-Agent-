def summarize(reports):
    if not reports:
        return {"windows":0}
    keys=("trades","win_rate","expectancy","profit_factor","max_drawdown","average_R")
    return {"windows":len(reports),**{k:sum(float(r.get("metrics",{}).get(k) or 0) for r in reports)/len(reports) for k in keys}}
