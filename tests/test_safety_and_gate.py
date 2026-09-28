from smc_agent.safety import SafetyGate
from smc_agent.final_gate import readiness
def test_safety_defaults_block(): assert not SafetyGate().allow(.0001,1,0,0)
def test_readiness_reports_missing(): assert readiness({"live_disabled":True})["ready"] is False
