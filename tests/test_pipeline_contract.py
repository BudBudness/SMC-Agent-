import pandas as pd
import numpy as np
from smc_agent.pipeline import run
from smc_agent.report_schema import validate_report
from smc_agent.benchmark import score_detection

def test_pipeline_contract():
    idx=pd.date_range("2025-01-01",periods=5000,freq="min",tz="UTC")
    x=np.arange(len(idx))/100000
    df=pd.DataFrame({"open":1+x,"high":1+x+.0005,"low":1+x-.0005,"close":1+x+.0001},index=idx)
    result=run(df)
    assert result["dataset_validation"]["valid"]
    assert validate_report(result["report"])["valid"]

def test_benchmark_metrics():
    r=score_detection(["sweep","choch"],["sweep","fvg"])
    assert r["true_positive"]==1
    assert 0 <= r["f1"] <= 1
