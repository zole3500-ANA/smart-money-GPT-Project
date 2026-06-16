
from smart_money_agent.data_sources.public_free import has_payload, merge_optional_feeds

def test_has_payload_ignores_empty_and_meta():
    assert not has_payload({})
    assert not has_payload({"_meta": {"x": 1}})
    assert not has_payload({"a": None, "b": ""})
    assert has_payload({"a": 1})

def test_merge_optional_feeds_local_wins_and_public_fills():
    local = {"options_flow": {"call_put_volume_ratio": 2.0}, "institutional_flow": {}, "_meta": {"options_flow": {"confidence": 0.8}}}
    public = {"options_flow": {"call_put_volume_ratio": 1.2}, "institutional_flow": {"institutional_ownership_pct": 30}, "_meta": {"institutional_flow": {"confidence": 0.4}}}
    merged = merge_optional_feeds(local, public)
    assert merged["options_flow"]["call_put_volume_ratio"] == 2.0
    assert merged["institutional_flow"]["institutional_ownership_pct"] == 30
    assert merged["_meta"]["institutional_flow"]["confidence"] == 0.4
