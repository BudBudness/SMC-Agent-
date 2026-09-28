from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class TradeConfig:
    risk_pct: float=0.005; daily_limit: float=0.015; weekly_limit: float=0.03
    max_positions: int=1; spread: float=0.00002; slippage: float=0.00001
    commission_per_unit: float=0.0; stop_first_on_same_bar: bool=True

@dataclass
class Trade:
    entry_time: Any; exit_time: Any; direction: str; size: float; entry: float; stop: float
    t1: float|None; t2: float|None; final: float; exit_price: float; exit_reason: str
    gross_pnl: float; costs: float; net_pnl: float; r_multiple: float

class TradeSimulator:
    def __init__(self,equity=10000.0,config=None):
        self.initial_equity=equity; self.equity=equity; self.cfg=config or TradeConfig()
        self.trades=[]; self.open_count=0; self.day_pnl={}; self.week_pnl={}
    def _size(self,entry,stop): 
        d=abs(entry-stop); return 0.0 if d<=0 else self.equity*self.cfg.risk_pct/d
    def _hit(self,d,b,level): return b["high"]>=level if d=="LONG" else b["low"]<=level
    def _period_loss(self,t,weekly=False):
        key=t.isocalendar()[:2] if weekly else t.date()
        book=self.week_pnl if weekly else self.day_pnl
        return -min(book.get(key,0.0),0.0)/self.initial_equity
    def run(self,bars,signals):
        bars=list(bars)
        for s in signals:
            if str(s.get("status","")).upper() not in {"TRADE_SIGNAL","PAPER","VALID"}: continue
            d=s["direction"].upper(); entry=float(s["entry"]); stop=float(s["stop"])
            if d not in {"LONG","SHORT"} or entry==stop or self.open_count>=self.cfg.max_positions: continue
            ts=s["timestamp"]; 
            if self._period_loss(ts)>=self.cfg.daily_limit or self._period_loss(ts,True)>=self.cfg.weekly_limit: continue
            size=self._size(entry,stop)
            start=next((i for i,b in enumerate(bars) if b["timestamp"]>ts),None)
            if start is None or size<=0: continue
            final=float(s.get("final_target",s.get("target",s.get("t2",s.get("t1",entry)))))
            for b in bars[start:]:
                sh,fh=self._hit(d,b,stop),self._hit(d,b,final)
                if not(sh or fh): continue
                reason,px=("STOP_SAME_BAR",stop) if sh and fh and self.cfg.stop_first_on_same_bar else (("STOP",stop) if sh else ("FINAL",final))
                px += self.cfg.slippage if d=="LONG" else -self.cfg.slippage
                gross=(px-entry)*size*(1 if d=="LONG" else -1)
                costs=size*(self.cfg.spread+self.cfg.commission_per_unit); net=gross-costs
                risk=abs(entry-stop)*size
                tr=Trade(ts,b["timestamp"],d,size,entry,stop,s.get("t1"),s.get("t2"),final,px,reason,gross,costs,net,net/risk if risk else 0)
                self.trades.append(tr); self.equity+=net
                self.day_pnl[b["timestamp"].date()]=self.day_pnl.get(b["timestamp"].date(),0)+net
                k=b["timestamp"].isocalendar()[:2]; self.week_pnl[k]=self.week_pnl.get(k,0)+net
                break
        return self.trades
    def ledger(self): return [asdict(t) for t in self.trades]
    def metrics(self):
        pnl=[t.net_pnl for t in self.trades]; wins=[x for x in pnl if x>0]; losses=[x for x in pnl if x<0]
        eq=self.initial_equity; peak=eq; dd=0
        for x in pnl: eq+=x; peak=max(peak,eq); dd=max(dd,(peak-eq)/peak if peak else 0)
        return {"trades":len(pnl),"win_rate":len(wins)/len(pnl) if pnl else 0,"expectancy":sum(pnl)/len(pnl) if pnl else 0,
                "profit_factor":sum(wins)/abs(sum(losses)) if losses else None,"max_drawdown":dd,
                "average_R":sum(t.r_multiple for t in self.trades)/len(self.trades) if self.trades else 0,"final_equity":self.equity}
