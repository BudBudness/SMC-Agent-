import pandas as pd
from smc_agent.paper_loop import PaperLoop
df=pd.read_csv("data/EURUSD_1m.csv",parse_dates=["timestamp"]).set_index("timestamp")
signal,order=PaperLoop().on_bars(df)
print(signal.as_dict()); print(order)
