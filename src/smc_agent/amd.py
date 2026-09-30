"""4H accumulation/manipulation/distribution investigation."""
def classify_amd(df):
    if len(df)<20:return "UNCLASSIFIED"
    r=df.iloc[-20:]; rng=float(r.high.max()-r.low.min())
    if rng<=0:return "UNCLASSIFIED"
    first=r.iloc[:7]; middle=r.iloc[7:14]; last=r.iloc[14:]
    fr=float(first.high.max()-first.low.min()); mr=float(middle.high.max()-middle.low.min()); lr=float(last.high.max()-last.low.min())
    fd=abs(float(first.close.iloc[-1]-first.close.iloc[0])); md=max(abs(float(middle.high.max()-first.high.max())),abs(float(first.low.min()-middle.low.min())))
    ld=abs(float(last.close.iloc[-1]-last.close.iloc[0]))
    compression=fr<rng*.55; manipulation=md>max(fr*.35,rng*.12); delivery=ld>max(fd*1.25,rng*.10) and lr>fr*.7
    if compression and manipulation and delivery:return "DISTRIBUTION" if last.close.iloc[-1]<first.close.iloc[0] else "ACCUMULATION"
    if manipulation and delivery:return "MANIPULATION"
    return "UNCLASSIFIED"
