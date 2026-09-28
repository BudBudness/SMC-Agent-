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
        if timeframe != "M1":
            raise ValueError("HistDataProvider currently supports M1 only")
        with open(self.path,"r",encoding="utf-8") as f:
            first=f.readline().strip()
        sep=";" if ";" in first else ","
        df=pd.read_csv(self.path,sep=sep,header=None,skiprows=1 if first.lower().startswith("timestamp") else 0)
        if sep==";":
            if df.shape[1] < 5:
                raise ValueError("unsupported M1 CSV schema")
            df=df.iloc[:,:6]
            while df.shape[1] < 6:
                df[df.shape[1]]=0
            df.columns=["timestamp","open","high","low","close","volume"]
            raw=df["timestamp"].astype(str)
            ts=pd.to_datetime(raw,format="%Y%m%d %H%M%S")
            fixed_est=timezone(timedelta(hours=-5))
            df["timestamp"]=ts.dt.tz_localize(fixed_est).dt.tz_convert("UTC")
        else:
            if df.shape[1] < 6:
                raise ValueError("unsupported comma M1 CSV schema")
            first_value=str(df.iloc[0,0])
            if "-" in first_value and ":" in first_value:
                ts=pd.to_datetime(df.iloc[:,0],errors="raise",utc=True)
                cols={"open":df.iloc[:,1],"high":df.iloc[:,2],"low":df.iloc[:,3],"close":df.iloc[:,4],"volume":df.iloc[:,5]}
            else:
                raw=df.iloc[:,0].astype(str)+" "+df.iloc[:,1].astype(str)
                ts=pd.to_datetime(raw,errors="raise",utc=True)
                cols={"open":df.iloc[:,2],"high":df.iloc[:,3],"low":df.iloc[:,4],"close":df.iloc[:,5],"volume":df.iloc[:,6] if df.shape[1]>=7 else 0}
            df=pd.DataFrame({"timestamp":ts,**cols})
        for c in ["open","high","low","close","volume"]:
            df[c]=pd.to_numeric(df[c],errors="coerce")
        df=df.set_index("timestamp").sort_index()
        if start is not None:
            df=df[df.index>=self._utc(start)]
        if end is not None:
            df=df[df.index<=self._utc(end)]
        return df[["open","high","low","close","volume"]]
