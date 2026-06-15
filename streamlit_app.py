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


def score_level(score: float) -> str:
    """Beginner-friendly score label."""
    if score >= 75:
        return "แข็งแรงมาก"
    if score >= 60:
        return "ค่อนข้างดี"
    if score >= 40:
        return "กลาง / รอดู"
    if score >= 20:
        return "อ่อน"
    return "อ่อนมาก"


def component_interpretation(component: str, score: float) -> str:
    """Translate each component score into plain Thai."""
    if component == "Smart money flow":
        if score >= 75:
            return "มีสัญญาณว่าเงินใหญ่หรือ Smart Money ไหลเข้าเด่นชัด"
        if score >= 60:
            return "เริ่มเห็นแรงสะสมของเงินใหญ่ แต่ยังไม่แรงมาก"
        if score >= 40:
            return "กระแสเงินยังไม่ชัดเจน อยู่ในช่วงรอดู"
        return "ยังไม่เห็นแรงสนับสนุนจาก Smart Money ชัดเจน"

    if component == "Technical trend":
        if score >= 75:
            return "แนวโน้มทางเทคนิคแข็งแรง ราคาอยู่ในโครงสร้างขาขึ้น"
        if score >= 60:
            return "แนวโน้มเทคนิคค่อนข้างดี แต่ยังต้องดูการยืนราคา"
        if score >= 40:
            return "แนวโน้มยังกลาง ๆ อาจเป็น sideway"
        return "แนวโน้มเทคนิคอ่อน มีความเสี่ยงทางลง"

    if component == "Options flow":
        if score >= 75:
            return "มีสัญญาณ options flow เชิงบวกค่อนข้างเด่น"
        if score >= 60:
            return "options flow เริ่มหนุนฝั่งบวก"
        if score >= 40:
            return "options flow ยังไม่ชัดเจน"
        return "options flow ยังไม่สนับสนุน หรือออกเชิงลบ"

    if component == "Short pressure/squeeze":
        if score >= 75:
            return "มีโอกาสเกิด short squeeze หรือแรงกดจาก short เริ่มลดลง"
        if score >= 60:
            return "แรง short ยังพอรับได้ และมีโอกาสเด้ง"
        if score >= 40:
            return "สถานะ short pressure ยังกลาง ๆ"
        return "มีแรงกดจาก short สูง หรือเสี่ยงถูกกดราคา"

    if component == "Fundamental quality":
        if score >= 75:
            return "พื้นฐานบริษัทดี รายได้/กำไร/งบดุลสนับสนุน"
        if score >= 60:
            return "พื้นฐานค่อนข้างดี ยังพอรองรับราคาได้"
        if score >= 40:
            return "พื้นฐานกลาง ๆ ยังไม่มีจุดเด่นมาก"
        return "พื้นฐานค่อนข้างอ่อน ต้องระวังความเสี่ยง"

    if component == "Institutional/13F":
        if score >= 75:
            return "สถาบันหรือกองทุนมีแนวโน้มถือครอง/สะสมเพิ่ม"
        if score >= 60:
            return "การถือครองของสถาบันเริ่มดูดี"
        if score >= 40:
            return "ยังไม่เห็นภาพสถาบันชัดเจน"
        return "ยังไม่เห็นแรงสนับสนุนจากสถาบันมากนัก"

    if component == "Insider flow":
        if score >= 75:
            return "insider flow บวก เช่น ผู้บริหารซื้อหรือไม่มีแรงขายกดดัน"
        if score >= 60:
            return "insider flow ค่อนข้างโอเค"
        if score >= 40:
            return "insider flow ยังเป็นกลาง"
        return "insider flow ไม่ค่อยหนุน หรือมีแรงขายจาก insider"

    if component == "Dark pool/block":
        if score >= 75:
            return "มี block trade / dark pool flow ที่ดูหนุนฝั่งบวก"
        if score >= 60:
            return "กระแส dark pool/block เริ่มดูดี"
        if score >= 40:
            return "ยังไม่เห็นสัญญาณชัดเจนจาก dark pool/block"
        return "dark pool/block flow ยังไม่สนับสนุน"

    if component == "Relative strength":
        if score >= 75:
            return "หุ้นแข็งกว่าตลาดหรือแข็งกว่า SPY/QQQ ชัดเจน"
        if score >= 60:
            return "หุ้นเริ่ม outperform ตลาด"
        if score >= 40:
            return "แรงเทียบตลาดยังกลาง ๆ"
        return "หุ้นอ่อนกว่าตลาดโดยรวม"

    if component == "Psychology/sentiment":
        if score >= 75:
            return "จิตวิทยาตลาดและ sentiment ค่อนข้างหนุนฝั่งบวก"
        if score >= 60:
            return "sentiment โดยรวมโอเค"
        if score >= 40:
            return "อารมณ์ตลาดยังไม่ชัด"
        return "sentiment อ่อน หรือมี fear มากกว่า confidence"

    if component == "Catalyst/filing risk":
        if score >= 75:
            return "มี catalyst เชิงบวก หรือความเสี่ยงจาก filing ต่ำ"
        if score >= 60:
            return "ภาพรวม catalyst/risk พอใช้"
        if score >= 40:
            return "ยังไม่มี catalyst เด่น หรือยังต้องติดตามข่าว"
        return "มีความเสี่ยงจาก filing/news/catalyst ที่ควรระวัง"

    return "ไม่มีคำอธิบาย"


