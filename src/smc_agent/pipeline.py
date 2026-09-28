"""Canonical end-to-end intelligence pipeline."""
from .dataset_validation import validate_ohlc
from .engine import analyze

def run(df,symbol="EURUSD",news_events=None,now=None):
    validation=validate_ohlc(df)
    if not validation["valid"]:
        raise ValueError({"dataset_validation":validation})
    report=analyze(df,symbol=symbol,news_events=news_events,now=now)
    return {"dataset_validation":validation,"report":report.as_dict()}
