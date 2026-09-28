from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class TradeConfig:
    risk_pct: float = 0.005
    daily_limit: float = 0.015
    weekly_limit: float = 0.03
    max_positions: int = 1
    spread: float = 0.00002
    slippage: float = 0.00001
    commission_per_unit: float = 0.0
    stop_first_on_same_bar: bool = True

@dataclass
class Trade:
    entry_time: Any
    exit_time: Any
    direction: str
    size: float
    entry: float
    stop: float
    t1: float | None
    t2: float | None
    final: float
    exit_price: float
    exit_reason: str
    gross_pnl: float
    costs: float
    net_pnl: float
    r_multiple: float

class TradeSimulator:
    def __init__(self, equity=10000.0, config=None):
        self.initial_equity = equity
        self.equity = equity
        self.cfg = config or TradeConfig()
        self.trades = []

    def _size(self, entry, stop):
        d = abs(entry - stop)
        return 0.0 if d <= 0 else self.equity * self.cfg.risk_pct / d

    def _hit(self, direction, bar, level):
        return bar["high"] >= level if direction == "LONG" else bar["low"] <= level

    def run(self, bars, signals):
        bars = list(bars)
        for s in signals:
            if str(s.get("status", "")).upper() not in {"TRADE_SIGNAL", "PAPER", "VALID"}:
                continue
            direction = s["direction"].upper()
            entry, stop = float(s["entry"]), float(s["stop"])
            if direction not in {"LONG", "SHORT"} or entry == stop:
                continue
            size = self._size(entry, stop)
            start = next((i for i,b in enumerate(bars) if b["timestamp"] > s["timestamp"]), None)
            if start is None or size <= 0:
                continue
            final = float(s.get("final_target", s.get("target", s.get("t2", s.get("t1", entry)))))
            for i in range(start, len(bars)):
                b = bars[i]
                sh, fh = self._hit(direction,b,stop), self._hit(direction,b,final)
                if not (sh or fh):
                    continue
                if sh and fh and self.cfg.stop_first_on_same_bar:
                    reason, px = "STOP_SAME_BAR", stop
                elif sh:
                    reason, px = "STOP", stop
                else:
                    reason, px = "FINAL", final
                px += self.cfg.slippage if direction == "LONG" else -self.cfg.slippage
                gross = (px-entry) * size * (1 if direction=="LONG" else -1)
                costs = size * (self.cfg.spread + self.cfg.commission_per_unit)
                net = gross - costs
                risk = abs(entry-stop) * size
                self.trades.append(Trade(s["timestamp"],b["timestamp"],direction,size,entry,stop,s.get("t1"),s.get("t2"),final,px,reason,gross,costs,net,net/risk if risk else 0))
                self.equity += net
                break
        return self.trades

    def ledger(self):
        return [asdict(t) for t in self.trades]

    def metrics(self):
        pnl = [t.net_pnl for t in self.trades]
        wins = [x for x in pnl if x > 0]
        losses = [x for x in pnl if x < 0]
        eq, peak, dd = self.initial_equity, self.initial_equity, 0.0
        for x in pnl:
            eq += x
            peak = max(peak, eq)
            dd = max(dd, (peak-eq)/peak if peak else 0)
        return {"trades":len(pnl),"win_rate":len(wins)/len(pnl) if pnl else 0,"expectancy":sum(pnl)/len(pnl) if pnl else 0,"profit_factor":sum(wins)/abs(sum(losses)) if losses else None,"max_drawdown":dd,"average_R":sum(t.r_multiple for t in self.trades)/len(self.trades) if self.trades else 0,"final_equity":self.equity}
