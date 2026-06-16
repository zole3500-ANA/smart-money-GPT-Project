from __future__ import annotations

import math
from typing import Any, Dict, Optional

from .schemas import SignalScore


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def sigmoid_score(x: float, midpoint: float = 0, scale: float = 1) -> float:
    try:
        return 100 / (1 + math.exp(-(x - midpoint) / scale))
    except OverflowError:
        return 100 if x > midpoint else 0


# -----------------------------
# Component scores
# -----------------------------

def smart_money_flow_score(ind: Dict[str, float]) -> float:
    score = 50
    volume_z = _num(ind.get("VolumeZ"))
    rel_volume = _num(ind.get("RelativeVolume30"), 1)
    cmf = _num(ind.get("CMF20"))
    mfi = ind.get("MFI14")
    close = ind.get("Close")
    vwap = ind.get("VWAP")
    return_1d = _num(ind.get("Return1D"))
    obv_trend = _num(ind.get("OBVTrend20"))
    adl_trend = _num(ind.get("ADLTrend20"))
    adl_divergence = _num(ind.get("ADLPriceDivergence20"))
    vpt_trend = _num(ind.get("VPTTrend20"))
    vpt_divergence = _num(ind.get("VPTPriceDivergence20"))
    ease_of_movement = _num(ind.get("EaseOfMovement14"))
    updown = _num(ind.get("UpDownVolumeRatio20"), 1)
    clv = _num(ind.get("CloseLocationValue"))
    pocket = _num(ind.get("PocketPivotProxy"))
    pocket_count = _num(ind.get("PocketPivotCount20"))
    accumulation_days = _num(ind.get("AccumulationDayCount25"))
    distribution_days = _num(ind.get("DistributionDayCount25"))
    net_accumulation_days = _num(ind.get("NetAccumulationDays25"))

    score += clamp(volume_z * 7, -20, 24)
    score += clamp((rel_volume - 1) * 12, -10, 18)
    score += clamp(cmf * 70, -22, 22)
    if mfi is not None:
        mfi = _num(mfi, 50)
        if 45 <= mfi <= 75:
            score += 6
        elif mfi > 85:
            score -= 5
        elif mfi < 25:
            score -= 5
    if close and vwap:
        score += 8 if close > vwap else -8
    if obv_trend > 0:
        score += 6
    elif obv_trend < 0:
        score -= 6
    if adl_trend > 0:
        score += 5
    elif adl_trend < 0:
        score -= 5
    if vpt_trend > 0:
        score += 5
    elif vpt_trend < 0:
        score -= 5
    if ease_of_movement > 0:
        score += 3
    elif ease_of_movement < 0:
        score -= 3
    if adl_divergence > 0 or vpt_divergence > 0:
        score += 7
    if adl_divergence < 0 or vpt_divergence < 0:
        score -= 7
    score += clamp((updown - 1) * 8, -8, 10)
    score += clamp(clv * 8, -8, 8)
    if volume_z > 2 and return_1d > 0:
        score += 10
    if volume_z > 2 and return_1d < -3:
        score -= 10
    if pocket > 0:
        score += 6
    score += clamp(pocket_count * 1.2, 0, 8)
    score += clamp(net_accumulation_days * 2.5, -12, 12)
    return clamp(score)


def technical_trend_score(ind: Dict[str, float]) -> float:
    score = 50
    close = ind.get("Close")
    sma20 = ind.get("SMA20")
    sma50 = ind.get("SMA50")
    sma200 = ind.get("SMA200")
    ema8 = ind.get("EMA8")
    ema21 = ind.get("EMA21")
    rsi = ind.get("RSI14")
    hist = _num(ind.get("macd_hist"))
    roc20 = _num(ind.get("ROC20"))
    slope20 = _num(ind.get("TrendSlope20"))
    slope50 = _num(ind.get("TrendSlope50"))
    breakout = _num(ind.get("Breakout20DFlag"))
    breakdown = _num(ind.get("Breakdown20DFlag"))

    if close and sma20:
        score += 6 if close > sma20 else -6
    if close and sma50:
        score += 10 if close > sma50 else -10
    if close and sma200:
        score += 12 if close > sma200 else -12
    if sma20 and sma50:
        score += 7 if sma20 > sma50 else -7
    if ema8 and ema21:
        score += 5 if ema8 > ema21 else -5
    if slope20 > 0:
        score += 5
    elif slope20 < 0:
        score -= 5
    if slope50 > 0:
        score += 5
    elif slope50 < 0:
        score -= 5
    if rsi is not None:
        rsi = _num(rsi, 50)
        if 45 <= rsi <= 65:
            score += 7
        elif 65 < rsi <= 75:
            score += 4
        elif rsi > 80:
            score -= 6
        elif rsi < 30:
            score -= 6
    score += clamp(hist * 50, -10, 10)
    score += clamp(roc20 * 0.7, -8, 10)
    if breakout > 0:
        score += 7
    if breakdown > 0:
        score -= 7
    return clamp(score)


