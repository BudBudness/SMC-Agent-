import json,sys
from smc_agent.oos import summarize
with open(sys.argv[1],encoding="utf-8") as f: reports=json.load(f)
print(json.dumps(summarize(reports),indent=2,default=str))
