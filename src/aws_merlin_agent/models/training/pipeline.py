from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from typing import Tuple

import boto3
import pandas as pd

from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.models.registry import register_model
from aws_merlin_agent.models.training.demand_forecast import train
from aws_merlin_agent.utils.logging import get_logger

logger = get_logger(__name__)


def _download_curated_sales(bucket: str, prefix: str, local_dir: Path, region: str) -> Tuple[Path, pd.DataFrame]:
    s3 = boto3.client("s3", region_name=region)
    paginator = s3.get_paginator("list_objects_v2")
    frames = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".parquet"):
                local_path = local_dir / Path(key).name
                s3.download_file(bucket, key, str(local_path))
                frames.append(pd.read_parquet(local_path))
    if not frames:
        raise FileNotFoundError(f"No Parquet files found at s3://{bucket}/{prefix}")
    df = pd.concat(frames, ignore_index=True)
    return local_dir, df


def run_training_job(env: str | None = None) -> str:
    settings = EnvironmentSettings.load()
    if env:
        settings.env = env  # type: ignore[attr-defined]
    curated_prefix = "sales_fact/"
    artifact_prefix = f"models/{settings.env}/demand_forecast"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        _, df = _download_curated_sales(settings.curated_bucket, curated_prefix, tmp_path, settings.region)
        df = df.rename(
            columns={
                "net_revenue_usd": "net_revenue",
                "ad_spend_usd": "ad_spend",
            }
        )
        prepare_path = tmp_path / "training_data.parquet"
        df.to_parquet(prepare_path, index=False)

        model_path = tmp_path / "demand_forecast.json"
        score = train(str(prepare_path), str(model_path))

        artifact_key = f"{artifact_prefix}/model.json"
        s3 = boto3.client("s3", region_name=settings.region)
        s3.upload_file(str(model_path), settings.curated_bucket, artifact_key)
        artifact_uri = f"s3://{settings.curated_bucket}/{artifact_key}"

    metrics = {"r2": score}
    model_id = register_model(artifact_uri, metrics)
    logger.info("Training complete. Model %s stored at %s", model_id, artifact_uri)
    return model_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the MERLIN demand forecast training pipeline.")
    parser.add_argument("--env", help="Execution environment (dev/demo/prod)")
    args = parser.parse_args()
    run_training_job(args.env)


if __name__ == "__main__":
    main()
