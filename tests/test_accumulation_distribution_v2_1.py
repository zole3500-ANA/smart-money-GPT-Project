
import numpy as np
import pandas as pd

from smart_money_agent.indicators import add_indicators, latest_indicator_snapshot


def test_accumulation_distribution_v2_1_columns_exist():
    dates = pd.date_range("2025-01-01", periods=80, freq="D")
    close = pd.Series(np.linspace(10, 20, 80) + np.sin(np.arange(80)), index=dates)
    df = pd.DataFrame({
        "Open": close * 0.99,
        "High": close * 1.03,
        "Low": close * 0.97,
        "Close": close,
        "Volume": np.linspace(1_000_000, 2_000_000, 80),
    }, index=dates)

    enriched = add_indicators(df)
    required = [
        "ADL", "ADLTrend20", "ADLPriceDivergence20",
        "MFI14", "VPT", "VPTTrend20", "VPTPriceDivergence20",
        "EaseOfMovement14", "EaseOfMovementTrend5", "CloseLocationValue",
        "UpDownVolumeRatio20", "PocketPivotProxy", "PocketPivotCount20",
        "DistributionDayFlag", "DistributionDayCount25",
        "AccumulationDayFlag", "AccumulationDayCount25", "NetAccumulationDays25",
    ]

    for col in required:
        assert col in enriched.columns

    snap = latest_indicator_snapshot(enriched)
    for col in required:
        assert col in snap
