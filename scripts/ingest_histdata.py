#!/usr/bin/env python3
"""Validate and normalize a HistData EUR/USD M1 CSV."""
import argparse
from smc_agent.providers import HistDataProvider
from smc_agent.dataset_validation import validate_ohlc

def main():
    p=argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--out",default="data/normalized/EURUSD_M1.csv")
    a=p.parse_args()
    df=HistDataProvider(a.csv).candles()
    result=validate_ohlc(df)
    print(result)
    if not result["valid"]: raise SystemExit(1)
    df.to_csv(a.out)
    print(f"wrote {len(df)} rows to {a.out}")
if __name__=="__main__": main()