def psychology_score(ind: Dict[str, float], sentiment: Optional[dict] = None) -> float:
    score = 50
    gap = _num(ind.get("GapPct"))
    ret = _num(ind.get("Return1D"))
    intraday = _num(ind.get("IntradayReturnPct"))
    atr_pct = _num(ind.get("ATRPercent"))
    rsi = ind.get("RSI14")
    volume_z = _num(ind.get("VolumeZ"))
    sentiment = sentiment or {}

    if gap > 3 and ret > 0:
        score += 10
    elif gap > 3 and ret < 0:
        score -= 12
    elif gap < -3 and ret > 0:
        score += 9
    elif gap < -3 and ret < 0:
        score -= 9
    if intraday > 2:
        score += 5
    elif intraday < -2:
        score -= 5
    if atr_pct > 8:
        score -= 8
    elif 2 <= atr_pct <= 5:
        score += 4
    if rsi is not None:
        rsi = _num(rsi, 50)
        if rsi > 82:
            score -= 9
        elif rsi < 25 and ret > 0:
            score += 6
        elif rsi < 25:
            score -= 5
    if volume_z > 3 and ret > 0:
        score += 6
    elif volume_z > 3 and ret < 0:
        score -= 6

    score += clamp(_num(sentiment.get("news_sentiment_score")) * 18, -12, 12)
    score += clamp(_num(sentiment.get("social_sentiment_score")) * 12, -8, 8)
    score += clamp(_num(sentiment.get("mention_volume_zscore")) * 3, -6, 9)
    score += clamp(_num(sentiment.get("analyst_revision_score")) * 18, -10, 10)
    return clamp(score)


def short_pressure_score(short_ratio: Optional[float], optional: Optional[dict] = None, ind: Optional[dict] = None) -> float:
    optional = optional or {}
    ind = ind or {}
    score = 50

    if short_ratio is not None:
        # High daily short volume is a negative pressure unless price is resisting strongly.
        score += clamp(20 - _num(short_ratio) * 45, -25, 20)

    short_float = optional.get("short_interest_pct_float")
    days_to_cover = optional.get("days_to_cover")
    borrow_fee = optional.get("borrow_fee_rate_pct")
    short_change = optional.get("short_interest_change_pct")
    ftd_value = optional.get("fails_to_deliver_value_usd")
    price_resilience = _num(ind.get("Return5D")) > 0 and _num(ind.get("CMF20")) > 0

    if short_float is not None:
        short_float = _num(short_float)
        if short_float > 20 and price_resilience:
            score += 12  # squeeze setup
        elif short_float > 20:
            score -= 12
        elif short_float > 10 and price_resilience:
            score += 6
        elif short_float > 10:
            score -= 5
    if days_to_cover is not None:
        dtc = _num(days_to_cover)
        if dtc > 5 and price_resilience:
            score += 9
        elif dtc > 5:
            score -= 7
    if borrow_fee is not None:
        fee = _num(borrow_fee)
        if fee > 10 and price_resilience:
            score += 7
        elif fee > 10:
            score -= 5
    if short_change is not None:
        score += clamp(-_num(short_change) * 1.2, -8, 8)
    if ftd_value is not None and _num(ftd_value) > 1_000_000:
        score -= 4
    return clamp(score)


def fundamental_quality_score(facts: Optional[dict]) -> float:
    if not facts:
        return 50
    score = 50
    revenue_growth = facts.get("revenue_growth")
    net_margin = facts.get("net_margin")
    debt_to_assets = facts.get("debt_to_assets")
    if revenue_growth is not None:
        score += clamp(_num(revenue_growth) * 80, -15, 20)
    if net_margin is not None:
        score += clamp(_num(net_margin) * 100, -20, 20)
    if debt_to_assets is not None:
        score -= clamp((_num(debt_to_assets) - 0.5) * 50, -10, 15)
    return clamp(score)


