"""Macro surprise semantics; numeric surprise is not directional interpretation."""
def surprise(event):
    try:
        a,e=event.get("actual"),event.get("expected")
        return None if a is None or e is None else float(a)-float(e)
    except (TypeError,ValueError): return None

def classify_surprise(event):
    s=surprise(event)
    polarity=event.get("polarity","NEUTRAL")
    direction="UNKNOWN"
    if s is not None:
        if polarity=="HIGHER_IS_POSITIVE": direction="POSITIVE" if s>0 else "NEGATIVE" if s<0 else "NEUTRAL"
        elif polarity=="HIGHER_IS_NEGATIVE": direction="NEGATIVE" if s>0 else "POSITIVE" if s<0 else "NEUTRAL"
        else: direction="UNINTERPRETED"
    return {"surprise":s,"direction":direction,"polarity":polarity}

def enrich(events):
    return [{**e,**classify_surprise(e)} for e in events or []]
