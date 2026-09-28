from dataclasses import dataclass
from .engine import analyze

@dataclass
class BacktestConfig:
    warmup:int=100
    step:int=1
    spread:float=0.00002
    slippage:float=0.00001

class Backtester:
    """Causal replay: signal at bar i is evaluated only from df[:i]."""
    def __init__(self,df,equity=10000,risk=0.005,config=None):
        self.df=df.sort_index()
        self.equity=equity
        self.risk=risk
        self.config=config or BacktestConfig()

    def run(self):
        signals=[]
        for i in range(self.config.warmup,len(self.df),self.config.step):
            s=analyze(self.df.iloc[:i])
            if s.status=="TRADE SIGNAL":
                signals.append(s.as_dict())
        return {
            "initial_equity":self.equity,
            "trades":len(signals),
            "signals":signals,
            "execution_model":{
                "spread":self.config.spread,
                "slippage":self.config.slippage,
                "lookahead":False
            },
            "note":"Signal-replay baseline. No profitability claim until fills, exits, costs and OOS evaluation are implemented."
        }
