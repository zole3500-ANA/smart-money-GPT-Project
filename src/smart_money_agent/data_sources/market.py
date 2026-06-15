from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
import requests
import yfinance as yf


def fetch_ohlcv(ticker: str, period: str = "6mo", polygon_api_key: Optional[str] = None) -> pd.DataFrame:
    """Fetch daily OHLCV.

    Priority:
    1) Polygon, if POLYGON_API_KEY is supplied
    2) Yahoo Finance via yfinance
    3) Stooq CSV fallback for US tickers, useful when yfinance returns an empty frame on Streamlit Cloud
    """
    ticker = ticker.upper().strip()
    polygon_api_key = polygon_api_key or os.getenv("POLYGON_API_KEY")

    if polygon_api_key:
        try:
            df = _fetch_polygon_daily(ticker, period, polygon_api_key)
            if not df.empty:
                return _clean_ohlcv(df)
        except Exception:
            # Fallback keeps the agent usable for experiments.
            pass

    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=False, progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = _clean_ohlcv(df)
        if not df.empty:
            return df
    except Exception:
        pass

    try:
        df = _fetch_stooq_daily(ticker, period)
        df = _clean_ohlcv(df)
        if not df.empty:
            return df
    except Exception:
        pass

    return pd.DataFrame()


def _clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    rename_map = {
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    }
    df = df.rename(columns={c: rename_map.get(str(c).lower(), c) for c in df.columns})

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return pd.DataFrame()

    df = df[required].copy()
    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Open", "High", "Low", "Close"], how="any")
    df = df[df["Volume"].fillna(0) >= 0]
    return df.dropna(how="all")


def _period_to_dates(period: str) -> tuple[str, str]:
    end = datetime.utcnow().date()
    days = 180
    if period.endswith("mo"):
        days = int(period[:-2]) * 31
    elif period.endswith("y"):
        days = int(period[:-1]) * 365
    elif period.endswith("d"):
        days = int(period[:-1])
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def _fetch_polygon_daily(ticker: str, period: str, api_key: str) -> pd.DataFrame:
    start, end = _period_to_dates(period)
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker.upper()}/range/1/day/{start}/{end}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    payload = r.json()
    rows = payload.get("results", [])
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["t"], unit="ms")
    df = df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})
    return df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]


def _fetch_stooq_daily(ticker: str, period: str) -> pd.DataFrame:
    """Fetch daily OHLCV from Stooq CSV.

    Stooq uses lowercase US symbols with .us suffix, for example AAPL.US or BURU.US.
    For symbols that already include a market suffix, the function keeps the symbol as-is.
    """
    start, end = _period_to_dates(period)
    d1 = start.replace("-", "")
    d2 = end.replace("-", "")

    symbol = ticker.lower()
    if "." not in symbol:
        symbol = f"{symbol}.us"

    url = "https://stooq.com/q/d/l/"
    params = {"s": symbol, "i": "d", "d1": d1, "d2": d2}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    # Stooq returns "No data" as plain text.
    text = r.text.strip()
    if not text or text.lower().startswith("no data"):
        return pd.DataFrame()

    from io import StringIO

    df = pd.read_csv(StringIO(text))
    if df.empty or "Date" not in df.columns:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.set_index("Date")
    return df[["Open", "High", "Low", "Close", "Volume"]]


def list_us_tickers(limit: int = 5000, polygon_api_key: Optional[str] = None) -> List[str]:
    """List active US common-stock tickers using Polygon. Requires API key for production scans."""
    polygon_api_key = polygon_api_key or os.getenv("POLYGON_API_KEY")
    if not polygon_api_key:
        raise RuntimeError("POLYGON_API_KEY is required for all-US-stock scanning.")

    url = "https://api.polygon.io/v3/reference/tickers"
    params = {
        "market": "stocks",
        "active": "true",
        "type": "CS",
        "locale": "us",
        "limit": 1000,
        "apiKey": polygon_api_key,
    }
    tickers: List[str] = []
    while url and len(tickers) < limit:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        tickers.extend([x["ticker"] for x in data.get("results", []) if "ticker" in x])
        url = data.get("next_url")
        params = {"apiKey": polygon_api_key} if url else None
    return tickers[:limit]
