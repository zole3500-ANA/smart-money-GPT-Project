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


def sentiment_status_from_text(text: str) -> tuple[str, str]:
    """Return Thai status label and emoji based on interpretation text."""
    if text is None:
        return "กลาง", "🟡"

    t = str(text).lower()

    negative_words = [
        "ลบ", "ขาย", "อ่อน", "เสี่ยง", "ระวัง", "กดดัน", "fear", "bearish",
        "ต่ำกว่า", "ไม่สนับสนุน", "ลด", "เงินออก", "seller", "bid", "put สูง",
        "ขายสุทธิ", "ขายหมด", "กระจาย", "แพ้ตลาด", "downside", "ลงแรง"
    ]
    positive_words = [
        "บวก", "ซื้อ", "แข็ง", "ดี", "สะสม", "เงินเข้า", "bullish", "หนุน",
        "เหนือ", "ได้เปรียบ", "outperform", "buy", "ask", "call สูง", "ซื้อสุทธิ",
        "open market buy", "cluster buying", "สัญญาณบวก", "วาฬเร่งเข้า"
    ]
    neutral_words = [
        "กลาง", "สมดุล", "ไม่ชัด", "รอดู", "ไม่มีข้อมูล", "ใกล้ศูนย์",
        "ยังไม่พบ", "ยังไม่มี", "ปกติ", "ต้องดู", "ติดตาม", "อาจไม่ใช่ลบเสมอ"
    ]

    neg = any(w in t for w in negative_words)
    pos = any(w in t for w in positive_words)
    neu = any(w in t for w in neutral_words)

    # If both positive and negative words appear, prefer neutral unless the text has strong explicit direction.
    if pos and not neg:
        return "บวก", "🟢"
    if neg and not pos:
        return "ลบ", "🔴"
    if pos and neg:
        if "สัญญาณบวก" in t or "bullish" in t or "ซื้อสุทธิ" in t:
            return "บวก", "🟢"
        if "สัญญาณลบ" in t or "bearish" in t or "ขายสุทธิ" in t:
            return "ลบ", "🔴"
        return "กลาง", "🟡"
    return "กลาง", "🟡"


def add_status_columns(df: pd.DataFrame, interpretation_col: str | None = None) -> pd.DataFrame:
    """Add emoji/status columns to a table."""
    if df is None or df.empty:
        return df

    out = df.copy()
    if interpretation_col is None:
        for candidate in ["การตีความ", "สำคัญอย่างไร / การตีความ", "ใช้วิเคราะห์ / การตีความ", "แปลผลตอนนี้", "คำแปลความหมาย"]:
            if candidate in out.columns:
                interpretation_col = candidate
                break

    if interpretation_col and interpretation_col in out.columns:
        statuses = out[interpretation_col].apply(sentiment_status_from_text)
        out.insert(0, "สัญญาณ", [emoji for _, emoji in statuses])
        out.insert(1, "สถานะ", [label for label, _ in statuses])
    return out



def style_status_table(df: pd.DataFrame):
    """Deprecated in v2.7: keep for compatibility."""
    return df


def render_status_html_table(df: pd.DataFrame) -> str:
    """Render a readable wrapped HTML table with dark text and row colors."""
    if df is None or df.empty:
        return "<div style='padding:0.75rem;border:1px solid #e5e7eb;border-radius:12px;background:#ffffff;color:#111827;'>ไม่มีข้อมูล</div>"

    columns = list(df.columns)
    # Column width hints
    width_map = {
        "สัญญาณ": "56px",
        "สถานะ": "72px",
        "Indicator": "18%",
        "ค่า": "9%",
        "ความหมาย": "23%",
        "การตีความ": "28%",
        "สำคัญอย่างไร / การตีความ": "28%",
        "ใช้วิเคราะห์ / การตีความ": "28%",
        "แปลผลตอนนี้": "24%",
        "คำแปลความหมาย": "26%",
    }

    def row_colors(status: str):
        status = str(status)
        if status == "บวก":
            return ("#ecfdf5", "#065f46", "#a7f3d0")
        if status == "ลบ":
            return ("#fef2f2", "#991b1b", "#fecaca")
        return ("#fffbeb", "#92400e", "#fde68a")

    html = []
    html.append("""
    <style>
    .sm-wrap-table-wrap {width:100%; overflow-x:hidden; margin:0.35rem 0 1rem 0;}
    .sm-wrap-table {width:100%; border-collapse:separate; border-spacing:0; table-layout:fixed; font-size:14px; color:#111827; background:#ffffff; border:1px solid #e5e7eb; border-radius:14px; overflow:hidden;}
    .sm-wrap-table thead th {background:#f8fafc; color:#334155; font-weight:700; text-align:left; padding:10px 10px; border-bottom:1px solid #e5e7eb; white-space:normal; word-break:break-word;}
    .sm-wrap-table tbody td {padding:10px 10px; vertical-align:top; border-bottom:1px solid #e5e7eb; white-space:normal; overflow-wrap:anywhere; word-break:break-word; line-height:1.35;}
    .sm-wrap-table tbody tr:last-child td {border-bottom:none;}
    .sm-wrap-table .sm-center {text-align:center;}
    .sm-wrap-table .sm-badge {display:inline-block; padding:2px 8px; border-radius:999px; font-weight:700; font-size:12px;}
    @media (max-width: 900px) {
      .sm-wrap-table {font-size:13px;}
      .sm-wrap-table thead th, .sm-wrap-table tbody td {padding:8px 8px;}
    }
    </style>
    """)
    html.append("<div class='sm-wrap-table-wrap'><table class='sm-wrap-table'>")
    html.append("<thead><tr>")
    for col in columns:
        w = width_map.get(col, "auto")
        align = " sm-center" if col in {"สัญญาณ", "สถานะ", "ค่า"} else ""
        html.append(f"<th class='{align.strip()}' style='width:{w};'>{col}</th>")
    html.append("</tr></thead><tbody>")

    for _, row in df.iterrows():
        status = row.get("สถานะ", "กลาง")
        bg, text_color, border = row_colors(status)
        html.append(f"<tr style='background:{bg}; color:{text_color};'>")
        for col in columns:
            val = "" if pd.isna(row[col]) else str(row[col])
            align = "sm-center" if col in {"สัญญาณ", "สถานะ", "ค่า"} else ""
            if col == "สถานะ":
                badge_bg = "#d1fae5" if status == "บวก" else ("#fee2e2" if status == "ลบ" else "#fef3c7")
                badge_color = "#065f46" if status == "บวก" else ("#991b1b" if status == "ลบ" else "#92400e")
                val = f"<span class='sm-badge' style='background:{badge_bg}; color:{badge_color}; border:1px solid {border};'>{val}</span>"
            html.append(f"<td class='{align}'>{val}</td>")
        html.append("</tr>")

    html.append("</tbody></table></div>")
    return "".join(html)


def show_status_dataframe(df: pd.DataFrame, interpretation_col: str | None = None):
    """Display readable wrapped table with status icon and color."""
    status_df = add_status_columns(df, interpretation_col=interpretation_col)
    st.markdown(render_status_html_table(status_df), unsafe_allow_html=True)


