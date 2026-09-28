import pandas as pd
from smc_agent.backtest import Backtester
def test_backtest_empty_is_causal():
 d=pd.DataFrame({"open":[1.0]*120,"high":[1.1]*120,"low":[.9]*120,"close":[1.0]*120},index=pd.date_range("2025-01-01",periods=120,freq="min",tz="UTC"))
 r=Backtester(d).run(); assert r["execution_model"]["lookahead"] is False
