#!/usr/bin/env python3
import sys
from smc_agent.data import load_csv
from smc_agent.dataset_validation import validate_ohlc
path=sys.argv[1]
result=validate_ohlc(load_csv(path))
print(result)
raise SystemExit(0 if result["valid"] else 1)
