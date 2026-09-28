import os
from .risk import position_size

class PaperBroker:
    def __init__(self):
        self.orders=[]
    def submit(self,signal,size):
        order={"mode":"PAPER","symbol":signal.symbol,"direction":signal.direction.value,"size":size,"status":"ACCEPTED"}
        self.orders.append(order)
        return order
    def emergency_close(self):
        return {"mode":"PAPER","action":"EMERGENCY_CLOSE","status":"SIMULATED"}

class LiveBroker:
    def submit(self,*args,**kwargs):
        if os.getenv("ENABLE_LIVE_TRADING","false").lower()!="true":
            raise RuntimeError("LIVE TRADING DISABLED")
        raise NotImplementedError("Concrete broker adapter and live validation required")
    def emergency_close(self):
        raise RuntimeError("LIVE BROKER NOT CONFIGURED")
