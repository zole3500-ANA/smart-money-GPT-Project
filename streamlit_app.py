from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from smart_money_agent.agent import SmartMoneyAgentConfig, SmartMoneyWhaleAgent
from smart_money_agent.data_sources.market import fetch_ohlcv
from smart_money_agent.indicators import add_indicators

load_dotenv()

st.set_page_config(page_title="Smart Money Whale Agent v2", layout="wide")
st.title("🐋 Smart Money Whale Agent v2 — US Stocks")
st.caption("วิเคราะห์วาฬ / Smart Money จากราคา ปริมาณซื้อขาย VWAP CMF OBV options-flow 13F insider dark-pool short pressure และ relative strength")

with st.sidebar:
    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    period = st.selectbox("Lookback", ["3mo", "6mo", "1y", "2y"], index=1)
    finra_date = st.text_input("FINRA date YYYYMMDD (optional)", value="") or None
    optional_feed_dir = st.text_input("Optional feed directory", value="data/optional_feeds")
    use_sec = st.checkbox("Use SEC EDGAR", value=True)
    use_rs = st.checkbox("Use relative strength vs SPY/QQQ", value=True)
    run = st.button("Analyze", type="primary")

if run and ticker:
    agent = SmartMoneyWhaleAgent(
        SmartMoneyAgentConfig(
            period=period,
            finra_date_yyyymmdd=finra_date,
            use_sec=use_sec,
            use_relative_strength=use_rs,
            optional_feed_dir=optional_feed_dir,
        )
    )
    with st.spinner("Analyzing..."):
        report = agent.analyze(ticker)
        df = add_indicators(fetch_ohlcv(ticker, period=period))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current price", f"{report.current_price:.2f}" if report.current_price else "N/A")
    c2.metric("Composite", f"{report.score.composite}/100", report.score.label)
    c3.metric("Probability up", f"{report.forecast.probability_up:.1%}")
    c4.metric("Next-day bias", report.forecast.next_day_bias)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
    for col in ["SMA20", "SMA50", "SMA200", "VWAP"]:
        if col in df:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, mode="lines"))
    fig.update_layout(height=550, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Component Scores")
    score_df = pd.DataFrame([
        {"component": "Smart money flow", "score": report.score.smart_money_flow},
        {"component": "Technical trend", "score": report.score.technical_trend},
        {"component": "Options flow", "score": report.score.options_flow},
        {"component": "Short pressure/squeeze", "score": report.score.short_pressure},
        {"component": "Fundamental quality", "score": report.score.fundamental_quality},
        {"component": "Institutional/13F", "score": report.score.institutional_flow},
        {"component": "Insider flow", "score": report.score.insider_flow},
        {"component": "Dark pool/block", "score": report.score.dark_pool_flow},
        {"component": "Relative strength", "score": report.score.relative_strength},
        {"component": "Psychology/sentiment", "score": report.score.psychology},
        {"component": "Catalyst/filing risk", "score": report.score.catalyst_risk},
    ])
    st.bar_chart(score_df.set_index("component"))

    st.subheader("Three-view + Smart Money Analysis")
    for k, v in report.three_view_analysis.items():
        st.markdown(f"**{k}**  \n{v}")

    st.subheader("Key Indicators")
    key_cols = [
        "Close", "SMA20", "SMA50", "SMA200", "RSI14", "ATRPercent", "VolumeZ", "RelativeVolume30",
        "CMF20", "MFI14", "VWAPDeviationPct", "OBVTrend20", "ADLTrend20", "DistributionDayCount25",
        "AccumulationDayCount25", "RS_SPY_Return20DSpread", "RS_QQQ_Return20DSpread",
    ]
    key_data = {k: report.indicators.get(k) for k in key_cols if k in report.indicators}
    st.dataframe(pd.DataFrame([key_data]).T.rename(columns={0: "value"}), use_container_width=True)

    st.subheader("Raw JSON")
    st.json(report.model_dump())
else:
    st.info("ใส่ ticker แล้วกด Analyze")
