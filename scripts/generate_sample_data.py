import numpy as np,pandas as pd
n=5000; rng=np.random.default_rng(7); t=pd.date_range("2025-01-01",periods=n,freq="15min",tz="UTC")
r=rng.normal(0,.00035,n); c=1.1+np.cumsum(r); o=np.r_[c[0],c[:-1]]; x=np.abs(rng.normal(.00015,.00005,n))
pd.DataFrame({"time":t,"open":o,"high":np.maximum(o,c)+x,"low":np.minimum(o,c)-x,"close":c,"volume":rng.integers(100,1000,n)}).to_csv("sample.csv",index=False)