def status_legend():
    st.markdown(
        "<div style='margin:0.2rem 0 0.8rem 0; font-size:0.95rem; color:#374151;'>"
        "<strong>สัญลักษณ์:</strong> "
        "<span style='color:#15803d; font-weight:700;'>🟢 บวก / น่าสนใจ</span> &nbsp;|&nbsp; "
        "<span style='color:#a16207; font-weight:700;'>🟡 กลาง ๆ / รอดู</span> &nbsp;|&nbsp; "
        "<span style='color:#dc2626; font-weight:700;'>🔴 ลบ / ต้องระวัง</span>"
        "</div>",
        unsafe_allow_html=True,
    )


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
            return "options flow เชิงบวกเด่น เช่น call/put สูง, sweep ที่ ask, premium ฝั่ง bullish หรือ OTM call เด่น"
        if score >= 60:
            return "options flow เริ่มหนุนฝั่งบวก"
        if score >= 40:
            return "options flow ยังไม่ชัดเจน"
        return "options flow ยังไม่สนับสนุน หรือเอน bearish เช่น put/call สูง, ขายที่ bid หรือ premium ฝั่ง put เด่น"

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
            return "สถาบัน/กองทุนสะสมชัด มี net flow, new positions หรือ QoQ change เป็นบวก"
        if score >= 60:
            return "การถือครองของสถาบันเริ่มดูดี มีแรงสนับสนุนระดับหนึ่ง"
        if score >= 40:
            return "ภาพสถาบันยังกลาง ๆ ต้องดูว่าซื้อเพิ่มหรือลดพอร์ตมากกว่ากัน"
        return "ยังไม่เห็นแรงสนับสนุนจากสถาบัน หรือมีการลดพอร์ต/ขายหมดเด่น"

    if component == "Insider flow":
        if score >= 75:
            return "insider flow บวก เช่น ผู้บริหารซื้อสุทธิ มี cluster buying หรือ direct open market buy"
        if score >= 60:
            return "insider flow ค่อนข้างโอเค"
        if score >= 40:
            return "insider flow ยังเป็นกลาง"
        return "insider flow ไม่ค่อยหนุน หรือมีแรงขายจาก insider/CEO-CFO ที่ควรตรวจเหตุผล"

    if component == "Dark pool/block":
        if score >= 75:
            return "dark pool/off-exchange หนุนฝั่งบวกชัด เช่น block เหนือ VWAP หรือ buy bias เด่น"
        if score >= 60:
            return "dark pool/off-exchange เริ่มดูดี มีร่องรอย block หรือ buy bias"
        if score >= 40:
            return "มี activity นอกกระดานแต่ bias ยังไม่ชัด ต้องดู ratio, VWAP และ net bias"
        return "dark pool/off-exchange ออกเชิงลบหรือยังไม่สนับสนุน"

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
        "MFI14": ("Money Flow Index 14 วัน", "RSI แบบรวม Volume เข้าไปด้วย ใช้เห็นแรงซื้อขายพร้อมปริมาณเงิน"),
        "VWAPDeviationPct": ("ราคาห่างจาก VWAP", "ดูว่าราคาปัจจุบันอยู่สูงหรือต่ำกว่าราคาเฉลี่ยถ่วงน้ำหนักด้วย Volume"),
        "OBVTrend20": ("แนวโน้ม OBV 20 วัน", "ดูว่า Volume สะสมกำลังไปทางซื้อหรือขาย"),
        "ADL": ("Accumulation/Distribution Line", "เส้นเงินสะสมหรือเงินไหลออก ใช้จับ divergence ระหว่างราคาและปริมาณเงิน"),
        "ADLTrend20": ("แนวโน้ม ADL 20 วัน", "ดูแรงสะสม/กระจายหุ้นจากตำแหน่งราคาปิดและ Volume"),
        "ADLPriceDivergence20": ("ADL Divergence 20 วัน", "ดูว่าราคาและ ADL สวนทางกันหรือไม่ ถ้าราคาลงแต่ ADL ขึ้นอาจมีการสะสมเงียบ"),
        "VPT": ("Volume Price Trend", "ดูว่า Volume สนับสนุนการขึ้นลงของราคาหรือไม่ คล้าย OBV แต่ละเอียดกว่า"),
        "VPTTrend20": ("แนวโน้ม VPT 20 วัน", "วัดว่า Volume ที่ถ่วงด้วยการเปลี่ยนแปลงราคากำลังหนุนขึ้นหรือลง"),
        "VPTPriceDivergence20": ("VPT Divergence 20 วัน", "จับสัญญาณราคาและ VPT สวนทางกัน"),
        "EaseOfMovement14": ("Ease of Movement 14 วัน", "ดูว่าราคาขึ้นง่ายหรือลงง่ายเมื่อเทียบกับ Volume"),
        "EaseOfMovementTrend5": ("แนวโน้ม Ease of Movement", "ดูทิศทางล่าสุดของการขยับราคาว่าเริ่มง่ายขึ้นหรือยากขึ้น"),
        "CloseLocationValue": ("Close Location Value", "ดูว่าราคาปิดใกล้ High หรือ Low ของวัน ปิดใกล้ High แปลว่าผู้ซื้อคุมเกมมากกว่า"),
        "UpDownVolumeRatio20": ("Up/Down Volume Ratio 20 วัน", "Volume วันขึ้นเทียบกับ Volume วันลง ใช้ดูเงินเข้าออก"),
        "PocketPivotProxy": ("Pocket Pivot Signal", "สัญญาณ Volume เข้าในจังหวะราคาดี เป็น proxy ของการสะสมจากสถาบัน"),
        "PocketPivotCount20": ("จำนวน Pocket Pivot 20 วัน", "จำนวนครั้งที่เกิด Pocket Pivot ในช่วง 20 วัน"),
        "DistributionDayFlag": ("Distribution Day ล่าสุด", "วันลงแรงพร้อม Volume สูง ใช้จับแรงขายจากกองทุน"),
        "DistributionDayCount25": ("Distribution Day Count 25 วัน", "จำนวนวันลงแรงพร้อม Volume สูง ใช้จับกองทุนขาย"),
        "AccumulationDayFlag": ("Accumulation Day ล่าสุด", "วันขึ้นแรงพร้อม Volume สูง ใช้จับแรงซื้อสะสม"),
        "AccumulationDayCount25": ("Accumulation Day Count 25 วัน", "จำนวนวันขึ้นแรงพร้อม Volume สูง ใช้จับแรงซื้อสะสม"),
        "NetAccumulationDays25": ("Net Accumulation Days 25 วัน", "จำนวนวันสะสมลบจำนวนวันกระจายของ ค่าบวกแปลว่าแรงสะสมมากกว่า"),
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
    elif name in {"ADL", "VPT"}:
        value_display = _fmt_num(v, decimals=0)
        interpretation = "ดูทิศทางและ divergence ร่วมกับแนวโน้ม 20 วัน ไม่เน้นดูค่าดิบเดี่ยว ๆ"
    elif name in {"ADLPriceDivergence20", "VPTPriceDivergence20"}:
        value_display = _fmt_num(v, decimals=0)
        if v > 0:
            interpretation = "Bullish divergence: ราคาอ่อนแต่เส้นสะสมยังดี อาจมีการเก็บของเงียบ"
        elif v < 0:
            interpretation = "Bearish divergence: ราคาดูดีแต่เงินสะสมไม่ตาม ระวังขึ้นหลอก"
        else:
            interpretation = "ยังไม่พบ divergence ชัดเจน"
    elif name == "EaseOfMovement14":
        value_display = _fmt_num(v)
        if v > 0:
            interpretation = "ราคาขยับขึ้นได้ค่อนข้างง่ายเมื่อเทียบกับ Volume เป็นบวกต่อฝั่งซื้อ"
        elif v < 0:
            interpretation = "ราคาขยับลงง่ายกว่า หรือมีแรงต้านต่อการขึ้น"
        else:
            interpretation = "การเคลื่อนที่ของราคายังไม่ชัด"
    elif name == "CloseLocationValue":
        value_display = _fmt_num(v)
        if v >= 0.5:
            interpretation = "ปิดใกล้ High ของวัน ผู้ซื้อคุมเกมชัดเจน"
        elif v >= 0.1:
            interpretation = "ปิดค่อนข้างสูงในกรอบวัน ฝั่งซื้อได้เปรียบ"
        elif v > -0.1:
            interpretation = "ปิดกลางกรอบวัน ตลาดยังสมดุล"
        elif v > -0.5:
            interpretation = "ปิดค่อนข้างต่ำในกรอบวัน ฝั่งขายได้เปรียบ"
        else:
            interpretation = "ปิดใกล้ Low ของวัน ผู้ขายคุมเกมชัดเจน"
    elif name == "UpDownVolumeRatio20":
        value_display = _fmt_num(v, suffix="x")
        if v >= 1.5:
            interpretation = "Volume วันขึ้นมากกว่าวันลงชัดเจน สะท้อนเงินเข้า"
        elif v >= 1.05:
            interpretation = "Volume ฝั่งขึ้นมากกว่าฝั่งลงเล็กน้อย"
        elif v > 0.95:
            interpretation = "Volume วันขึ้นและวันลงใกล้เคียงกัน"
        elif v > 0.67:
            interpretation = "Volume วันลงเริ่มมากกว่า ต้องระวังแรงขาย"
        else:
            interpretation = "Volume วันลงมากกว่าวันขึ้นชัดเจน สะท้อนเงินออก"
    elif name in {"PocketPivotProxy", "DistributionDayFlag", "AccumulationDayFlag"}:
        value_display = "เกิดสัญญาณ" if v >= 1 else "ไม่เกิด"
        if name == "PocketPivotProxy":
            interpretation = "เกิด Pocket Pivot วันนี้ เป็นสัญญาณบวกเชิงสถาบัน" if v >= 1 else "วันนี้ยังไม่เกิด Pocket Pivot"
        elif name == "DistributionDayFlag":
            interpretation = "วันนี้เป็นวันขายกระจายของ ต้องระวัง" if v >= 1 else "วันนี้ยังไม่ใช่วันขายกระจายของ"
        else:
            interpretation = "วันนี้เป็นวันสะสม มีแรงซื้อพร้อม Volume" if v >= 1 else "วันนี้ยังไม่ใช่วันสะสม"
    elif name == "PocketPivotCount20":
        value_display = _fmt_num(v, decimals=0, suffix=" ครั้ง")
        if v >= 4:
            interpretation = "เกิด Pocket Pivot หลายครั้งใน 20 วัน เป็นสัญญาณสะสมที่น่าสนใจ"
        elif v >= 1:
            interpretation = "มี Pocket Pivot บ้าง เริ่มมีร่องรอยแรงซื้อคุณภาพ"
        else:
            interpretation = "ยังไม่พบ Pocket Pivot ในช่วงล่าสุด"
    elif name == "NetAccumulationDays25":
        value_display = _fmt_num(v, decimals=0, suffix=" วัน")
        if v >= 3:
            interpretation = "วันสะสมมากกว่าวันกระจายของชัดเจน ภาพเงินใหญ่เป็นบวก"
        elif v > 0:
            interpretation = "วันสะสมมากกว่าวันขายเล็กน้อย"
        elif v == 0:
            interpretation = "วันสะสมและวันขายสมดุลกัน"
        elif v > -3:
            interpretation = "วันขายมากกว่าวันสะสมเล็กน้อย"
        else:
            interpretation = "วันขายมากกว่าวันสะสมชัดเจน ต้องระวัง"
    elif name in {"OBVTrend20", "ADLTrend20", "VPTTrend20", "EaseOfMovementTrend5"}:
        value_display = _fmt_num(v)
        if v > 0:
            interpretation = "แนวโน้มเป็นบวก สะท้อนแรงสะสม/แรงซื้อเริ่มได้เปรียบ"
        elif v < 0:
            interpretation = "แนวโน้มเป็นลบ สะท้อนแรงขายหรือการกระจายของ"
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






