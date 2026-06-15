from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd
import requests


def fetch_regsho_daily_file(date_yyyymmdd: str) -> pd.DataFrame:
    """Fetch FINRA consolidated NMS short volume file.

    FINRA file availability depends on trade date and publication time. For robust production,
    keep a retry queue and store downloaded files locally.
    """
    url = f"https://cdn.finra.org/equity/regsho/daily/CNMSshvol{date_yyyymmdd}.txt"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    from io import StringIO

    return pd.read_csv(StringIO(r.text), sep="|")


def short_sale_ratio_for_ticker(ticker: str, date_yyyymmdd: Optional[str] = None) -> Optional[float]:
    if date_yyyymmdd is None:
        # Caller should supply the last completed trading date. MVP leaves this None to avoid weekend/holiday ambiguity.
        return None
    try:
        df = fetch_regsho_daily_file(date_yyyymmdd)
    except Exception:
        return None
    row = df[df["Symbol"].astype(str).str.upper() == ticker.upper()]
    if row.empty:
        return None
    short_volume = float(row.iloc[0].get("ShortVolume", 0))
    total_volume = float(row.iloc[0].get("TotalVolume", 0))
    return short_volume / total_volume if total_volume else None
