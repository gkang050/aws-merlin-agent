from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
from uuid import uuid4

from boto3.dynamodb.conditions import Attr

from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.utils import aws, logging

logger = logging.get_logger(__name__)


def register_model(artifact_uri: str, metrics: Dict[str, float], model_type: str = "demand_forecast") -> str:
    """Persist model metadata to the runs DynamoDB table and return the model identifier."""
    settings = EnvironmentSettings.load()
    dynamodb = aws.resource("dynamodb", region_name=settings.region)
    table = dynamodb.Table(settings.dynamodb_table_runs)

    model_id = str(uuid4())
    safe_metrics: Dict[str, Decimal] = {}
    for key, value in metrics.items():
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            logger.warning("Skipping non-numeric metric %s=%s", key, value)
            continue
        if not numeric == numeric or numeric in (float("inf"), float("-inf")):  # NaN/Inf check
            logger.warning("Skipping non-finite metric %s=%s", key, value)
            continue
        safe_metrics[key] = Decimal(str(round(numeric, 6)))

    item = {
        "run_id": model_id,
        "model_type": model_type,
        "artifact_uri": artifact_uri,
        "metrics": safe_metrics,
        "created_at": datetime.utcnow().isoformat(),
    }
    table.put_item(Item=item)
    logger.info("Registered model %s with metrics %s", model_id, metrics)
    return model_id


def latest_model(model_type: str = "demand_forecast") -> Optional[Dict]:
    """Fetch the most recent model metadata for the given type."""
    settings = EnvironmentSettings.load()
    dynamodb = aws.resource("dynamodb", region_name=settings.region)
    table = dynamodb.Table(settings.dynamodb_table_runs)
    response = table.scan(FilterExpression=Attr("model_type").eq(model_type))
    items = response.get("Items", [])
    if not items:
        return None
    return max(items, key=lambda item: item.get("created_at", ""))
