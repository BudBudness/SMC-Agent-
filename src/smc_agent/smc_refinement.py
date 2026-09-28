from dataclasses import dataclass

@dataclass(frozen=True)
class Swing:
    index: int
    price: float
    kind: str

def protected_swings(bars, lookback=2):
    out = []
    for i in range(lookback, len(bars)-lookback):
        h, l = bars[i]["high"], bars[i]["low"]
        if h == max(x["high"] for x in bars[i-lookback:i+lookback+1]):
            out.append(Swing(i,h,"HIGH"))
        if l == min(x["low"] for x in bars[i-lookback:i+lookback+1]):
            out.append(Swing(i,l,"LOW"))
    return out

def cluster_levels(levels, tolerance=0.0005):
    clusters = []
    for x in sorted(levels):
        if not clusters or abs(x - sum(clusters[-1])/len(clusters[-1])) > tolerance:
            clusters.append([x])
        else:
            clusters[-1].append(x)
    return [sum(c)/len(c) for c in clusters]

def liquidity_map(bars):
    return {"BSL":cluster_levels([b["high"] for b in bars]),"SSL":cluster_levels([b["low"] for b in bars])}

def displacement(bar, atr=0.0):
    body = abs(bar["close"]-bar["open"])
    rng = max(bar["high"]-bar["low"],1e-12)
    threshold = max(atr,rng*0.6)
    return "EXTREME" if body > 1.8*threshold else "STRONG" if body > threshold else "MODERATE" if body/rng > .5 else "WEAK"
