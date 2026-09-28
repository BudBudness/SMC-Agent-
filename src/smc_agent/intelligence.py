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
def build_report(symbol,timestamp,state,liquidity,events,macro,hypotheses):
    hs=[asdict(h) if hasattr(h,"__dataclass_fields__") else h for h in hypotheses]
    supported=[h for h in hs if float(h.get("confidence",0))>=0.7]
    conclusion="Evidence is insufficient for a dominant hypothesis." if not supported else "Multiple hypotheses remain; inspect evidence and invalidation conditions."
    return IntelligenceReport(symbol,timestamp,state,liquidity,events,macro,hs,conclusion)
