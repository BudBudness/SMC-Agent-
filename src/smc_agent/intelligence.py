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
    evidence:list
    analogue_research:dict
    def as_dict(self): return asdict(self)

def build_report(symbol,timestamp,state,liquidity,events,macro,hypotheses,evidence=None,analogue_research=None):
    hs=[]
    for h in hypotheses:
        x=asdict(h) if hasattr(h,"__dataclass_fields__") else dict(h)
        x.pop("confidence",None)
        hs.append(x)
    conflict=len(state.get("contradictions",[])) if isinstance(state,dict) else 0
    if not hs:
        conclusion="No hypotheses generated."
    elif conflict:
        conclusion="Structural conflict remains unresolved across timeframes."
    else:
        conclusion="Multiple hypotheses remain under investigation; review evidence, contradictions and invalidation conditions."
    return IntelligenceReport(symbol,timestamp,state,liquidity,events,macro,hs,conclusion,evidence or [],
                              analogue_research or {"status":"NOT_PROVIDED","matches":[],"samples":0,
                                                    "warning":"No historical episode set was supplied; no analogue inference was made."})
