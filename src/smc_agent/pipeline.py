"""Canonical end-to-end intelligence pipeline with integrity gates."""
from .dataset_validation import validate_ohlc,validate_alignment
from .engine import analyze
from .timeframes import reconstruct
def run(df,symbol="EURUSD",news_events=None,now=None):
    validation=validate_ohlc(df)
    if not validation["valid"]: raise ValueError({"dataset_validation":validation})
    frames=reconstruct(df); alignment=validate_alignment(frames)
    if not alignment["valid"]: raise ValueError({"dataset_alignment":alignment})
    report=analyze(df,symbol=symbol,news_events=news_events,now=now)
    return {"dataset_validation":validation,"mtf_validation":alignment,"report":report.as_dict()}
