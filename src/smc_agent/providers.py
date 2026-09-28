from datetime import timezone, timedelta
from typing import Protocol
import pandas as pd

class MarketDataProvider(Protocol):
    def candles(self,symbol:str,timeframe:str,start=None,end=None)->pd.DataFrame: ...

class EconomicCalendarProvider(Protocol):
    def events(self,start=None,end=None): ...

class HistDataProvider:
    """Reader for HistData-style and compatible EUR/USD M1 CSV files."""
    def __init__(self,path): self.path=path

    @staticmethod
    def _utc(value):
        ts=pd.Timestamp(value)
        return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")

    def candles(self,symbol="EURUSD",timeframe="M1",start=None,end=None):
        if timeframe != "M1": raise ValueError("HistDataProvider currently supports M1 only")
        with open(self.path,"r",encoding="utf-8") as f:
            first=f.readline().strip()
        sep=";" if ";" in first else ","
        df=pd.read_csv(self.path,sep=sep,header=None)
        if df.shape[1] < 5: raise ValueError("unsupported M1 CSV schema")
        if df.shape[1] >= 6:
            df=df.iloc[:,:6]
            df.columns=["timestamp","open","high","low","close","volume"]
        else:
            df=df.iloc[:,:5]
            df.columns=["timestamp","open","high","low","close"]
            df["volume"]=0
        raw=df["timestamp"].astype(str)
        try:
            ts=pd.to_datetime(raw,format="%Y%m%d %H%M%S")
            fixed_est=timezone(timedelta(hours=-5))
            ts=ts.dt.tz_localize(fixed_est).dt.tz_convert("UTC")
        except (ValueError,TypeError):
            ts=pd.to_datetime(raw+" "+df.iloc[:,1].astype(str),errors="raise")
            ts=ts.dt.tz_localize("UTC") if ts.dt.tz is None else ts.dt.tz_convert("UTC")
            df["open"]=df.iloc[:,2]; df["high"]=df.iloc[:,3]; df["low"]=df.iloc[:,4]; df["close"]=df.iloc[:,5]
            if df.shape[1)>6: df["volume"]=df.iloc[:,6]
        df["timestamp"]=ts
        for c in ["open","high","low","close","volume"]: df[c]=pd.to_numeric(df[c],errors="coerce")
        df=df.set_index("timestamp").sort_index()
        if start is not None: df=df[df.index>=self._utc(start)]
        if end is not None: df=df[df.index<=self._utc(end)]
        return df[["open","high","low","close","volume"]]
