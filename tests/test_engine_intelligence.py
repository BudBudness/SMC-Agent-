import pandas as pd
import numpy as np
from smc_agent.engine import analyze

def test_engine_returns_intelligence_report():
    idx=pd.date_range("2024-01-01",periods=5000,freq="min",tz="UTC")
    x=np.arange(len(idx))/100000
    df=pd.DataFrame({"open":1+x,"high":1+x+.0005,"low":1+x-.0005,"close":1+x+.0001},index=idx)
    report=analyze(df)
    assert hasattr(report,"as_dict")
    assert "contradictions" in report.market_state
    assert isinstance(report.hypotheses,list)
