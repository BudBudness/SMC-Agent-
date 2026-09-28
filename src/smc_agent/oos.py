"""Out-of-sample research summaries without trading metrics."""
def summarize(reports):
    if not reports:return {"windows":0}
    return {"windows":len(reports),"valid_windows":sum(bool(r.get("valid",False)) for r in reports),
            "samples":sum(int(r.get("samples",0)) for r in reports),
            "mean_reaction":_mean([r.get("mean_reaction") for r in reports])}
def _mean(values):
    v=[float(x) for x in values if x is not None]
    return None if not v else sum(v)/len(v)
