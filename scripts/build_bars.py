#!/usr/bin/env python3
import argparse, pathlib
import pandas as pd
RULES={"1m":"1min","5m":"5min","15m":"15min","1h":"1h","4h":"4h","D":"1D","W":"1W","3M":"3MS","6M":"6MS","12M":"12MS"}
def build(src,out):
    df=pd.read_csv(src,parse_dates=["timestamp"]).sort_values("timestamp").drop_duplicates("timestamp")
    if not {"timestamp","bid","ask"}.issubset(df.columns): raise SystemExit("required columns: timestamp,bid,ask")
    df["mid"]=(df.bid+df.ask)/2; df=df.set_index("timestamp"); pathlib.Path(out).mkdir(parents=True,exist_ok=True)
    for name,rule in RULES.items(): df.mid.resample(rule,label="right",closed="right").ohlc().dropna().to_csv(f"{out}/EURUSD_{name}.csv")
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("src"); p.add_argument("--out",default="data/bars"); a=p.parse_args(); build(a.src,a.out)
