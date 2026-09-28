import pandas as pd
from smc_agent.engine import analyze

def test_engine_no_trade_on_insufficient_data():
    d=pd.DataFrame({"open":[1],"high":[1],"low":[1],"close":[1]},index=pd.date_range("2025-01-01",periods=1,tz="UTC"))
    s=analyze(d); assert s.status=="NO TRADE"
