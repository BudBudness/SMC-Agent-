"""4H AMD investigation using explicit phase evidence, not forced classification."""
def classify_amd(df):
    if len(df)<20:return {"phase":"UNCLASSIFIED","evidence":[]}
    r=df.iloc[-20:]; first=r.iloc[:7]; middle=r.iloc[7:14]; last=r.iloc[14:]
    full_range=float(r.high.max()-r.low.min())
    if full_range<=0:return {"phase":"UNCLASSIFIED","evidence":[]}
    fr=float(first.high.max()-first.low.min()); mr=float(middle.high.max()-middle.low.min())
    lr=float(last.high.max()-last.low.min())
    first_drift=float(abs(first.close.iloc[-1]-first.close.iloc[0]))
    middle_excursion=float(max(abs(middle.high.max()-first.high.max()),abs(first.low.min()-middle.low.min())))
    last_drift=float(abs(last.close.iloc[-1]-last.close.iloc[0]))
    compression=fr<=full_range*.55
    manipulation=middle_excursion>=max(fr*.35,full_range*.12)
    delivery=last_drift>=max(first_drift*1.25,full_range*.10) and lr>=fr*.70
    evidence=[{"factor":"accumulation_compression","observed":compression},
              {"factor":"manipulation_excursion","observed":manipulation},
              {"factor":"delivery_expansion","observed":delivery}]
    if compression and manipulation and delivery:
        phase="DISTRIBUTION" if float(last.close.iloc[-1])<float(first.close.iloc[0]) else "ACCUMULATION"
    elif manipulation and delivery: phase="MANIPULATION"
    else: phase="UNCLASSIFIED"
    return {"phase":phase,"evidence":evidence,"window_bars":20}