def options_indicator_explanation(name: str, value):
    """Beginner-friendly explanation for options-flow optional feed values."""
    v = _to_float(value)
    catalog = {
        "unusual_options_volume": ("Unusual Options Volume", "Volume options สูงผิดปกติ มีคน bet ใหญ่"),
        "unusual_options_volume_z": ("Unusual Options Volume Z-Score", "options volume สูงกว่าปกติกี่ส่วนเบี่ยงเบนมาตรฐาน"),
        "call_volume": ("Call Volume", "ปริมาณซื้อขาย Call ใช้สะท้อนมุมมองขึ้น"),
        "put_volume": ("Put Volume", "ปริมาณซื้อขาย Put ใช้สะท้อนมุมมองลงหรือ hedge"),
        "call_put_volume_ratio": ("Call/Put Volume Ratio", "Call เทียบ Put สูง = bullish sentiment"),
        "put_call_ratio": ("Put/Call Ratio", "Put เทียบ Call สูง = fear หรือ hedge"),
        "options_volume_open_interest_ratio": ("Options Volume / Open Interest", "Volume เทียบ OI สูง = มีสถานะใหม่"),
        "sweep_order_count": ("Sweep Orders", "คำสั่งไล่ซื้อหลายตลาด วาฬเร่งเข้า"),
        "sweep_premium_usd": ("Sweep Premium", "มูลค่า premium จาก sweep orders"),
        "options_block_trade_count": ("Block Trades", "รายการใหญ่ เงินก้อนใหญ่"),
        "block_trade_premium_usd": ("Block Trade Premium", "มูลค่า premium จาก block trades"),
        "premium_paid_usd": ("Premium Paid", "มูลค่า options ที่จ่าย ดูขนาดเงินจริง"),
        "aggressor_side": ("Aggressor Side", "ซื้อที่ ask หรือขายที่ bid แยกว่าเปิด bullish/bearish"),
        "near_term_call_premium_usd": ("Near-term Call Flow", "options ใกล้หมดอายุฝั่ง Call เก็งกำไรระยะสั้น"),
        "near_term_put_premium_usd": ("Near-term Put Flow", "options ใกล้หมดอายุฝั่ง Put เก็งลงหรือ hedge ระยะสั้น"),
        "leaps_call_premium_usd": ("LEAPS Call Flow", "options อายุยาวฝั่ง Call มุมมองระยะยาวเชิงบวก"),
        "leaps_put_premium_usd": ("LEAPS Put Flow", "options อายุยาวฝั่ง Put มุมมองระยะยาวเชิงลบหรือ hedge"),
        "otm_call_premium_usd": ("OTM Call Buying", "ซื้อ call นอกเงิน เก็งขึ้นแรง"),
        "otm_put_premium_usd": ("OTM Put Buying", "ซื้อ put นอกเงิน เก็งลงแรงหรือประกัน"),
        "gamma_exposure": ("Gamma Exposure", "dealer gamma ใช้คาดแรงเหวี่ยง"),
        "gamma_exposure_pct_float": ("Gamma Exposure % Float", "gamma exposure เทียบ float"),
        "bullish_premium_ratio": ("Bullish Premium Ratio", "สัดส่วน premium ฝั่ง bullish ต่อ directional premium ทั้งหมด"),
    }

    display_name, meaning = catalog.get(name, (name, "ข้อมูล options flow"))
    if name == "aggressor_side":
        if value is None:
            return display_name, "ไม่มีข้อมูล", meaning, "ยังไม่มีข้อมูลจาก optional feed"
        side = str(value).lower().strip()
        if side in {"ask", "buy", "buyer", "bought_at_ask"}:
            interpretation = "ซื้อที่ ask / buyer initiated เป็น bias เชิงบวก"
        elif side in {"bid", "sell", "seller", "sold_at_bid"}:
            interpretation = "ขายที่ bid / seller initiated เป็น bias เชิงลบ"
        elif side in {"mid", "neutral"}:
            interpretation = "ซื้อขายแถว mid ยังแยกฝั่งไม่ชัด"
        else:
            interpretation = "ยังไม่รู้ฝั่ง aggressor ชัดเจน"
        return display_name, str(value), meaning, interpretation

    if v is None:
        return display_name, "ไม่มีข้อมูล", meaning, "ยังไม่มีข้อมูลจาก optional feed"

    if name in {
        "sweep_premium_usd", "block_trade_premium_usd", "premium_paid_usd",
        "near_term_call_premium_usd", "near_term_put_premium_usd",
        "leaps_call_premium_usd", "leaps_put_premium_usd",
        "otm_call_premium_usd", "otm_put_premium_usd", "gamma_exposure"
    }:
        value_display = "$" + _fmt_num(v, decimals=0)
    elif name in {"call_put_volume_ratio", "put_call_ratio", "options_volume_open_interest_ratio", "gamma_exposure_pct_float", "bullish_premium_ratio"}:
        value_display = _fmt_num(v, suffix="x" if name.endswith("ratio") and name != "bullish_premium_ratio" else "")
        if name == "bullish_premium_ratio":
            value_display = _fmt_num(v * 100 if v <= 1 else v, suffix="%")
    elif name in {"unusual_options_volume", "call_volume", "put_volume"}:
        value_display = _fmt_num(v, decimals=0, suffix=" contracts")
    elif name in {"sweep_order_count", "options_block_trade_count"}:
        value_display = _fmt_num(v, decimals=0, suffix=" รายการ")
    else:
        value_display = _fmt_num(v)

    if name == "unusual_options_volume":
        interpretation = "options volume สูงมาก มีคน bet ใหญ่" if v >= 100000 else ("มี options activity น่าสนใจ" if v >= 20000 else "options volume ยังไม่สูงมาก")
    elif name == "unusual_options_volume_z":
        interpretation = "สูงผิดปกติมาก ควรจับตา" if v >= 3 else ("สูงกว่าปกติ" if v >= 1.5 else "ยังไม่ผิดปกติมาก")
    elif name == "call_volume":
        interpretation = "Call volume สูง สะท้อนการเก็งขึ้น/hedge ฝั่งขึ้น" if v >= 50000 else "Call volume ใช้เทียบกับ Put volume เพื่อดู bias"
    elif name == "put_volume":
        interpretation = "Put volume สูง อาจเป็นการเก็งลงหรือ hedge" if v >= 50000 else "Put volume ใช้เทียบกับ Call volume เพื่อดู fear/hedge"
    elif name == "call_put_volume_ratio":
        interpretation = "Call มากกว่า Put ชัดเจน เป็น bullish sentiment" if v >= 1.5 else ("สมดุล" if v >= 0.8 else "Call น้อยกว่า Put ภาพไม่ค่อย bullish")
    elif name == "put_call_ratio":
        interpretation = "Put สูงกว่า Call มาก อาจเป็น fear หรือ hedge" if v >= 1.5 else ("Put/Call อยู่กลาง ๆ" if v >= 0.7 else "Put ต่ำกว่า Call ภาพเอน bullish")
    elif name == "options_volume_open_interest_ratio":
        interpretation = "Volume เทียบ OI สูงมาก อาจมีการเปิดสถานะใหม่" if v >= 2 else ("มีโอกาสเป็นสถานะใหม่บางส่วน" if v >= 1 else "ส่วนใหญ่ยังไม่ชัดว่าเป็นสถานะใหม่")
    elif name == "sweep_order_count":
        interpretation = "Sweep orders จำนวนมาก วาฬอาจเร่งเข้า" if v >= 10 else ("มี sweep orders ให้ติดตาม" if v >= 1 else "ยังไม่พบ sweep orders")
    elif name == "options_block_trade_count":
        interpretation = "Block trades หลายรายการ เงินก้อนใหญ่เคลื่อนไหว" if v >= 10 else ("มี block trades ให้ติดตาม" if v >= 1 else "ยังไม่พบ block trades")
    elif name in {"sweep_premium_usd", "block_trade_premium_usd", "premium_paid_usd"}:
        interpretation = "premium สูงมาก สะท้อนเงินก้อนใหญ่" if v >= 1_000_000 else ("มี premium ให้ติดตาม" if v > 0 else "ยังไม่มี premium")
    elif name == "near_term_call_premium_usd":
        interpretation = "มี near-term call flow สูง เก็งขึ้นระยะสั้น" if v >= 1_000_000 else "ใช้ดูการเก็งกำไรระยะสั้นฝั่งขึ้น"
    elif name == "near_term_put_premium_usd":
        interpretation = "มี near-term put flow สูง อาจเก็งลงหรือ hedge ระยะสั้น" if v >= 1_000_000 else "ใช้ดูการ hedge/เก็งลงระยะสั้น"
    elif name == "leaps_call_premium_usd":
        interpretation = "LEAPS call สูง สะท้อนมุมมองบวกระยะยาว" if v >= 1_000_000 else "ใช้ดูมุมมองระยะยาวฝั่งขึ้น"
    elif name == "leaps_put_premium_usd":
        interpretation = "LEAPS put สูง อาจเป็นมุมมองลบหรือ hedge ระยะยาว" if v >= 1_000_000 else "ใช้ดูมุมมองระยะยาวฝั่งลง/hedge"
    elif name == "otm_call_premium_usd":
        interpretation = "OTM call สูง เก็งขึ้นแรง" if v >= 1_000_000 else "ใช้ดูการเก็งขึ้นแรง"
    elif name == "otm_put_premium_usd":
        interpretation = "OTM put สูง เก็งลงแรงหรือซื้อประกัน" if v >= 1_000_000 else "ใช้ดูการเก็งลงแรง/ประกันความเสี่ยง"
    elif name == "gamma_exposure":
        interpretation = "gamma บวก อาจช่วยลดแรงเหวี่ยง" if v > 0 else ("gamma ลบ อาจเพิ่มแรงเหวี่ยง" if v < 0 else "gamma ใกล้ศูนย์")
    elif name == "gamma_exposure_pct_float":
        interpretation = "gamma exposure เทียบ float สูง อาจส่งผลต่อแรงเหวี่ยงราคา" if abs(v) >= 2 else "gamma exposure ยังไม่สูงมาก"
    elif name == "bullish_premium_ratio":
        ratio = v * 100 if v <= 1 else v
        interpretation = "premium ส่วนใหญ่เอนฝั่ง bullish" if ratio >= 60 else ("premium สมดุล" if ratio >= 40 else "premium เอนฝั่ง bearish/hedge")
    else:
        interpretation = "ใช้ประกอบกับ options flow score และ smart money score"

    return display_name, value_display, meaning, interpretation

