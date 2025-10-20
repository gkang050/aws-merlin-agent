import tempfile
from pathlib import Path

import boto3
import pandas as pd

from aws_merlin_agent.models.training.pipeline import run_training_job


def test_training_pipeline_generates_artifact(dummy_settings, moto_aws):
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="merlin-test-curated")

    # Create curated parquet sample
    df = pd.DataFrame(
        {
            "seller_id": ["seller-123"] * 5,
            "sku": ["SKU-001"] * 5,
            "date": ["2024-02-0" + str(i + 1) for i in range(5)],
            "units_sold": [10, 12, 9, 14, 11],
            "net_revenue_usd": [200, 240, 180, 280, 220],
            "ad_spend_usd": [20, 24, 18, 28, 22],
            "inventory_on_hand": [50, 48, 47, 45, 44],
            "sale_date": ["2024-02-01"] * 5,
        }
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "sample.parquet"
        df.to_parquet(path, index=False)
        s3.upload_file(str(path), "merlin-test-curated", "sales_fact/sample.parquet")

    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="merlin-test-runs",
        KeySchema=[{"AttributeName": "run_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "run_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    model_id = run_training_job()
    assert model_id

    objects = s3.list_objects_v2(Bucket="merlin-test-curated", Prefix="models/test/demand_forecast")
    assert objects.get("KeyCount") >= 1
