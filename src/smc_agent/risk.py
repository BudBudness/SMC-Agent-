from dataclasses import dataclass
@dataclass
class ResearchLimits:
    max_history_years:int=30
    require_confirmed_candles:bool=True
    forbid_lookahead:bool=True
    minimum_evidence_events:int=20
