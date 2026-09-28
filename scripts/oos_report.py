import json,sys
from smc_agent.oos import summarize
print(json.dumps(summarize(json.load(open(sys.argv[1])),indent=2,default=str))
