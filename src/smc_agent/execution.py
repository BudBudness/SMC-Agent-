import os
class PaperBroker:
    def __init__(self): self.orders=[]
    def submit(self,signal,size):
        order={"mode":"PAPER","symbol":signal.symbol,"direction":signal.direction.value,"size":size}
        self.orders.append(order); return order

class LiveBroker:
    def submit(self,*args,**kwargs):
        if os.getenv("ENABLE_LIVE_TRADING","false").lower()!="true":
            raise RuntimeError("LIVE TRADING DISABLED")
        raise NotImplementedError("Attach and validate a concrete broker adapter before live use")
