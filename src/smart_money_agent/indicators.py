from __future__ import annotations

import numpy as np
import pandas as pd


# -----------------------------
# Utilities
# -----------------------------

def _safe_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype(float)


def _safe_div(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator / denominator.replace(0, np.nan)


def _slope(series: pd.Series, window: int = 5) -> pd.Series:
    s = _safe_series(series)
    return s.diff(window) / window


def _rolling_zscore(series: pd.Series, window: int = 30) -> pd.Series:
    s = _safe_series(series)
    return (s - s.rolling(window).mean()) / s.rolling(window).std().replace(0, np.nan)


def _last_valid_float(row: pd.Series, key: str):
    if key not in row or pd.isna(row[key]):
        return None
    value = row[key]
    return float(value) if isinstance(value, (int, float, np.number)) else value


# -----------------------------
# Core technical indicators
# -----------------------------

def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    close = _safe_series(close)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def ema(series: pd.Series, span: int) -> pd.Series:
    return _safe_series(series).ewm(span=span, adjust=False).mean()


def macd(close: pd.Series) -> pd.DataFrame:
    macd_line = ema(close, 12) - ema(close, 26)
    signal = ema(macd_line, 9)
    hist = macd_line - signal
    return pd.DataFrame({"macd": macd_line, "macd_signal": signal, "macd_hist": hist})


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    high = _safe_series(df["High"])
    low = _safe_series(df["Low"])
    close = _safe_series(df["Close"])
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()


def vwap(df: pd.DataFrame) -> pd.Series:
    typical_price = (_safe_series(df["High"]) + _safe_series(df["Low"]) + _safe_series(df["Close"])) / 3
    volume = _safe_series(df["Volume"])
    cumulative_pv = (typical_price * volume).cumsum()
    cumulative_volume = volume.cumsum().replace(0, np.nan)
    return cumulative_pv / cumulative_volume


def obv(df: pd.DataFrame) -> pd.Series:
    close = _safe_series(df["Close"])
    volume = _safe_series(df["Volume"])
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


def chaikin_money_flow(df: pd.DataFrame, window: int = 20) -> pd.Series:
    high = _safe_series(df["High"])
    low = _safe_series(df["Low"])
    close = _safe_series(df["Close"])
    volume = _safe_series(df["Volume"])
    denom = (high - low).replace(0, np.nan)
    money_flow_multiplier = ((close - low) - (high - close)) / denom
    money_flow_volume = money_flow_multiplier.fillna(0) * volume
    return money_flow_volume.rolling(window).sum() / volume.rolling(window).sum().replace(0, np.nan)


def money_flow_index(df: pd.DataFrame, window: int = 14) -> pd.Series:
    high = _safe_series(df["High"])
    low = _safe_series(df["Low"])
    close = _safe_series(df["Close"])
    volume = _safe_series(df["Volume"])
    typical_price = (high + low + close) / 3
    raw_money_flow = typical_price * volume
    direction = typical_price.diff()
    positive_flow = raw_money_flow.where(direction > 0, 0.0)
    negative_flow = raw_money_flow.where(direction < 0, 0.0)
    ratio = positive_flow.rolling(window).sum() / negative_flow.rolling(window).sum().replace(0, np.nan)
    return 100 - (100 / (1 + ratio))


def accumulation_distribution_line(df: pd.DataFrame) -> pd.Series:
    high = _safe_series(df["High"])
    low = _safe_series(df["Low"])
    close = _safe_series(df["Close"])
    volume = _safe_series(df["Volume"])
    clv = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    return (clv.fillna(0) * volume).cumsum()


def volume_price_trend(df: pd.DataFrame) -> pd.Series:
    close = _safe_series(df["Close"])
    volume = _safe_series(df["Volume"])
    return (volume * close.pct_change().fillna(0)).cumsum()


def ease_of_movement(df: pd.DataFrame, window: int = 14) -> pd.Series:
    high = _safe_series(df["High"])
    low = _safe_series(df["Low"])
    volume = _safe_series(df["Volume"])
    midpoint_move = ((high + low) / 2).diff()
    box_ratio = (volume / 1_000_000) / (high - low).replace(0, np.nan)
    emv = midpoint_move / box_ratio.replace(0, np.nan)
    return emv.rolling(window).mean()


def close_location_value(df: pd.DataFrame) -> pd.Series:
    high = _safe_series(df["High"])
    low = _safe_series(df["Low"])
    close = _safe_series(df["Close"])
    return ((close - low) - (high - close)) / (high - low).replace(0, np.nan)


# -----------------------------
# Enrichment
# -----------------------------

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add v2 technical, money-flow, volatility, and tape-reading indicators."""
    if df.empty:
        return df
    out = df.copy()
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        out[col] = _safe_series(out[col])

    close = out["Close"]
    high = out["High"]
    low = out["Low"]
    open_ = out["Open"]
    volume = out["Volume"]

    # Trend
    out["SMA10"] = close.rolling(10).mean()
    out["SMA20"] = close.rolling(20).mean()
    out["SMA50"] = close.rolling(50).mean()
    out["SMA100"] = close.rolling(100).mean()
    out["SMA200"] = close.rolling(200).mean()
    out["EMA8"] = ema(close, 8)
    out["EMA21"] = ema(close, 21)
    out["EMA50"] = ema(close, 50)
    out["TrendSlope20"] = _slope(out["SMA20"], 5)
    out["TrendSlope50"] = _slope(out["SMA50"], 10)
    out["DistanceFromSMA20Pct"] = (close / out["SMA20"] - 1) * 100
    out["DistanceFromSMA50Pct"] = (close / out["SMA50"] - 1) * 100
    out["DistanceFromSMA200Pct"] = (close / out["SMA200"] - 1) * 100
    out["GoldenCrossFlag"] = ((out["SMA50"] > out["SMA200"]) & (out["SMA50"].shift(1) <= out["SMA200"].shift(1))).astype(float)
    out["DeathCrossFlag"] = ((out["SMA50"] < out["SMA200"]) & (out["SMA50"].shift(1) >= out["SMA200"].shift(1))).astype(float)

    # Momentum
    out["RSI14"] = rsi(close)
    out["RSI5"] = rsi(close, 5)
    out = pd.concat([out, macd(close)], axis=1)
    out["ROC5"] = close.pct_change(5) * 100
    out["ROC20"] = close.pct_change(20) * 100
    out["StochK14"] = (close - low.rolling(14).min()) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, np.nan) * 100
    out["StochD3"] = out["StochK14"].rolling(3).mean()

    # Volatility
    out["ATR14"] = atr(out)
    out["ATRPercent"] = out["ATR14"] / close * 100
    out["TrueRangePct"] = (high - low) / close * 100
    out["RealizedVol20"] = close.pct_change().rolling(20).std() * np.sqrt(252) * 100
    out["BollingerMid20"] = out["SMA20"]
    out["BollingerUpper20"] = out["SMA20"] + 2 * close.rolling(20).std()
    out["BollingerLower20"] = out["SMA20"] - 2 * close.rolling(20).std()
    out["BollingerWidthPct"] = (out["BollingerUpper20"] - out["BollingerLower20"]) / out["BollingerMid20"] * 100

    # Volume and money flow
    out["VWAP"] = vwap(out)
    out["VWAPDeviationPct"] = (close / out["VWAP"] - 1) * 100
    out["OBV"] = obv(out)
    out["OBVTrend20"] = _slope(out["OBV"], 20)
    out["CMF20"] = chaikin_money_flow(out)
    out["MFI14"] = money_flow_index(out)
    out["ADL"] = accumulation_distribution_line(out)
    out["ADLTrend20"] = _slope(out["ADL"], 20)
    out["VPT"] = volume_price_trend(out)
    out["VPTTrend20"] = _slope(out["VPT"], 20)
    out["EaseOfMovement14"] = ease_of_movement(out)
    out["CloseLocationValue"] = close_location_value(out)
    out["DollarVolume"] = close * volume
    out["AvgDollarVolume20"] = out["DollarVolume"].rolling(20).mean()
    out["AvgVolume30"] = volume.rolling(30).mean()
    out["RelativeVolume30"] = volume / out["AvgVolume30"].replace(0, np.nan)
    out["VolumeZ"] = _rolling_zscore(volume, 30)
    out["UpVolume"] = volume.where(close.diff() > 0, 0.0)
    out["DownVolume"] = volume.where(close.diff() < 0, 0.0)
    out["UpDownVolumeRatio20"] = out["UpVolume"].rolling(20).sum() / out["DownVolume"].rolling(20).sum().replace(0, np.nan)
    out["FloatRotationProxy"] = volume / volume.rolling(60).mean().replace(0, np.nan)

    # Gap, return, tape behavior
    out["GapPct"] = (open_ / close.shift(1) - 1) * 100
    out["Return1D"] = close.pct_change() * 100
    out["Return5D"] = close.pct_change(5) * 100
    out["Return20D"] = close.pct_change(20) * 100
    out["IntradayReturnPct"] = (close / open_ - 1) * 100
    out["HighLowRangePct"] = (high / low - 1) * 100
    out["CloseToHighPct"] = (close / high - 1) * 100
    out["CloseToLowPct"] = (close / low - 1) * 100
    out["OpeningRangeBreakoutProxy"] = ((close > high.shift(1)) & (volume > volume.rolling(30).mean())).astype(float)
    out["DistributionDayFlag"] = ((out["Return1D"] < -1.5) & (volume > volume.shift(1))).astype(float)
    out["DistributionDayCount25"] = out["DistributionDayFlag"].rolling(25).sum()
    out["AccumulationDayFlag"] = ((out["Return1D"] > 1.5) & (volume > volume.shift(1))).astype(float)
    out["AccumulationDayCount25"] = out["AccumulationDayFlag"].rolling(25).sum()
    out["PocketPivotProxy"] = ((close > out["SMA10"]) & (volume > volume.rolling(10).max().shift(1)) & (out["Return1D"] > 0)).astype(float)

    # Price structure
    out["High52W"] = high.rolling(252, min_periods=60).max()
    out["Low52W"] = low.rolling(252, min_periods=60).min()
    out["DistanceFrom52WHighPct"] = (close / out["High52W"] - 1) * 100
    out["DistanceFrom52WLowPct"] = (close / out["Low52W"] - 1) * 100
    out["Breakout20DFlag"] = (close > high.rolling(20).max().shift(1)).astype(float)
    out["Breakdown20DFlag"] = (close < low.rolling(20).min().shift(1)).astype(float)

    return out


def add_relative_strength(df: pd.DataFrame, benchmark_df: pd.DataFrame, benchmark_name: str = "SPY") -> pd.DataFrame:
    """Add relative-strength indicators against a benchmark OHLCV frame."""
    if df.empty or benchmark_df.empty:
        return df
    out = df.copy()
    bench = benchmark_df.copy()
    if isinstance(bench.columns, pd.MultiIndex):
        bench.columns = bench.columns.get_level_values(0)
    bench_close = _safe_series(bench["Close"]).reindex(out.index).ffill()
    close = _safe_series(out["Close"])
    prefix = f"RS_{benchmark_name.upper()}"
    out[f"{prefix}_Ratio"] = close / bench_close.replace(0, np.nan)
    out[f"{prefix}_Trend20"] = _slope(out[f"{prefix}_Ratio"], 20)
    out[f"{prefix}_Return20DSpread"] = close.pct_change(20) * 100 - bench_close.pct_change(20) * 100
    out[f"{prefix}_Return60DSpread"] = close.pct_change(60) * 100 - bench_close.pct_change(60) * 100
    out[f"{prefix}_Outperform20DFlag"] = (out[f"{prefix}_Return20DSpread"] > 0).astype(float)
    return out


def latest_indicator_snapshot(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    row = df.dropna(how="all").iloc[-1]
    keys = [
        # OHLCV
        "Open", "High", "Low", "Close", "Volume",
        # Trend
        "SMA10", "SMA20", "SMA50", "SMA100", "SMA200", "EMA8", "EMA21", "EMA50",
        "TrendSlope20", "TrendSlope50", "DistanceFromSMA20Pct", "DistanceFromSMA50Pct",
        "DistanceFromSMA200Pct", "GoldenCrossFlag", "DeathCrossFlag",
        # Momentum
        "RSI14", "RSI5", "macd", "macd_signal", "macd_hist", "ROC5", "ROC20",
        "StochK14", "StochD3",
        # Volatility
        "ATR14", "ATRPercent", "TrueRangePct", "RealizedVol20", "BollingerWidthPct",
        # Money flow
        "VWAP", "VWAPDeviationPct", "OBV", "OBVTrend20", "CMF20", "MFI14", "ADL",
        "ADLTrend20", "VPT", "VPTTrend20", "EaseOfMovement14", "CloseLocationValue",
        "DollarVolume", "AvgDollarVolume20", "AvgVolume30", "RelativeVolume30", "VolumeZ",
        "UpDownVolumeRatio20", "FloatRotationProxy",
        # Tape/gap/price action
        "GapPct", "Return1D", "Return5D", "Return20D", "IntradayReturnPct",
        "HighLowRangePct", "CloseToHighPct", "CloseToLowPct", "OpeningRangeBreakoutProxy",
        "DistributionDayFlag", "DistributionDayCount25", "AccumulationDayFlag",
        "AccumulationDayCount25", "PocketPivotProxy",
        # Price structure
        "High52W", "Low52W", "DistanceFrom52WHighPct", "DistanceFrom52WLowPct",
        "Breakout20DFlag", "Breakdown20DFlag",
        # Relative strength, if added
        "RS_SPY_Ratio", "RS_SPY_Trend20", "RS_SPY_Return20DSpread", "RS_SPY_Return60DSpread",
        "RS_SPY_Outperform20DFlag", "RS_QQQ_Ratio", "RS_QQQ_Trend20", "RS_QQQ_Return20DSpread",
        "RS_QQQ_Return60DSpread", "RS_QQQ_Outperform20DFlag",
    ]
    result = {}
    for key in keys:
        value = _last_valid_float(row, key)
        if value is not None:
            result[key] = value
    return result
