from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
import requests
import yfinance as yf


def fetch_ohlcv(ticker: str, period: str = "6mo", polygon_api_key: Optional[str] = None) -> pd.DataFrame:
    """Fetch daily OHLCV. Polygon is preferred when a key is supplied; yfinance is fallback."""
    polygon_api_key = polygon_api_key or os.getenv("POLYGON_API_KEY")
    if polygon_api_key:
        try:
            return _fetch_polygon_daily(ticker, period, polygon_api_key)
        except Exception:
            # Fallback keeps the agent usable for experiments.
            pass
    df = yf.download(ticker, period=period, interval="1d", auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
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
