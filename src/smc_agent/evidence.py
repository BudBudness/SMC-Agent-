"""Research evidence ledger with provenance and non-predictive strength semantics."""
from dataclasses import dataclass,asdict
from typing import Optional

@dataclass
class Evidence:
    claim_id:str
    observation:str
    source:str
    timeframe:str=""
    timestamp:object=None
    method:str=""
    supports:list=None
    contradicts:list=None
    invalidates:list=None
    provenance:dict=None
    strength:Optional[str]=None
    confidence:Optional[float]=None

class EvidenceLedger:
    VALID_STRENGTH={"LOW","MODERATE","HIGH","UNRESOLVED"}
    def __init__(self): self.items=[]
    def add(self,e):
        item=asdict(e) if hasattr(e,"__dataclass_fields__") else dict(e)
        for k in ("supports","contradicts","invalidates"): item.setdefault(k,[])
        item.setdefault("provenance",{})
        if item.get("strength") is None: item["strength"]="UNRESOLVED"
        self.items.append(item)
    def for_claim(self,claim_id): return [x for x in self.items if x.get("claim_id")==claim_id]
    def validate(self):
        errors=[]
        for i,e in enumerate(self.items):
            for key in ("claim_id","observation","source"):
                if not e.get(key): errors.append((i,f"missing {key}"))
            if e.get("strength") not in self.VALID_STRENGTH: errors.append((i,"invalid evidence strength"))
            if not isinstance(e.get("provenance"),dict): errors.append((i,"provenance must be an object"))
            if e.get("confidence") is not None:
                try:
                    c=float(e["confidence"])
                    if not 0 <= c <= 1: errors.append((i,"confidence outside 0..1"))
                except (TypeError,ValueError): errors.append((i,"invalid confidence metadata"))
        return {"valid":not errors,"errors":errors,"count":len(self.items)}
