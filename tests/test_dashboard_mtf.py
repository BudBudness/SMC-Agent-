import pandas as pd

from scripts.build_dashboard_mtf import asof_state


def test_full_history_asof_state_uses_confirmed_swings():
    idx = pd.date_range("2020-01-01", periods=12, freq="D", tz="UTC")
    values = [1, 2, 1, 3, 2, 4, 3, 5, 4, 6, 5, 7]
    df = pd.DataFrame({
        "open": values,
        "high": [v + 0.2 for v in values],
        "low": [v - 0.2 for v in values],
        "close": values,
    }, index=idx)
    state, points = asof_state(df)
    assert state in {"LONG", "SHORT", "NEUTRAL"}
    assert points
