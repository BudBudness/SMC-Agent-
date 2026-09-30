"""Inducement investigation with explicit temporal requirements."""

def detect(liquidity, sweep_event=None, structure=None):
    if not sweep_event:
        return {"detected":False,"reason":"no liquidity sweep observation"}
    swept_time=sweep_event.get("time")
    internal=[z for z in liquidity or [] if z.get("scope")=="internal"]
    external=[z for z in liquidity or [] if z.get("scope")=="external"]
    if not internal or not external:
        return {"detected":False,"reason":"missing internal or external liquidity context","structure":structure or {}}
    prior_internal=[z for z in internal if z.get("time") is not None and z["time"] < swept_time]
    prior_external=[z for z in external if z.get("time") is not None and z["time"] < swept_time]
    if not prior_internal:
        return {"detected":False,"reason":"no internal liquidity confirmed before sweep","structure":structure or {}}
    if not prior_external:
        return {"detected":False,"reason":"no external liquidity context confirmed before sweep","structure":structure or {}}
    return {
        "detected":False,
        "reason":"temporal inducement requires a documented internal-liquidity event followed by external-liquidity interaction; current detector has only a single sweep observation",
        "reference_internal":prior_internal[-1],
        "reference_external":prior_external[-1],
        "structure":structure or {},
    }
