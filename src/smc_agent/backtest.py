from dataclasses import dataclass
from .engine import analyze
from .trade_simulator import TradeSimulator,TradeConfig
@dataclass
class BacktestConfig:
    warmup:int=100; step:int=1; spread:float=0.00002; slippage:float=0.00001; commission:float=0.0
class Backtester:
    def __init__(self,df,equity=10000,risk=0.005,config=None):
        self.df=df.sort_index(); self.equity=equity; self.risk=risk; self.config=config or BacktestConfig()
    def run(self):
        signals=[]
        for i in range(self.config.warmup,len(self.df),self.config.step):
            s=analyze(self.df.iloc[:i])
            if s.status=="TRADE SIGNAL": 
                d=s.as_dict(); d["timestamp"]=self.df.index[i-1]; signals.append(d)
        bars=[{"timestamp":i,**{k:float(r[k]) for k in ["open","high","low","close"]}} for i,r in self.df.iterrows()]
        sim=TradeSimulator(self.equity,TradeConfig(risk_pct=self.risk,spread=self.config.spread,slippage=self.config.slippage,commission_per_unit=self.config.commission))
        sim.run(bars,signals)
        return {"initial_equity":self.equity,"signals":len(signals),"trades":len(sim.trades),"metrics":sim.metrics(),"ledger":sim.ledger(),
                "execution_model":{"spread":self.config.spread,"slippage":self.config.slippage,"commission":self.config.commission,"lookahead":False}}
