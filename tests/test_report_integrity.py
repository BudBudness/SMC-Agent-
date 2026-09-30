import pandas as pd
import numpy as np
import pytest
from smc_agent.pipeline import run
from smc_agent.report_schema import validate_report
from smc_agent.macro_reaction import classify_surprise

def _df(n=5000):
    idx=pd.date_range("2025-01-01",periods=n,freq="min",tz="UTC")
    x=np.arange(n)/100000
    return pd.DataFrame({"open":1+x,"high":1+x+.0005,"low":1+x-.0005,"close":1+x+.0001},index=idx)

def test_canonical_report_has_evidence_and_analogue_surfaces():
    r=run(_df())
    report=r["report"]
    assert "evidence" in report
    assert "analogue_research" in report
    assert report["analogue_research"]["status"]=="NOT_PROVIDED"
    assert validate_report(report)["valid"]

def test_schema_rejects_unsupported_hypothesis_confidence():
    r=run(_df())["report"]
    r["hypotheses"][0]["confidence"]=0.9
    assert not validate_report(r)["valid"]

def test_macro_surprise_requires_explicit_polarity_for_direction():
    assert classify_surprise({"actual":105,"expected":100})["direction"]=="UNINTERPRETED"
    assert classify_surprise({"actual":105,"expected":100,"polarity":"HIGHER_IS_POSITIVE"})["direction"]=="POSITIVE"
    assert classify_surprise({"actual":105,"expected":100,"polarity":"HIGHER_IS_NEGATIVE"})["direction"]=="NEGATIVE"

def test_pipeline_rejects_bad_ohlc():
    df=_df(500)
    df.iloc[10,df.columns.get_loc("high")]=0.5
    with pytest.raises(ValueError):
        run(df)
