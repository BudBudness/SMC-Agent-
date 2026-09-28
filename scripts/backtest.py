import sys
from smc_agent.data import load_csv
from smc_agent.backtest import Backtester
print(Backtester(load_csv(sys.argv[1])).run())
