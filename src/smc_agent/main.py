import argparse,json
import pandas as pd
from .engine import analyze

def load(path):
    d=pd.read_csv(path)
    d["time"]=pd.to_datetime(d["time"],utc=True)
    return d.set_index("time").sort_index()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("csv"); p.add_argument("--symbol",default="EURUSD")
    a=p.parse_args()
    print(json.dumps(analyze(load(a.csv),a.symbol).as_dict(),indent=2,default=str))

if __name__=="__main__": main()
