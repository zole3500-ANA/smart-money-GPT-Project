
from smart_money_agent.scoring import institutional_flow_score

def test_institutional_score_bullish():
    score = institutional_flow_score({
        "net_institutional_flow_pct": 4.5,
        "new_positions_count": 7,
        "increased_positions_count": 22,
        "decreased_positions_count": 8,
        "sold_out_positions_count": 1,
        "top10_holder_concentration_pct": 36,
        "institutional_ownership_pct": 42,
        "qoq_holding_change_pct": 5.2,
        "whale_accumulation_score": 72,
    })
    assert score > 60

def test_institutional_score_bearish():
    score = institutional_flow_score({
        "net_institutional_flow_pct": -6.0,
        "new_positions_count": 1,
        "increased_positions_count": 4,
        "decreased_positions_count": 20,
        "sold_out_positions_count": 8,
        "top10_holder_concentration_pct": 12,
        "institutional_ownership_pct": 9,
        "qoq_holding_change_pct": -7.5,
        "whale_accumulation_score": 28,
    })
    assert score < 45
