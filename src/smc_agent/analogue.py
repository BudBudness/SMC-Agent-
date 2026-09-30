"""Historical analogue research. Descriptive only; never a prediction or ranking recommendation."""
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
    matches.sort(key=lambda x:x[0],reverse=True)
    return [{"similarity":round(s,6),"record":r} for s,r in matches[:limit]]

def conditional_stats(matches,outcome_key="outcome"):
    records=[m.get("record",m) for m in matches or []]
    vals=[float(r[outcome_key]) for r in records if r.get(outcome_key) is not None]
    if not vals:return {"samples":0,"status":"INSUFFICIENT_SAMPLE","warning":"No usable historical outcomes."}
    mean=sum(vals)/len(vals)
    return {"samples":len(vals),"mean":mean,"min":min(vals),"max":max(vals),
            "std":(sum((v-mean)**2 for v in vals)/len(vals))**.5,
            "status":"DESCRIPTIVE_ONLY","warning":"Historical analogue frequency is descriptive and is not a prediction."}

def research(history,pattern,limit=20,min_similarity=.35,outcome_key="outcome"):
    if not history:
        return {"status":"NOT_PROVIDED","matches":[],"samples":0,
                "warning":"No historical episode set was supplied; analogue research is unavailable."}
    matches=find_analogues(history,pattern,limit=limit,min_similarity=min_similarity)
    stats=conditional_stats(matches,outcome_key)
    return {"status":stats["status"],"matches":matches,"samples":stats["samples"],
            "conditional_stats":stats,"method":"feature_similarity","min_similarity":min_similarity,
            "warning":"Matches are descriptive historical analogues; similarity does not imply causality or future direction."}
