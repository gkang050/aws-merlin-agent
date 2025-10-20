from __future__ import annotations

import argparse
import json
from pathlib import Path

import boto3

from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.utils.logging import get_logger

logger = get_logger(__name__)


def load_sample_data(directory: Path) -> None:
    settings = EnvironmentSettings.load()
    s3 = boto3.client("s3", region_name=settings.region)
    for path in directory.glob("*.json"):
        key = f"landing/demo/{path.name}"
        logger.info("Uploading %s to s3://%s/%s", path, settings.data_lake_bucket, key)
        s3.upload_file(str(path), settings.data_lake_bucket, key)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load sample datasets into the MERLIN landing bucket.")
    parser.add_argument("--path", type=Path, default=Path("data/sample"), help="Directory containing sample JSON files")
    args = parser.parse_args()
    load_sample_data(args.path)


if __name__ == "__main__":
    main()
