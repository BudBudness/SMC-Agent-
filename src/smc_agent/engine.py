import pandas as pd
from .structure import swings,weekly_bias,choch_bos
from .liquidity import map_liquidity,sweep
from .scoring import score,grade
from .fvg import find_fvg
from .order_blocks import find_order_blocks
from .amd import classify_amd
from .models import Signal,Direction
def _resample(df,rule):
    return df.resample(rule).agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()
def _disp(df):
    if len(df)<25:return "NONE"
    body=(df.close-df.open).abs(); rng=(df.high-df.low).replace(0,pd.NA); atr=rng.rolling(20).mean().iloc[-1]
    if pd.isna(atr):return "NONE"
    r=body.iloc[-1]/atr
    return "EXTREME" if r>=2.5 else "STRONG" if r>=1.8 else "MODERATE" if r>=1.3 else "WEAK"
def analyze(df,symbol="EURUSD",news_events=None,now=None):
    if len(df)<100:return Signal(symbol,Direction.NEUTRAL,Direction.NEUTRAL,0,"NO TRADE",state="WAITING",reasons=["insufficient data"])
    df=df.sort_index()
    m={r:_resample(df,r) for r in ["12ME","6ME","3ME","W","D","4h","1h","15min","5min","1min"]}
    bias=Direction(weekly_bias(m["W"]))
    if bias is Direction.NEUTRAL:return Signal(symbol,Direction.NEUTRAL,bias,0,"NO TRADE",state="MACRO_ANALYSIS",reasons=["Weekly structure is neutral"])
    ws=swings(m["W"]); zones=map_liquidity(ws); sw=sweep(df,zones); shift=choch_bos(m["15min"],bias.value); disp=_disp(m["15min"])
    fvgs=find_fvg(m["15min"]); obs=find_order_blocks(m["15min"]); amd=classify_amd(m["4h"])
    mid=(m["D"].high.iloc[-1]+m["D"].low.iloc[-1])/2
    loc=(m["D"].close.iloc[-1]<mid) if bias is Direction.LONG else (m["D"].close.iloc[-1]>mid)
    inducement={"detected":True,"reference":zones[-2]["price"]} if sw and len(zones)>=2 else None
    nr="LOCKED" if news_events and now is not None else "CLEAR"
    features={"weekly_structure":True,"weekly_location":loc,"liquidity":bool(zones),"inducement":bool(inducement),
      "sweep":bool(sw),"structure_shift":shift["choch"] or shift["bos"],"displacement":disp in {"STRONG","EXTREME"},
      "fvg_ob":bool(fvgs or obs),"premium_discount":loc,"economic":nr=="CLEAR","session":True}
    sc=score(features); g=grade(sc); eligible=sc>=80 and bool(sw) and (shift["choch"] or shift["bos"]) and disp in {"STRONG","EXTREME"} and nr=="CLEAR"
    entry=float(df.close.iloc[-1]); stop=None; target=None
    if sw:
        stop=float(sw["price"]); risk=abs(entry-stop)
        target=entry+risk*2 if bias is Direction.LONG else entry-risk*2
    return Signal(symbol,bias,bias,sc,g,entry=entry if eligible else None,stop=stop if eligible else None,
      t1=target if eligible else None,t2=target if eligible else None,rr=2.0 if eligible else None,
      macro_regime=f"WEEKLY_STRUCTURE|4H_{amd}",liquidity_sweep=sw,inducement=inducement,
      choch=shift["choch"],bos=shift["bos"],displacement=disp,fvg=fvgs[-1] if fvgs else None,
      order_block=obs[-1] if obs else None,news_risk=nr,state="TRADE_SIGNAL" if eligible else "WAITING",
      status="TRADE SIGNAL" if eligible else "NO TRADE",
      reasons=[f"Weekly bias={bias.value}",f"CHoCH={shift['choch']}",f"BOS={shift['bos']}",f"displacement={disp}",f"4H AMD={amd}"]+([] if eligible else ["A/A+ threshold or confirmation not met"]))
