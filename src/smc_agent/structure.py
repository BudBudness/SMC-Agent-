import pandas as pd

def swings(df, left=2, right=2):
    """Return confirmed swing points using vectorized rolling windows."""
    if len(df) <= left + right:
        return []

    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")
    prior_high = high.shift(1).rolling(left, min_periods=left).max()
    future_high = high.shift(-1).rolling(right, min_periods=right).max()
    prior_low = low.shift(1).rolling(left, min_periods=left).min()
    future_low = low.shift(-1).rolling(right, min_periods=right).min()

    high_positions = high.index[high.gt(prior_high) & high.ge(future_high)]
    low_positions = low.index[low.lt(prior_low) & low.le(future_low)]

    out = []
    for pos in high_positions:
        i = df.index.get_loc(pos)
        out.append(("HIGH", pos, float(high.loc[pos]), df.index[i + right]))
    for pos in low_positions:
        i = df.index.get_loc(pos)
        out.append(("LOW", pos, float(low.loc[pos]), df.index[i + right]))
    out.sort(key=lambda x: x[1])
    return out


def protected_swings(df):
    return swings(df, 3, 3)


def structure_state(df):
    s = swings(df)
    highs = [x[2] for x in s if x[0] == "HIGH"]
    lows = [x[2] for x in s if x[0] == "LOW"]
    if len(highs) < 2 or len(lows) < 2:
        return "NEUTRAL"
    if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        return "LONG"
    if highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        return "SHORT"
    return "NEUTRAL"


def weekly_bias(df):
    return structure_state(df)


def choch_bos(df, direction):
    if len(df) < 8:
        return {"choch": False, "bos": False}
    s = swings(df)
    if len(s) < 4:
        return {"choch": False, "bos": False}
    last = float(df.close.iloc[-1])
    highs = [x[2] for x in s if x[0] == "HIGH"]
    lows = [x[2] for x in s if x[0] == "LOW"]
    choch = (
        direction == "LONG" and len(highs) >= 2 and last > highs[-1]
    ) or (
        direction == "SHORT" and len(lows) >= 2 and last < lows[-1]
    )
    bos = (
        direction == "LONG" and len(highs) >= 3 and highs[-1] > highs[-2]
    ) or (
        direction == "SHORT" and len(lows) >= 3 and lows[-1] < lows[-2]
    )
    return {"choch": bool(choch), "bos": bool(bos)}
