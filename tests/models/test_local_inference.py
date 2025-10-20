import tempfile
from pathlib import Path

import boto3
import pandas as pd

from aws_merlin_agent.models.inference.demand_forecast_client import DemandForecastClient
from aws_merlin_agent.models.registry import register_model
from aws_merlin_agent.models.training.demand_forecast import train
from aws_merlin_agent.features.engineering import build_feature_frame


def test_local_inference_uses_registered_model(monkeypatch, dummy_settings, moto_aws):
    monkeypatch.setenv("MERLIN_INFERENCE_MODE", "local")

    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="merlin-test-curated")

    df = pd.DataFrame(
        {
            "seller_id": ["seller-123", "seller-123"],
            "sku": ["SKU-001", "SKU-001"],
            "date": ["2024-02-01", "2024-02-02"],
            "units_sold": [10, 12],
            "net_revenue": [200, 240],
            "ad_spend": [20, 24],
            "inventory_on_hand": [50, 48],
        }
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "model.json"
        training_path = Path(tmpdir) / "training.parquet"
        df.to_parquet(training_path, index=False)
        train(str(training_path), str(path))
        s3.upload_file(str(path), "merlin-test-curated", "models/test/demand_forecast/model.json")

    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="merlin-test-runs",
        KeySchema=[{"AttributeName": "run_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "run_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    register_model("s3://merlin-test-curated/models/test/demand_forecast/model.json", {"r2": 1.0})

    client = DemandForecastClient()
    engineered = build_feature_frame(df)
    engineered["lag_days"] = range(len(engineered))
    inference_features = engineered.select_dtypes(include=["number"]).drop(columns=["units_sold"], errors="ignore").iloc[:1]
    response = client.predict({"instances": inference_features.to_dict(orient="records")})
    assert "predictions" in response
    assert len(response["predictions"]) == 1
