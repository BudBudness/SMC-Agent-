from dataclasses import dataclass,asdict
@dataclass
class Hypothesis:
    name:str
    evidence:list
    contradictions:list
    invalidation:list
    confidence:float
@dataclass
class IntelligenceReport:
    symbol:str
    timestamp:object
    market_state:dict
    liquidity:dict
    events:list
    macro:dict
    hypotheses:list
    conclusion:str
    def as_dict(self): return asdict(self)

def build_report(symbol,timestamp,state,liquidity,events,macro,hypotheses):
    hs=[asdict(h) if hasattr(h,"__dataclass_fields__") else h for h in hypotheses]
    hs.sort(key=lambda h:float(h.get("confidence",0)),reverse=True)
    conflict=len(state.get("contradictions",[])) if isinstance(state,dict) else 0
    top=hs[0] if hs else None
    if not top: conclusion="No hypotheses generated."
    elif conflict and conflict>=2: conclusion="Structural conflict remains unresolved across timeframes."
    elif float(top.get("confidence",0))<0.5: conclusion="Evidence is insufficient for a dominant hypothesis."
    else: conclusion=f"Leading hypothesis: {top['name']}; review supporting evidence and invalidation conditions."
    return IntelligenceReport(symbol,timestamp,state,liquidity,events,macro,hs,conclusion)
