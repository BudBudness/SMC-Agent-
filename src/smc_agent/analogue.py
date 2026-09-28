def find_analogues(history,pattern,limit=20):
    matches=[]
    for item in history:
        if all(item.get(k)==v for k,v in pattern.items()):
            matches.append(item)
            if len(matches)>=limit: break
    return matches
def conditional_stats(matches,outcome_key="outcome"):
    if not matches:return {"samples":0}
    vals=[m.get(outcome_key) for m in matches if m.get(outcome_key) is not None]
    if not vals:return {"samples":0}
    return {"samples":len(vals),"mean":sum(vals)/len(vals)}
