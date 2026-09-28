import pandas as pd
from .structure import swings,weekly_bias
from .liquidity import map_liquidity,sweep
from .scoring import score,grade
from .models import Signal,Direction

def analyze(df,symbol="EURUSD"):
    if len(df)<50:return Signal(symbol,Direction.NEUTRAL,Direction.NEUTRAL,0,"NO TRADE",reasons=["insufficient data"])
    df=df.sort_index()
    w=df.resample("W").agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()
    bias=weekly_bias(w)
    direction=Direction(bias)
    ws=swings(w)
    zones=map_liquidity(ws)
    sw=sweep(df,zones)
    f={"weekly_structure":bias!="NEUTRAL","weekly_location":True,"liquidity":bool(zones),
       "inducement":False,"sweep":bool(sw),"structure_shift":False,"displacement":False,
       "fvg_ob":False,"premium_discount":False,"economic":False,"session":True}
    sc=score(f); g=grade(sc)
    reasons=[f"Weekly bias={bias}",f"liquidity_zones={len(zones)}"]
    if sw: reasons.append(f"sweep={sw['kind']} @ {sw['price']}")
    if sc<70: reasons.append("confirmation stack incomplete")
    status="TRADE SIGNAL" if sc>=80 and sw else "NO TRADE"
    return Signal(symbol,direction,direction,sc,g,reasons=reasons,status=status)
