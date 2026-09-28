import pandas as pd
from .structure import swings,weekly_bias,choch_bos
from .liquidity import map_liquidity,sweep
from .scoring import score,grade
from .models import Signal,Direction
def _resample(df,rule):
    return df.resample(rule).agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()
def _disp(df):
    if len(df)<25:return "NONE"
    body=(df.close-df.open).abs(); rng=(df.high-df.low).replace(0,pd.NA); atr=rng.rolling(20).mean().iloc[-1]
    if pd.isna(atr):return "NONE"
    r=body.iloc[-1]/atr
    return "EXTREME" if r>=2.5 else "STRONG" if r>=1.8 else "MODERATE" if r>=1.3 else "WEAK"
def analyze(df,symbol="EURUSD"):
    if len(df)<100:return Signal(symbol,Direction.NEUTRAL,Direction.NEUTRAL,0,"NO TRADE",state="WAITING",reasons=["insufficient data"])
    df=df.sort_index()
    m={r:_resample(df,r) for r in ["12ME","6ME","3ME","W","D","4h","1h","15min","5min","1min"]}
    bias=Direction(weekly_bias(m["W"]))
    if bias is Direction.NEUTRAL:return Signal(symbol,Direction.NEUTRAL,bias,0,"NO TRADE",state="MACRO_ANALYSIS",reasons=["Weekly structure is neutral"])
    zones=map_liquidity(swings(m["W"])); sw=sweep(df,zones); shift=choch_bos(m["15min"],bias.value); disp=_disp(m["15min"])
    # Inducement is deliberately conservative: a failed internal level before the external sweep.
    inducement=None
    if sw and len(zones)>=2: inducement={"detected":True,"reference":zones[-2]["price"]}
    features={"weekly_structure":True,"weekly_location":True,"liquidity":bool(zones),"inducement":bool(inducement),
      "sweep":bool(sw),"structure_shift":shift["choch"] or shift["bos"],"displacement":disp in {"STRONG","EXTREME"},
      "fvg_ob":False,"premium_discount":False,"economic":False,"session":True}
    sc=score(features); g=grade(sc); eligible=sc>=80 and bool(sw) and (shift["choch"] or shift["bos"]) and disp in {"STRONG","EXTREME"}
    return Signal(symbol,bias,bias,sc,g,macro_regime="WEEKLY_STRUCTURE",liquidity_sweep=sw,inducement=inducement,
      choch=shift["choch"],bos=shift["bos"],displacement=disp,state="TRADE_SIGNAL" if eligible else "WAITING",
      status="TRADE SIGNAL" if eligible else "NO TRADE",reasons=[f"Weekly bias={bias.value}",f"CHoCH={shift['choch']}",f"BOS={shift['bos']}",f"displacement={disp}"]+([] if eligible else ["A/A+ threshold not met"]))
