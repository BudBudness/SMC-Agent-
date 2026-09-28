from dataclasses import dataclass

@dataclass
class SafetyGate:
    live_enabled:bool=False
    max_spread:float=0.0003
    stale_seconds:int=60
    daily_limit:float=0.015
    weekly_limit:float=0.03

    def allow(self,spread,data_age_seconds,daily_loss,weekly_loss,news_locked=False):
        return bool(self.live_enabled and spread<=self.max_spread and data_age_seconds<=self.stale_seconds and daily_loss<self.daily_limit and weekly_loss<self.weekly_limit and not news_locked)
