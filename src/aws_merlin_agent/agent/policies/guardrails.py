from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ActionThresholds:
    """Centralized thresholds for autonomous price and bid actions."""

    price_delta_pct: float = 10.0
    bid_delta_pct: float = 20.0
    confidence_threshold: float = 0.7


DEFAULT_THRESHOLDS = ActionThresholds()


def is_price_change_allowed(current: float, proposed: float, thresholds: ActionThresholds = DEFAULT_THRESHOLDS) -> bool:
    if current <= 0:
        return False
    delta_pct = abs(proposed - current) / current * 100
    return delta_pct <= thresholds.price_delta_pct


def is_bid_change_allowed(current: float, proposed: float, thresholds: ActionThresholds = DEFAULT_THRESHOLDS) -> bool:
    if current <= 0:
        return False
    delta_pct = abs(proposed - current) / current * 100
    return delta_pct <= thresholds.bid_delta_pct
