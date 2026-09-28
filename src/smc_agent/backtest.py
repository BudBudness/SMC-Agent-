from .engine import analyze
class Backtester:
    def __init__(self,df,equity=10000,risk=0.005): self.df=df; self.equity=equity; self.risk=risk
    def run(self):
        trades=[]
        for i in range(100,len(self.df),20):
            s=analyze(self.df.iloc[:i])
            if s.status=="TRADE SIGNAL": trades.append(s.as_dict())
        return {"trades":len(trades),"signals":trades,"note":"research baseline; no profitability claim"}
