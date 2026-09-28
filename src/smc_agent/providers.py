from typing import Protocol
import pandas as pd

class MarketDataProvider(Protocol):
    def candles(self,symbol:str,timeframe:str,start=None,end=None)->pd.DataFrame: ...

class EconomicCalendarProvider(Protocol):
    def events(self,start=None,end=None): ...
