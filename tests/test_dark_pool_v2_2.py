
from smart_money_agent.scoring import dark_pool_flow_score


def test_dark_pool_score_bullish_setup():
    score = dark_pool_flow_score({
        "dark_pool_volume": 4_200_000,
        "total_volume": 10_000_000,
        "dark_pool_volume_ratio": 0.42,
        "large_block_trade_count": 14,
        "large_block_value_usd": 8_250_000,
        "block_price_vs_vwap_pct": 0.35,
        "repeated_print_count": 6,
        "off_exchange_trend_5d": 6.5,
        "off_exchange_trend_20d": 12.0,
        "dark_pool_net_bias": 0.24,
    })
    assert score > 55


def test_dark_pool_score_bearish_setup():
    score = dark_pool_flow_score({
        "dark_pool_volume_ratio": 0.58,
        "large_block_trade_count": 10,
        "block_price_vs_vwap_pct": -1.2,
        "repeated_print_count": 8,
        "off_exchange_trend_5d": 8.0,
        "off_exchange_trend_20d": 15.0,
        "dark_pool_net_bias": -0.35,
    })
    assert score < 50
