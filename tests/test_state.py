import pytest
from smc_agent.state import State,StateMachine

def test_order():
    s=StateMachine(); s.advance(State.MACRO_ANALYSIS); s.advance(State.WEEKLY_BIAS_FOUND)
    assert s.state==State.WEEKLY_BIAS_FOUND

def test_skip_rejected():
    with pytest.raises(ValueError): StateMachine().advance(State.WEEKLY_BIAS_FOUND)
