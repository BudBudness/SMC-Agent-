from smc_agent.agents.orchestrator import run_research_orchestration

def test_weekly_authority_blocks_lower_timeframe_override():
    result = run_research_orchestration(
        {"12M":"LONG","6M":"LONG","3M":"LONG","W":"LONG","D":"LONG","4H":"LONG","1H":"SHORT","15M":"SHORT","5M":"SHORT","1M":"SHORT"},
        evidence=[{"claim_id":"weekly_structure"},{"claim_id":"structure_break"}],
        contradictions=[{"higher":"W","higher_state":"LONG","lower":"1H","lower_state":"SHORT"}],
    )
    assert result["authority"] == "W"
    assert result["ceo"]["status"] == "CONFLICTED"
    assert result["ceo"]["execution_allowed"] is False

def test_insufficient_confluence_is_not_forced():
    result = run_research_orchestration(
        {"12M":"LONG","6M":"LONG","3M":"LONG","W":"LONG","15M":"LONG"},
        evidence=[{"claim_id":"weekly_structure"}],
        contradictions=[],
    )
    assert result["ceo"]["status"] == "CONDITIONAL"
    assert result["ceo"]["sufficient_confluence"] is False
    assert result["ceo"]["execution_allowed"] is False

def test_neutral_weekly_is_insufficient():
    result = run_research_orchestration(
        {"12M":"LONG","6M":"LONG","3M":"LONG","W":"NEUTRAL","15M":"LONG"},
        evidence=[{"claim_id":"structure_break"},{"claim_id":"displacement"}],
        contradictions=[],
    )
    assert result["ceo"]["status"] == "INSUFFICIENT_EVIDENCE"
