"""Deterministic manager graph for Henryz SMC research."""
from .managers import (
    macro_manager, day_trading_manager, structure_liquidity_manager,
    premium_discount_manager, short_trap_manager, h4_range_manager,
    execution_manager, m1_execution_manager, risk_manager, stop_loss_manager,
    reporting_manager,
)
from .synthesis import synthesize, as_dict

def run_research_orchestration(states, methodology=None, evidence=None, contradictions=None):
    states = states or {}
    methodology = methodology or {}
    evidence = evidence or []
    contradictions = contradictions or []

    observations = [
        macro_manager(states),
        day_trading_manager(states, methodology),
        structure_liquidity_manager(states, methodology),
        premium_discount_manager(methodology),
        short_trap_manager(methodology),
        h4_range_manager(states, methodology),
        execution_manager(states),
        m1_execution_manager(states),
        risk_manager(),
        stop_loss_manager(),
    ]
    observations.append(reporting_manager(observations))
    decision = synthesize(states, evidence, contradictions, observations)

    return {
        "architecture": "MACRO → DAY_TRADING → STRUCTURE_LIQUIDITY → EXECUTION_RESEARCH → RISK_RESEARCH → REPORTING → CEO_SYNTHESIS",
        "authority": "W",
        "decision_boundary": "RESEARCH_ONLY",
        "observations": [
            {
                "agent": o.agent, "layer": o.layer, "timeframe": o.timeframe,
                "state": o.state, "observations": list(o.observations),
                "evidence": list(o.evidence), "conflicts": list(o.conflicts),
                "metadata": o.metadata,
            } for o in observations
        ],
        "ceo": as_dict(decision),
    }
