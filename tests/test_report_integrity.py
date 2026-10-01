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
\n\ndef test_source_integrity_reports_duplicate_and_invalid_ohlc():\n    from smc_agent.data_integrity import validate_source\n    df = _df(20)\n    df = pd.concat([df, df.iloc[[0]]])\n    df.iloc[-1, df.columns.get_loc("high")] = 0.5\n    result = validate_source(df)\n    assert result["status"] == "FAIL"\n    assert result["duplicate_timestamps"] == 1\n    assert result["invalid_ohlc_rows"] == 1\n\n\ndef test_source_integrity_passes_clean_fixture():\n    from smc_agent.data_integrity import validate_source\n    result = validate_source(_df(20))\n    assert result["status"] == "PASS"\n    assert result["invalid_ohlc_rows"] == 0\n

def test_event_study_excludes_incomplete_forward_horizons():
    from smc_agent.event_study import event_reactions, summarize
    df = _df(5)
    events = [{"name": "test", "time": df.index[-2], "timeframe": "1M"}]
    reactions = event_reactions(df, events, horizons=(1, 3))
    assert len(reactions) == 1
    assert pd.notna(reactions.iloc[0]["h1"])
    assert pd.isna(reactions.iloc[0]["h3"])
    summary = summarize(reactions)
    assert summary["complete_samples"]["h1"] == 1
    assert summary["complete_samples"]["h3"] == 0
    assert summary["status"] == "DESCRIPTIVE_ONLY"
