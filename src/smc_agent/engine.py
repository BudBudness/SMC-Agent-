import pandas as pd
from .structure import swings,weekly_bias,choch_bos
from .liquidity import map_liquidity,sweep
from .scoring import score,grade
from .models import Signal,Direction
from .risk import risk_valid

TF={"W":"W","D":"D","4H":"4h","1H":"1h","15M":"15min","5M":"5min","1M":"1min"}

def _resample(df,rule):
    return df.resample(rule).agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()

def analyze(df,symbol="EURUSD"):
    if len(df)<100:
        return Signal(symbol,Direction.NEUTRAL,Direction.NEUTRAL,0,"NO TRADE",state="WAITING",reasons=["insufficient data"])
    df=df.sort_index()
    weekly=_resample(df,"W")
    daily=_resample(df,"D")
    h4=_resample(df,"4h")
    h1=_resample(df,"1h")
    m15=_resample(df,"15min")
    m5=_resample(df,"5min")
    bias=Direction(weekly_bias(weekly))
    if bias is Direction.NEUTRAL:
        return Signal(symbol,Direction.NEUTRAL,bias,0,"NO TRADE",state="MACRO_ANALYSIS",reasons=["Weekly structure is neutral"])
    zones=map_liquidity(swings(weekly))
    sw=sweep(df,zones)
    shift=choch_bos(m15,bias.value)
    displacement=bool(abs(m15.close.diff().iloc[-3:].sum()) > m15.close.diff().rolling(20).std().iloc[-1]*2) if len(m15)>25 else False
    features={"weekly_structure":True,"weekly_location":True,"liquidity":bool(zones),
      "inducement":False,"sweep":bool(sw),"structure_shift":shift["choch"] or shift["bos"],
      "displacement":displacement,"fvg_ob":False,"premium_discount":False,
      "economic":False,"session":True}
    sc=score(features); g=grade(sc)
    state="TRADE_SIGNAL" if sc>=80 and sw and (shift["choch"] or shift["bos"]) and displacement else "WAITING"
    reasons=[f"Weekly bias={bias.value}",f"liquidity_zones={len(zones)}",
             f"CHoCH={shift['choch']}",f"BOS={shift['bos']}",f"displacement={displacement}"]
    if sw: reasons.append(f"sweep={sw['kind']} @ {sw['price']}")
    if sc<80: reasons.append("A/A+ confirmation threshold not met")
    return Signal(symbol,bias,bias,sc,g,macro_regime="WEEKLY_STRUCTURE",liquidity_sweep=sw,
      choch=shift["choch"],bos=shift["bos"],displacement="STRONG" if displacement else "NONE",
      state=state,status="TRADE SIGNAL" if state=="TRADE_SIGNAL" else "NO TRADE",reasons=reasons)
