"""Reproducible evidence ledger."""
from dataclasses import dataclass,asdict
@dataclass
class Evidence:
    claim_id:str; observation:str; source:str; timeframe:str; timestamp:object; method:str
    supports:list; contradicts:list; invalidates:list; confidence:float
class EvidenceLedger:
    def __init__(self): self.items=[]
    def add(self,e): self.items.append(asdict(e) if hasattr(e,"__dataclass_fields__") else dict(e))
    def for_claim(self,claim_id): return [x for x in self.items if x.get("claim_id")==claim_id]
    def validate(self):
        errors=[]
        for i,e in enumerate(self.items):
            if not e.get("claim_id"):errors.append((i,"missing claim_id"))
            if not e.get("observation"):errors.append((i,"missing observation"))
            if not e.get("source"):errors.append((i,"missing source"))
            try:c=float(e.get("confidence",0))
            except (TypeError,ValueError):c=-1
            if not 0<=c<=1:errors.append((i,"confidence outside 0..1"))
        return {"valid":not errors,"errors":errors,"count":len(self.items)}
