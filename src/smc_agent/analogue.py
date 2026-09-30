"""Historical analogue research with explicit provenance and sample-size disclosure."""
DEFAULT_WEIGHTS={"regime":2.0,"weekly_bias":2.0,"location":1.0,"sweep":2.0,"displacement":1.5,"choch":1.5,"bos":1.0,"amd":1.0}
def _sim(a,b,weights=None):
    weights=weights or DEFAULT_WEIGHTS; total=score=0.0
    for k,w in weights.items():
        if k not in a or k not in b: continue
        total+=w; av,bv=a[k],b[k]
        if isinstance(av,(int,float)) and isinstance(bv,(int,float)): score+=w*max(0,1-abs(float(av)-float(bv)))
        else: score+=w if av==bv else 0
    return score/total if total else 0.0
def find_analogues(history,pattern,limit=20,weights=None,min_similarity=.35):
    matches=[(_sim(x,pattern,weights),x) for x in history or []]
    matches=[x for x in matches if x[0]>=min_similarity]
    matches.sort(reverse=True,key=lambda x:x[0])
    return [{"similarity":round(s,6),"record":r} for s,r in matches[:limit]]
def conditional_stats(matches,outcome_key="outcome"):
    records=[m.get("record",m) for m in matches or []]
    vals=[float(r[outcome_key]) for r in records if r.get(outcome_key) is not None]
    if not vals:return {"samples":0,"status":"INSUFFICIENT_SAMPLE"}
    mean=sum(vals)/len(vals)
    return {"samples":len(vals),"mean":mean,"min":min(vals),"max":max(vals),"std":(sum((v-mean)**2 for v in vals)/len(vals))**.5,
            "status":"DESCRIPTIVE_ONLY","warning":"Historical analogue frequency is not a prediction."}
def regime_conditioned(history,pattern,regime_key="regime",outcome_key="outcome"):
    regime=pattern.get(regime_key)
    subset=[x for x in history or [] if regime is None or x.get(regime_key)==regime]
    return conditional_stats(find_analogues(subset,pattern),outcome_key)