def insider_indicator_explanation(name: str, value):
    """Beginner-friendly explanation for insider trading optional feed values."""
    v = _to_float(value)

    catalog = {
        "insider_net_buy_value_usd": ("Insider Net Buy/Sell", "ผู้บริหารซื้อหรือขายสุทธิ ซื้อ = บวก, ขาย = ต้องดูเหตุผล"),
        "insider_buy_count": ("Insider Buy Count", "จำนวนรายการซื้อ ซื้อหลายคนพร้อมกันน่าสนใจ"),
        "insider_sell_count": ("Insider Sell Count", "จำนวนรายการขาย ขายเยอะอาจกดดัน"),
        "ceo_cfo_transaction_count": ("CEO/CFO Transaction", "ผู้บริหารระดับสูงซื้อขาย น้ำหนักสูงกว่าคนทั่วไป"),
        "ceo_cfo_net_buy_value_usd": ("CEO/CFO Net Buy/Sell", "มูลค่าสุทธิที่ CEO/CFO ซื้อหรือขาย"),
        "cluster_buying_count": ("Cluster Buying", "ผู้บริหารหลายคนซื้อพร้อมกัน เป็นสัญญาณบวกแรง"),
        "buy_size_vs_salary_ratio": ("Buy Size vs Salary", "มูลค่าซื้อเทียบฐานะผู้บริหาร ซื้อเยอะผิดปกติน่าสนใจ"),
        "option_exercise_then_sell_count": ("Option Exercise then Sell", "ใช้สิทธิแล้วขาย อาจไม่ใช่ลบเสมอ"),
        "direct_open_market_buy_count": ("Direct Open Market Buy", "ซื้อในตลาดจริง สัญญาณบวกที่สุดในกลุ่ม insider"),
        "direct_open_market_buy_value_usd": ("Direct Open Market Buy Value", "มูลค่าซื้อจริงในตลาดเปิด"),
    }

    display_name, meaning = catalog.get(name, (name, "ข้อมูล insider trading"))
    if v is None:
        return display_name, "ไม่มีข้อมูล", meaning, "ยังไม่มีข้อมูลจาก optional feed"

    if name in {"insider_net_buy_value_usd", "ceo_cfo_net_buy_value_usd", "direct_open_market_buy_value_usd"}:
        value_display = "$" + _fmt_num(v, decimals=0)
    elif name in {"insider_buy_count", "insider_sell_count", "ceo_cfo_transaction_count", "cluster_buying_count", "option_exercise_then_sell_count", "direct_open_market_buy_count"}:
        value_display = _fmt_num(v, decimals=0, suffix=" รายการ")
    elif name == "buy_size_vs_salary_ratio":
        value_display = _fmt_num(v, suffix="x")
    else:
        value_display = _fmt_num(v)

    if name == "insider_net_buy_value_usd":
        if v >= 1_000_000:
            interpretation = "ผู้บริหารซื้อสุทธิระดับใหญ่ เป็นสัญญาณบวก"
        elif v > 0:
            interpretation = "ผู้บริหารซื้อสุทธิ เป็นสัญญาณบวก"
        elif v == 0:
            interpretation = "ซื้อขายสุทธิใกล้ศูนย์"
        elif v > -1_000_000:
            interpretation = "ผู้บริหารขายสุทธิ ต้องดูเหตุผล เช่น ภาษีหรือกระจายพอร์ต"
        else:
            interpretation = "ผู้บริหารขายสุทธิระดับใหญ่ เป็นแรงกดดัน"
    elif name == "insider_buy_count":
        if v >= 5:
            interpretation = "มีรายการซื้อหลายครั้ง น่าสนใจ โดยเฉพาะถ้าหลายคนซื้อพร้อมกัน"
        elif v >= 1:
            interpretation = "มี insider buy ให้ติดตาม"
        else:
            interpretation = "ยังไม่พบรายการซื้อ"
    elif name == "insider_sell_count":
        if v >= 8:
            interpretation = "รายการขายเยอะ อาจกดดัน sentiment"
        elif v >= 1:
            interpretation = "มีรายการขาย ต้องดูว่าเป็นขายปกติหรือขายผิดปกติ"
        else:
            interpretation = "ยังไม่พบรายการขาย"
    elif name == "ceo_cfo_transaction_count":
        if v >= 2:
            interpretation = "CEO/CFO มีการซื้อขายหลายรายการ น้ำหนักสูงกว่าผู้บริหารทั่วไป"
        elif v >= 1:
            interpretation = "มี CEO/CFO transaction ให้ติดตาม"
        else:
            interpretation = "ยังไม่มีรายการจาก CEO/CFO"
    elif name == "ceo_cfo_net_buy_value_usd":
        if v > 0:
            interpretation = "CEO/CFO ซื้อสุทธิ เป็นสัญญาณบวกคุณภาพสูง"
        elif v < 0:
            interpretation = "CEO/CFO ขายสุทธิ ต้องระวังและดูเหตุผลประกอบ"
        else:
            interpretation = "CEO/CFO net buy/sell ใกล้ศูนย์"
    elif name == "cluster_buying_count":
        if v >= 3:
            interpretation = "เกิด cluster buying หลายคนซื้อพร้อมกัน เป็นสัญญาณบวกแรง"
        elif v >= 1:
            interpretation = "เริ่มมี cluster buying"
        else:
            interpretation = "ยังไม่พบ cluster buying"
    elif name == "buy_size_vs_salary_ratio":
        if v >= 2:
            interpretation = "มูลค่าซื้อใหญ่เมื่อเทียบฐานะผู้บริหาร น่าสนใจมาก"
        elif v >= 0.5:
            interpretation = "ขนาดซื้อพอมีนัยสำคัญ"
        else:
            interpretation = "ขนาดซื้อยังไม่ใหญ่มาก"
    elif name == "option_exercise_then_sell_count":
        if v >= 5:
            interpretation = "มีการใช้สิทธิแล้วขายหลายครั้ง อาจกดดัน แต่ไม่ใช่ลบเสมอ"
        elif v >= 1:
            interpretation = "มี exercise then sell ต้องแยกจากการขายหุ้นปกติ"
        else:
            interpretation = "ยังไม่พบ exercise then sell"
    elif name == "direct_open_market_buy_count":
        if v >= 3:
            interpretation = "มี direct open market buy หลายครั้ง เป็นสัญญาณบวกที่สุดในกลุ่ม insider"
        elif v >= 1:
            interpretation = "มีการซื้อจริงในตลาด เป็นสัญญาณบวก"
        else:
            interpretation = "ยังไม่พบ direct open market buy"
    elif name == "direct_open_market_buy_value_usd":
        if v >= 1_000_000:
            interpretation = "มูลค่าซื้อในตลาดจริงสูงมาก เป็นสัญญาณบวก"
        elif v > 0:
            interpretation = "มีมูลค่าซื้อในตลาดจริง เป็นบวก"
        else:
            interpretation = "ยังไม่มีมูลค่าซื้อในตลาดจริง"
    else:
        interpretation = "ใช้ประกอบกับ insider flow score และ smart money score"

    return display_name, value_display, meaning, interpretation

