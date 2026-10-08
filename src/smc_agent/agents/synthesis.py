"""CEO research synthesis: classification only, never trade execution."""
from .contracts import AgentObservation, ResearchDecision, normalize_state

def synthesize(states, evidence, contradictions, observations):
    weekly = normalize_state(states.get("W"))
    macro = normalize_state(states.get("6M"))
    macro3 = normalize_state(states.get("3M"))
    macro_thesis = macro if macro in {"LONG", "SHORT"} and macro == macro3 else "NEUTRAL"
    conflicts = tuple(
        f'{c.get("higher")}={c.get("higher_state")} conflicts with '
        f'{c.get("lower")}={c.get("lower_state")}'
        for c in contradictions
    )
    evidence_count = len(evidence or [])
    has_structural_confirmation = any(
        o.agent == "structure_liquidity_manager" and "15M" in o.evidence
        for o in observations
    )
    sufficient = bool(
        weekly != "NEUTRAL"
        and evidence_count >= 2
        and has_structural_confirmation
        and not conflicts
    )
    if weekly == "NEUTRAL":
        status = "INSUFFICIENT_EVIDENCE"
    elif conflicts:
        status = "CONFLICTED"
    elif sufficient:
        status = "ALIGNED_RESEARCH_STATE"
    else:
        status = "CONDITIONAL"
    rationale = [
        "Weekly is the authoritative timeframe.",
        "Lower timeframes add evidence but cannot override higher-timeframe structure.",
        "No setup is forced when confluence is insufficient.",
        "Output is research classification only."
    ]
    return ResearchDecision(
        status=status,
        authority="W",
        weekly_state=weekly,
        macro_thesis=macro_thesis,
        conflicts=conflicts,
        evidence_count=evidence_count,
        sufficient_confluence=sufficient,
        execution_allowed=False,
        rationale=tuple(rationale),
    )

def as_dict(decision):
    return {
        "status": decision.status,
        "authority": decision.authority,
        "weekly_state": decision.weekly_state,
        "macro_thesis": decision.macro_thesis,
        "conflicts": list(decision.conflicts),
        "evidence_count": decision.evidence_count,
        "sufficient_confluence": decision.sufficient_confluence,
        "execution_allowed": False,
        "rationale": list(decision.rationale),
    }