def options_flow_score(options: Optional[dict]) -> float:
    """Score short-term whale options flow from optional options-flow feed.

    Higher score = options tape supports bullish/accumulation setup.
    Lower score = put-heavy, bearish aggressor, or negative gamma setup.
    """
    if not options:
        return 50

    score = 50

    unusual_volume = _num(options.get("unusual_options_volume"))
    unusual_volume_z = _num(options.get("unusual_options_volume_z"))
    call_volume = _num(options.get("call_volume"))
    put_volume = _num(options.get("put_volume"))
    call_put_ratio = options.get("call_put_volume_ratio")
    put_call_ratio = options.get("put_call_ratio")
    options_vol_oi = _num(options.get("options_volume_open_interest_ratio"))
    sweep_count = _num(options.get("sweep_order_count", options.get("sweep_count")))
    sweep_premium = _num(options.get("sweep_premium_usd"))
    block_trade_count = _num(options.get("options_block_trade_count", options.get("block_trade_count")))
    block_premium = _num(options.get("block_trade_premium_usd"))
    premium_paid = _num(options.get("premium_paid_usd", options.get("premium_usd")))
    aggressor_side = str(options.get("aggressor_side", "")).lower().strip()
    near_term_call_premium = _num(options.get("near_term_call_premium_usd"))
    near_term_put_premium = _num(options.get("near_term_put_premium_usd"))
    leaps_call_premium = _num(options.get("leaps_call_premium_usd"))
    leaps_put_premium = _num(options.get("leaps_put_premium_usd"))
    otm_call_premium = _num(options.get("otm_call_premium_usd"))
    otm_put_premium = _num(options.get("otm_put_premium_usd"))
    gamma_exposure = _num(options.get("gamma_exposure", options.get("dealer_gamma_exposure")))
    gamma_exposure_pct_float = _num(options.get("gamma_exposure_pct_float"))
    bullish_premium_ratio = options.get("bullish_premium_ratio")

    if call_put_ratio is None and put_volume > 0:
        call_put_ratio = call_volume / put_volume
    call_put_ratio = _num(call_put_ratio, 1)

    if put_call_ratio is None and call_volume > 0:
        put_call_ratio = put_volume / call_volume
    put_call_ratio = _num(put_call_ratio, 1)

    if bullish_premium_ratio is None:
        bullish_premium = near_term_call_premium + leaps_call_premium + otm_call_premium
        bearish_premium = near_term_put_premium + leaps_put_premium + otm_put_premium
        if bullish_premium + bearish_premium > 0:
            bullish_premium_ratio = bullish_premium / (bullish_premium + bearish_premium)
    bullish_premium_ratio = _num(bullish_premium_ratio, 0.5)

    # Unusual options activity.
    score += clamp(unusual_volume_z * 4, -8, 18)
    if unusual_volume > 0:
        score += clamp(math.log10(unusual_volume + 1) - 4, 0, 8)

    # Direction from calls vs puts.
    score += clamp((call_put_ratio - 1) * 9, -16, 18)
    score -= clamp((put_call_ratio - 1) * 8, -8, 18)

    # Volume/OI > 1 often means new positions are being opened.
    if options_vol_oi >= 2:
        score += 8
    elif options_vol_oi >= 1:
        score += 5
    elif options_vol_oi > 0 and options_vol_oi < 0.5:
        score -= 2

    # Sweeps imply urgency. Bias comes from aggressor/premium mix.
    score += clamp(sweep_count * 0.9, 0, 12)
    if sweep_premium > 0:
        score += clamp(math.log10(sweep_premium + 1) - 5, 0, 10)

    # Block trades = large money, but direction must be inferred.
    score += clamp(block_trade_count * 0.5, 0, 8)
    if block_premium > 0:
        score += clamp(math.log10(block_premium + 1) - 5, 0, 8)

    if premium_paid > 0:
        score += clamp(math.log10(premium_paid + 1) - 5.5, 0, 12)

    # Aggressor side: ask = buyer-initiated, bid = seller-initiated.
    if aggressor_side in {"ask", "buy", "buyer", "bought_at_ask"}:
        score += 10
    elif aggressor_side in {"bid", "sell", "seller", "sold_at_bid"}:
        score -= 10
    elif aggressor_side in {"mid", "neutral"}:
        score += 0

    # Premium mix.
    score += clamp((bullish_premium_ratio - 0.5) * 35, -18, 18)

    # Near-term calls are speculative bullish. Near-term puts can be hedge or bearish.
    if near_term_call_premium + near_term_put_premium > 0:
        nt_bias = (near_term_call_premium - near_term_put_premium) / max(near_term_call_premium + near_term_put_premium, 1)
        score += clamp(nt_bias * 10, -10, 10)

    # LEAPS call premium supports long-term bullish view.
    if leaps_call_premium + leaps_put_premium > 0:
        leaps_bias = (leaps_call_premium - leaps_put_premium) / max(leaps_call_premium + leaps_put_premium, 1)
        score += clamp(leaps_bias * 8, -8, 8)

    # OTM calls can signal upside speculation; OTM puts can signal downside speculation/hedge.
    if otm_call_premium + otm_put_premium > 0:
        otm_bias = (otm_call_premium - otm_put_premium) / max(otm_call_premium + otm_put_premium, 1)
        score += clamp(otm_bias * 10, -10, 10)

    # Gamma exposure: positive can dampen moves, negative can amplify volatility.
    if gamma_exposure > 0:
        score += 3
    elif gamma_exposure < 0:
        score -= 3

    if gamma_exposure_pct_float != 0:
        score += clamp(gamma_exposure_pct_float * 0.5, -6, 6)

    # Combination rules.
    if sweep_count >= 5 and aggressor_side in {"ask", "buy", "buyer", "bought_at_ask"} and call_put_ratio > 1.5:
        score += 8
    if put_call_ratio > 1.5 and aggressor_side in {"bid", "sell", "seller", "sold_at_bid"}:
        score -= 8
    if options_vol_oi >= 2 and call_put_ratio > 1.5 and premium_paid > 1_000_000:
        score += 8
    if options_vol_oi >= 2 and put_call_ratio > 1.5 and premium_paid > 1_000_000:
        score -= 8

    return clamp(score)


