import pandas as pd

def swings(df,left=2,right=2):
    out=[]
    for i in range(left,len(df)-right):
        h=df.high.iloc[i]; l=df.low.iloc[i]
        if h>df.high.iloc[i-left:i].max() and h>=df.high.iloc[i+1:i+right+1].max():
            out.append(("HIGH",df.index[i],float(h),df.index[i+right]))
        if l<df.low.iloc[i-left:i].min() and l<=df.low.iloc[i+1:i+right+1].min():
            out.append(("LOW",df.index[i],float(l),df.index[i+right]))
    return sorted(out,key=lambda x:x[1])

def weekly_bias(df):
    s=swings(df)
    hi=[x[2] for x in s if x[0]=="HIGH"]; lo=[x[2] for x in s if x[0]=="LOW"]
    if len(hi)<2 or len(lo)<2: return "NEUTRAL"
    if hi[-1]>hi[-2] and lo[-1]>lo[-2]: return "LONG"
    if hi[-1]<hi[-2] and lo[-1]<lo[-2]: return "SHORT"
    return "NEUTRAL"
