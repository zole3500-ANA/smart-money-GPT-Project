
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from io import StringIO
from typing import Any, Dict, Optional
import math
import re
import xml.etree.ElementTree as ET

import pandas as pd
import requests
try:
    import yfinance as yf
except Exception:  # optional runtime dependency
    yf = None

from .finra import fetch_regsho_daily_file


DEFAULT_USER_AGENT = "SmartMoneyWhaleAgent/0.2.8 contact@example.com"


def has_payload(payload: Dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False
    for key, value in payload.items():
        if key.startswith("_"):
            continue
        if value not in (None, "", [], {}):
            return True
    return False


def _meta(source: str, confidence: float, notes: list[str], freshness: str = "unknown") -> Dict[str, Any]:
    return {
        "source": source,
        "confidence": round(float(confidence), 2),
        "freshness": freshness,
        "notes": notes,
    }


def merge_optional_feeds(local: Dict[str, Any], public: Dict[str, Any]) -> Dict[str, Any]:
    """Merge local JSON optional feeds with public free feeds.

    Local JSON wins when a group is present because user-provided vendor data is usually more specific.
    Public data fills only missing groups. Metadata is merged and preserved.
    """
    result = dict(local or {})
    result.setdefault("_meta", {})
    public = public or {}
    for group, payload in public.items():
        if group == "_meta":
            continue
        if has_payload(result.get(group, {})):
            continue
        if has_payload(payload):
            result[group] = payload
            if "_meta" in public and group in public["_meta"]:
                result["_meta"][group] = public["_meta"][group]
    for group, meta in (public.get("_meta") or {}).items():
        result["_meta"].setdefault(group, meta)
    return result


def collect_public_optional_feeds(
    ticker: str,
    finra_date_yyyymmdd: Optional[str] = None,
    sec_user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """Collect best-effort no-API-key public/proxy data.

    This is not equivalent to paid options/dark-pool feeds. It verifies what can be found from
    public pages/files and omits groups that cannot be supported.
    """
    ticker = ticker.upper().strip()
    ua = sec_user_agent or DEFAULT_USER_AGENT
    payload: Dict[str, Any] = {
        "options_flow": {},
        "institutional_flow": {},
        "insider_flow": {},
        "dark_pool": {},
        "_meta": {},
    }

    options, options_meta = collect_yfinance_options_proxy(ticker)
    if has_payload(options):
        payload["options_flow"] = options
        payload["_meta"]["options_flow"] = options_meta

    insider, insider_meta = collect_sec_form4_insider(ticker, ua)
    if has_payload(insider):
        payload["insider_flow"] = insider
        payload["_meta"]["insider_flow"] = insider_meta

    institutional, institutional_meta = collect_yfinance_institutional_proxy(ticker)
    if has_payload(institutional):
        payload["institutional_flow"] = institutional
        payload["_meta"]["institutional_flow"] = institutional_meta

    dark, dark_meta = collect_finra_off_exchange_proxy(ticker, finra_date_yyyymmdd)
    if has_payload(dark):
        payload["dark_pool"] = dark
        payload["_meta"]["dark_pool"] = dark_meta

    return payload


def collect_yfinance_options_proxy(ticker: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Approximate Options Flow from public option-chain snapshots via yfinance.

    Does not provide sweeps/aggressor side/gamma. Confidence is moderate-low.
    """
    try:
        if yf is None:
            return {}, _meta("public_option_chain_yfinance_proxy", 0.0, ["yfinance is not installed; cannot fetch public option chain proxy."], "failed")
        tk = yf.Ticker(ticker)
        expirations = list(tk.options or [])
        if not expirations:
            return {}, _meta("yfinance_option_chain", 0.0, ["No public option chain returned."], "not_found")

        price = None
        try:
            hist = tk.history(period="5d")
            if not hist.empty:
                price = float(hist["Close"].dropna().iloc[-1])
        except Exception:
            price = None

        call_volume = put_volume = 0.0
        call_oi = put_oi = 0.0
        near_call_premium = near_put_premium = 0.0
        leaps_call_premium = leaps_put_premium = 0.0
        otm_call_premium = otm_put_premium = 0.0
        total_premium = 0.0

        now = datetime.now(timezone.utc).date()
        used_expirations = 0
        for expiry in expirations[:8]:
            try:
                chain = tk.option_chain(expiry)
                calls = chain.calls.copy()
                puts = chain.puts.copy()
            except Exception:
                continue

            used_expirations += 1
            exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
            days = (exp_date - now).days

            for df, is_call in [(calls, True), (puts, False)]:
                if df is None or df.empty:
                    continue
                vol = pd.to_numeric(df.get("volume", 0), errors="coerce").fillna(0)
                oi = pd.to_numeric(df.get("openInterest", 0), errors="coerce").fillna(0)
                last = pd.to_numeric(df.get("lastPrice", 0), errors="coerce").fillna(0)
                strike = pd.to_numeric(df.get("strike", 0), errors="coerce").fillna(0)
                premium = (last * vol * 100).fillna(0)
                p_sum = float(premium.sum())

                if is_call:
                    call_volume += float(vol.sum())
                    call_oi += float(oi.sum())
                    if days <= 45:
                        near_call_premium += p_sum
                    if days >= 365:
                        leaps_call_premium += p_sum
                    if price is not None:
                        otm_call_premium += float(premium[strike > price].sum())
                else:
                    put_volume += float(vol.sum())
                    put_oi += float(oi.sum())
                    if days <= 45:
                        near_put_premium += p_sum
                    if days >= 365:
                        leaps_put_premium += p_sum
                    if price is not None:
                        otm_put_premium += float(premium[strike < price].sum())
                total_premium += p_sum

        total_volume = call_volume + put_volume
        total_oi = call_oi + put_oi
        if total_volume <= 0 and total_oi <= 0:
            return {}, _meta("yfinance_option_chain", 0.0, ["Option chain existed but no volume/OI was available."], "not_found")

        bullish_premium = near_call_premium + leaps_call_premium + otm_call_premium
        bearish_premium = near_put_premium + leaps_put_premium + otm_put_premium
        directional = bullish_premium + bearish_premium

        out = {
            "unusual_options_volume": total_volume,
            "call_volume": call_volume,
            "put_volume": put_volume,
            "call_put_volume_ratio": call_volume / put_volume if put_volume else None,
            "put_call_ratio": put_volume / call_volume if call_volume else None,
            "options_volume_open_interest_ratio": total_volume / total_oi if total_oi else None,
            "premium_paid_usd": total_premium,
            "near_term_call_premium_usd": near_call_premium,
            "near_term_put_premium_usd": near_put_premium,
            "leaps_call_premium_usd": leaps_call_premium,
            "leaps_put_premium_usd": leaps_put_premium,
            "otm_call_premium_usd": otm_call_premium,
            "otm_put_premium_usd": otm_put_premium,
            "bullish_premium_ratio": bullish_premium / directional if directional else None,
        }
        return out, _meta(
            "public_option_chain_yfinance_proxy",
            0.55,
            [
                f"Derived from {used_expirations} public option-chain expirations.",
                "No sweep orders, block-trade aggressor side, or dealer gamma is available from this free proxy.",
            ],
            "snapshot",
        )
    except Exception as exc:
        return {}, _meta("public_option_chain_yfinance_proxy", 0.0, [f"Fetch failed: {exc}"], "failed")


def _sec_headers(user_agent: str) -> Dict[str, str]:
    return {"User-Agent": user_agent or DEFAULT_USER_AGENT, "Accept-Encoding": "gzip, deflate", "Host": "data.sec.gov"}


def _sec_archive_headers(user_agent: str) -> Dict[str, str]:
    return {"User-Agent": user_agent or DEFAULT_USER_AGENT, "Accept-Encoding": "gzip, deflate"}


def get_sec_cik_for_ticker(ticker: str, user_agent: str) -> Optional[int]:
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": user_agent or DEFAULT_USER_AGENT, "Accept-Encoding": "gzip, deflate"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    for item in data.values():
        if str(item.get("ticker", "")).upper() == ticker.upper():
            return int(item["cik_str"])
    return None


def _find_text_any(elem: ET.Element, path: str) -> Optional[str]:
    found = elem.find(path)
    if found is not None and found.text:
        return found.text.strip()
    return None


def collect_sec_form4_insider(ticker: str, user_agent: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Parse recent SEC Form 4 XML for open-market P/S and exercise M events."""
    try:
        cik = get_sec_cik_for_ticker(ticker, user_agent)
        if not cik:
            return {}, _meta("sec_edgar_form4", 0.0, ["Ticker CIK not found in SEC company_tickers.json."], "not_found")

        sub_url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
        r = requests.get(sub_url, headers=_sec_headers(user_agent), timeout=20)
        r.raise_for_status()
        recent = r.json().get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accessions = recent.get("accessionNumber", [])
        docs = recent.get("primaryDocument", [])
        dates = recent.get("filingDate", [])

        net_buy = 0.0
        buy_count = sell_count = 0
        ceo_cfo_count = 0
        ceo_cfo_net = 0.0
        option_exercise_then_sell = 0
        direct_open_market_buy_count = 0
        direct_open_market_buy_value = 0.0
        buyer_names: set[str] = set()
        parsed_files = 0

        for form, acc, doc, filing_date in list(zip(forms, accessions, docs, dates))[:80]:
            if str(form).strip() != "4":
                continue
            acc_nodash = acc.replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/{doc}"
            try:
                fr = requests.get(url, headers=_sec_archive_headers(user_agent), timeout=20)
                fr.raise_for_status()
                text = fr.text
                if "<ownershipDocument" not in text and "<nonDerivativeTransaction" not in text:
                    continue
                root = ET.fromstring(text.encode("utf-8"))
                parsed_files += 1
            except Exception:
                continue

            owner_name = _find_text_any(root, ".//{*}reportingOwner/{*}reportingOwnerId/{*}rptOwnerName") or ""
            title = _find_text_any(root, ".//{*}reportingOwnerRelationship/{*}officerTitle") or ""
            title_low = title.lower()
            is_ceo_cfo = any(x in title_low for x in ["ceo", "chief executive", "cfo", "chief financial", "principal financial", "president"])

            for tx in root.findall(".//{*}nonDerivativeTransaction") + root.findall(".//{*}derivativeTransaction"):
                code = _find_text_any(tx, ".//{*}transactionCoding/{*}transactionCode") or ""
                shares = _find_text_any(tx, ".//{*}transactionAmounts/{*}transactionShares/{*}value")
                price = _find_text_any(tx, ".//{*}transactionAmounts/{*}transactionPricePerShare/{*}value")
                acq_disp = _find_text_any(tx, ".//{*}transactionAmounts/{*}transactionAcquiredDisposedCode/{*}value") or ""
                try:
                    sh = float(shares or 0)
                    pr = float(price or 0)
                    value = sh * pr
                except Exception:
                    value = 0.0

                if code.upper() == "P" or (acq_disp.upper() == "A" and code.upper() in {"P"}):
                    buy_count += 1
                    net_buy += value
                    direct_open_market_buy_count += 1
                    direct_open_market_buy_value += value
                    if owner_name:
                        buyer_names.add(owner_name)
                    if is_ceo_cfo:
                        ceo_cfo_count += 1
                        ceo_cfo_net += value
                elif code.upper() == "S" or (acq_disp.upper() == "D" and code.upper() in {"S"}):
                    sell_count += 1
                    net_buy -= value
                    if is_ceo_cfo:
                        ceo_cfo_count += 1
                        ceo_cfo_net -= value
                elif code.upper() == "M":
                    option_exercise_then_sell += 1
                    if is_ceo_cfo:
                        ceo_cfo_count += 1

        if parsed_files == 0:
            return {}, _meta("sec_edgar_form4", 0.0, ["No recent parseable Form 4 XML filings found."], "not_found")

        out = {
            "insider_net_buy_value_usd": net_buy,
            "insider_buy_count": buy_count,
            "insider_sell_count": sell_count,
            "ceo_cfo_transaction_count": ceo_cfo_count,
            "ceo_cfo_net_buy_value_usd": ceo_cfo_net,
            "cluster_buying_count": len(buyer_names),
            "option_exercise_then_sell_count": option_exercise_then_sell,
            "direct_open_market_buy_count": direct_open_market_buy_count,
            "direct_open_market_buy_value_usd": direct_open_market_buy_value,
        }
        confidence = 0.82 if (buy_count + sell_count + option_exercise_then_sell) > 0 else 0.55
        return out, _meta(
            "sec_edgar_form4_public",
            confidence,
            [f"Parsed {parsed_files} recent Form 4 XML filings from SEC EDGAR.", "Transaction coding P/S/M used; compensation context not fully available."],
            "recent_filings",
        )
    except Exception as exc:
        return {}, _meta("sec_edgar_form4_public", 0.0, [f"Fetch failed: {exc}"], "failed")


def collect_yfinance_institutional_proxy(ticker: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Low-confidence public proxy for institutional ownership.

    True 13F net-flow requires quarterly 13F data set aggregation; this proxy only uses public holders snapshots when available.
    """
    try:
        if yf is None:
            return {}, _meta("public_holders_yfinance_proxy", 0.0, ["yfinance is not installed; cannot fetch public holders snapshot."], "failed")
        tk = yf.Ticker(ticker)
        holders = None
        for attr in ["institutional_holders", "mutualfund_holders"]:
            try:
                df = getattr(tk, attr)
                if df is not None and not df.empty:
                    holders = df.copy()
                    break
            except Exception:
                continue

        out: Dict[str, Any] = {}
        if holders is not None and not holders.empty:
            # Try to infer top holder concentration if a pct column exists.
            pct_col = None
            for col in holders.columns:
                if "pct" in str(col).lower() or "%" in str(col):
                    pct_col = col
                    break
            if pct_col is not None:
                pct = pd.to_numeric(holders[pct_col].astype(str).str.replace("%", "", regex=False), errors="coerce")
                if pct.max(skipna=True) is not None and pct.max(skipna=True) <= 1:
                    pct = pct * 100
                out["top10_holder_concentration_pct"] = float(pct.head(10).sum(skipna=True))
                out["institutional_ownership_pct"] = float(pct.sum(skipna=True))
            out["new_positions_count"] = None
            out["increased_positions_count"] = None
            out["decreased_positions_count"] = None
            out["sold_out_positions_count"] = None

        if not has_payload(out):
            return {}, _meta("public_holders_yfinance_proxy", 0.0, ["No public institutional holders snapshot returned."], "not_found")

        return out, _meta(
            "public_holders_yfinance_proxy",
            0.38,
            ["Public holders snapshot only; does not provide verified QoQ 13F flow, increased/decreased positions, or sold-out positions."],
            "snapshot",
        )
    except Exception as exc:
        return {}, _meta("public_holders_yfinance_proxy", 0.0, [f"Fetch failed: {exc}"], "failed")


def collect_finra_off_exchange_proxy(ticker: str, date_yyyymmdd: Optional[str] = None) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Use FINRA daily short-sale volume as an off-exchange/short-volume proxy.

    This is not true dark-pool net bias. It is included with low-medium confidence.
    """
    tried: list[str] = []
    dates: list[str] = []
    if date_yyyymmdd:
        dates.append(date_yyyymmdd)
    today = datetime.now(timezone.utc).date()
    for i in range(1, 15):
        d = today - timedelta(days=i)
        if d.weekday() < 5:
            dates.append(d.strftime("%Y%m%d"))

    for d in dates:
        if d in tried:
            continue
        tried.append(d)
        try:
            df = fetch_regsho_daily_file(d)
            row = df[df["Symbol"].astype(str).str.upper() == ticker.upper()]
            if row.empty:
                continue
            r = row.iloc[0]
            short_vol = float(r.get("ShortVolume", 0) or 0)
            total_vol = float(r.get("TotalVolume", 0) or 0)
            if total_vol <= 0:
                continue
            out = {
                "dark_pool_volume": total_vol,
                "dark_pool_volume_ratio": None,
                "off_exchange_trend_5d": None,
                "dark_pool_net_bias": None,
                "finra_short_volume": short_vol,
                "finra_total_reported_volume": total_vol,
                "finra_short_volume_ratio": short_vol / total_vol,
            }
            return out, _meta(
                "finra_daily_short_sale_volume_proxy",
                0.45,
                [f"FINRA consolidated short-volume file date {d}. Proxy only; no block prints, VWAP bias, or dark-pool buy/sell aggressor side."],
                d,
            )
        except Exception:
            continue

    return {}, _meta("finra_daily_short_sale_volume_proxy", 0.0, ["No FINRA daily short-volume row found in recent files."], "not_found")
