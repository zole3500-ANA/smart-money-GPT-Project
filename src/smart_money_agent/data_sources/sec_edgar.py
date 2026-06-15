from __future__ import annotations

import os
import time
from functools import lru_cache
from typing import Dict, Optional

import requests

SEC_BASE = "https://data.sec.gov"
SEC_FILES = "https://www.sec.gov/files"


def _headers() -> dict:
    user_agent = os.getenv("SEC_USER_AGENT", "SmartMoneyAgent/0.1 contact@example.com")
    return {"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate", "Host": "data.sec.gov"}


@lru_cache(maxsize=1)
def company_tickers() -> Dict[str, dict]:
    url = f"{SEC_FILES}/company_tickers.json"
    headers = {"User-Agent": os.getenv("SEC_USER_AGENT", "SmartMoneyAgent/0.1 contact@example.com")}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    raw = r.json()
    return {item["ticker"].upper(): item for item in raw.values()}


def ticker_to_cik(ticker: str) -> Optional[str]:
    item = company_tickers().get(ticker.upper())
    if not item:
        return None
    return str(item["cik_str"]).zfill(10)


def get_company_facts(ticker: str, sleep_sec: float = 0.15) -> Optional[dict]:
    cik = ticker_to_cik(ticker)
    if not cik:
        return None
    url = f"{SEC_BASE}/api/xbrl/companyfacts/CIK{cik}.json"
    time.sleep(sleep_sec)
    r = requests.get(url, headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def get_submissions(ticker: str, sleep_sec: float = 0.15) -> Optional[dict]:
    cik = ticker_to_cik(ticker)
    if not cik:
        return None
    url = f"{SEC_BASE}/submissions/CIK{cik}.json"
    time.sleep(sleep_sec)
    r = requests.get(url, headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def _latest_usd_fact(facts: dict, concept: str) -> Optional[float]:
    try:
        units = facts["facts"]["us-gaap"][concept]["units"]
    except KeyError:
        return None
    values = units.get("USD") or units.get("shares") or next(iter(units.values()), [])
    clean = [x for x in values if "val" in x and x.get("form") in {"10-K", "10-Q"}]
    if not clean:
        return None
    clean = sorted(clean, key=lambda x: x.get("end", ""))
    return float(clean[-1]["val"])


def extract_simple_fundamentals(facts: Optional[dict]) -> dict:
    """Create a compact fundamentals proxy. SEC taxonomy varies by company, so missing values are normal."""
    if not facts:
        return {}
    revenue = _latest_usd_fact(facts, "Revenues") or _latest_usd_fact(facts, "SalesRevenueNet")
    net_income = _latest_usd_fact(facts, "NetIncomeLoss")
    assets = _latest_usd_fact(facts, "Assets")
    liabilities = _latest_usd_fact(facts, "Liabilities")

    out = {}
    if revenue and net_income is not None:
        out["net_margin"] = net_income / revenue if revenue else None
    if assets and liabilities is not None:
        out["debt_to_assets"] = liabilities / assets if assets else None
    # revenue_growth needs historical period normalization; keep None in MVP.
    out["revenue_growth"] = None
    out["latest_revenue"] = revenue
    out["latest_net_income"] = net_income
    out["latest_assets"] = assets
    out["latest_liabilities"] = liabilities
    return out


def recent_filings_summary(ticker: str, forms: tuple[str, ...] = ("4", "13F-HR", "8-K"), max_items: int = 10) -> list[dict]:
    submissions = get_submissions(ticker)
    if not submissions:
        return []
    recent = submissions.get("filings", {}).get("recent", {})
    forms_list = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    results = []
    for form, date, accession in zip(forms_list, dates, accessions):
        if form in forms:
            results.append({"form": form, "filing_date": date, "accession": accession})
        if len(results) >= max_items:
            break
    return results
