#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import pandas as pd
from smc_agent.engine import analyze
from smc_agent.report_schema import validate_report

p=argparse.ArgumentParser()
p.add_argument("csv")
p.add_argument("--out",required=True)
p.add_argument("--episodes",default=None,help="JSON benchmark artifact containing chronological episode_results")
a=p.parse_args()
df=pd.read_csv(a.csv,parse_dates=["timestamp"]).sort_values("timestamp")
df["timestamp"]=pd.to_datetime(df["timestamp"],utc=True)
df=df.set_index("timestamp")

historical_episodes=None
if a.episodes:
    benchmark=json.loads(Path(a.episodes).read_text(encoding="utf-8"))
    historical_episodes=[]
    for row in benchmark.get("episode_results",[]):
        historical_episodes.append({
            "episode":row.get("episode"),
            "timestamp":row.get("end"),
            "regime":row.get("regime"),
            "weekly_bias":row.get("weekly_bias"),
            "location":row.get("daily_location"),
            "sweep":"sweep" in row.get("reference_events",[]),
            "displacement":row.get("displacement"),
            "choch":"choch" in row.get("reference_events",[]),
            "bos":"bos" in row.get("reference_events",[]),
            "amd":row.get("amd"),
            "outcome":row.get("outcome_20m"),
        })

report=analyze(df,historical_episodes=historical_episodes).as_dict()
report["dataset"]={
    "rows":int(len(df)),
    "start":df.index[0].isoformat(),
    "end":df.index[-1].isoformat(),
    "source":"HistData EUR/USD M1",
    "analysis_window":"validated research window",
}
report["dataset"]["analogue_episode_count"]=len(historical_episodes or [])
check=validate_report(report)
if not check["valid"]:
    raise SystemExit(json.dumps(check,indent=2))
payload={
    "schema_version":"2.0",
    "generated_at":pd.Timestamp.now(tz="UTC").isoformat(),
    "dataset":report["dataset"],
    **report,
}
Path(a.out).parent.mkdir(parents=True,exist_ok=True)
Path(a.out).write_text(json.dumps(payload,default=str,indent=2),encoding="utf-8")
print(json.dumps({
    "validation":"PASS",
    "rows":len(df),
    "analogue_status":report["analogue_research"].get("status"),
    "analogue_samples":report["analogue_research"].get("samples"),
    "out":a.out,
}))
