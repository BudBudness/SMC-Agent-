"""Semantic validation for the canonical research report."""
from datetime import datetime

SCHEMA_VERSION="2.0"
REQUIRED=("symbol","timestamp","market_state","liquidity","events","macro","hypotheses","conclusion","evidence","analogue_research")
STATES={"LONG","SHORT","NEUTRAL","UNKNOWN","INSUFFICIENT_DATA"}
STRENGTH={"LOW","MODERATE","HIGH","UNRESOLVED"}

def _is_time(v):
    if isinstance(v,datetime): return True
    try: return bool(v) and bool(__import__("pandas").Timestamp(v))
    except Exception: return False

def validate_report(report):
    errors=[]
    if not isinstance(report,dict): return {"valid":False,"errors":["report must be an object"],"schema_version":SCHEMA_VERSION}
    missing=[k for k in REQUIRED if k not in report]
    errors.extend(f"missing {k}" for k in missing)
    if missing: return {"valid":False,"errors":errors,"missing":missing,"schema_version":SCHEMA_VERSION}
    if not isinstance(report["symbol"],str) or not report["symbol"]: errors.append("symbol must be non-empty")
    if not _is_time(report["timestamp"]): errors.append("timestamp must be parseable")
    ms=report["market_state"]
    if not isinstance(ms,dict): errors.append("market_state must be an object")
    elif ms.get("weekly_bias") not in STATES: errors.append("invalid weekly_bias")
    liq=report["liquidity"]
    if not isinstance(liq,dict): errors.append("liquidity must be an object")
    elif not isinstance(liq.get("zones"),list): errors.append("liquidity.zones must be a list")
    if not isinstance(report["events"],list): errors.append("events must be a list")
    else:
        for i,e in enumerate(report["events"]):
            if not isinstance(e,dict): errors.append(f"events[{i}] must be an object"); continue
            for k in ("name","time","timeframe"): 
                if not e.get(k): errors.append(f"events[{i}] missing {k}")
    macro=report["macro"]
    if not isinstance(macro,dict) or not isinstance(macro.get("events"),list): errors.append("macro.events must be a list")
    hyps=report["hypotheses"]
    if not isinstance(hyps,list): errors.append("hypotheses must be a list")
    else:
        for i,h in enumerate(hyps):
            if not isinstance(h,dict): errors.append(f"hypotheses[{i}] must be an object"); continue
            for k in ("name","evidence","contradictions","invalidation"):
                if k not in h: errors.append(f"hypotheses[{i}] missing {k}")
            if "confidence" in h and h["confidence"] is not None: errors.append(f"hypotheses[{i}] contains unsupported confidence")
    ev=report["evidence"]
    if not isinstance(ev,list): errors.append("evidence must be a list")
    else:
        for i,e in enumerate(ev):
            if not isinstance(e,dict): errors.append(f"evidence[{i}] must be an object"); continue
            for k in ("claim_id","observation","source","provenance"): 
                if not e.get(k): errors.append(f"evidence[{i}] missing {k}")
            if e.get("strength") not in STRENGTH: errors.append(f"evidence[{i}] invalid strength")
    ar=report["analogue_research"]
    if not isinstance(ar,dict): errors.append("analogue_research must be an object")
    else:
        if ar.get("status") not in {"NOT_PROVIDED","DESCRIPTIVE_ONLY","INSUFFICIENT_SAMPLE"}: errors.append("invalid analogue_research.status")
        if not isinstance(ar.get("matches"),list): errors.append("analogue_research.matches must be a list")
    return {"valid":not errors,"errors":errors,"missing":missing,"schema_version":SCHEMA_VERSION}
