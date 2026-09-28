from typing import Protocol
import pandas as pd

class MarketDataProvider(Protocol):
    def candles(self,symbol:str,timeframe:str,start=None,end=None)->pd.DataFrame: ...

class EconomicCalendarProvider(Protocol):
    def events(self,start=None,end=None): ...

class HistDataProvider:
    """Reader for HistData Generic ASCII M1 CSV files.

    HistData timestamps are EST without daylight-saving adjustment; this adapter
    converts them to UTC before exposing the canonical OHLC schema.
    """
    def __init__(self,path): self.path=path
    def candles(self,symbol="EURUSD",timeframe="M1",start=None,end=None):
        if timeframe != "M1": raise ValueError("HistDataProvider currently supports M1 only")
        df=pd.read_csv(self.path,sep=";",header=None,names=["timestamp","open","high","low","close","volume"])
        ts=pd.to_datetime(df["timestamp"],format="%Y%m%d %H%M%S")
        df["timestamp"]=ts.dt.tz_localize("America/New_York",ambiguous="infer",nonexistent="shift_forward").dt.tz_convert("UTC")
        df=df.set_index("timestamp").sort_index()
        if start is not None: df=df[df.index>=pd.Timestamp(start,tz="UTC")]
        if end is not None: df=df[df.index<=pd.Timestamp(end,tz="UTC")]
        return df[["open","high","low","close","volume"]]
