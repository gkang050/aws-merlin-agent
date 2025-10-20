from aws_merlin_agent.agent.policies.guardrails import (
    ActionThresholds,
    is_bid_change_allowed,
    is_price_change_allowed,
)


def test_price_guardrail_within_threshold():
    assert is_price_change_allowed(100.0, 107.0, ActionThresholds(price_delta_pct=10))


def test_price_guardrail_exceeds_threshold():
    assert not is_price_change_allowed(100.0, 120.0, ActionThresholds(price_delta_pct=10))


def test_bid_guardrail_within_threshold():
    assert is_bid_change_allowed(1.0, 1.15, ActionThresholds(bid_delta_pct=20))
