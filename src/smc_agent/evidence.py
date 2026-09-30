"""Reproducible evidence ledger; confidence is optional metadata, not a required score."""
from dataclasses import dataclass,asdict
from typing import Optional
@dataclass
class Evidence:
    claim_id:str; observation:str; source:str; timeframe:str=""; timestamp:object=None; method:str=""
    supports:list=None; contradicts:list=None; invalidates:list=None; confidence:Optional[float]=None
class EvidenceLedger:
    def __init__(self): self.items=[]
    def add(self,e):
        item=asdict(e) if hasattr(e,"__dataclass_fields__") else dict(e)
        for k in ("supports","contradicts","invalidates"): item.setdefault(k,[])
        self.items.append(item)
    def for_claim(self,claim_id): return [x for x in self.items if x.get("claim_id")==claim_id]
    def validate(self):
        errors=[]
        for i,e in enumerate(self.items):
            for key in ("claim_id","observation","source"):
                if not e.get(key): errors.append((i,f"missing {key}"))
            if e.get("confidence") is not None:
                try:c=float(e["confidence"])
                except (TypeError,ValueError): c=-1
                if not 0<=c<=1: errors.append((i,"confidence outside 0..1"))
        return {"valid":not errors,"errors":errors,"count":len(self.items)}