def institutional_indicator_explanation(name: str, value):
    """Beginner-friendly explanation for institutional / whale ownership optional feed values."""
    v = _to_float(value)
    catalog = {
        "net_institutional_flow_pct": ("13F Net Institutional Flow", "กองทุนเพิ่มหรือลดหุ้นสุทธิ ใช้จับเงินสถาบัน"),
        "net_institutional_flow_value_usd": ("13F Net Institutional Flow Value", "มูลค่าซื้อ/ขายสุทธิของสถาบันโดยประมาณ"),
        "new_positions_count": ("New Institutional Positions", "มีกองทุนเปิดสถานะใหม่กี่ราย ใช้ดูความสนใจใหม่"),
        "increased_positions_count": ("Increased Positions", "กองทุนเดิมซื้อเพิ่ม เป็นสัญญาณสะสม"),
        "decreased_positions_count": ("Decreased Positions", "กองทุนเดิมลดพอร์ต เป็นสัญญาณขาย"),
        "sold_out_positions_count": ("Sold Out Positions", "กองทุนขายหมด เป็นสัญญาณลบ"),
        "top10_holder_concentration_pct": ("Top 10 Holder Concentration", "ผู้ถือหุ้นใหญ่ 10 อันดับแรกถือรวมกี่เปอร์เซ็นต์ ใช้ดูความกระจุกตัว"),
        "institutional_ownership_pct": ("Institutional Ownership %", "สถาบันถือหุ้นกี่เปอร์เซ็นต์ ใช้ดูว่าหุ้นมีเจ้ามือสถาบันไหม"),
        "qoq_holding_change_pct": ("Quarter-over-quarter Holding Change", "การถือครองเปลี่ยนจากไตรมาสก่อนเท่าไร ใช้ดู trend การสะสม"),
        "whale_accumulation_score": ("Whale Accumulation Score", "คะแนนสะสมโดยรายใหญ่ ใช้รวมเป็น smart money score"),
    }
    display_name, meaning = catalog.get(name, (name, "ข้อมูล institutional / whale ownership"))
    if v is None:
        return display_name, "ไม่มีข้อมูล", meaning, "ยังไม่มีข้อมูลจาก optional feed"

    if name in {"net_institutional_flow_pct", "top10_holder_concentration_pct", "institutional_ownership_pct", "qoq_holding_change_pct"}:
        if abs(v) <= 1 and v != 0:
            v *= 100
        value_display = _fmt_num(v, suffix="%")
    elif name == "net_institutional_flow_value_usd":
        value_display = "$" + _fmt_num(v, decimals=0)
    elif name in {"new_positions_count", "increased_positions_count", "decreased_positions_count", "sold_out_positions_count"}:
        value_display = _fmt_num(v, decimals=0, suffix=" กองทุน")
    else:
        value_display = _fmt_num(v)

    if name == "net_institutional_flow_pct":
        interpretation = "สถาบันเพิ่มการถือครองชัดเจน เป็นสัญญาณบวก" if v >= 5 else ("สถาบันเพิ่มการถือครองเล็กน้อยถึงปานกลาง" if v > 0 else ("การถือครองสุทธิแทบไม่เปลี่ยน" if v == 0 else ("สถาบันลดการถือครองเล็กน้อย ต้องติดตาม" if v > -5 else "สถาบันลดการถือครองชัดเจน เป็นสัญญาณลบ")))
    elif name == "net_institutional_flow_value_usd":
        interpretation = "เม็ดเงินสถาบันซื้อสุทธิระดับใหญ่" if v >= 10_000_000 else ("เม็ดเงินสถาบันซื้อสุทธิ" if v > 0 else ("เม็ดเงินสุทธิใกล้ศูนย์" if v == 0 else ("เม็ดเงินสถาบันขายสุทธิ" if v > -10_000_000 else "เม็ดเงินสถาบันขายสุทธิระดับใหญ่")))
    elif name == "new_positions_count":
        interpretation = "มีกองทุนใหม่เข้ามาหลายราย ความสนใจใหม่สูง" if v >= 10 else ("เริ่มมี institutional sponsor รายใหม่" if v >= 3 else "กองทุนใหม่ยังไม่มาก")
    elif name == "increased_positions_count":
        interpretation = "กองทุนเดิมซื้อเพิ่มจำนวนมาก สะท้อนการสะสม" if v >= 20 else ("มีกองทุนเดิมซื้อเพิ่มพอสมควร" if v >= 5 else "การซื้อเพิ่มจากกองทุนเดิมยังไม่เด่น")
    elif name == "decreased_positions_count":
        interpretation = "กองทุนเดิมลดพอร์ตจำนวนมาก เป็นแรงกดดัน" if v >= 20 else ("มีแรงลดพอร์ตจากกองทุนเดิม ต้องดูเทียบกับ increased positions" if v >= 5 else "การลดพอร์ตยังไม่มาก")
    elif name == "sold_out_positions_count":
        interpretation = "มีกองทุนขายหมดหลายราย เป็นสัญญาณลบชัด" if v >= 10 else ("มีกองทุนบางส่วนขายหมด ต้องติดตาม" if v >= 3 else "กองทุนขายหมดไม่มาก")
    elif name == "top10_holder_concentration_pct":
        interpretation = "ผู้ถือหุ้นใหญ่กระจุกตัวสูงมาก อาจช่วยพยุงราคาแต่เสี่ยงถ้ารายใหญ่ขาย" if v >= 60 else ("มีผู้ถือหุ้นใหญ่ค่อนข้างชัด หุ้นมี sponsor ระดับหนึ่ง" if v >= 30 else "การถือครองไม่กระจุกตัวมาก")
    elif name == "institutional_ownership_pct":
        interpretation = "สถาบันถือหุ้นสูง หุ้นมี institutional sponsor ชัด" if v >= 50 else ("สถาบันถือหุ้นระดับพอใช้" if v >= 20 else ("สถาบันถือหุ้นต่ำ ยังพึ่งพารายย่อยมากกว่า" if v > 0 else "ไม่มีข้อมูล ownership"))
    elif name == "qoq_holding_change_pct":
        interpretation = "การถือครองเพิ่มขึ้นจากไตรมาสก่อนชัดเจน เป็น trend สะสม" if v >= 5 else ("การถือครองเพิ่มขึ้นเล็กน้อย" if v > 0 else ("การถือครองไม่เปลี่ยนมาก" if v == 0 else ("การถือครองลดลงเล็กน้อย" if v > -5 else "การถือครองลดลงชัดเจน")))
    elif name == "whale_accumulation_score":
        interpretation = "คะแนนสะสมโดยรายใหญ่แข็งแรงมาก" if v >= 75 else ("คะแนนสะสมโดยรายใหญ่ค่อนข้างดี" if v >= 60 else ("คะแนนยังกลาง ๆ" if v >= 40 else "คะแนนสะสมโดยรายใหญ่ยังอ่อน"))
    else:
        interpretation = "ใช้ประกอบกับ institutional flow และ smart money score"
    return display_name, value_display, meaning, interpretation

