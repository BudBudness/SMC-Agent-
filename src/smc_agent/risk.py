from dataclasses import dataclass

@dataclass(frozen=True)
class RiskLimits:
    trade_pct:float=0.005
    daily_pct:float=0.015
    weekly_pct:float=0.03
    max_positions:int=1
    max_correlated:int=1
    max_spread:float=0.0003

def risk_valid(entry,stop,equity,risk_pct=0.005,spread=0.0,limits=RiskLimits()):
    if equity<=0 or entry is None or stop is None:return False
    if entry==stop or spread>limits.max_spread:return False
    return abs(entry-stop)>0 and 0<risk_pct<=limits.trade_pct
