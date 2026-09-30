from dataclasses import dataclass,asdict
from typing import Optional

@dataclass
class Hypothesis:
    name:str
    evidence:list
    contradictions:list
    invalidation:list
    confidence:Optional[float]=None

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
    conflict=len(state.get("contradictions",[])) if isinstance(state,dict) else 0
    if not hs:
        conclusion="No hypotheses generated."
    elif conflict:
        conclusion="Structural conflict remains unresolved across timeframes."
    else:
        conclusion="Multiple hypotheses remain under investigation; review evidence, contradictions and invalidation conditions."
    return IntelligenceReport(symbol,timestamp,state,liquidity,events,macro,hs,conclusion)
