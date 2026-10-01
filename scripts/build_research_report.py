#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import pandas as pd
from smc_agent.engine import analyze
from smc_agent.report_schema import validate_report

p=argparse.ArgumentParser()
p.add_argument("csv")
p.add_argument("--out",required=True)
a=p.parse_args()
df=pd.read_csv(a.csv,parse_dates=["timestamp"]).sort_values("timestamp")
df["timestamp"]=pd.to_datetime(df["timestamp"],utc=True)
df=df.set_index("timestamp")
report=analyze(df).as_dict()
report["dataset"]={"rows":int(len(df)),"start":df.index[0].isoformat(),"end":df.index[-1].isoformat(),"source":"HistData EUR/USD M1","analysis_window":"validated research window"}
check=validate_report(report)
if not check["valid"]: raise SystemExit(json.dumps(check,indent=2))
payload={"schema_version":"2.0","generated_at":pd.Timestamp.utcnow().isoformat(),"dataset":report["dataset"],**report}
Path(a.out).parent.mkdir(parents=True,exist_ok=True)
Path(a.out).write_text(json.dumps(payload,default=str,indent=2),encoding="utf-8")
print(json.dumps({"validation":"PASS","rows":len(df),"out":a.out}))
