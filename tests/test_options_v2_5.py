
from smart_money_agent.scoring import options_flow_score

def test_options_score_bullish():
    score = options_flow_score({
        "unusual_options_volume": 185000,
        "unusual_options_volume_z": 4.2,
        "call_volume": 132000,
        "put_volume": 53000,
        "call_put_volume_ratio": 2.49,
        "put_call_ratio": 0.40,
        "options_volume_open_interest_ratio": 2.15,
        "sweep_order_count": 18,
        "sweep_premium_usd": 3250000,
        "options_block_trade_count": 11,
        "premium_paid_usd": 7200000,
        "aggressor_side": "ask",
        "near_term_call_premium_usd": 2600000,
        "near_term_put_premium_usd": 900000,
        "leaps_call_premium_usd": 1800000,
        "leaps_put_premium_usd": 550000,
        "otm_call_premium_usd": 2300000,
        "otm_put_premium_usd": 750000,
        "gamma_exposure": 12500000,
    })
    assert score > 70

def test_options_score_bearish():
    score = options_flow_score({
        "unusual_options_volume": 160000,
        "unusual_options_volume_z": 3.8,
        "call_volume": 40000,
        "put_volume": 140000,
        "call_put_volume_ratio": 0.28,
        "put_call_ratio": 3.5,
        "options_volume_open_interest_ratio": 2.4,
        "sweep_order_count": 14,
        "premium_paid_usd": 6500000,
        "aggressor_side": "bid",
        "near_term_call_premium_usd": 500000,
        "near_term_put_premium_usd": 3000000,
        "leaps_call_premium_usd": 400000,
        "leaps_put_premium_usd": 2200000,
        "otm_call_premium_usd": 300000,
        "otm_put_premium_usd": 2800000,
        "gamma_exposure": -9000000,
    })
    assert score < 45
