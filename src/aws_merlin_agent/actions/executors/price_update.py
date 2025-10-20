from __future__ import annotations

import json
from decimal import Decimal
from typing import Dict

from aws_merlin_agent.agent.policies.guardrails import is_price_change_allowed
from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.utils import aws, logging

logger = logging.get_logger(__name__)


def handler(event: Dict, _context) -> Dict:
    """Lambda entry point that applies price updates after guardrail validation."""
    settings = EnvironmentSettings.load()
    dynamodb = aws.resource("dynamodb", region_name=settings.region)
    table = dynamodb.Table(settings.dynamodb_table_actions)

    payload = event.get("detail", {})
    current_price = Decimal(str(payload.get("current_price", "0")))
    proposed_price = Decimal(str(payload.get("proposed_price", "0")))
    sku = payload.get("sku")

    if not sku or not is_price_change_allowed(float(current_price), float(proposed_price)):
        logger.warning("Rejected price change for sku=%s current=%s proposed=%s", sku, current_price, proposed_price)
        return {"status": "rejected", "reason": "guardrail_violation"}

    logger.info("Applying price change for sku=%s", sku)
    # Placeholder: integrate with seller pricing API.

    table.put_item(
        Item={
            "action_id": payload.get("action_id"),
            "sku": sku,
            "type": "price_update",
            "current_price": str(current_price),
            "proposed_price": str(proposed_price),
            "status": "applied",
        }
    )
    return {"status": "applied", "payload": json.dumps(payload)}
