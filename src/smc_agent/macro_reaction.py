"""Macro surprise classification and reaction context."""
def surprise(event):
    try:
        a,e=event.get("actual"),event.get("expected")
        return None if a is None or e is None else float(a)-float(e)
    except (TypeError,ValueError): return None
def classify_surprise(event):
    s=surprise(event)
    return {"surprise":s,"direction":"POSITIVE" if s>0 else "NEGATIVE" if s<0 else "NEUTRAL"} if s is not None else {"surprise":None,"direction":"UNKNOWN"}
def enrich(events): return [{**e,**classify_surprise(e)} for e in events or []]
