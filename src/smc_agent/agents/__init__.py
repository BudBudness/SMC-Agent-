"""Deterministic manager/agent orchestration for Henryz SMC research.

Agents are analytical modules. They never execute trades and cannot override
higher-timeframe authority.
"""

from .orchestrator import run_research_orchestration

__all__ = ["run_research_orchestration"]
