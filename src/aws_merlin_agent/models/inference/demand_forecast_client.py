from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.models.inference.local_runner import LocalDemandForecaster
from aws_merlin_agent.models.registry import latest_model
from aws_merlin_agent.utils import aws


class DemandForecastClient:
    """Lightweight wrapper around the SageMaker runtime API for demand forecasts."""

    def __init__(self, endpoint_name: Optional[str] = None) -> None:
        self.settings = EnvironmentSettings.load()
        self.mode = os.getenv("MERLIN_INFERENCE_MODE", "sagemaker")
        env_endpoint = os.getenv("FORECAST_ENDPOINT_NAME")
        if self.mode == "local":
            metadata = latest_model()
            if metadata is None:
                raise RuntimeError("No registered model found for local inference")
            artifact = metadata["artifact_uri"]
            self.local_runner = LocalDemandForecaster(artifact, self.settings.region)
            self.endpoint_name = None
            self.runtime = None
        else:
            self.endpoint_name = endpoint_name or env_endpoint or f"merlin-{self.settings.env}-demand-forecast"
            self.runtime = aws.client("sagemaker-runtime", region_name=self.settings.region)
            self.local_runner = None

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.mode == "local":
            return self.local_runner.predict(payload)  # type: ignore[union-attr]
        response = self.runtime.invoke_endpoint(  # type: ignore[union-attr]
            EndpointName=self.endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload),
        )
        return json.loads(response["Body"].read().decode("utf-8"))
