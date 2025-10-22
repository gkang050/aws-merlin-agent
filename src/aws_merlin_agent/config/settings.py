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
        """Load required settings from the environment, falling back to CloudFormation outputs or defaults."""
        env = os.getenv("MERLIN_ENV", "dev")
        region = os.getenv("AWS_REGION", "us-east-1")
        prefix = f"merlin-{env}"
        
        # Try to get actual resource names from CloudFormation if not in env vars
        def get_from_cfn(env_var: str, output_key: str, default: str) -> str:
            value = os.getenv(env_var)
            if value:
                return value
            
            # Try to get from CloudFormation
            try:
                import boto3
                cf = boto3.client("cloudformation", region_name=region)
                stack_name = f"MerlinDataPlatformStack-{env}"
                response = cf.describe_stacks(StackName=stack_name)
                outputs = response["Stacks"][0]["Outputs"]
                return next(o["OutputValue"] for o in outputs if o["OutputKey"] == output_key)
            except Exception:
                return default
        
        return cls(
            env=env,
            region=region,
            data_lake_bucket=get_from_cfn("MERLIN_DATA_LAKE_BUCKET", "LandingBucketOutput", f"{prefix}-landing"),
            curated_bucket=get_from_cfn("MERLIN_CURATED_BUCKET", "CuratedBucketOutput", f"{prefix}-curated"),
            creative_bucket=get_from_cfn("MERLIN_CREATIVE_BUCKET", "CreativeBucketOutput", f"{prefix}-creative"),
            dynamodb_table_runs=get_from_cfn("MERLIN_RUNS_TABLE", "RunsTableOutput", f"{prefix}-runs"),
            dynamodb_table_actions=get_from_cfn("MERLIN_ACTIONS_TABLE", "ActionsTableOutput", f"{prefix}-actions"),
            agent_policy_param=os.getenv("MERLIN_AGENT_POLICY_PARAM"),
        )
