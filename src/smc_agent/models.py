from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Direction(str, Enum):
    LONG="LONG"; SHORT="SHORT"; NEUTRAL="NEUTRAL"

@dataclass
class Signal:
    symbol:str
    direction:Direction
    weekly_bias:Direction
    score:float
    grade:str
    entry:Optional[float]=None
    stop:Optional[float]=None
    t1:Optional[float]=None
    t2:Optional[float]=None
    rr:Optional[float]=None
    macro_regime:str="UNKNOWN"
    liquidity_sweep:Optional[dict]=None
    inducement:Optional[dict]=None
    choch:bool=False
    bos:bool=False
    displacement:str="NONE"
    fvg:Optional[dict]=None
    order_block:Optional[dict]=None
    news_risk:str="UNKNOWN"
    state:str="WAITING"
    reasons:list[str]=field(default_factory=list)
    status:str="NO TRADE"

    def as_dict(self):
        return {k:(v.value if isinstance(v,Enum) else v) for k,v in self.__dict__.items()}
