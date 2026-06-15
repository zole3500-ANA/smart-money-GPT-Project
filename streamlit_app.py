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

st.set_page_config(page_title="Smart Money Whale Agent v2.2", layout="wide")
st.title("🐋 Smart Money Whale Agent v2.2 — US Stocks")
st.caption("วิเคราะห์วาฬ / Smart Money จากราคา ปริมาณซื้อขาย VWAP CMF OBV ADL MFI VPT EMV dark-pool off-exchange options-flow 13F insider dark-pool short pressure และ relative strength")

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
    st.dataframe(indicator_df, use_container_width=True, hide_index=True)

    st.subheader("v2.1 Accumulation / Distribution Indicators")
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
    st.dataframe(pd.DataFrame(ad_rows), use_container_width=True, hide_index=True)

    st.subheader("v2.2 Dark Pool / Off-exchange Indicators")
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
    st.dataframe(pd.DataFrame(dark_rows), use_container_width=True, hide_index=True)

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
