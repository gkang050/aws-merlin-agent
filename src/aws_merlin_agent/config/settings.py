from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EnvironmentSettings:
    """Runtime configuration loaded from environment variables or Parameter Store."""

    env: str
    region: str
    data_lake_bucket: str
    curated_bucket: str
    creative_bucket: str
    dynamodb_table_runs: str
    dynamodb_table_actions: str
    agent_policy_param: Optional[str] = None

    @classmethod
    def load(cls) -> "EnvironmentSettings":
        """Load required settings from the environment, falling back to sane defaults for local dev."""
        env = os.getenv("MERLIN_ENV", "dev")
        region = os.getenv("AWS_REGION", "us-east-1")
        prefix = f"merlin-{env}"
        return cls(
            env=env,
            region=region,
            data_lake_bucket=os.getenv("MERLIN_DATA_LAKE_BUCKET", f"{prefix}-landing"),
            curated_bucket=os.getenv("MERLIN_CURATED_BUCKET", f"{prefix}-curated"),
            creative_bucket=os.getenv("MERLIN_CREATIVE_BUCKET", f"{prefix}-creative"),
            dynamodb_table_runs=os.getenv("MERLIN_RUNS_TABLE", f"{prefix}-runs"),
            dynamodb_table_actions=os.getenv("MERLIN_ACTIONS_TABLE", f"{prefix}-actions"),
            agent_policy_param=os.getenv("MERLIN_AGENT_POLICY_PARAM"),
        )