def dark_pool_indicator_explanation(name: str, value):
    """Beginner-friendly explanation for dark-pool/off-exchange optional feed values."""
    v = _to_float(value)

    catalog = {
        "dark_pool_volume": ("Dark Pool Volume", "จำนวนหุ้นที่ซื้อขายนอกตลาดหลัก ใช้ดูว่ามีเงินใหญ่ซ่อนอยู่ไหม"),
        "dark_pool_volume_ratio": ("Dark Pool % of Total Volume", "สัดส่วน volume นอกตลาดหลักเทียบกับ volume ทั้งหมด สูงผิดปกติควรจับตา"),
        "dark_pool_pct_total_volume": ("Dark Pool % of Total Volume", "สัดส่วน volume นอกตลาดหลักแบบเปอร์เซ็นต์"),
        "large_block_trade_count": ("Large Block Print", "จำนวนรายการซื้อขายก้อนใหญ่ ใช้ดูว่าวาฬเข้าออกหรือไม่"),
        "large_block_volume": ("Large Block Volume", "จำนวนหุ้นรวมจากรายการ block trade ขนาดใหญ่"),
        "large_block_value_usd": ("Large Block Value", "มูลค่ารวมของรายการ block trade ขนาดใหญ่"),
        "largest_block_value_usd": ("Largest Block Print", "มูลค่ารายการ block trade ก้อนใหญ่ที่สุด"),
        "block_price_vs_vwap_pct": ("Block Trade Price vs VWAP", "ดูว่า block ซื้อขายแพงหรือถูกกว่า VWAP เพื่ออ่าน bias"),
        "repeated_print_count": ("Repeated Prints", "จำนวน block ซ้ำหรือรายการขนาดคล้ายกัน อาจสะสมหรือกระจายของ"),
        "repeated_print_ratio": ("Repeated Print Ratio", "สัดส่วน repeated prints ต่อรายการ block ทั้งหมด"),
        "off_exchange_trend_5d": ("Off-exchange Trend 5 วัน", "ดูว่า dark pool/off-exchange เพิ่มต่อเนื่องในระยะสั้นไหม"),
        "off_exchange_trend_20d": ("Off-exchange Trend 20 วัน", "ดูแนวโน้มการเคลื่อนไหวเงียบระยะกลาง"),
        "dark_pool_buy_volume": ("Dark Pool Buy Volume", "volume ฝั่งซื้อใน dark pool ถ้า provider มี aggressor side"),
        "dark_pool_sell_volume": ("Dark Pool Sell Volume", "volume ฝั่งขายใน dark pool ถ้า provider มี aggressor side"),
        "dark_pool_net_bias": ("Dark Pool Net Bias", "ค่า -1 ถึง +1; บวกคือซื้อเด่น ลบคือขายเด่น"),
    }

    display_name, meaning = catalog.get(name, (name, "ข้อมูลเสริมจาก dark pool/off-exchange feed"))
    if v is None:
        return display_name, "ไม่มีข้อมูล", meaning, "ยังไม่มีข้อมูลจาก optional feed"

    value_display = _fmt_num(v)

    if name in {"dark_pool_volume", "large_block_volume", "dark_pool_buy_volume", "dark_pool_sell_volume"}:
        value_display = _fmt_num(v, decimals=0, suffix=" หุ้น")
        interpretation = "ใช้ดูขนาดการเคลื่อนไหว ต้องอ่านร่วมกับ total volume และ net bias"
    elif name in {"large_block_value_usd", "largest_block_value_usd"}:
        value_display = "$" + _fmt_num(v, decimals=0)
        if v >= 10_000_000:
            interpretation = "มูลค่าก้อนใหญ่มาก สะท้อนการเคลื่อนไหวของเงินใหญ่"
        elif v >= 1_000_000:
            interpretation = "มี block value ระดับน่าสนใจ ควรอ่านร่วมกับราคาเทียบ VWAP"
        else:
            interpretation = "มูลค่า block ยังไม่ใหญ่มาก"
    elif name in {"dark_pool_volume_ratio", "repeated_print_ratio"}:
        ratio = v / 100 if v > 1.5 else v
        value_display = f"{ratio * 100:,.2f}%"
        if name == "dark_pool_volume_ratio":
            if ratio >= 0.60:
                interpretation = "สัดส่วน dark pool สูงมาก มีการซื้อขายนอกกระดานเด่น ควรดู bias ประกอบ"
            elif ratio >= 0.45:
                interpretation = "สัดส่วน dark pool สูงกว่าปกติ ควรจับตา"
            elif ratio >= 0.25:
                interpretation = "มี off-exchange activity ระดับปานกลาง"
            else:
                interpretation = "สัดส่วน dark pool ยังไม่สูง"
        else:
            if ratio >= 0.30:
                interpretation = "มี repeated prints สูง อาจมีการสะสมหรือกระจายเป็นชุด"
            elif ratio >= 0.10:
                interpretation = "มี repeated prints ให้ติดตาม"
            else:
                interpretation = "repeated prints ยังไม่เด่น"
    elif name == "dark_pool_pct_total_volume":
        value_display = _fmt_num(v, suffix="%")
        if v >= 60:
            interpretation = "สัดส่วน dark pool สูงมาก ต้องดู net bias และ VWAP เพื่อแยกสะสม/ขาย"
        elif v >= 45:
            interpretation = "สัดส่วน dark pool สูง ควรจับตาการเคลื่อนไหวเงียบ"
        elif v >= 25:
            interpretation = "สัดส่วนปานกลาง"
        else:
            interpretation = "สัดส่วนยังไม่สูง"
    elif name == "large_block_trade_count":
        value_display = _fmt_num(v, decimals=0, suffix=" รายการ")
        if v >= 20:
            interpretation = "มี block prints จำนวนมาก วาฬ/สถาบันอาจเคลื่อนไหวชัด"
        elif v >= 5:
            interpretation = "มี block prints ระดับน่าสนใจ"
        else:
            interpretation = "จำนวน block prints ยังไม่มาก"
    elif name == "block_price_vs_vwap_pct":
        value_display = _fmt_num(v, suffix="%")
        if v >= 1:
            interpretation = "block ซื้อขายเหนือ VWAP ชัดเจน เป็น bias บวก"
        elif v > 0:
            interpretation = "block ซื้อขายเหนือ VWAP เล็กน้อย ฝั่งซื้อเริ่มได้เปรียบ"
        elif v == 0:
            interpretation = "block ใกล้ VWAP ยังเป็นกลาง"
        elif v > -1:
            interpretation = "block ต่ำกว่า VWAP เล็กน้อย ฝั่งขายเริ่มได้เปรียบ"
        else:
            interpretation = "block ต่ำกว่า VWAP ชัดเจน เป็น bias ลบ"
    elif name == "repeated_print_count":
        value_display = _fmt_num(v, decimals=0, suffix=" ครั้ง")
        if v >= 10:
            interpretation = "มี repeated prints หลายครั้ง อาจเป็นการทยอยสะสมหรือทยอยขาย"
        elif v >= 3:
            interpretation = "เริ่มมี repeated prints ให้ติดตาม"
        else:
            interpretation = "repeated prints ยังไม่เด่น"
    elif name in {"off_exchange_trend_5d", "off_exchange_trend_20d"}:
        value_display = _fmt_num(v, suffix="%")
        if v >= 10:
            interpretation = "off-exchange เพิ่มขึ้นชัดเจน มีการเคลื่อนไหวเงียบมากขึ้น"
        elif v > 0:
            interpretation = "off-exchange เพิ่มขึ้นเล็กน้อย"
        elif v == 0:
            interpretation = "off-exchange ไม่เปลี่ยนมาก"
        else:
            interpretation = "off-exchange ลดลง"
    elif name == "dark_pool_net_bias":
        value_display = _fmt_num(v)
        if v >= 0.30:
            interpretation = "buy bias ชัดเจน ฝั่งซื้อใน dark pool เด่น"
        elif v > 0.05:
            interpretation = "buy bias เล็กน้อยถึงปานกลาง"
        elif v >= -0.05:
            interpretation = "bias ใกล้กลาง ยังแยกฝั่งซื้อขายไม่ชัด"
        elif v > -0.30:
            interpretation = "sell bias เล็กน้อยถึงปานกลาง"
        else:
            interpretation = "sell bias ชัดเจน ระวังแรงขายซ่อนอยู่"
    else:
        interpretation = "ใช้ประกอบกับ dark pool ratio, block price vs VWAP และ net bias"

    return display_name, value_display, meaning, interpretation