def institutional_flow_score(institutional: Optional[dict]) -> float:
    """Score institutional / whale ownership flow from optional 13F-style feed."""
    if not institutional:
        return 50

    score = 50

    # Backward compatible keys + v2.3 keys
    net_flow_pct = _num(
        institutional.get("net_institutional_flow_pct",
        institutional.get("thirteen_f_net_shares_change_pct"))
    )
    net_flow_value = _num(institutional.get("net_institutional_flow_value_usd"))
    new_positions = _num(
        institutional.get("new_positions_count",
        institutional.get("new_institutional_positions"))
    )
    increased_positions = _num(
        institutional.get("increased_positions_count",
        institutional.get("increased_positions"))
    )
    decreased_positions = _num(
        institutional.get("decreased_positions_count",
        institutional.get("decreased_positions"))
    )
    sold_out_positions = _num(
        institutional.get("sold_out_positions_count",
        institutional.get("sold_out_positions"))
    )
    top10_concentration = _num(institutional.get("top10_holder_concentration_pct"))
    ownership_pct = _num(institutional.get("institutional_ownership_pct"))
    qoq_change_pct = _num(institutional.get("qoq_holding_change_pct"))
    whale_acc_score = _num(institutional.get("whale_accumulation_score"))

    if abs(net_flow_pct) <= 1 and net_flow_pct != 0:
        net_flow_pct *= 100
    if abs(top10_concentration) <= 1 and top10_concentration != 0:
        top10_concentration *= 100
    if abs(ownership_pct) <= 1 and ownership_pct != 0:
        ownership_pct *= 100
    if abs(qoq_change_pct) <= 1 and qoq_change_pct != 0:
        qoq_change_pct *= 100

    score += clamp(net_flow_pct * 1.2, -18, 18)
    if net_flow_value != 0:
        score += clamp((math.log10(abs(net_flow_value) + 1) - 6) * (1 if net_flow_value > 0 else -1), -8, 8)

    score += clamp(new_positions * 0.9, 0, 10)
    score += clamp(increased_positions * 0.45, 0, 12)
    score -= clamp(decreased_positions * 0.45, 0, 12)
    score -= clamp(sold_out_positions * 0.8, 0, 14)

    if ownership_pct >= 35:
        score += 7
    elif ownership_pct >= 15:
        score += 4
    elif ownership_pct > 0 and ownership_pct < 8:
        score -= 3

    if top10_concentration >= 55:
        score -= 1  # sponsor benefit but concentration risk
    elif top10_concentration >= 25:
        score += 4

    score += clamp(qoq_change_pct * 1.1, -15, 15)

    if whale_acc_score:
        if whale_acc_score <= 1:
            whale_acc_score *= 100
        score += clamp((whale_acc_score - 50) * 0.35, -18, 18)

    if net_flow_pct > 0 and increased_positions > decreased_positions and qoq_change_pct > 0:
        score += 8
    if net_flow_pct < 0 and decreased_positions + sold_out_positions > increased_positions:
        score -= 8
    if new_positions >= 5 and qoq_change_pct > 0:
        score += 4
    if sold_out_positions >= 5 and qoq_change_pct < 0:
        score -= 5

    return clamp(score)


