import pandas as pd
def load_csv(path):
    d=pd.read_csv(path); col="timestamp" if "timestamp" in d.columns else "time"; d[col]=pd.to_datetime(d[col],utc=True)
    return d.set_index(col).sort_index()
def resample_ohlcv(df,rule):
    a={"open":"first","high":"max","low":"min","close":"last"}
    if "volume" in df.columns:a["volume"]="sum"
    return df.resample(rule).agg(a).dropna()
