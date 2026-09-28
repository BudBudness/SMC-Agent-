import pandas as pd
from smc_agent.providers import HistDataProvider

def test_histdata_provider_parses_and_normalizes(tmp_path):
    p=tmp_path/"EURUSD.csv"
    p.write_text("20120201 000000;1.306600;1.306600;1.306560;1.306560;0\n20120201 000100;1.306570;1.306570;1.306470;1.306560;0\n")
    df=HistDataProvider(p).candles()
    assert isinstance(df.index,pd.DatetimeIndex)
    assert str(df.index.tz)=="UTC"
    assert list(df.columns)==["open","high","low","close","volume"]
    assert len(df)==2
