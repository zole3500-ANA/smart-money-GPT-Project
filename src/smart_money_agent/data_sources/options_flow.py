from __future__ import annotations

import os
from typing import Optional

import requests


def fetch_intrinio_unusual_options(symbol: str, api_key: Optional[str] = None) -> dict:
    """Optional paid data source for unusual options: large trades, sweeps, and blocks."""
    api_key = api_key or os.getenv("INTRINIO_API_KEY")
    if not api_key:
        return {"enabled": False, "items": [], "note": "INTRINIO_API_KEY not set"}
    url = f"https://api-v2.intrinio.com/options/unusual_activity/{symbol.upper()}"
    r = requests.get(url, auth=(api_key, ""), timeout=30)
    r.raise_for_status()
    return {"enabled": True, "items": r.json()}
