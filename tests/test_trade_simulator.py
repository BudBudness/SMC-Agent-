from smc_agent.trade_simulator import TradeSimulator

def test_stop_first_same_bar():
    bars=[{"timestamp":1,"open":100,"high":102,"low":98,"close":101}]
    signals=[{"timestamp":0,"status":"TRADE_SIGNAL","direction":"LONG","entry":100,"stop":99,"t1":101,"target":102}]
    sim=TradeSimulator()
    sim.run(bars,signals)
    assert sim.trades[0].exit_reason=="STOP_SAME_BAR"

def test_empty_metrics():
    assert TradeSimulator().metrics()["trades"]==0
