"""Research evidence ledger with provenance and non-predictive strength semantics."""
from dataclasses import dataclass,asdict

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
    strength:str="UNRESOLVED"

class EvidenceLedger:
    VALID_STRENGTH={"LOW","MODERATE","HIGH","UNRESOLVED"}
    def __init__(self): self.items=[]
    def add(self,e):
        item=asdict(e) if hasattr(e,"__dataclass_fields__") else dict(e)
        for k in ("supports","contradicts","invalidates"): item.setdefault(k,[])
        item.setdefault("provenance",{})
        if not item["provenance"]: item["provenance"]={"status":"UNSPECIFIED","note":"Legacy evidence item; canonical engine supplies method/source context."}
        item.setdefault("strength","UNRESOLVED")
        self.items.append(item)
    def for_claim(self,claim_id): return [x for x in self.items if x.get("claim_id")==claim_id]
    def validate(self):
        errors=[]
        for i,e in enumerate(self.items):
            for k in ("claim_id","observation","source"):
                if not e.get(k): errors.append((i,f"missing {k}"))
            if e.get("strength") not in self.VALID_STRENGTH: errors.append((i,"invalid evidence strength"))
            if not isinstance(e.get("provenance"),dict): errors.append((i,"provenance must be an object"))
            if e.get("timestamp") is not None and not hasattr(e["timestamp"],"isoformat"): errors.append((i,"timestamp must be datetime-like"))
            # Legacy confidence metadata is accepted for compatibility but is not interpreted as predictive confidence.
        return {"valid":not errors,"errors":errors,"count":len(self.items)}
    def as_list(self): return list(self.items)
