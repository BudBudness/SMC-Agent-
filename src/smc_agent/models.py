from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Direction(str, Enum):
    LONG="LONG"; SHORT="SHORT"; NEUTRAL="NEUTRAL"

@dataclass
class Signal:
    symbol: str
    direction: Direction
    weekly_bias: Direction
    score: float
    grade: str
    entry: Optional[float]=None
    stop: Optional[float]=None
    t1: Optional[float]=None
    t2: Optional[float]=None
    rr: Optional[float]=None
    reasons: list[str]=field(default_factory=list)
    status: str="NO TRADE"

    def as_dict(self):
        return {"symbol":self.symbol,"direction":self.direction.value,"weekly_bias":self.weekly_bias.value,
                "score":self.score,"grade":self.grade,"entry":self.entry,"stop":self.stop,
                "T1":self.t1,"T2":self.t2,"RR":self.rr,"reasons":self.reasons,"status":self.status}
