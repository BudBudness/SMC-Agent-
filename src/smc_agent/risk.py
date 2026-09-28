def position_size(equity,risk_fraction,entry,stop):
    distance=abs(entry-stop)
    if distance<=0:return 0.0
    return equity*risk_fraction/distance

def risk_ok(daily_pnl,weekly_pnl,equity,open_positions,cfg):
    if daily_pnl <= -equity*cfg["max_daily_loss"]: return False,"daily_loss_limit"
    if weekly_pnl <= -equity*cfg["max_weekly_loss"]: return False,"weekly_loss_limit"
    if open_positions >= cfg["max_simultaneous_trades"]: return False,"position_limit"
    return True,"ok"
