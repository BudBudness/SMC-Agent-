import pandas as pd

def swings(df,left=2,right=2):
    out=[]
    for i in range(left,len(df)-right):
        h=float(df.high.iloc[i]); l=float(df.low.iloc[i])
        if h>df.high.iloc[i-left:i].max() and h>=df.high.iloc[i+1:i+right+1].max():
            out.append(("HIGH",df.index[i],h,df.index[i+right]))
        if l<df.low.iloc[i-left:i].min() and l<=df.low.iloc[i+1:i+right+1].min():
            out.append(("LOW",df.index[i],l,df.index[i+right]))
    return sorted(out,key=lambda x:x[1])

def protected_swings(df):
    return swings(df,3,3)

def structure_state(df):
    s=swings(df)
    highs=[x[2] for x in s if x[0]=="HIGH"]; lows=[x[2] for x in s if x[0]=="LOW"]
    if len(highs)<2 or len(lows)<2:return "NEUTRAL"
    if highs[-1]>highs[-2] and lows[-1]>lows[-2]:return "LONG"
    if highs[-1]<highs[-2] and lows[-1]<lows[-2]:return "SHORT"
    return "NEUTRAL"

def weekly_bias(df):
    return structure_state(df)

def choch_bos(df,direction):
    if len(df)<8:return {"choch":False,"bos":False}
    s=swings(df)
    if len(s)<4:return {"choch":False,"bos":False}
    last=float(df.close.iloc[-1])
    highs=[x[2] for x in s if x[0]=="HIGH"]; lows=[x[2] for x in s if x[0]=="LOW"]
    choch = (direction=="LONG" and len(highs)>=2 and last>highs[-1]) or (direction=="SHORT" and len(lows)>=2 and last<lows[-1])
    bos = (direction=="LONG" and len(highs)>=3 and highs[-1]>highs[-2]) or (direction=="SHORT" and len(lows)>=3 and lows[-1]<lows[-2])
    return {"choch":bool(choch),"bos":bool(bos)}
