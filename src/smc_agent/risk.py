from dataclasses import dataclass

@dataclass(frozen=True)
class RiskLimits:
    trade_pct:float=0.005
    daily_pct:float=0.015
    weekly_pct:float=0.03
    max_positions:int=1
    max_correlated:int=1
    max_spread:float=0.0003

def risk_valid(entry,stop,equity,risk_pct=0.005,spread=0.0,limits=RiskLimits(),daily_loss=0.0,weekly_loss=0.0,open_positions=0,correlated_positions=0):
    if equity<=0 or entry is None or stop is None or entry==stop:return False
    if spread>limits.max_spread or not 0<risk_pct<=limits.trade_pct:return False
    if open_positions>=limits.max_positions or correlated_positions>=limits.max_correlated:return False
    if daily_loss>=limits.daily_pct or weekly_loss>=limits.weekly_pct:return False
    return True

def position_size(equity,entry,stop,risk_pct=0.005):
    d=abs(entry-stop)
    return 0.0 if d<=0 else equity*risk_pct/d
