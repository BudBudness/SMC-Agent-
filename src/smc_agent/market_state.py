from dataclasses import dataclass,asdict
@dataclass
class MarketState:
    symbol:str
    regime:str
    weekly_bias:str
    timeframe_states:dict
    liquidity:dict
    active_events:list
    contradictions:list
def snapshot(symbol,regime,weekly_bias,timeframe_states,liquidity,active_events=None,contradictions=None):
    return asdict(MarketState(symbol,regime,weekly_bias,timeframe_states,liquidity,active_events or [],contradictions or []))
