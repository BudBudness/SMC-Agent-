"""Event ordering engine: observations first, interpretation second."""
from dataclasses import dataclass, asdict

ORDER={"liquidity_formation":0,"inducement":1,"approach":2,"sweep":3,
       "rejection":4,"displacement":5,"choch":6,"bos":7,"fvg":8,"order_block":9,"reaction":10}

@dataclass
class Event:
    name:str
    time:object
    timeframe:str
    kind:str="observation"
    evidence:dict|None=None

def sequence(events):
    normalized=[asdict(e) if hasattr(e,"__dataclass_fields__") else dict(e) for e in events]
    normalized.sort(key=lambda e:(e.get("time") is None,e.get("time")))
    rank_errors=[]
    previous=-1
    for e in normalized:
        rank=ORDER.get(e.get("name"),99)
        if rank<previous:
            rank_errors.append({"event":e.get("name"),"issue":"out_of_sequence"})
        previous=max(previous,rank)
    return {"events":normalized,"sequence_valid":not rank_errors,"ordering_issues":rank_errors}

def build_sequence(observations):
    return sequence(observations)
