
from smart_money_agent.scoring import insider_flow_score

def test_insider_score_bullish():
    score = insider_flow_score({
        "insider_net_buy_value_usd": 2_000_000,
        "insider_buy_count": 6,
        "insider_sell_count": 1,
        "ceo_cfo_transaction_count": 2,
        "ceo_cfo_net_buy_value_usd": 800_000,
        "cluster_buying_count": 3,
        "buy_size_vs_salary_ratio": 2.0,
        "option_exercise_then_sell_count": 0,
        "direct_open_market_buy_count": 4,
        "direct_open_market_buy_value_usd": 1_700_000,
    })
    assert score > 70

def test_insider_score_bearish():
    score = insider_flow_score({
        "insider_net_buy_value_usd": -2_500_000,
        "insider_buy_count": 0,
        "insider_sell_count": 9,
        "ceo_cfo_transaction_count": 3,
        "ceo_cfo_net_buy_value_usd": -1_200_000,
        "cluster_buying_count": 0,
        "buy_size_vs_salary_ratio": 0,
        "option_exercise_then_sell_count": 6,
        "direct_open_market_buy_count": 0,
        "direct_open_market_buy_value_usd": 0,
    })
    assert score < 40
