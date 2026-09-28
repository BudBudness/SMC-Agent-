#!/usr/bin/env python3
import json,sys
from smc_agent.data import load_csv
from smc_agent.pipeline import run
path=sys.argv[1]
result=run(load_csv(path),symbol=sys.argv[2] if len(sys.argv)>2 else "EURUSD")
print(json.dumps(result,indent=2,default=str))