def insider_flow_score(insider: Optional[dict]) -> float:
    """Score insider trading behavior from optional Form 4 / insider transaction feed.

    Higher score = insider behavior supports accumulation.
    Lower score = insider selling or weak insider sponsorship.
    """
    if not insider:
        return 50

    score = 50

    # Backward-compatible keys + v2.4 keys
    net_buy_value = _num(insider.get("insider_net_buy_value_usd", insider.get("net_buy_value_usd")))
    buy_count = _num(insider.get("insider_buy_count", insider.get("buy_count")))
    sell_count = _num(insider.get("insider_sell_count", insider.get("sell_count")))
    ceo_cfo_net_buy_value = _num(insider.get("ceo_cfo_net_buy_value_usd"))
    ceo_cfo_transaction_count = _num(insider.get("ceo_cfo_transaction_count"))
    cluster_buying_count = _num(insider.get("cluster_buying_count"))
    buy_size_vs_salary = _num(insider.get("buy_size_vs_salary_ratio"))
    option_exercise_then_sell_count = _num(insider.get("option_exercise_then_sell_count"))
    direct_open_market_buy_count = _num(insider.get("direct_open_market_buy_count"))
    direct_open_market_buy_value = _num(insider.get("direct_open_market_buy_value_usd"))

    if net_buy_value != 0:
        score += clamp((math.log10(abs(net_buy_value) + 1) - 5) * (1 if net_buy_value > 0 else -1) * 4, -22, 22)

    if buy_count + sell_count > 0:
        score += clamp((buy_count - sell_count) / max(buy_count + sell_count, 1) * 18, -18, 18)

    if ceo_cfo_net_buy_value != 0:
        score += clamp((math.log10(abs(ceo_cfo_net_buy_value) + 1) - 4.7) * (1 if ceo_cfo_net_buy_value > 0 else -1) * 3.5, -16, 16)

    # Senior executive transactions matter more than ordinary officers.
    if ceo_cfo_transaction_count > 0 and ceo_cfo_net_buy_value > 0:
        score += clamp(ceo_cfo_transaction_count * 1.5, 0, 8)
    elif ceo_cfo_transaction_count > 0 and ceo_cfo_net_buy_value < 0:
        score -= clamp(ceo_cfo_transaction_count * 1.5, 0, 8)

    score += clamp(cluster_buying_count * 3.0, 0, 18)
    score += clamp(buy_size_vs_salary * 5.0, 0, 15)

    # Exercise-then-sell is not always bearish, so penalize lightly.
    score -= clamp(option_exercise_then_sell_count * 1.2, 0, 8)

    # Direct open market buys are the highest-quality insider signal.
    score += clamp(direct_open_market_buy_count * 3.0, 0, 18)
    if direct_open_market_buy_value > 0:
        score += clamp((math.log10(direct_open_market_buy_value + 1) - 5) * 4, 0, 16)

    # Combination rules.
    if cluster_buying_count >= 2 and direct_open_market_buy_count >= 1 and net_buy_value > 0:
        score += 10
    if sell_count >= 5 and buy_count == 0 and net_buy_value < 0:
        score -= 10
    if ceo_cfo_net_buy_value > 0 and direct_open_market_buy_value > 0:
        score += 6
    if ceo_cfo_net_buy_value < 0 and sell_count > buy_count:
        score -= 6

    return clamp(score)


