"""Inducement detector requiring internal liquidity and subsequent external interaction."""
def detect(liquidity,sweep_event=None,structure=None):
    internal=[z for z in liquidity or [] if z.get("scope")=="internal"]
    external=[z for z in liquidity or [] if z.get("scope")!="internal"]
    if not internal or not sweep_event:return {"detected":False,"reason":"insufficient internal-liquidity and sweep evidence"}
    swept=float(sweep_event.get("price",0))
    prior=[z for z in internal if abs(float(z.get("price",0))-swept)>0]
    if not prior:return {"detected":False,"reason":"no distinct internal liquidity"}
    return {"detected":bool(external),"reference":prior[-1],"evidence":[
        "internal liquidity existed before external interaction",
        "subsequent liquidity interaction observed" if external else "no external confirmation"] ,
        "structure":structure or {}}
