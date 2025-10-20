import json
from types import SimpleNamespace

import boto3

from aws_merlin_agent.data_ingestion.handlers.api_ingest import handler


def test_api_ingest_stages_payload(dummy_settings, moto_aws):
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="merlin-test-landing")

    event = {
        "pathParameters": {"sellerId": "seller-123"},
        "body": json.dumps(
            [
                {
                    "seller_id": "seller-123",
                    "sku": "SKU-001",
                    "date": "2024-02-01",
                    "units_sold": 12,
                    "net_revenue": 240.0,
                    "ad_spend": 24.0,
                }
            ]
        ),
    }

    response = handler(event, SimpleNamespace(aws_request_id="abc123"))

    assert response["statusCode"] == 202
    objects = s3.list_objects(Bucket="merlin-test-landing")
    keys = [obj["Key"] for obj in objects.get("Contents", [])]
    assert any(key.startswith("landing/seller-123/") for key in keys)


def test_api_ingest_rejects_invalid_payload(dummy_settings, moto_aws):
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="merlin-test-landing")

    event = {
        "pathParameters": {"sellerId": "seller-123"},
        "body": "{}",  # not a list of records
    }

    response = handler(event, SimpleNamespace(aws_request_id="abc123"))
    assert response["statusCode"] == 400
