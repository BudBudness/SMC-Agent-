#!/usr/bin/env python3
"""Fetch long EUR/USD M1 history for substantive multi-timeframe research."""
import argparse
from pathlib import Path
import pandas as pd
from histdata_fetcher import HistDataFetcher

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",default="2003-05-01")
    p.add_argument("--end",default="2026-09-28")
    p.add_argument("--out",default="data/long_history/EURUSD_M1.csv")
    a=p.parse_args()
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    fetcher=HistDataFetcher()
    df=fetcher.fetch("eurusd",timeframe="1min",start_date=a.start,end_date=a.end)
    if df.empty: raise SystemExit("No EURUSD M1 data returned")
    df=df.rename(columns={"datetime":"timestamp"})
    df["timestamp"]=pd.to_datetime(df["timestamp"],utc=True)
    df=df.set_index("timestamp").sort_index()
    df=df[["open","high","low","close","volume"]]
    df.to_csv(out)
    print({"rows":len(df),"start":df.index[0].isoformat(),"end":df.index[-1].isoformat(),"out":str(out)})

if __name__=="__main__":
    main()
