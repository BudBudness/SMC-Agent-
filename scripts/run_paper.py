import sys,json
from smc_agent.data import load_csv
from smc_agent.engine import analyze
from smc_agent.execution import PaperBroker
s=analyze(load_csv(sys.argv[1])); print(json.dumps(s.as_dict(),indent=2,default=str))
if s.status=="TRADE SIGNAL": print(PaperBroker().submit(s,1.0))
else: print("NO TRADE")
