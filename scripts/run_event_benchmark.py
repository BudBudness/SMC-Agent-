#!/usr/bin/env python3
"""Run a historical reaction benchmark on a real EURUSD M1 fixture."""
import argparse, json, os
from smc_agent.providers import HistDataProvider
from smc_agent.dataset_validation import validate_ohlc
from smc_agent.engine import analyze
from smc_agent.event_study import event_reactions, summarize

def main():
    p=argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--out",default="benchmark-results/eurusd-reaction.json")
    a=p.parse_args()
    df=HistDataProvider(a.csv).candles()
    validation=validate_ohlc(df)
    if not validation["valid"]: raise SystemExit(json.dumps(validation))
    report=analyze(df,symbol="EURUSD",now=df.index[-1])
    events=report.as_dict()["events"]
    reactions=event_reactions(df,events)
    result={
        "symbol":"EURUSD",
        "rows":len(df),
        "start":df.index[0].isoformat(),
        "end":df.index[-1].isoformat(),
        "dataset_validation":validation,
        "events_observed":len(events),
        "event_reaction_summary":summarize(reactions),
    }
    os.makedirs(a.out.rsplit("/",1)[0],exist_ok=True)
    with open(a.out,"w",encoding="utf-8") as f: json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
