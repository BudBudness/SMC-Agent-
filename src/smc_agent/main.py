import argparse,json
import pandas as pd
from .engine import analyze
def load(path):
    d=pd.read_csv(path)
    col="timestamp" if "timestamp" in d.columns else "time"
    d[col]=pd.to_datetime(d[col],utc=True)
    return d.set_index(col).sort_index()[["open","high","low","close"]]
def main():
    p=argparse.ArgumentParser(); p.add_argument("csv"); p.add_argument("--symbol",default="EURUSD"); a=p.parse_args()
    print(json.dumps(analyze(load(a.csv),a.symbol).as_dict(),indent=2,default=str))
if __name__=="__main__": main()
