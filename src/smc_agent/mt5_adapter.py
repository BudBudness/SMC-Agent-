import os
class MT5Broker:
    def __init__(self):
        self.enabled=os.getenv("ENABLE_LIVE_TRADING","false").lower()=="true"
    def place_order(self,*args,**kwargs):
        if not self.enabled: raise RuntimeError("LIVE TRADING DISABLED")
        raise NotImplementedError("Install/configure MetaTrader5 adapter in the execution environment before LIVE")
    def close_position(self,*args,**kwargs):
        if not self.enabled: raise RuntimeError("LIVE TRADING DISABLED")
        raise NotImplementedError("MT5 close adapter not configured")
