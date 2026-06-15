import pandas as pd

from smart_money_agent.indicators import add_indicators, rsi


def test_rsi_returns_series():
    close = pd.Series([1, 2, 3, 2, 3, 4, 5, 4, 5, 6, 7, 8, 7, 8, 9, 10, 11, 12])
    out = rsi(close)
    assert len(out) == len(close)


def test_add_indicators_columns():
    df = pd.DataFrame({
        "Open": [10, 11, 12, 13, 14] * 50,
        "High": [11, 12, 13, 14, 15] * 50,
        "Low": [9, 10, 11, 12, 13] * 50,
        "Close": [10.5, 11.5, 12.5, 13.5, 14.5] * 50,
        "Volume": [1000, 1200, 1500, 1300, 1800] * 50,
    })
    out = add_indicators(df)
    assert "RSI14" in out.columns
    assert "VWAP" in out.columns
    assert "CMF20" in out.columns
