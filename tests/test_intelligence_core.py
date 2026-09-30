import pandas as pd
from smc_agent.contradictions import compare
from smc_agent.analogue import find_analogues,conditional_stats
from smc_agent.macro_reaction import classify_surprise
from smc_agent.dataset_validation import validate_ohlc
from smc_agent.evidence import EvidenceLedger

def test_contradictions():
    r=compare({"W":"LONG","D":"SHORT","4H":"LONG","15M":"SHORT"})
    assert r["authority_state"]=="LONG"
    assert r["conflict_count"]>=2

def test_analogue_similarity():
    h=[{"regime":"TREND","weekly_bias":"LONG","outcome":1},{"regime":"RANGE","weekly_bias":"SHORT","outcome":-1}]
    m=find_analogues(h,{"regime":"TREND","weekly_bias":"LONG"})
    assert m and conditional_stats(m)["mean"]==1

def test_macro_surprise():
    assert classify_surprise({"actual":105,"expected":100})["direction"]=="UNINTERPRETED"

def test_dataset_validation():
    idx=pd.date_range("2026-01-01",periods=3,freq="h",tz="UTC")
    df=pd.DataFrame({"open":[1,2,3],"high":[2,3,4],"low":[0,1,2],"close":[1.5,2.5,3.5]},index=idx)
    assert validate_ohlc(df)["valid"]

def test_evidence_ledger():
    l=EvidenceLedger()
    l.add({"claim_id":"c1","observation":"x","source":"test","confidence":.8})
    assert l.validate()["valid"]