def dark_pool_flow_score(dark: Optional[dict]) -> float:
    """Score dark-pool / off-exchange activity.

    Higher score means the dark-pool tape is more constructive.
    It is not automatically bullish when off-exchange volume is high;
    the score needs bias, block price vs VWAP, repeated prints, and trend confirmation.
    """
    if not dark:
        return 50

    score = 50

    dark_volume = _num(dark.get("dark_pool_volume"))
    total_volume = _num(dark.get("total_volume"))
    ratio = dark.get("dark_pool_volume_ratio")
    if ratio is None:
        ratio = dark.get("dark_pool_pct_total_volume")
    if ratio is None and total_volume > 0:
        ratio = dark_volume / total_volume
    ratio = _num(ratio, 0)

    # Allow either 0.42 or 42 as user input.
    if ratio > 1.5:
        ratio = ratio / 100

    block_count = _num(dark.get("large_block_trade_count"))
    block_volume = _num(dark.get("large_block_volume"))
    block_value = _num(dark.get("large_block_value_usd"))
    largest_block_value = _num(dark.get("largest_block_value_usd"))
    block_price_vs_vwap = _num(dark.get("block_price_vs_vwap_pct"))
    repeated_count = _num(dark.get("repeated_print_count"))
    repeated_ratio = _num(dark.get("repeated_print_ratio"))
    off_ex_trend_5d = _num(dark.get("off_exchange_trend_5d"))
    off_ex_trend_20d = _num(dark.get("off_exchange_trend_20d"))

    net_bias = dark.get("dark_pool_net_bias")
    if net_bias is None:
        buy_volume = _num(dark.get("dark_pool_buy_volume"))
        sell_volume = _num(dark.get("dark_pool_sell_volume"))
        if buy_volume + sell_volume > 0:
            net_bias = (buy_volume - sell_volume) / (buy_volume + sell_volume)
    net_bias = _num(net_bias)

    # High off-exchange participation is notable but neutral without directional evidence.
    if ratio >= 0.60:
        score += 4
    elif ratio >= 0.45:
        score += 2
    elif ratio < 0.15 and ratio > 0:
        score -= 2

    # Large block prints = whale activity. Direction comes from VWAP/bias.
    score += clamp(block_count * 0.7, 0, 12)
    if block_value > 0:
        score += clamp(math.log10(max(block_value, 1)) - 6, 0, 8)
    if largest_block_value > 0:
        score += clamp((math.log10(max(largest_block_value, 1)) - 5.7) * 0.8, 0, 6)
    if block_volume > 0 and dark_volume > 0:
        score += clamp((block_volume / max(dark_volume, 1)) * 8, 0, 8)

    # Price above VWAP suggests buyers were willing to pay up; below VWAP is bearish bias.
    score += clamp(block_price_vs_vwap * 9, -15, 15)

    # Repeated prints can mean accumulation/distribution. Give small activity credit,
    # then let net bias and VWAP decide direction.
    score += clamp(repeated_count * 0.5, 0, 8)
    if repeated_ratio > 1.5:
        repeated_ratio = repeated_ratio / 100
    score += clamp(repeated_ratio * 10, 0, 8)

    # Trend in off-exchange activity. Positive trend with positive bias is constructive;
    # positive trend with negative bias can mean hidden selling.
    if off_ex_trend_5d > 0 or off_ex_trend_20d > 0:
        if net_bias > 0:
            score += clamp((off_ex_trend_5d + off_ex_trend_20d) * 0.35, 0, 10)
        elif net_bias < 0:
            score -= clamp((off_ex_trend_5d + off_ex_trend_20d) * 0.35, 0, 10)

    score += clamp(net_bias * 25, -25, 25)

    # Combination rules.
    if ratio >= 0.45 and block_price_vs_vwap > 0 and net_bias > 0:
        score += 8
    if ratio >= 0.45 and block_price_vs_vwap < 0 and net_bias < 0:
        score -= 8
    if repeated_count >= 5 and net_bias > 0 and block_price_vs_vwap > 0:
        score += 6
    if repeated_count >= 5 and net_bias < 0 and block_price_vs_vwap < 0:
        score -= 6

    return clamp(score)


