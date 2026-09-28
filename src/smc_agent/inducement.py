"""Research-oriented inducement detector. It requires internal liquidity and structural context."""
def detect(liquidity, sweep_event=None, structure=None):
    structure=structure or {}
    internal=[z for z in liquidity or [] if z.get("scope")=="internal"]
    if not internal or not sweep_event:
        return {"detected":False,"reason":"insufficient internal-liquidity and sweep evidence"}
    swept=float(sweep_event.get("price",0))
    prior=[z for z in internal if abs(float(z.get("price",0))-swept)>0]
    if not prior:
        return {"detected":False,"reason":"no distinct internal liquidity preceding sweep"}
    return {
        "detected":True,
        "reference":prior[-1],
        "evidence":["internal liquidity existed before external sweep","external liquidity was subsequently swept"],
        "structure":structure,
    }
