def classify_amd(df):
    if len(df)<10:return "UNCLASSIFIED"
    r=df.iloc[-10:]; rng=r.high.max()-r.low.min()
    if rng<=0:return "UNCLASSIFIED"
    first=r.iloc[:3].close.std(); last=r.iloc[-3:].close.std()
    if first<r.close.std()*.7 and last>first*1.5:return "DISTRIBUTION"
    return "UNCLASSIFIED"
