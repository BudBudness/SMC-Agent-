"""Contracts for the Henryz manager/agent hierarchy."""
from dataclasses import dataclass, field
from typing import Any

TIMEFRAME_ORDER = ("12M", "6M", "3M", "W", "D", "4H", "1H", "15M", "5M", "1M")
DIRECTIONAL = {"LONG", "SHORT", "NEUTRAL"}

@dataclass(frozen=True)
class AgentObservation:
    agent: str
    layer: str
    timeframe: str
    state: str = "NEUTRAL"
    observations: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ResearchDecision:
    status: str
    authority: str
    weekly_state: str
    macro_thesis: str
    conflicts: tuple[str, ...]
    evidence_count: int
    sufficient_confluence: bool
    execution_allowed: bool = False
    rationale: tuple[str, ...] = ()

def normalize_state(value: Any) -> str:
    value = str(value or "NEUTRAL").upper()
    return value if value in DIRECTIONAL else "NEUTRAL"