def _to_float(value):
    """Safely convert indicator values to float."""
    try:
        if value is None:
            return None
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def _fmt_num(value, decimals=2, suffix=""):
    v = _to_float(value)
    if v is None:
        return "ไม่มีข้อมูล"
    return f"{v:,.{decimals}f}{suffix}"


def _fmt_price(value):
    return _fmt_num(value, decimals=4)


def indicator_explanation(name: str, value):
    """Beginner-friendly explanation for key indicators.

    Returns: display_name, value_display, beginner_meaning, interpretation
    """
    v = _to_float(value)

    catalog = {
        "Close": ("ราคาปิดล่าสุด", "ราคาหุ้นตอนปิดตลาดวันล่าสุด ใช้เป็นฐานในการวิเคราะห์ทั้งหมด"),
        "SMA20": ("เส้นค่าเฉลี่ย 20 วัน", "เส้นแนวโน้มระยะสั้น ประมาณ 1 เดือน"),
        "SMA50": ("เส้นค่าเฉลี่ย 50 วัน", "เส้นแนวโน้มระยะกลางที่นักลงทุนจำนวนมากใช้ดูทิศทาง"),
        "SMA200": ("เส้นค่าเฉลี่ย 200 วัน", "เส้นแนวโน้มใหญ่ ใช้ดูว่าหุ้นยังอยู่ในขาขึ้นใหญ่หรือขาลงใหญ่"),
        "RSI14": ("RSI 14 วัน", "ดัชนีวัดแรงซื้อแรงขาย ค่า 0-100 ใช้ดูว่าหุ้นร้อนแรงหรือถูกขายมากเกินไป"),
        "ATRPercent": ("ATR%", "ระดับความผันผวนของหุ้นเทียบกับราคา ยิ่งสูงยิ่งแกว่งแรง"),
        "VolumeZ": ("Volume Z-Score", "ปริมาณซื้อขายวันนี้สูงกว่าปกติมากน้อยแค่ไหน"),
        "RelativeVolume30": ("Relative Volume 30 วัน", "Volume วันนี้เทียบกับค่าเฉลี่ย 30 วัน ค่า 1 คือปกติ มากกว่า 1 คือคึกคักกว่าปกติ"),
        "CMF20": ("CMF 20 วัน", "ตัวชี้วัดเงินไหลเข้า/ออกจากหุ้น ถ้าค่าบวกแปลว่าแรงซื้อเด่นกว่า"),
        "MFI14": ("MFI 14 วัน", "RSI ที่รวม Volume เข้าไปด้วย ใช้ดูแรงซื้อแรงขายแบบมีปริมาณเงินประกอบ"),
        "VWAPDeviationPct": ("ราคาห่างจาก VWAP", "ดูว่าราคาปัจจุบันอยู่สูงหรือต่ำกว่าราคาเฉลี่ยถ่วงน้ำหนักด้วย Volume"),
        "OBVTrend20": ("แนวโน้ม OBV 20 วัน", "ดูว่า Volume สะสมกำลังไปทางซื้อหรือขาย"),
        "ADLTrend20": ("แนวโน้ม ADL 20 วัน", "ดูแรงสะสม/กระจายหุ้นจากตำแหน่งราคาปิดและ Volume"),
        "DistributionDayCount25": ("จำนวนวันขายกระจายของ 25 วัน", "นับวันที่ราคาลงพร้อม Volume สูง ใช้จับแรงขายจากรายใหญ่"),
        "AccumulationDayCount25": ("จำนวนวันสะสมของ 25 วัน", "นับวันที่ราคาขึ้นพร้อม Volume สูง ใช้จับแรงซื้อสะสม"),
        "RS_SPY_Return20DSpread": ("แรงเทียบตลาด SPY 20 วัน", "ดูว่าหุ้นตัวนี้แข็งหรืออ่อนกว่า S&P 500 ในช่วง 20 วัน"),
        "RS_QQQ_Return20DSpread": ("แรงเทียบตลาด QQQ 20 วัน", "ดูว่าหุ้นตัวนี้แข็งหรืออ่อนกว่า Nasdaq/หุ้นเทค ในช่วง 20 วัน"),
    }

    display_name, meaning = catalog.get(name, (name, "ตัวชี้วัดประกอบการวิเคราะห์"))

    if v is None:
        return display_name, "ไม่มีข้อมูล", meaning, "ยังไม่มีข้อมูลเพียงพอสำหรับแปลผล"

    # Default value display
    value_display = _fmt_num(v)

    if name == "Close":
        value_display = _fmt_price(v)
        interpretation = "เป็นราคาปิดล่าสุด ใช้เทียบกับเส้นค่าเฉลี่ยและแนวรับแนวต้าน"
    elif name in {"SMA20", "SMA50", "SMA200"}:
        value_display = _fmt_price(v)
        interpretation = "ใช้เทียบกับราคาปิด ถ้าราคาปิดอยู่เหนือเส้นนี้ มักถือว่าแนวโน้มยังดีกว่าอยู่ใต้เส้น"
    elif name == "RSI14":
        value_display = _fmt_num(v)
        if v >= 80:
            interpretation = "ร้อนแรงมาก ระวังไล่ซื้อปลายรอบหรือพักตัว"
        elif v >= 70:
            interpretation = "แรงซื้อสูง แต่เริ่มเข้าเขตร้อนแรง"
        elif v >= 55:
            interpretation = "โมเมนตัมค่อนข้างดี ฝั่งซื้อยังได้เปรียบ"
        elif v >= 45:
            interpretation = "กลาง ๆ ยังไม่มีแรงซื้อขายชัดเจน"
        elif v >= 30:
            interpretation = "ค่อนข้างอ่อน ฝั่งขายยังมีน้ำหนัก"
        else:
            interpretation = "ขายมากเกินไป อาจมีเด้งได้ แต่ยังต้องรอสัญญาณกลับตัว"
    elif name == "ATRPercent":
        value_display = _fmt_num(v, suffix="%")
        if v >= 10:
            interpretation = "ผันผวนสูงมาก เหมาะกับคนรับความเสี่ยงสูง ต้องระวังการเหวี่ยงแรง"
        elif v >= 5:
            interpretation = "ผันผวนสูง ราคาอาจขึ้นลงแรงในวันเดียว"
        elif v >= 2:
            interpretation = "ผันผวนปานกลาง อยู่ในระดับที่ติดตามได้"
        else:
            interpretation = "ผันผวนต่ำ ราคาค่อนข้างนิ่ง"
    elif name == "VolumeZ":
        value_display = _fmt_num(v)
        if v >= 5:
            interpretation = "Volume ผิดปกติมาก อาจมีข่าวหรือเงินก้อนใหญ่เข้าออก"
        elif v >= 3:
            interpretation = "Volume สูงผิดปกติ ควรดูว่าราคาปิดเขียวหรือแดงประกอบ"
        elif v >= 2:
            interpretation = "Volume เริ่มสูงกว่าปกติ มีความสนใจเพิ่มขึ้น"
        elif v >= 0:
            interpretation = "Volume ใกล้เคียงปกติ ยังไม่ผิดปกติมาก"
        else:
            interpretation = "Volume ต่ำกว่าปกติ แรงซื้อขายยังไม่เด่น"
    elif name == "RelativeVolume30":
        value_display = _fmt_num(v, suffix="x")
        if v >= 3:
            interpretation = "ซื้อขายคึกคักมากกว่าปกติหลายเท่า อาจมีแรงเงินใหญ่หรือข่าวสำคัญ"
        elif v >= 1.5:
            interpretation = "Volume สูงกว่าปกติชัดเจน ตลาดเริ่มให้ความสนใจ"
        elif v >= 0.8:
            interpretation = "Volume ปกติ"
        else:
            interpretation = "Volume เบากว่าปกติ สัญญาณยังไม่น่าเชื่อถือมาก"
    elif name == "CMF20":
        value_display = _fmt_num(v)
        if v >= 0.20:
            interpretation = "เงินไหลเข้าเด่นชัด ฝั่งซื้อคุมเกม"
        elif v >= 0.05:
            interpretation = "เงินไหลเข้าเล็กน้อยถึงปานกลาง"
        elif v > -0.05:
            interpretation = "เงินไหลเข้าออกยังสมดุล"
        elif v > -0.20:
            interpretation = "เริ่มมีเงินไหลออก ต้องระวังแรงขาย"
        else:
            interpretation = "เงินไหลออกชัดเจน ฝั่งขายมีน้ำหนัก"
    elif name == "MFI14":
        value_display = _fmt_num(v)
        if v >= 80:
            interpretation = "เงินไหลเข้ามากจนเริ่มร้อนแรง ระวังพักตัว"
        elif v >= 60:
            interpretation = "แรงซื้อพร้อม Volume อยู่ในเกณฑ์ดี"
        elif v >= 40:
            interpretation = "แรงซื้อขายยังกลาง ๆ"
        elif v >= 20:
            interpretation = "แรงขายมีน้ำหนัก"
        else:
            interpretation = "ถูกขายมาก อาจมีเด้งทางเทคนิคได้แต่ยังเสี่ยง"
    elif name == "VWAPDeviationPct":
        value_display = _fmt_num(v, suffix="%")
        if v >= 5:
            interpretation = "ราคาสูงกว่า VWAP มาก อาจแข็งแรง แต่เสี่ยงย่อถ้าไล่ซื้อสูง"
        elif v >= 1:
            interpretation = "ราคาอยู่เหนือ VWAP ฝั่งซื้อได้เปรียบ"
        elif v > -1:
            interpretation = "ราคาใกล้ VWAP ตลาดยังสมดุล"
        elif v > -5:
            interpretation = "ราคาอยู่ต่ำกว่า VWAP ฝั่งขายเริ่มได้เปรียบ"
        else:
            interpretation = "ราคาต่ำกว่า VWAP มาก ระวังแรงขายหรือความอ่อนแอ"
    elif name in {"OBVTrend20", "ADLTrend20"}:
        value_display = _fmt_num(v)
        if v > 0:
            interpretation = "แนวโน้มเป็นบวก สะท้อนการสะสม/แรงซื้อโดยรวม"
        elif v < 0:
            interpretation = "แนวโน้มเป็นลบ สะท้อนการขายออกหรือกระจายของ"
        else:
            interpretation = "ยังไม่เห็นทิศทางสะสมหรือขายออกชัดเจน"
    elif name == "DistributionDayCount25":
        value_display = _fmt_num(v, decimals=0, suffix=" วัน")
        if v >= 6:
            interpretation = "มีวันขายกระจายของหลายวัน เสี่ยงถูกกดดันจากแรงขายใหญ่"
        elif v >= 3:
            interpretation = "มีแรงขายให้ระวัง แต่ยังไม่รุนแรงมาก"
        else:
            interpretation = "แรงขายกระจายของยังไม่มาก"
    elif name == "AccumulationDayCount25":
        value_display = _fmt_num(v, decimals=0, suffix=" วัน")
        if v >= 6:
            interpretation = "มีวันสะสมหลายวัน เป็นสัญญาณบวกจากแรงซื้อ"
        elif v >= 3:
            interpretation = "เริ่มมีร่องรอยการสะสม"
        else:
            interpretation = "ยังไม่เห็นการสะสมเด่นชัด"
    elif name in {"RS_SPY_Return20DSpread", "RS_QQQ_Return20DSpread"}:
        value_display = _fmt_num(v, suffix="%")
        if v >= 10:
            interpretation = "หุ้นแข็งกว่าตลาดมาก เป็นสัญญาณ relative strength ที่ดี"
        elif v >= 3:
            interpretation = "หุ้นแข็งกว่าตลาด"
        elif v > -3:
            interpretation = "เคลื่อนไหวใกล้เคียงตลาด"
        elif v > -10:
            interpretation = "หุ้นอ่อนกว่าตลาด"
        else:
            interpretation = "หุ้นอ่อนกว่าตลาดมาก ต้องระวัง"
    else:
        interpretation = "ใช้ประกอบการตัดสินใจร่วมกับหมวดคะแนนและกราฟราคา"

    return display_name, value_display, meaning, interpretation


