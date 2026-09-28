import pandas as pd
def load_csv(path):
    d=pd.read_csv(path); d["time"]=pd.to_datetime(d["time"],utc=True)
    return d.set_index("time").sort_index()
def resample_ohlcv(df,rule):
    return df.resample(rule).agg({"open":"first","high":"max","low":"min","close":"last","volume":"sum"}).dropna()
