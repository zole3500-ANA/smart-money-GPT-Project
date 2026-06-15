from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .agent import SmartMoneyAgentConfig, SmartMoneyWhaleAgent
from .data_sources.market import list_us_tickers


def analyze_ticker_for_scan(ticker: str, config: SmartMoneyAgentConfig) -> dict:
    agent = SmartMoneyWhaleAgent(config)
    try:
        report = agent.analyze(ticker)
        return {
            "ticker": ticker,
            "current_price": report.current_price,
            "composite": report.score.composite,
            "label": report.score.label,
            "probability_up": report.forecast.probability_up,
            "smart_money_flow": report.score.smart_money_flow,
            "technical_trend": report.score.technical_trend,
            "options_flow": report.score.options_flow,
            "short_pressure": report.score.short_pressure,
            "fundamental_quality": report.score.fundamental_quality,
            "institutional_flow": report.score.institutional_flow,
            "insider_flow": report.score.insider_flow,
            "dark_pool_flow": report.score.dark_pool_flow,
            "relative_strength": report.score.relative_strength,
            "psychology": report.score.psychology,
            "catalyst_risk": report.score.catalyst_risk,
            "error": "",
        }
    except Exception as exc:  # keep batch scanning resilient
        return {"ticker": ticker, "error": str(exc)}


def scan_tickers(
    tickers: Iterable[str],
    config: SmartMoneyAgentConfig,
    max_workers: int = 4,
) -> pd.DataFrame:
    rows: List[dict] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(analyze_ticker_for_scan, ticker, config): ticker for ticker in tickers}
        for future in as_completed(futures):
            rows.append(future.result())
    df = pd.DataFrame(rows)
    if "composite" in df.columns:
        df = df.sort_values("composite", ascending=False, na_position="last")
    return df


def scan_all_us_stocks(
    limit: int = 500,
    period: str = "6mo",
    output_path: str | Path = "outputs/us_stock_smart_money_ranking.csv",
    finra_date_yyyymmdd: str | None = None,
    use_sec: bool = False,
    max_workers: int = 4,
) -> Path:
    """Scan active US common stocks using Polygon's ticker reference endpoint.

    Requires POLYGON_API_KEY. SEC is disabled by default for broad scans to avoid
    excessive EDGAR requests; run ticker-level analysis for SEC details.
    """
    tickers = list_us_tickers(limit=limit)
    config = SmartMoneyAgentConfig(
        period=period,
        finra_date_yyyymmdd=finra_date_yyyymmdd,
        use_sec=use_sec,
    )
    df = scan_tickers(tickers, config, max_workers=max_workers)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    return output
