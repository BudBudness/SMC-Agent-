"""Pure deterministic managers over the existing engine output."""
from .contracts import AgentObservation, normalize_state

def _state(states, tf):
    return normalize_state(states.get(tf))

def macro_manager(states):
    agreement = _state(states, "6M") in {"LONG", "SHORT"} and _state(states, "6M") == _state(states, "3M")
    thesis = _state(states, "6M") if agreement else "NEUTRAL"
    evidence = tuple(tf for tf in ("12M", "6M", "3M") if _state(states, tf) != "NEUTRAL")
    return AgentObservation(
        "macro_manager", "MACRO", "12M→6M→3M→W",
        thesis, ("WHERE/WHY macro context", "6M/3M agreement required for directional macro thesis"),
        evidence, metadata={"12M": _state(states, "12M"), "6M": _state(states, "6M"), "3M": _state(states, "3M")}
    )

def day_trading_manager(states, methodology=None):
    return AgentObservation(
        "day_trading_manager", "DAY_TRADING", "D→4H→15M",
        _state(states, "15M"),
        ("Daily target context", "4H range/AMD", "15M confirmation"),
        tuple(tf for tf in ("D", "4H", "15M") if _state(states, tf) != "NEUTRAL"),
        metadata={"daily": _state(states, "D"), "4H": _state(states, "4H"),
                  "amd": (methodology or {}).get("4H", {}).get("amd")}
    )

def structure_liquidity_manager(states, methodology=None):
    m = methodology or {}
    return AgentObservation(
        "structure_liquidity_manager", "STRUCTURE_LIQUIDITY", "1H→15M→5M",
        _state(states, "15M"),
        ("1H liquidity zones", "liquidity sweep observations", "15M structural confirmation"),
        tuple(tf for tf in ("1H", "15M", "5M") if _state(states, tf) != "NEUTRAL"),
        metadata={"1H_liquidity": m.get("1H", {}).get("liquidity_zones", []),
                  "1H_sweep": m.get("1H", {}).get("sweep"),
                  "15M_confirmation": m.get("15M", {}).get("confirmation")}
    )

def premium_discount_manager(methodology=None):
    m = methodology or {}
    daily = m.get("daily", {})
    return AgentObservation(
        "premium_discount_agent", "STRUCTURE_LIQUIDITY", "D",
        normalize_state(m.get("weekly", {}).get("direction")),
        ("Daily premium/discount classification",),
        ("daily_location",) if daily.get("location") else (),
        metadata={"location": daily.get("location")}
    )

def short_trap_manager(methodology=None):
    m = methodology or {}
    return AgentObservation(
        "short_trap_agent", "STRUCTURE_LIQUIDITY", "1H→15M",
        "NEUTRAL",
        ("Trap classification is evidence-only until structural confirmation exists",),
        (),
        metadata={"sweep": m.get("1H", {}).get("sweep")}
    )

def h4_range_manager(states, methodology=None):
    m = methodology or {}
    return AgentObservation(
        "h4_range_agent", "DAY_TRADING", "4H",
        _state(states, "4H"),
        ("4H swing structure", "AMD phase classification"),
        ("4H",) if _state(states, "4H") != "NEUTRAL" else (),
        metadata={"amd": m.get("4H", {}).get("amd")}
    )

def execution_manager(states):
    return AgentObservation(
        "execution_manager", "EXECUTION_RESEARCH", "5M→1M",
        _state(states, "5M"),
        ("5M refinement", "1M fill observation"),
        tuple(tf for tf in ("5M", "1M") if _state(states, tf) != "NEUTRAL"),
        metadata={"execution_semantics": "research_observation_only"}
    )

def m1_execution_manager(states):
    return AgentObservation(
        "m1_execution_agent", "EXECUTION_RESEARCH", "1M",
        _state(states, "1M"),
        ("1M microstructure observation",),
        ("1M",) if _state(states, "1M") != "NEUTRAL" else (),
        metadata={"execution_allowed": False}
    )

def risk_manager():
    return AgentObservation(
        "risk_manager", "RISK_RESEARCH", "W→1M",
        "NEUTRAL",
        ("Risk/invalidation evidence may be recorded", "No position construction is emitted"),
        (),
        metadata={"position_sizing": False, "stop_recommendation": False, "target_recommendation": False}
    )

def stop_loss_manager():
    return AgentObservation(
        "stop_loss_agent", "RISK_RESEARCH", "5M→1M",
        "NEUTRAL",
        ("Invalidation evidence only",),
        (),
        metadata={"stop_instruction": False}
    )

def reporting_manager(observations):
    return AgentObservation(
        "reporting_manager", "REPORTING", "ALL",
        "NEUTRAL",
        ("Research artifact aggregation", "Lineage-preserving synthesis"),
        tuple(o.agent for o in observations if o.evidence),
        metadata={"observation_count": len(observations)}
    )
