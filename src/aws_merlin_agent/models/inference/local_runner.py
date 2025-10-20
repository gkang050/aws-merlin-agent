from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict

import boto3
import pandas as pd
from xgboost import XGBRegressor

from aws_merlin_agent.utils.logging import get_logger

logger = get_logger(__name__)


def _payload_to_frame(payload: Dict[str, Any]) -> pd.DataFrame:
    instances = payload.get("instances")
    if instances is None:
        raise ValueError("Payload missing 'instances' key")
    if isinstance(instances, dict):
        return pd.DataFrame(instances)
    if isinstance(instances, list):
        return pd.DataFrame(instances)
    raise ValueError("Unsupported payload shape; expected list[dict] or dict[str, list]")


def _parse_s3_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("s3://"):
        raise ValueError(f"Invalid S3 URI: {uri}")
    without_scheme = uri[5:]
    bucket, _, key = without_scheme.partition("/")
    if not bucket or not key:
        raise ValueError(f"Invalid S3 URI: {uri}")
    return bucket, key


class LocalDemandForecaster:
    """Loads an XGBoost regressor artifact from S3 and serves predictions locally."""

    def __init__(self, artifact_uri: str, region: str) -> None:
        self.artifact_uri = artifact_uri
        self.region = region
        self.model = self._load_model()

    def _load_model(self) -> XGBRegressor:
        bucket, key = _parse_s3_uri(self.artifact_uri)
        s3 = boto3.client("s3", region_name=self.region)
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = Path(tmpdir) / "model.json"
            s3.download_file(bucket, key, str(local_path))
            model = XGBRegressor()
            model.load_model(str(local_path))
            logger.info("Loaded local model from %s", self.artifact_uri)
            return model

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        frame = _payload_to_frame(payload)
        predictions = self.model.predict(frame)
        return {"predictions": predictions.tolist()}