st.set_page_config(page_title="Smart Money Whale Agent v2", layout="wide")
st.title("🐋 Smart Money Whale Agent v2 — US Stocks")
st.caption("วิเคราะห์วาฬ / Smart Money จากราคา ปริมาณซื้อขาย VWAP CMF OBV options-flow 13F insider dark-pool short pressure และ relative strength")

with st.sidebar:
    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    period = st.selectbox("Lookback", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    finra_date = st.text_input("FINRA date YYYYMMDD (optional)", value="") or None
    optional_feed_dir = st.text_input("Optional feed directory", value="data/optional_feeds")
    use_sec = st.checkbox("Use SEC EDGAR", value=False)
    use_rs = st.checkbox("Use relative strength vs SPY/QQQ", value=True)
    run = st.button("Analyze", type="primary")

st.info(
    "เริ่มทดสอบด้วย AAPL, NVDA, TSLA, PLTR หรือ IREN ก่อน หากหุ้นเล็กบางตัวไม่มีข้อมูลจาก yfinance "
    "ระบบจะพยายามใช้ Stooq fallback และจะแจ้งเตือนแทนการ crash"
)

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

    try:
        with st.spinner("Analyzing..."):
            report = agent.analyze(ticker)
            raw_df = fetch_ohlcv(ticker, period=period)
            if raw_df.empty:
                st.error(f"ไม่พบข้อมูลราคา OHLCV สำหรับ {ticker}")
                st.warning(
                    "ให้ลองเปลี่ยน Lookback เป็น 1mo/3mo, ตรวจ ticker ให้ตรงตลาด, "
                    "หรือเพิ่ม POLYGON_API_KEY ใน Streamlit Secrets เพื่อใช้ provider ที่เสถียรกว่า"
                )
                st.stop()
            df = add_indicators(raw_df)
    except RuntimeError as exc:
        st.error(str(exc))
        st.warning(
            "สาเหตุที่พบบ่อย: ticker ไม่มีข้อมูลใน yfinance/แหล่งฟรีชั่วคราว, ticker ไม่ตรงตลาด, "
            "หรือหุ้นเล็ก/เพนนีบางตัวไม่มี historical OHLCV จาก provider ฟรีบน Streamlit Cloud"
        )
        st.markdown(
            """
**วิธีแก้เร็ว**
1. ลองใส่ `AAPL` หรือ `NVDA` เพื่อเช็กว่าแอปรันปกติ  
2. ถ้าต้องการวิเคราะห์ `BURU` ให้ลอง `BURU` ตัวพิมพ์ใหญ่ และเลือก Lookback `1mo` หรือ `3mo`  
3. ปิด `Use SEC EDGAR` ก่อนในช่วงทดสอบ  
4. ถ้ายังไม่ขึ้น ให้ใส่ `POLYGON_API_KEY` ใน Streamlit Secrets เพื่อใช้ข้อมูลราคาที่เสถียรกว่า
            """
        )
        st.stop()
    except Exception as exc:
        st.error("เกิดข้อผิดพลาดระหว่างวิเคราะห์")
        st.exception(exc)
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current price", f"{report.current_price:.4f}" if report.current_price else "N/A")
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

    st.subheader("คำแปลผลคะแนนรายหมวด")
    interpret_rows = []
    for _, row in score_df.iterrows():
        component = row["component"]
        score = float(row["score"])
        interpret_rows.append({
            "หมวด": component,
            "คะแนน": round(score, 2),
            "ระดับ": score_level(score),
            "คำแปลความหมาย": component_interpretation(component, score),
        })

    interpret_df = pd.DataFrame(interpret_rows)
    st.dataframe(interpret_df, use_container_width=True, hide_index=True)

    strong_points = interpret_df[interpret_df["คะแนน"] >= 60]["หมวด"].tolist()
    weak_points = interpret_df[interpret_df["คะแนน"] < 40]["หมวด"].tolist()

    c_strength, c_risk = st.columns(2)
    with c_strength:
        if strong_points:
            st.success("จุดแข็ง: " + ", ".join(strong_points))
        else:
            st.info("ยังไม่มีหมวดที่เด่นมากเป็นพิเศษ")
    with c_risk:
        if weak_points:
            st.warning("จุดที่ต้องระวัง: " + ", ".join(weak_points))
        else:
            st.success("ยังไม่มีหมวดที่อ่อนมากอย่างชัดเจน")

    st.subheader("Three-view + Smart Money Analysis")
    for k, v in report.three_view_analysis.items():
        st.markdown(f"**{k}**  \n{v}")

    st.subheader("Key Indicators — แปลผลให้อ่านง่าย")

    st.caption(
        "ตารางนี้แปลค่าตัวเลขเป็นภาษาง่าย ๆ สำหรับมือใหม่ เพื่อให้รู้ว่าแต่ละ indicator กำลังบอกอะไร "
        "ควรอ่านร่วมกับกราฟราคาและ Component Scores ไม่ควรใช้ indicator ตัวเดียวตัดสินใจ"
    )

    key_cols = [
        "Close", "SMA20", "SMA50", "SMA200", "RSI14", "ATRPercent", "VolumeZ", "RelativeVolume30",
        "CMF20", "MFI14", "VWAPDeviationPct", "OBVTrend20", "ADLTrend20", "DistributionDayCount25",
        "AccumulationDayCount25", "RS_SPY_Return20DSpread", "RS_QQQ_Return20DSpread",
    ]

    indicator_rows = []
    for key in key_cols:
        raw_value = report.indicators.get(key)
        display_name, value_display, beginner_meaning, interpretation = indicator_explanation(key, raw_value)
        indicator_rows.append({
            "Indicator": display_name,
            "ค่า": value_display,
            "คืออะไร": beginner_meaning,
            "แปลผลตอนนี้": interpretation,
        })

    indicator_df = pd.DataFrame(indicator_rows)
    st.dataframe(indicator_df, use_container_width=True, hide_index=True)

    st.subheader("สรุป Key Indicators แบบภาษาคนเริ่มต้น")
    simple_notes = []

    rsi = _to_float(report.indicators.get("RSI14"))
    cmf = _to_float(report.indicators.get("CMF20"))
    rv = _to_float(report.indicators.get("RelativeVolume30"))
    vwap_dev = _to_float(report.indicators.get("VWAPDeviationPct"))
    atrp = _to_float(report.indicators.get("ATRPercent"))
    dist_days = _to_float(report.indicators.get("DistributionDayCount25"))
    acc_days = _to_float(report.indicators.get("AccumulationDayCount25"))
    rs_spy = _to_float(report.indicators.get("RS_SPY_Return20DSpread"))

    if rsi is not None:
        if rsi >= 70:
            simple_notes.append("RSI สูง: หุ้นกำลังร้อนแรง ควรระวังการไล่ซื้อ")
        elif rsi <= 30:
            simple_notes.append("RSI ต่ำ: หุ้นถูกขายมาก อาจมีเด้งได้ แต่ยังต้องรอสัญญาณกลับตัว")
        else:
            simple_notes.append("RSI ยังไม่สุดโต่ง: แรงซื้อขายยังไม่เกินไปทางใดทางหนึ่งมาก")

    if cmf is not None:
        if cmf > 0.05:
            simple_notes.append("CMF เป็นบวก: มีภาพเงินไหลเข้า")
        elif cmf < -0.05:
            simple_notes.append("CMF เป็นลบ: มีภาพเงินไหลออก")
        else:
            simple_notes.append("CMF ใกล้ศูนย์: เงินไหลเข้าออกยังไม่ชัด")

    if rv is not None:
        if rv >= 1.5:
            simple_notes.append("Volume สูงกว่าปกติ: ตลาดกำลังให้ความสนใจหุ้นตัวนี้")
        elif rv < 0.8:
            simple_notes.append("Volume เบา: สัญญาณจากราคายังไม่น่าเชื่อถือมาก")
        else:
            simple_notes.append("Volume ปกติ: ยังไม่มีความผิดปกติด้านปริมาณซื้อขาย")

    if vwap_dev is not None:
        if vwap_dev > 1:
            simple_notes.append("ราคาอยู่เหนือ VWAP: ฝั่งซื้อได้เปรียบระหว่างวัน/ช่วงล่าสุด")
        elif vwap_dev < -1:
            simple_notes.append("ราคาอยู่ต่ำกว่า VWAP: ฝั่งขายยังได้เปรียบ")
        else:
            simple_notes.append("ราคาใกล้ VWAP: ตลาดยังสมดุล")

    if atrp is not None:
        if atrp >= 5:
            simple_notes.append("ATR% สูง: หุ้นแกว่งแรง ต้องวางแผนความเสี่ยงให้ดี")
        else:
            simple_notes.append("ATR% ไม่สูงมาก: ความผันผวนยังอยู่ในระดับที่พอควบคุมได้")

    if acc_days is not None and dist_days is not None:
        if acc_days > dist_days:
            simple_notes.append("วันสะสมมากกว่าวันขาย: เริ่มมีภาพการเก็บของมากกว่ากระจายของ")
        elif dist_days > acc_days:
            simple_notes.append("วันขายมากกว่าวันสะสม: ต้องระวังแรงขายจากรายใหญ่")
        else:
            simple_notes.append("วันสะสมและวันขายใกล้กัน: ภาพเงินใหญ่ยังไม่ชัดเจน")

    if rs_spy is not None:
        if rs_spy > 3:
            simple_notes.append("หุ้นแข็งกว่า SPY: ถือว่า outperform ตลาดในช่วงสั้น")
        elif rs_spy < -3:
            simple_notes.append("หุ้นอ่อนกว่า SPY: ยังแพ้ตลาดโดยรวม")
        else:
            simple_notes.append("หุ้นเคลื่อนไหวใกล้เคียงตลาด")

    if simple_notes:
        for note in simple_notes:
            st.markdown(f"- {note}")
    else:
        st.info("ยังไม่มีข้อมูล Key Indicators เพียงพอสำหรับสรุปแบบภาษาง่าย")

    st.subheader("Raw JSON")
    st.json(report.model_dump())
else:
    st.info("ใส่ ticker แล้วกด Analyze")
