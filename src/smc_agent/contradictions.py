"""Cross-timeframe structural agreement and contradiction analysis."""
from dataclasses import dataclass, asdict

ORDER = ["12M","6M","3M","W","D","4H","1H","15M","5M","1M"]

@dataclass
class TimeframeEvidence:
    timeframe: str
    state: str
    evidence: list
    status: str

@dataclass
class Contradiction:
    higher: str
    higher_state: str
    lower: str
    lower_state: str
    relation: str
    explanation: str

def _norm(v):
    v = str(v or "NEUTRAL").upper()
    return v if v in {"LONG","SHORT","NEUTRAL"} else "NEUTRAL"

def compare(timeframe_states, authority="W"):
    rows=[]
    contradictions=[]
    for i,tf in enumerate(ORDER):
        state=_norm(timeframe_states.get(tf))
        rows.append(asdict(TimeframeEvidence(tf,state,[], "MISSING" if tf not in timeframe_states else "OBSERVED")))
        if state=="NEUTRAL": continue
        for higher in reversed(ORDER[:i]):
            hs=_norm(timeframe_states.get(higher))
            if hs=="NEUTRAL": continue
            if hs != state:
                contradictions.append(asdict(Contradiction(
                    higher,hs,tf,state,"CONFLICT",
                    f"{tf} structure conflicts with {higher} structure."
                )))
                break
    authority_state=_norm(timeframe_states.get(authority))
    return {
        "timeframes": rows,
        "contradictions": contradictions,
        "authority": authority,
        "authority_state": authority_state,
        "agreement_count": sum(r["state"]==authority_state for r in rows if r["state"]!="NEUTRAL") if authority_state!="NEUTRAL" else 0,
    }
