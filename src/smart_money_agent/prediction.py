from __future__ import annotations

from typing import Dict

from .schemas import Forecast, SignalScore


def forecast_next_day(ticker: str, indicators: Dict[str, float], score: SignalScore) -> Forecast:
    composite = score.composite

    # Convert composite score to a calibrated, conservative directional probability.
    # This intentionally avoids extreme certainty because a one-day forecast is noisy.
    probability_up = 0.5 + (composite - 50) / 140
    probability_up = max(0.08, min(0.92, probability_up))

    close = indicators.get("Close")
    atr = indicators.get("ATR14")
    atr_pct = indicators.get("ATRPercent")
    expected_low = expected_high = None

    if close and atr:
        confidence = abs(probability_up - 0.5) * 2
        direction = 1 if probability_up >= 0.5 else -1
        center = close + direction * atr * 0.18 * confidence
        expected_low = round(center - atr, 2)
        expected_high = round(center + atr, 2)

    if probability_up >= 0.60:
        bias = "Bullish / โอกาสบวกมากกว่า"
    elif probability_up <= 0.40:
        bias = "Bearish / โอกาสลบมากกว่า"
    else:
        bias = "Neutral / ยังไม่ชัดเจน"

    notes = []
    rsi = indicators.get("RSI14")
    volume_z = indicators.get("VolumeZ")
    gap = indicators.get("GapPct")
    if rsi and rsi > 78:
        notes.append("RSI สูงมาก อาจมีแรงขายทำกำไรระยะสั้น")
    if rsi and rsi < 28:
        notes.append("RSI ต่ำมาก อาจเด้งได้แต่ยังเสี่ยงถ้าไม่มี volume ยืนยัน")
    if volume_z and volume_z > 2:
        notes.append("ปริมาณซื้อขายผิดปกติ ควรตรวจข่าว/filing/options flow ประกอบ")
    if atr_pct and atr_pct > 8:
        notes.append("ATR% สูงมาก กรอบคาดการณ์กว้างและความเสี่ยงสูง")
    if gap and abs(gap) > 4:
        notes.append("มี gap แรง ควรระวัง bull trap หรือ panic reversal")
    if score.label == "Neutral":
        notes.append("คะแนนรวมอยู่โซนกลาง ควรลดความมั่นใจในการพยากรณ์")

    return Forecast(
        ticker=ticker.upper(),
        next_day_bias=bias,
        probability_up=round(probability_up, 3),
        expected_range_low=expected_low,
        expected_range_high=expected_high,
        risk_notes=notes,
    )