def relative_strength_score(ind: Dict[str, float]) -> float:
    score = 50
    spy20 = ind.get("RS_SPY_Return20DSpread")
    spy60 = ind.get("RS_SPY_Return60DSpread")
    qqq20 = ind.get("RS_QQQ_Return20DSpread")
    qqq60 = ind.get("RS_QQQ_Return60DSpread")
    for value, weight in [(spy20, 1.6), (spy60, 1.0), (qqq20, 1.1), (qqq60, 0.7)]:
        if value is not None:
            score += clamp(_num(value) * weight, -12, 12)
    if _num(ind.get("RS_SPY_Trend20")) > 0:
        score += 5
    if _num(ind.get("RS_QQQ_Trend20")) > 0:
        score += 3
    return clamp(score)


def catalyst_risk_score(catalyst: Optional[dict], filings: Optional[list] = None) -> float:
    # Higher score means cleaner catalyst profile; lower score means more risk.
    score = 50
    catalyst = catalyst or {}
    filings = filings or []
    days_to_earnings = catalyst.get("days_to_earnings")
    if days_to_earnings is not None:
        days = _num(days_to_earnings)
        if 0 <= days <= 7:
            score -= 8
        elif 8 <= days <= 30:
            score += 3
    score += clamp(_num(catalyst.get("earnings_surprise_pct")) * 0.8, -12, 12)
    score += clamp(_num(catalyst.get("guidance_revision_score")) * 20, -15, 15)
    if _num(catalyst.get("offering_risk_flag")) > 0:
        score -= 18
    if _num(catalyst.get("lawsuit_risk_flag")) > 0:
        score -= 10
    if _num(catalyst.get("ma_rumor_flag")) > 0:
        score += 4

    risky_forms = {"S-1", "S-3", "424B5", "424B3", "8-K"}
    for filing in filings[:10]:
        form = str(filing.get("form", "")).upper()
        if form in risky_forms:
            score -= 2 if form == "8-K" else 6
    return clamp(score)


# -----------------------------
# Composite
# -----------------------------

def composite_score(
    indicators: dict,
    facts: Optional[dict],
    short_ratio: Optional[float],
    weights: Optional[dict] = None,
    optional_feeds: Optional[dict] = None,
    filings: Optional[list] = None,
) -> SignalScore:
    optional_feeds = optional_feeds or {}
    weights = weights or {
        "smart_money_flow": 0.23,
        "technical_trend": 0.15,
        "options_flow": 0.14,
        "short_pressure": 0.10,
        "fundamental_quality": 0.10,
        "institutional_flow": 0.09,
        "insider_flow": 0.05,
        "dark_pool_flow": 0.05,
        "relative_strength": 0.04,
        "psychology": 0.02,
        "catalyst_risk": 0.02,
    }

    sm = smart_money_flow_score(indicators)
    tech = technical_trend_score(indicators)
    opt = options_flow_score(optional_feeds.get("options_flow"))
    sp = short_pressure_score(short_ratio, optional_feeds.get("short_interest"), indicators)
    fund = fundamental_quality_score(facts)
    inst = institutional_flow_score(optional_feeds.get("institutional_flow"))
    insider = insider_flow_score(optional_feeds.get("insider_flow"))
    dark = dark_pool_flow_score(optional_feeds.get("dark_pool"))
    rel = relative_strength_score(indicators)
    psy = psychology_score(indicators, optional_feeds.get("sentiment"))
    cat = catalyst_risk_score(optional_feeds.get("catalyst"), filings)

    components = {
        "smart_money_flow": sm,
        "technical_trend": tech,
        "options_flow": opt,
        "short_pressure": sp,
        "fundamental_quality": fund,
        "institutional_flow": inst,
        "insider_flow": insider,
        "dark_pool_flow": dark,
        "relative_strength": rel,
        "psychology": psy,
        "catalyst_risk": cat,
    }
    total_weight = sum(weights.get(k, 0) for k in components) or 1
    composite = sum(components[k] * weights.get(k, 0) for k in components) / total_weight
    label = "Bullish" if composite >= 65 else "Bearish" if composite <= 35 else "Neutral"
    return SignalScore(
        smart_money_flow=round(sm, 2),
        technical_trend=round(tech, 2),
        options_flow=round(opt, 2),
        short_pressure=round(sp, 2),
        fundamental_quality=round(fund, 2),
        institutional_flow=round(inst, 2),
        insider_flow=round(insider, 2),
        dark_pool_flow=round(dark, 2),
        relative_strength=round(rel, 2),
        psychology=round(psy, 2),
        catalyst_risk=round(cat, 2),
        composite=round(clamp(composite), 2),
        label=label,
    )
