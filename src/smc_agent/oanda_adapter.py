import os
class OANDABroker:
    def __init__(self): self.enabled=os.getenv("ENABLE_LIVE_TRADING","false").lower()=="true"; self.token=os.getenv("OANDA_API_TOKEN"); self.account=os.getenv("OANDA_ACCOUNT_ID")
    def place_order(self,*args,**kwargs):
        if not self.enabled: raise RuntimeError("LIVE TRADING DISABLED")
        if not self.token or not self.account: raise RuntimeError("OANDA credentials missing")
        raise NotImplementedError("OANDA REST adapter must be configured in deployment")
    def close_position(self,*args,**kwargs): raise NotImplementedError("OANDA close adapter must be configured")
