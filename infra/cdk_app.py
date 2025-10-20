#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.data_platform_stack import DataPlatformStack
from stacks.agent_stack import AgentStack

app = cdk.App()

env_name = app.node.try_get_context("env") or "dev"
model_artifact = app.node.try_get_context("forecastModelArtifact")
endpoint_override = app.node.try_get_context("forecastEndpointName")
cdk_env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
)

data_stack = DataPlatformStack(app, f"MerlinDataPlatformStack-{env_name}", env=cdk_env, env_name=env_name)
AgentStack(
    app,
    f"MerlinAgentStack-{env_name}",
    data_stack=data_stack,
    env=cdk_env,
    env_name=env_name,
    model_artifact=model_artifact,
    forecast_endpoint_name=endpoint_override,
    deploy_ui=bool(app.node.try_get_context("deployUI")),
)
app.synth()
