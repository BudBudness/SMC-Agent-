import sys
from smc_agent.data import load_csv
d=load_csv(sys.argv[1]); required={"open","high","low","close"}
assert required<=set(d.columns) and len(d)>50
assert d.index.is_monotonic_increasing and d.index.is_unique
print("VALID")
