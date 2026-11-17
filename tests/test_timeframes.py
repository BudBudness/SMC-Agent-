import pandas as pd

from smc_agent.timeframes import ANALYSIS_TIMEFRAMES, reconstruct, resample


def test_requested_timeframes_include_30m_and_week_daily_aliases():
    index = pd.date_range("2026-01-01", periods=120, freq="min", tz="UTC")
    values = list(range(120))
    source = pd.DataFrame(
        {
            "open": values,
            "high": [value + 1 for value in values],
            "low": [value - 1 for value in values],
            "close": values,
        },
        index=index,
    )

    frames = reconstruct(source)

    assert "30M" in ANALYSIS_TIMEFRAMES
    assert len(frames["30M"]) == 4
    assert frames["30M"].iloc[0].open == 0
    assert frames["30M"].iloc[0].high == 30
    assert frames["30M"].iloc[0].low == -1
    assert frames["30M"].iloc[0].close == 29
    assert resample(source, "1W").equals(frames["W"])
    assert resample(source, "1D").equals(frames["D"])