st.set_page_config(page_title="Smart Money Whale Agent v2.7", layout="wide")
st.title("🐋 Smart Money Whale Agent v2.7 — US Stocks")
st.caption("วิเคราะห์วาฬ / Smart Money จากราคา ปริมาณซื้อขาย VWAP CMF OBV ADL MFI VPT EMV options flow institutional 13F insider trading whale ownership dark-pool off-exchange 13F insider dark-pool short pressure และ relative strength")

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
    status_legend()
    show_status_dataframe(interpret_df, interpretation_col="คำแปลความหมาย")

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
        "CMF20", "MFI14", "VWAPDeviationPct", "OBVTrend20",
        "ADL", "ADLTrend20", "ADLPriceDivergence20",
        "VPT", "VPTTrend20", "VPTPriceDivergence20",
        "EaseOfMovement14", "EaseOfMovementTrend5", "CloseLocationValue", "UpDownVolumeRatio20",
        "PocketPivotProxy", "PocketPivotCount20", "DistributionDayFlag", "DistributionDayCount25",
        "AccumulationDayFlag", "AccumulationDayCount25", "NetAccumulationDays25",
        "RS_SPY_Return20DSpread", "RS_QQQ_Return20DSpread",
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
    status_legend()
    show_status_dataframe(indicator_df, interpretation_col="แปลผลตอนนี้")

    st.subheader("v2.1 Accumulation / Distribution Indicators")
    status_legend()
    ad_keys = [
        "ADL", "MFI14", "VPT", "EaseOfMovement14", "CloseLocationValue",
        "UpDownVolumeRatio20", "PocketPivotProxy", "DistributionDayCount25",
    ]
    ad_rows = []
    for key in ad_keys:
        raw_value = report.indicators.get(key)
        display_name, value_display, beginner_meaning, interpretation = indicator_explanation(key, raw_value)
        ad_rows.append({
            "Indicator": display_name,
            "ค่า": value_display,
            "ความหมาย": beginner_meaning,
            "การตีความ": interpretation,
        })
    show_status_dataframe(pd.DataFrame(ad_rows), interpretation_col="การตีความ")

    st.subheader("v2.5 Options Flow Indicators")
    status_legend()
    st.caption(
        "กลุ่มนี้สำคัญมากในการจับวาฬระยะสั้น ใช้ optional feed จาก options-flow provider "
        "เพราะข้อมูล sweep, aggressor side, premium และ gamma มักต้องใช้ผู้ให้บริการเฉพาะทาง"
    )

    options_data = report.indicators.get("optional_feeds", {}).get("options", {})
    options_keys = [
        "unusual_options_volume",
        "call_volume",
        "put_volume",
        "call_put_volume_ratio",
        "put_call_ratio",
        "options_volume_open_interest_ratio",
        "sweep_order_count",
        "options_block_trade_count",
        "premium_paid_usd",
        "aggressor_side",
        "near_term_call_premium_usd",
        "near_term_put_premium_usd",
        "leaps_call_premium_usd",
        "leaps_put_premium_usd",
        "otm_call_premium_usd",
        "otm_put_premium_usd",
        "gamma_exposure",
    ]

    options_rows = []
    for key in options_keys:
        display_name, value_display, meaning, interpretation = options_indicator_explanation(key, options_data.get(key))
        options_rows.append({
            "Indicator": display_name,
            "ค่า": value_display,
            "ความหมาย": meaning,
            "การตีความ": interpretation,
        })
    show_status_dataframe(pd.DataFrame(options_rows), interpretation_col="การตีความ")

    options_summary = []
    call_put = _to_float(options_data.get("call_put_volume_ratio"))
    put_call = _to_float(options_data.get("put_call_ratio"))
    vol_oi = _to_float(options_data.get("options_volume_open_interest_ratio"))
    sweeps = _to_float(options_data.get("sweep_order_count", options_data.get("sweep_count")))
    premium = _to_float(options_data.get("premium_paid_usd", options_data.get("premium_usd")))
    side = str(options_data.get("aggressor_side", "")).lower().strip()
    otm_call = _to_float(options_data.get("otm_call_premium_usd"))
    otm_put = _to_float(options_data.get("otm_put_premium_usd"))
    gamma = _to_float(options_data.get("gamma_exposure", options_data.get("dealer_gamma_exposure")))

    if call_put is not None:
        if call_put >= 1.5:
            options_summary.append("Call/Put ratio สูง: sentiment ฝั่ง options เอน bullish")
        elif call_put < 0.8:
            options_summary.append("Call/Put ratio ต่ำ: call ไม่เด่นเมื่อเทียบ put")

    if put_call is not None and put_call >= 1.5:
        options_summary.append("Put/Call ratio สูง: อาจมี fear หรือ hedge จำนวนมาก")

    if vol_oi is not None and vol_oi >= 1:
        options_summary.append("Options volume / open interest สูง: อาจมีการเปิดสถานะใหม่")

    if sweeps is not None and sweeps >= 5:
        options_summary.append("Sweep orders หลายรายการ: วาฬอาจเร่งเข้า position")

    if premium is not None and premium >= 1_000_000:
        options_summary.append("Premium paid สูง: มีเงินก้อนใหญ่ใน options flow")

    if side in {"ask", "buy", "buyer", "bought_at_ask"}:
        options_summary.append("Aggressor side อยู่ฝั่ง ask/buy: bias เชิงบวก")
    elif side in {"bid", "sell", "seller", "sold_at_bid"}:
        options_summary.append("Aggressor side อยู่ฝั่ง bid/sell: bias เชิงลบ")

    if otm_call is not None and otm_put is not None:
        if otm_call > otm_put:
            options_summary.append("OTM call premium มากกว่า OTM put: มีการเก็งขึ้นแรงมากกว่า")
        elif otm_put > otm_call:
            options_summary.append("OTM put premium มากกว่า OTM call: มีการเก็งลงหรือ hedge มากกว่า")

    if gamma is not None:
        if gamma > 0:
            options_summary.append("Gamma exposure เป็นบวก: อาจช่วยลดแรงเหวี่ยงบางส่วน")
        elif gamma < 0:
            options_summary.append("Gamma exposure เป็นลบ: ราคาอาจเหวี่ยงแรงขึ้น")

    if options_summary:
        st.markdown("**สรุป Options Flow แบบมือใหม่**")
        for note in options_summary:
            st.markdown(f"- {note}")
    else:
        st.info("ยังไม่มีข้อมูล Options Flow จาก optional feed สำหรับหุ้นตัวนี้")


    st.subheader("v2.3 Institutional / Whale Ownership Indicators")
    status_legend()
    st.caption(
        "ข้อมูลกลุ่มนี้ใช้ optional feed เช่น 13F aggregator หรือข้อมูลผู้ถือหุ้นสถาบัน "
        "เพราะ 13F เป็นข้อมูลรายไตรมาสและมีความล่าช้า ไม่ใช่ real-time"
    )
    inst_data = report.indicators.get("optional_feeds", {}).get("institutional", {})
    inst_keys = [
        "net_institutional_flow_pct", "new_positions_count", "increased_positions_count",
        "decreased_positions_count", "sold_out_positions_count", "top10_holder_concentration_pct",
        "institutional_ownership_pct", "qoq_holding_change_pct", "whale_accumulation_score",
        "net_institutional_flow_value_usd",
    ]
    inst_rows = []
    for key in inst_keys:
        display_name, value_display, meaning, interpretation = institutional_indicator_explanation(key, inst_data.get(key))
        inst_rows.append({
            "Indicator": display_name,
            "ค่า": value_display,
            "ความหมาย": meaning,
            "สำคัญอย่างไร / การตีความ": interpretation,
        })
    show_status_dataframe(pd.DataFrame(inst_rows), interpretation_col="สำคัญอย่างไร / การตีความ")

    inst_summary = []
    net_flow = _to_float(inst_data.get("net_institutional_flow_pct"))
    qoq = _to_float(inst_data.get("qoq_holding_change_pct"))
    new_pos = _to_float(inst_data.get("new_positions_count"))
    inc_pos = _to_float(inst_data.get("increased_positions_count"))
    dec_pos = _to_float(inst_data.get("decreased_positions_count"))
    sold_out = _to_float(inst_data.get("sold_out_positions_count"))
    own_pct = _to_float(inst_data.get("institutional_ownership_pct"))
    whale_score = _to_float(inst_data.get("whale_accumulation_score"))

    if net_flow is not None:
        if abs(net_flow) <= 1 and net_flow != 0:
            net_flow *= 100
        inst_summary.append("13F net flow เป็นบวก: สถาบันเพิ่มการถือครองสุทธิ" if net_flow > 0 else ("13F net flow เป็นลบ: สถาบันลดการถือครองสุทธิ" if net_flow < 0 else "13F net flow ใกล้ศูนย์: ยังไม่เห็นการเปลี่ยนแปลงชัด"))
    if inc_pos is not None and dec_pos is not None:
        if inc_pos > dec_pos:
            inst_summary.append("กองทุนซื้อเพิ่มมากกว่าลดพอร์ต: ภาพสะสมเป็นบวก")
        elif dec_pos > inc_pos:
            inst_summary.append("กองทุนลดพอร์ตมากกว่าซื้อเพิ่ม: ต้องระวังแรงขายจากสถาบัน")
    if new_pos is not None and new_pos >= 3:
        inst_summary.append("มี new institutional positions: เริ่มมี sponsor รายใหม่สนใจ")
    if sold_out is not None and sold_out >= 3:
        inst_summary.append("มี sold out positions หลายราย: เป็นสัญญาณลบที่ต้องติดตาม")
    if qoq is not None:
        if abs(qoq) <= 1 and qoq != 0:
            qoq *= 100
        inst_summary.append("QoQ holding change เพิ่มขึ้น: trend การสะสมดีขึ้น" if qoq > 0 else ("QoQ holding change ลดลง: trend การถือครองอ่อนลง" if qoq < 0 else "QoQ holding change ใกล้ศูนย์"))
    if own_pct is not None:
        if abs(own_pct) <= 1 and own_pct != 0:
            own_pct *= 100
        if own_pct >= 30:
            inst_summary.append("Institutional ownership สูง: หุ้นมีฐานผู้ถือหุ้นสถาบันชัด")
        elif own_pct > 0 and own_pct < 10:
            inst_summary.append("Institutional ownership ต่ำ: หุ้นอาจยังพึ่งพารายย่อยมากกว่า")
    if whale_score is not None and whale_score >= 60:
        inst_summary.append("Whale Accumulation Score ดี: โมเดลมองว่ารายใหญ่เริ่มสะสม")

    if inst_summary:
        st.markdown("**สรุป Institutional / Whale Ownership แบบมือใหม่**")
        for note in inst_summary:
            st.markdown(f"- {note}")
    else:
        st.info("ยังไม่มีข้อมูล Institutional / Whale Ownership จาก optional feed สำหรับหุ้นตัวนี้")


    st.subheader("v2.4 Insider Trading Indicators")
    status_legend()
    st.caption(
        "ข้อมูลกลุ่มนี้ใช้ optional feed จาก Form 4 / insider transaction aggregator "
        "ควรอ่านร่วมกับเหตุผลการขาย เพราะบางรายการเช่น option exercise then sell อาจไม่ใช่สัญญาณลบเสมอ"
    )

    insider_data = report.indicators.get("optional_feeds", {}).get("insider", {})
    insider_keys = [
        "insider_net_buy_value_usd",
        "insider_buy_count",
        "insider_sell_count",
        "ceo_cfo_transaction_count",
        "ceo_cfo_net_buy_value_usd",
        "cluster_buying_count",
        "buy_size_vs_salary_ratio",
        "option_exercise_then_sell_count",
        "direct_open_market_buy_count",
        "direct_open_market_buy_value_usd",
    ]

    insider_rows = []
    for key in insider_keys:
        display_name, value_display, meaning, interpretation = insider_indicator_explanation(key, insider_data.get(key))
        insider_rows.append({
            "Indicator": display_name,
            "ค่า": value_display,
            "ความหมาย": meaning,
            "การตีความ": interpretation,
        })
    show_status_dataframe(pd.DataFrame(insider_rows), interpretation_col="การตีความ")

    insider_summary = []
    net_buy = _to_float(insider_data.get("insider_net_buy_value_usd", insider_data.get("net_buy_value_usd")))
    buy_count = _to_float(insider_data.get("insider_buy_count", insider_data.get("buy_count")))
    sell_count = _to_float(insider_data.get("insider_sell_count", insider_data.get("sell_count")))
    ceo_cfo_net = _to_float(insider_data.get("ceo_cfo_net_buy_value_usd"))
    cluster_count = _to_float(insider_data.get("cluster_buying_count"))
    direct_buy_count = _to_float(insider_data.get("direct_open_market_buy_count"))
    exercise_sell = _to_float(insider_data.get("option_exercise_then_sell_count"))

    if net_buy is not None:
        if net_buy > 0:
            insider_summary.append("Insider net buy เป็นบวก: ผู้บริหารซื้อสุทธิมากกว่าขาย")
        elif net_buy < 0:
            insider_summary.append("Insider net buy เป็นลบ: ผู้บริหารขายสุทธิ ต้องดูเหตุผลประกอบ")
        else:
            insider_summary.append("Insider net buy ใกล้ศูนย์: ยังไม่เห็นภาพชัด")

    if buy_count is not None and sell_count is not None:
        if buy_count > sell_count:
            insider_summary.append("จำนวนรายการซื้อมากกว่าขาย: sentiment ภายในบริษัทดูดีขึ้น")
        elif sell_count > buy_count:
            insider_summary.append("จำนวนรายการขายมากกว่าซื้อ: อาจกดดัน sentiment")

    if ceo_cfo_net is not None:
        if ceo_cfo_net > 0:
            insider_summary.append("CEO/CFO ซื้อสุทธิ: เป็นสัญญาณบวกคุณภาพสูง")
        elif ceo_cfo_net < 0:
            insider_summary.append("CEO/CFO ขายสุทธิ: ต้องติดตามเหตุผลและขนาดรายการ")

    if cluster_count is not None and cluster_count >= 2:
        insider_summary.append("Cluster buying: ผู้บริหารหลายคนซื้อพร้อมกัน เป็นสัญญาณบวกแรง")

    if direct_buy_count is not None and direct_buy_count >= 1:
        insider_summary.append("Direct open market buy: มีการซื้อจริงในตลาด เป็นสัญญาณบวกมากกว่า exercise/options")

    if exercise_sell is not None and exercise_sell >= 1:
        insider_summary.append("มี option exercise then sell: ไม่ควรตีความเป็นลบทันที ต้องดูว่าเป็นแผนภาษี/ค่าตอบแทนหรือไม่")

    if insider_summary:
        st.markdown("**สรุป Insider Trading แบบมือใหม่**")
        for note in insider_summary:
            st.markdown(f"- {note}")
    else:
        st.info("ยังไม่มีข้อมูล Insider Trading จาก optional feed สำหรับหุ้นตัวนี้")


    st.subheader("v2.2 Dark Pool / Off-exchange Indicators")
    status_legend()
    st.caption(
        "ข้อมูลกลุ่มนี้มาจาก optional feed เช่น dark-pool provider, block trade provider หรือไฟล์ JSON ที่ใส่เอง "
        "ถ้าไม่มีข้อมูล ระบบจะแสดงว่าไม่มีข้อมูลและให้คะแนนกลาง"
    )

    dark_data = report.indicators.get("optional_feeds", {}).get("dark_pool", {})
    dark_keys = [
        "dark_pool_volume", "dark_pool_volume_ratio", "large_block_trade_count",
        "block_price_vs_vwap_pct", "repeated_print_count", "off_exchange_trend_5d",
        "off_exchange_trend_20d", "dark_pool_net_bias",
        "large_block_value_usd", "largest_block_value_usd",
        "dark_pool_buy_volume", "dark_pool_sell_volume",
    ]
    dark_rows = []
    for key in dark_keys:
        display_name, value_display, meaning, interpretation = dark_pool_indicator_explanation(key, dark_data.get(key))
        dark_rows.append({
            "Indicator": display_name,
            "ค่า": value_display,
            "ความหมาย": meaning,
            "ใช้วิเคราะห์ / การตีความ": interpretation,
        })
    show_status_dataframe(pd.DataFrame(dark_rows), interpretation_col="ใช้วิเคราะห์ / การตีความ")

    dark_summary = []
    dark_ratio = _to_float(dark_data.get("dark_pool_volume_ratio"))
    if dark_ratio is None:
        dark_pct = _to_float(dark_data.get("dark_pool_pct_total_volume"))
        dark_ratio = dark_pct / 100 if dark_pct is not None else None
    if dark_ratio is not None and dark_ratio > 1.5:
        dark_ratio = dark_ratio / 100

    block_vs_vwap = _to_float(dark_data.get("block_price_vs_vwap_pct"))
    net_bias = _to_float(dark_data.get("dark_pool_net_bias"))
    repeated_count = _to_float(dark_data.get("repeated_print_count"))
    offtrend_5d = _to_float(dark_data.get("off_exchange_trend_5d"))

    if dark_ratio is not None:
        if dark_ratio >= 0.45:
            dark_summary.append("Dark pool ratio สูง: มีการซื้อขายนอกกระดานมาก ควรจับตาเงินใหญ่")
        else:
            dark_summary.append("Dark pool ratio ยังไม่สูงมาก")

    if block_vs_vwap is not None:
        if block_vs_vwap > 0:
            dark_summary.append("Block trade อยู่เหนือ VWAP: bias เอียงไปทางฝั่งซื้อ")
        elif block_vs_vwap < 0:
            dark_summary.append("Block trade ต่ำกว่า VWAP: bias เอียงไปทางฝั่งขาย")

    if net_bias is not None:
        if net_bias > 0.05:
            dark_summary.append("Dark pool net bias เป็นบวก: ฝั่งซื้อเด่นกว่า")
        elif net_bias < -0.05:
            dark_summary.append("Dark pool net bias เป็นลบ: ฝั่งขายเด่นกว่า")
        else:
            dark_summary.append("Dark pool net bias ใกล้กลาง: ยังแยกฝั่งซื้อขายไม่ชัด")

    if repeated_count is not None and repeated_count >= 3:
        dark_summary.append("มี repeated prints หลายครั้ง: อาจเป็นการทยอยสะสมหรือทยอยกระจายของ")

    if offtrend_5d is not None and offtrend_5d > 0:
        dark_summary.append("Off-exchange trend 5 วันเพิ่มขึ้น: มีการเคลื่อนไหวเงียบมากขึ้นในระยะสั้น")

    if dark_summary:
        st.markdown("**สรุป Dark Pool แบบมือใหม่**")
        for note in dark_summary:
            st.markdown(f"- {note}")
    else:
        st.info("ยังไม่มีข้อมูล Dark Pool / Off-exchange จาก optional feed สำหรับหุ้นตัวนี้")

    st.subheader("สรุป Key Indicators แบบภาษาคนเริ่มต้น")
    simple_notes = []

    rsi = _to_float(report.indicators.get("RSI14"))
    cmf = _to_float(report.indicators.get("CMF20"))
    rv = _to_float(report.indicators.get("RelativeVolume30"))
    vwap_dev = _to_float(report.indicators.get("VWAPDeviationPct"))
    atrp = _to_float(report.indicators.get("ATRPercent"))
    dist_days = _to_float(report.indicators.get("DistributionDayCount25"))
    acc_days = _to_float(report.indicators.get("AccumulationDayCount25"))
    updown = _to_float(report.indicators.get("UpDownVolumeRatio20"))
    clv = _to_float(report.indicators.get("CloseLocationValue"))
    pocket_count = _to_float(report.indicators.get("PocketPivotCount20"))
    adl_div = _to_float(report.indicators.get("ADLPriceDivergence20"))
    vpt_div = _to_float(report.indicators.get("VPTPriceDivergence20"))
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


    if updown is not None:
        if updown >= 1.2:
            simple_notes.append("Up/Down Volume Ratio ดี: Volume วันขึ้นมากกว่าวันลง สะท้อนเงินเข้า")
        elif updown < 0.8:
            simple_notes.append("Up/Down Volume Ratio อ่อน: Volume วันลงมากกว่า ต้องระวังเงินออก")

    if clv is not None:
        if clv >= 0.3:
            simple_notes.append("Close Location Value ดี: ราคาปิดใกล้ High แปลว่าผู้ซื้อคุมเกม")
        elif clv <= -0.3:
            simple_notes.append("Close Location Value อ่อน: ราคาปิดใกล้ Low แปลว่าผู้ขายคุมเกม")

    if pocket_count is not None and pocket_count >= 1:
        simple_notes.append(f"มี Pocket Pivot {int(pocket_count)} ครั้งใน 20 วัน: เป็นร่องรอยแรงซื้อคุณภาพ")

    if adl_div is not None and adl_div > 0:
        simple_notes.append("ADL bullish divergence: ราคาอ่อนแต่เส้นสะสมยังดี อาจมีการเก็บของเงียบ")
    elif adl_div is not None and adl_div < 0:
        simple_notes.append("ADL bearish divergence: ราคาไปต่อแต่เงินสะสมไม่ตาม ระวังขึ้นหลอก")

    if vpt_div is not None and vpt_div > 0:
        simple_notes.append("VPT bullish divergence: Volume ยังสนับสนุนแม้ราคายังอ่อน")
    elif vpt_div is not None and vpt_div < 0:
        simple_notes.append("VPT bearish divergence: ราคาแข็งแต่ volume ไม่หนุน ต้องระวัง")

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
