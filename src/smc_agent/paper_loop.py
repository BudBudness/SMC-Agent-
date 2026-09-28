from .engine import analyze
from .execution import PaperBroker
class PaperLoop:
    def __init__(self,broker=None): self.broker=broker or PaperBroker()
    def on_bars(self,bars,symbol="EURUSD"):
        signal=analyze(bars,symbol)
        order=None
        if signal.status=="TRADE SIGNAL" and signal.entry is not None and signal.stop is not None:
            order=self.broker.submit(signal,1.0)
        return signal,order
