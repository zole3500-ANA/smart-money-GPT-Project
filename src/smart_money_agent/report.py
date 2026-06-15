from __future__ import annotations

import json
from pathlib import Path

from .schemas import AgentReport


def _fmt(value, digits: int = 2):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def to_markdown(report: AgentReport) -> str:
    ind = report.indicators
    score = report.score
    lines = [
        f"# Smart Money Whale Agent Report: {report.ticker}",
        "",
        "> Research-only output. This is not financial advice and should be validated with the original data sources before trading.",
        "",
        "## Executive Signal",
        f"- Current price: {report.current_price}",
        f"- Composite score: **{score.composite}/100** ({score.label})",
        f"- Next-day bias: **{report.forecast.next_day_bias}**",
        f"- Probability up: **{report.forecast.probability_up:.1%}**",
        f"- Expected range: {report.forecast.expected_range_low} - {report.forecast.expected_range_high}",
        "",
        "## Component Scores",
        f"- Smart money flow: {score.smart_money_flow}",
        f"- Technical trend: {score.technical_trend}",
        f"- Options flow: {score.options_flow}",
        f"- Short pressure / squeeze: {score.short_pressure}",
        f"- Fundamental quality: {score.fundamental_quality}",
        f"- Institutional / 13F flow: {score.institutional_flow}",
        f"- Insider flow: {score.insider_flow}",
        f"- Dark pool / block flow: {score.dark_pool_flow}",
        f"- Relative strength: {score.relative_strength}",
        f"- Psychology / sentiment: {score.psychology}",
        f"- Catalyst / filing risk: {score.catalyst_risk}",
        "",
        "## Key Indicators",
        f"- RSI14: {_fmt(ind.get('RSI14'))}",
        f"- MACD histogram: {_fmt(ind.get('macd_hist'))}",
        f"- ATR%: {_fmt(ind.get('ATRPercent'))}%",
        f"- Relative volume 30D: {_fmt(ind.get('RelativeVolume30'))}x",
        f"- Volume Z-score: {_fmt(ind.get('VolumeZ'))}",
        f"- CMF20: {_fmt(ind.get('CMF20'), 4)}",
        f"- MFI14: {_fmt(ind.get('MFI14'))}",
        f"- VWAP deviation: {_fmt(ind.get('VWAPDeviationPct'))}%",
        f"- OBV trend 20D: {_fmt(ind.get('OBVTrend20'))}",
        f"- ADL trend 20D: {_fmt(ind.get('ADLTrend20'))}",
        f"- Distribution days 25D: {_fmt(ind.get('DistributionDayCount25'), 0)}",
        f"- Accumulation days 25D: {_fmt(ind.get('AccumulationDayCount25'), 0)}",
        f"- RS vs SPY 20D spread: {_fmt(ind.get('RS_SPY_Return20DSpread'))}%",
        f"- RS vs QQQ 20D spread: {_fmt(ind.get('RS_QQQ_Return20DSpread'))}%",
        "",
        "## Optional Feed Status",
    ]
    optional = ind.get("optional_feeds", {}) or {}
    for key, payload in optional.items():
        lines.append(f"- {key}: {'loaded' if payload else 'not loaded / neutral default'}")
    lines += ["", "## Three-view Analysis"]
    for title, body in report.three_view_analysis.items():
        lines += [f"### {title}", body, ""]
    if report.forecast.risk_notes:
        lines += ["## Risk Notes"]
        lines += [f"- {x}" for x in report.forecast.risk_notes]
        lines += [""]
    lines += ["## Verification"]
    for item in report.verification:
        lines += [f"- {item.source}: confidence={item.confidence}, fresh={item.is_fresh}, notes={'; '.join(item.notes)}"]
    return "\n".join(lines)


def save_report(report: AgentReport, output_dir: str = "outputs") -> tuple[Path, Path]:
    path = Path(output_dir)
    path.mkdir(exist_ok=True)
    md_path = path / f"{report.ticker}_report.md"
    json_path = path / f"{report.ticker}_signal.json"
    md_path.write_text(to_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")
    return md_path, json_path
