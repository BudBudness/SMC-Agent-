#!/usr/bin/env python3
"""Evaluate substantive multi-timeframe structure and chronological OOS behavior."""
import argparse, json
from pathlib import Path
import pandas as pd
from smc_agent.providers import HistDataProvider
from smc_agent.timeframes import reconstruct, ANALYSIS_TIMEFRAMES
from smc_agent.structure import swings, structure_state

MIN_BARS={"12M":20,"6M":40,"3M":80,"W":100,"D":200,"4H":500,"1H":1000,"15M":2000,"5M":5000,"1M":10000}

def asof_states(frame):
    # State at time t uses only swings whose right-side confirmation is already available.
    out=[]
    for i in range(len(frame)):
        confirmed=frame.iloc[:i+1]
        if len(confirmed)<8:
            out.append("NEUTRAL"); continue
        s=swings(confirmed)
        highs=[x[2] for x in s if x[0]=="HIGH"]
        lows=[x[2] for x in s if x[0]=="LOW"]
        if len(highs)<2 or len(lows)<2:
            out.append("NEUTRAL")
        elif highs[-1]>highs[-2] and lows[-1]>lows[-2]:
            out.append("LONG")
        elif highs[-1]<highs[-2] and lows[-1]<lows[-2]:
            out.append("SHORT")
        else:
            out.append("NEUTRAL")
    return pd.Series(out,index=frame.index)

def evaluate_frame(tf,frame):
    states=asof_states(frame)
    counts=states.value_counts().to_dict()
    transitions=int((states!=states.shift()).sum()-1) if len(states) else 0
    s=swings(frame)
    highs=sum(x[0]=="HIGH" for x in s); lows=sum(x[0]=="LOW" for x in s)
    non_neutral=int((states!="NEUTRAL").sum())
    return {
        "bars":int(len(frame)),
        "start":frame.index[0].isoformat() if len(frame) else None,
        "end":frame.index[-1].isoformat() if len(frame) else None,
        "state_counts":{k:int(counts.get(k,0)) for k in ("LONG","SHORT","NEUTRAL")},
        "state_coverage":non_neutral/len(frame) if len(frame) else 0.0,
        "state_transitions":transitions,
        "confirmed_highs":highs,"confirmed_lows":lows,
        "dynamic":bool(transitions>0 and highs>0 and lows>0),
        "depth_ok":len(frame)>=MIN_BARS.get(tf,0),
    }

def oos(tf,frame,split=0.7):
    n=len(frame); cut=max(1,int(n*split))
    train=frame.iloc[:cut]; test=frame.iloc[cut:]
    a=evaluate_frame(tf,train); b=evaluate_frame(tf,test)
    return {"split_index":cut,"train":a,"test":b,
            "chronological":True,
            "future_leakage_control":"Each as-of state only uses candles available through that timestamp; swing confirmation is delayed by right=2 bars."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("csv"); p.add_argument("--out",default="benchmark-results/mtf_substantive_evaluation.json")
    a=p.parse_args()
    df=HistDataProvider(a.csv).candles()
    frames=reconstruct(df)
    evaluation={tf:evaluate_frame(tf,frames[tf]) for tf in ANALYSIS_TIMEFRAMES}
    oos_eval={tf:oos(tf,frames[tf]) for tf in ANALYSIS_TIMEFRAMES}
    result={
        "symbol":"EURUSD","source_rows":len(df),
        "source_start":df.index[0].isoformat(),"source_end":df.index[-1].isoformat(),
        "method":"chronological descriptive structural evaluation",
        "purpose":"Determine whether 3M/6M/12M produce substantive changing structural information rather than merely reconstructed bars.",
        "timeframes":evaluation,"oos":oos_eval,
        "substantive_test":{
            tf:{
                "passes_technical_depth":evaluation[tf]["depth_ok"],
                "passes_dynamic_structure":evaluation[tf]["dynamic"],
                "passes_oos_dynamic_structure":oos_eval[tf]["test"]["dynamic"],
                "interpretation":"substantive structure is evidenced only when depth, confirmed swings, and time-varying states exist in chronological/OOS segments; this is not a predictive or profitability test."
            } for tf in ("12M","6M","3M")
        }
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,indent=2))
    print(json.dumps(result["substantive_test"],indent=2))
if __name__=="__main__": main()
