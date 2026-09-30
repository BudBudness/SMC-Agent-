import pandas as pd
import numpy as np
from smc_agent.fvg import find_fvg
from smc_agent.order_blocks import find_order_blocks
from smc_agent.amd import classify_amd
from smc_agent.pipeline import run

def test_fvg_has_lifecycle_fields():
    idx=pd.date_range("2026-01-01",periods=5,freq="h",tz="UTC")
    df=pd.DataFrame({"open":[1,1,1,1,1],"high":[1.1,1.2,1.5,1.6,1.7],"low":[.9,.95,1.3,1.4,1.5],"close":[1.05,1.15,1.4,1.5,1.6]},index=idx)
    gaps=find_fvg(df)
    assert gaps
    assert {"formed_at","status"} <= set(gaps[0])

def test_order_blocks_have_lifecycle_fields():
    idx=pd.date_range("2026-01-01",periods=4,freq="h",tz="UTC")
    df=pd.DataFrame({"open":[2,1,1.5,1.6],"high":[2.1,1.6,2.3,2.4],"low":[1.8,.9,1.4,1.5],"close":[1.9,1.5,2.2,2.3]},index=idx)
    obs=find_order_blocks(df)
    assert obs
    assert {"formed_at","status"} <= set(obs[0])

def test_pipeline_exposes_mtf_validation():
    idx=pd.date_range("2026-01-01",periods=5000,freq="min",tz="UTC")
    x=np.arange(len(idx))/100000
    df=pd.DataFrame({"open":1+x,"high":1+x+.0005,"low":1+x-.0005,"close":1+x+.0001},index=idx)
    result=run(df)
    assert result["mtf_validation"]["valid"]
