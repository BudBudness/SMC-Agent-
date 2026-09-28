import pandas as pd
from .structure import swings,weekly_bias,choch_bos
from .liquidity import map_liquidity,sweep
from .scoring import score,grade
from .models import Signal,Direction

def _resample(df,rule):
    return df.resample(rule).agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()

def _displacement(df):
    if len(df)<25:return False
    body=(df.close-df.open).abs()
    rng=(df.high-df.low).replace(0,pd.NA)
    atr=rng.rolling(20).mean().iloc[-1]
    return bool(pd.notna(atr) and body.iloc[-1]>1.5*atr)

def analyze(df,symbol="EURUSD"):
    if len(df)<100:
        return Signal(symbol,Direction.NEUTRAL,Direction.NEUTRAL,0,"NO TRADE",state="WAITING",reasons=["insufficient data"])
    df=df.sort_index()
    # Hierarchy: 12M -> 6M -> 3M -> W -> D -> 4H -> 1H -> 15M -> 5M -> 1M.
    macro={r:_resample(df,r) for r in ["12ME","6ME","3ME","W","D","4h","1h","15min","5min","1min"]}
    weekly=macro["W"]; m15=macro["15min"]
    bias=Direction(weekly_bias(weekly))
    if bias is Direction.NEUTRAL:
        return Signal(symbol,Direction.NEUTRAL,bias,0,"NO TRADE",state="MACRO_ANALYSIS",reasons=["Weekly structure is neutral"])
    zones=map_liquidity(swings(weekly))
    sw=sweep(df,zones)
    shift=choch_bos(m15,bias.value)
    disp=_displacement(m15)
    features={"weekly_structure":True,"weekly_location":True,"liquidity":bool(zones),
      "inducement":False,"sweep":bool(sw),"structure_shift":shift["choch"] or shift["bos"],
      "displacement":disp,"fvg_ob":False,"premium_discount":False,"economic":False,"session":True}
    sc=score(features); g=grade(sc)
    eligible=sc>=80 and bool(sw) and (shift["choch"] or shift["bos"]) and disp
    state="TRADE_SIGNAL" if eligible else "WAITING"
    reasons=[f"Weekly bias={bias.value}",f"CHoCH={shift['choch']}",f"BOS={shift['bos']}",f"displacement={disp}"]
    if not eligible: reasons.append("A/A+ confirmation threshold not met")
    return Signal(symbol,bias,bias,sc,g,macro_regime="WEEKLY_STRUCTURE",liquidity_sweep=sw,
      choch=shift["choch"],bos=shift["bos"],displacement="STRONG" if disp else "NONE",
      state=state,status="TRADE SIGNAL" if eligible else "NO TRADE",reasons=reasons)
