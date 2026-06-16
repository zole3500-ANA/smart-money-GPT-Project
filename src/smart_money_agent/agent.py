from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .alternative_data import load_optional_feeds
from .data_sources.finra import short_sale_ratio_for_ticker
from .data_sources.market import fetch_ohlcv
from .data_sources.public_free import collect_public_optional_feeds, merge_optional_feeds, has_payload
from .data_sources.sec_edgar import extract_simple_fundamentals, get_company_facts, recent_filings_summary
from .indicators import add_indicators, add_relative_strength, latest_indicator_snapshot
from .prediction import forecast_next_day
from .schemas import AgentReport, VerificationResult
from .scoring import composite_score


@dataclass
class SmartMoneyAgentConfig:
    period: str = "6mo"
    weights: Optional[dict] = None
    finra_date_yyyymmdd: Optional[str] = None
    use_sec: bool = True
    use_relative_strength: bool = True
    optional_feed_dir: str = "data/optional_feeds"
    use_public_free_sources: bool = True
    sec_user_agent: Optional[str] = None


class SmartMoneyWhaleAgent:
    """Orchestrates data search, verification, analysis, synthesis, and forecast."""

    def __init__(self, config: Optional[SmartMoneyAgentConfig] = None):
        self.config = config or SmartMoneyAgentConfig()

    def analyze(self, ticker: str) -> AgentReport:
        ticker = ticker.upper().strip()
        verification: list[VerificationResult] = []

        # 1) Search / collect market data
        df = fetch_ohlcv(ticker, period=self.config.period)
        verification.append(
            VerificationResult(
                source="market_ohlcv",
                is_fresh=not df.empty,
                confidence=0.75 if not df.empty else 0.0,
                notes=["Polygon preferred if API key is set; yfinance fallback used otherwise."],
            )
        )
        if df.empty:
            raise RuntimeError(f"No market data returned for {ticker}")

        # 2) Verify / clean / indicators
        enriched = add_indicators(df)

        if self.config.use_relative_strength:
            for benchmark in ["SPY", "QQQ"]:
                try:
                    bench_df = fetch_ohlcv(benchmark, period=self.config.period)
                    enriched = add_relative_strength(enriched, bench_df, benchmark)
                    verification.append(
                        VerificationResult(
                            source=f"relative_strength_{benchmark}",
                            is_fresh=not bench_df.empty,
                            confidence=0.70 if not bench_df.empty else 0.0,
                            notes=[f"Relative strength spread vs {benchmark} added."],
                        )
                    )
                except Exception as exc:
                    verification.append(
                        VerificationResult(
                            source=f"relative_strength_{benchmark}",
                            is_fresh=False,
                            confidence=0.25,
                            notes=[f"Benchmark fetch failed: {exc}"],
                        )
                    )

        indicators = latest_indicator_snapshot(enriched)
        current_price = indicators.get("Close")

        # 3) SEC fundamentals + filings
        fundamentals = {}
        filings = []
        if self.config.use_sec:
            try:
                facts = get_company_facts(ticker)
                fundamentals = extract_simple_fundamentals(facts)
                filings = recent_filings_summary(ticker)
                verification.append(
                    VerificationResult(
                        source="sec_edgar",
                        is_fresh=True,
                        confidence=0.85,
                        notes=[f"Recent filing count captured: {len(filings)}"],
                    )
                )
            except Exception as exc:
                verification.append(
                    VerificationResult(
                        source="sec_edgar",
                        is_fresh=False,
                        confidence=0.25,
                        notes=[f"SEC fetch failed or unavailable: {exc}"],
                    )
                )

        # 4) FINRA short pressure
        short_ratio = short_sale_ratio_for_ticker(ticker, self.config.finra_date_yyyymmdd)
        verification.append(
            VerificationResult(
                source="finra_short_volume",
                is_fresh=short_ratio is not None,
                confidence=0.65 if short_ratio is not None else 0.35,
                notes=["Provide last trading date YYYYMMDD to enable FINRA short-volume ratio."],
            )
        )

        # 5) Optional paid / alternative data feeds from local JSON + no-API-key public/proxy sources
        optional_feeds = load_optional_feeds(ticker, self.config.optional_feed_dir)
        local_present = [k for k, v in optional_feeds.items() if k != "_meta" and v]
        verification.append(
            VerificationResult(
                source="optional_local_json_feeds",
                is_fresh=bool(local_present),
                confidence=0.80 if local_present else 0.10,
                notes=[
                    "Loaded local JSON: " + ", ".join(local_present) if local_present else "No local optional JSON feed found."
                ],
            )
        )

        if self.config.use_public_free_sources:
            public_feeds = collect_public_optional_feeds(
                ticker,
                finra_date_yyyymmdd=self.config.finra_date_yyyymmdd,
                sec_user_agent=self.config.sec_user_agent,
            )
            optional_feeds = merge_optional_feeds(optional_feeds, public_feeds)
            for group, meta in (public_feeds.get("_meta") or {}).items():
                payload = public_feeds.get(group, {})
                verification.append(
                    VerificationResult(
                        source=f"public_free_{group}",
                        is_fresh=has_payload(payload),
                        confidence=float(meta.get("confidence", 0.0)),
                        notes=[meta.get("source", "public_free")] + list(meta.get("notes", [])),
                    )
                )

        # 6) Synthesize scores
        score = composite_score(
            indicators,
            fundamentals,
            short_ratio,
            self.config.weights,
            optional_feeds=optional_feeds,
            filings=filings,
        )

        # Three forms of analysis
        three_view = self._three_view_analysis(indicators, fundamentals, filings, score, optional_feeds)

        # 7) Forecast next day
        forecast = forecast_next_day(ticker, indicators, score)

        return AgentReport(
            ticker=ticker,
            current_price=current_price,
            verification=verification,
            indicators={
                **indicators,
                "fundamentals": fundamentals,
                "recent_filings": filings,
                "short_ratio": short_ratio,
                "optional_feeds": optional_feeds,
            },
            score=score,
            three_view_analysis=three_view,
            forecast=forecast,
        )

    @staticmethod
    def _three_view_analysis(ind: dict, fundamentals: dict, filings: list, score, optional_feeds: Optional[dict] = None) -> dict:
        optional_feeds = optional_feeds or {}
        close = ind.get("Close")
        sma50 = ind.get("SMA50")
        sma200 = ind.get("SMA200")
        rsi = ind.get("RSI14")
        volume_z = ind.get("VolumeZ")
        rel_volume = ind.get("RelativeVolume30")
        cmf = ind.get("CMF20")
        vwap_dev = ind.get("VWAPDeviationPct")
        net_margin = fundamentals.get("net_margin") if fundamentals else None
        revenue_growth = fundamentals.get("revenue_growth") if fundamentals else None

        price_fund = []
        if close and sma50:
            price_fund.append("ราคายืนเหนือ SMA50" if close > sma50 else "ราคายังต่ำกว่า SMA50")
        if close and sma200:
            price_fund.append("โครงสร้างใหญ่เหนือ SMA200" if close > sma200 else "โครงสร้างใหญ่ยังต่ำกว่า SMA200")
        if net_margin is not None:
            price_fund.append(f"net margin ล่าสุดประมาณ {net_margin:.2%}")
        if revenue_growth is not None:
            price_fund.append(f"revenue growth ประมาณ {revenue_growth:.2%}")
        if filings:
            price_fund.append(f"พบ filing ล่าสุด {len(filings)} รายการ ควรอ่าน 10-Q/8-K/S-3 ก่อนตัดสินใจ")
        if not price_fund:
            price_fund.append("ข้อมูลพื้นฐานยังไม่ครบ ให้ใช้เป็นสัญญาณรอง")

        psychology = []
        if volume_z and volume_z > 2:
            psychology.append("ตลาดมี volume spike ผิดปกติ คล้ายช่วงวาฬสะสมหรือกระจายของ")
        if rel_volume and rel_volume > 2:
            psychology.append(f"relative volume ประมาณ {rel_volume:.2f} เท่า สะท้อนความสนใจสูงกว่าปกติ")
        if rsi and rsi > 75:
            psychology.append("RSI สูงมาก อารมณ์ตลาดอาจเริ่ม FOMO และเสี่ยงพักตัว")
        elif rsi and rsi < 35:
            psychology.append("RSI ต่ำ ตลาดอาจกลัวมาก แต่ต้องรอสัญญาณกลับตัว")
        else:
            psychology.append("อารมณ์ตลาดยังไม่สุดโต่ง")
        sent = optional_feeds.get("sentiment", {})
        if sent:
            psychology.append(f"sentiment feed: news={sent.get('news_sentiment_score')}, social={sent.get('social_sentiment_score')}")

        technical = []
        if rsi:
            technical.append(f"RSI14={rsi:.2f}")
        if cmf is not None:
            technical.append("CMF เป็นบวก สื่อถึงแรงซื้อสุทธิ" if cmf > 0 else "CMF เป็นลบ สื่อถึงแรงขายสุทธิ")
        if vwap_dev is not None:
            technical.append(f"VWAP deviation={vwap_dev:.2f}%")
        technical.append(f"คะแนนรวม {score.composite}/100 = {score.label}")

        smart_money = []
        opt = optional_feeds.get("options_flow", {})
        inst = optional_feeds.get("institutional_flow", {})
        insider = optional_feeds.get("insider_flow", {})
        dark = optional_feeds.get("dark_pool", {})
        short_i = optional_feeds.get("short_interest", {})
        if opt:
            smart_money.append(f"options score={score.options_flow}; call/put={opt.get('call_put_volume_ratio')}; sweep premium={opt.get('sweep_premium_usd')}")
        else:
            smart_money.append("options flow ยังไม่มี feed เสียเงิน จึงให้คะแนนกลาง 50")
        if inst:
            smart_money.append(f"13F/institutional score={score.institutional_flow}; net change={inst.get('thirteen_f_net_shares_change_pct')}%")
        if insider:
            smart_money.append(f"insider score={score.insider_flow}; net buy={insider.get('insider_net_buy_usd')}")
        if dark:
            smart_money.append(f"dark pool score={score.dark_pool_flow}; volume ratio={dark.get('dark_pool_volume_ratio')}")
        if short_i:
            smart_money.append(f"short/squeeze score={score.short_pressure}; short float={short_i.get('short_interest_pct_float')}%")
        if not smart_money:
            smart_money.append("Smart money หลักตอนนี้อิง volume, VWAP, CMF, OBV, ADL และ short-volume รายวัน")

        return {
            "1) กราฟและพื้นฐานจากราคาปัจจุบัน": "; ".join(price_fund),
            "2) ทางจิตวิทยา": "; ".join(psychology),
            "3) ทางเทคนิค": "; ".join(technical),
            "4) วาฬ / Smart Money": "; ".join(smart_money),
        }
