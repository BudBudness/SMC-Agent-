"""Canonical end-to-end intelligence pipeline with integrity gates."""
from .dataset_validation import validate_ohlc,validate_alignment
from .engine import analyze
from .timeframes import reconstruct
from .report_schema import validate_report

def run(df,symbol="EURUSD",news_events=None,historical_episodes=None,now=None):
    validation=validate_ohlc(df)
    if not validation["valid"]: raise ValueError({"dataset_validation":validation})
    frames=reconstruct(df)
    alignment=validate_alignment(frames)
    if not alignment["valid"]: raise ValueError({"dataset_alignment":alignment})
    report=analyze(df,symbol=symbol,news_events=news_events,historical_episodes=historical_episodes,now=now)
    payload=report.as_dict()
    schema=validate_report(payload)
    if not schema["valid"]: raise ValueError({"report_schema":schema})
    return {"dataset_validation":validation,"mtf_validation":alignment,"report":payload,
            "lineage":{"source_rows":len(df),"source_start":df.index.min().isoformat(),"source_end":df.index.max().isoformat(),
                       "timeframes":list(frames),"lookahead_policy":"confirmed swing events expose right-side confirmation timestamps; future bars are used only for explicitly labelled historical outcome studies."}}
