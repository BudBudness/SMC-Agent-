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

    high_mask = high.gt(prior_high) & high.ge(future_high)
    low_mask = low.lt(prior_low) & low.le(future_low)
    index_values = df.index.to_numpy()

    out = []
    for i in high_mask.to_numpy().nonzero()[0]:
        if i + right < len(index_values):
            out.append(("HIGH", index_values[i], float(high.iloc[i]), index_values[i + right]))
    for i in low_mask.to_numpy().nonzero()[0]:
        if i + right < len(index_values):
            out.append(("LOW", index_values[i], float(low.iloc[i]), index_values[i + right]))
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
