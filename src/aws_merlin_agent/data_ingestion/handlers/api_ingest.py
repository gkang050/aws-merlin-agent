from __future__ import annotations

import json

from base64 import b64decode
from datetime import datetime
from typing import List

from aws_lambda_powertools.utilities.typing import LambdaContext  # type: ignore[import-untyped]

from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.data_ingestion.schemas.sales import SalesRecord
from aws_merlin_agent.utils import aws, logging

logger = logging.get_logger(__name__)


def handler(event: dict, context: LambdaContext) -> dict:
    """
    Validate inbound seller datasets delivered through API Gateway and stage them into the landing bucket.

    This function is intentionally lightweight; heavy lifting is deferred to AWS Glue jobs.
    """
    seller_id = event.get("pathParameters", {}).get("sellerId", "unknown")
    body = event.get("body")
    if not body:
        logger.error("Empty payload for seller %s", seller_id)
        return {"statusCode": 400, "body": json.dumps({"error": "empty payload"})}

    if event.get("isBase64Encoded"):
        body = b64decode(body).decode("utf-8")

    try:
        payload = json.loads(body)
        if not isinstance(payload, list):
            raise ValueError("payload must be a list of sales records")
        records: List[SalesRecord] = [SalesRecord.model_validate(item) for item in payload]
    except (json.JSONDecodeError, ValueError) as exc:
        logger.exception("Invalid payload for seller %s: %s", seller_id, exc)
        return {"statusCode": 400, "body": json.dumps({"error": "invalid payload", "details": str(exc)})}

    settings = EnvironmentSettings.load()
    s3 = aws.client("s3", region_name=settings.region)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    key = f"landing/{seller_id}/{timestamp}-{context.aws_request_id}.json"
    s3.put_object(
        Bucket=settings.data_lake_bucket,
        Key=key,
        Body=json.dumps([record.model_dump() for record in records], default=str).encode("utf-8"),
        ContentType="application/json",
    )
    logger.info("Staged payload for seller %s at s3://%s/%s", seller_id, settings.data_lake_bucket, key)
    return {"statusCode": 202, "body": json.dumps({"message": "accepted", "key": key})}
