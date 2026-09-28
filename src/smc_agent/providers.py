from datetime import timezone, timedelta
from typing import Protocol
import pandas as pd

class MarketDataProvider(Protocol):
    def candles(self,symbol:str,timeframe:str,start=None,end=None)->pd.DataFrame: ...

class EconomicCalendarProvider(Protocol):
    def events(self,start=None,end=None): ...

class HistDataProvider:
    """Reader for HistData Generic ASCII M1 CSV files."""
    def __init__(self,path): self.path=path

    @staticmethod
    def _utc(value):
        ts=pd.Timestamp(value)
        return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")

    def candles(self,symbol="EURUSD",timeframe="M1",start=None,end=None):
        if timeframe != "M1": raise ValueError("HistDataProvider currently supports M1 only")
        df=pd.read_csv(self.path,sep=";",header=None,
                       names=["timestamp","open","high","low","close","volume"])
        ts=pd.to_datetime(df["timestamp"],format="%Y%m%d %H%M%S")
        # HistData explicitly defines timestamps as fixed EST without DST.
        fixed_est=timezone(timedelta(hours=-5))
        df["timestamp"]=ts.dt.tz_localize(fixed_est).dt.tz_convert("UTC")
        df=df.set_index("timestamp").sort_index()
        if start is not None: df=df[df.index>=self._utc(start)]
        if end is not None: df=df[df.index<=self._utc(end)]
        return df[["open","high","low","close","volume"]]
