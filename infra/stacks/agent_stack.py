from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING

from aws_cdk import (
    Duration,
    Stack,
    aws_apprunner as apprunner,
    aws_ec2 as ec2,
    aws_ecr_assets as ecr_assets,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_sagemaker as sagemaker,
)
from constructs import Construct

if TYPE_CHECKING:
    from .data_platform_stack import DataPlatformStack


XGBOOST_CONTAINER_REGISTRY: Dict[str, str] = {
    "us-east-1": "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.7-1",
    "us-east-2": "257758044811.dkr.ecr.us-east-2.amazonaws.com/sagemaker-xgboost:1.7-1",
    "us-west-1": "632365934929.dkr.ecr.us-west-1.amazonaws.com/sagemaker-xgboost:1.7-1",
    "us-west-2": "246618743249.dkr.ecr.us-west-2.amazonaws.com/sagemaker-xgboost:1.7-1",
    "eu-west-1": "141502667606.dkr.ecr.eu-west-1.amazonaws.com/sagemaker-xgboost:1.7-1",
    "eu-central-1": "121021644041.dkr.ecr.eu-central-1.amazonaws.com/sagemaker-xgboost:1.7-1",
    "ap-southeast-1": "475088953585.dkr.ecr.ap-southeast-1.amazonaws.com/sagemaker-xgboost:1.7-1",
    "ap-northeast-1": "354813040037.dkr.ecr.ap-northeast-1.amazonaws.com/sagemaker-xgboost:1.7-1",
}


def resolve_xgboost_image(region: str) -> str:
    image = XGBOOST_CONTAINER_REGISTRY.get(region)
    if not image:
        raise ValueError(
            f"Unsupported region {region} for built-in XGBoost container. "
            "Provide `forecastEndpointName` context to reuse an existing endpoint."
        )
    return image


class AgentStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        data_stack: "DataPlatformStack",
        env_name: str,
        forecast_endpoint_name: Optional[str] = None,
        model_artifact: Optional[str] = None,
        deploy_ui: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        endpoint_name = forecast_endpoint_name or f"merlin-{env_name}-demand-forecast"

        if model_artifact:
            container_image = resolve_xgboost_image(self.region)
            execution_role = iam.Role(
                self,
                "SageMakerExecutionRole",
                assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            )
            data_stack.curated_bucket.grant_read(execution_role)
            model = sagemaker.CfnModel(
                self,
                "DemandForecastModel",
                execution_role_arn=execution_role.role_arn,
                primary_container=sagemaker.CfnModel.ContainerDefinitionProperty(
                    image=container_image,
                    model_data_url=model_artifact,
                ),
                model_name=f"merlin-{env_name}-demand-model",
            )

            endpoint_config = sagemaker.CfnEndpointConfig(
                self,
                "DemandForecastEndpointConfig",
                production_variants=[
                    sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                        model_name=model.attr_model_name,
                        variant_name="AllTraffic",
                        initial_instance_count=1,
                        instance_type="ml.m5.xlarge",
                    )
                ],
                endpoint_config_name=f"merlin-{env_name}-demand-config",
            )

            endpoint = sagemaker.CfnEndpoint(
                self,
                "DemandForecastEndpoint",
                endpoint_config_name=endpoint_config.attr_endpoint_config_name,
                endpoint_name=endpoint_name,
            )
            endpoint.add_dependency(endpoint_config)
            endpoint_config.add_dependency(model)

        self.agent_lambda = lambda_.Function(
            self,
            "AgentOrchestrator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="aws_merlin_agent.agent.workflows.agent_plan.lambda_handler",
            code=lambda_.Code.from_asset("src"),
            timeout=Duration.minutes(5),
        )
        self.agent_lambda.add_environment("MERLIN_ENV", env_name)
        self.agent_lambda.add_environment("MERLIN_CURATED_BUCKET", data_stack.curated_bucket.bucket_name)
        self.agent_lambda.add_environment("MERLIN_DATA_LAKE_BUCKET", data_stack.landing_bucket.bucket_name)
        self.agent_lambda.add_environment("MERLIN_RUNS_TABLE", data_stack.runs_table.table_name)
        self.agent_lambda.add_environment("MERLIN_ACTIONS_TABLE", data_stack.actions_table.table_name)
        self.agent_lambda.add_environment("FORECAST_ENDPOINT_NAME", endpoint_name)

        self.event_rule = events.Rule(
            self,
            "ScheduledAgentRun",
            schedule=events.Schedule.rate(Duration.hours(6)),
        )
        self.event_rule.add_target(targets.LambdaFunction(self.agent_lambda))

        data_stack.curated_bucket.grant_read(self.agent_lambda)
        data_stack.landing_bucket.grant_read(self.agent_lambda)
        data_stack.runs_table.grant_read_write_data(self.agent_lambda)
        data_stack.actions_table.grant_read_write_data(self.agent_lambda)

        self.agent_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "sagemaker:InvokeEndpoint",
                ],
                resources=[
                    f"arn:aws:sagemaker:{self.region}:{self.account}:endpoint/{endpoint_name}"
                ],
            )
        )
        self.agent_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "athena:StartQueryExecution",
                    "athena:GetQueryExecution",
                    "athena:GetQueryResults",
                ],
                resources=["*"],
            )
        )
        self.agent_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeAgent",
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["*"],
            )
        )

        self.ui_service = None
        if deploy_ui:
            asset = ecr_assets.DockerImageAsset(
                self,
                "StreamlitImage",
                directory=".",
                file="streamlit.Dockerfile",
            )
            
            # Create IAM role for App Runner to access ECR
            access_role = iam.Role(
                self,
                "AppRunnerAccessRole",
                assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSAppRunnerServicePolicyForECRAccess")
                ],
            )
            
            # Create IAM role for the App Runner instance
            instance_role = iam.Role(
                self,
                "AppRunnerInstanceRole",
                assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com"),
            )
            
            # Grant instance role access to S3 and DynamoDB
            data_stack.curated_bucket.grant_read(instance_role)
            data_stack.landing_bucket.grant_read(instance_role)
            data_stack.runs_table.grant_read_data(instance_role)
            
            self.ui_service = apprunner.CfnService(
                self,
                "MerlinStreamlit",
                source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                    image_repository=apprunner.CfnService.ImageRepositoryProperty(
                        image_identifier=asset.image_uri,
                        image_repository_type="ECR",
                        image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                            port="8501",
                            runtime_environment_variables=[
                                apprunner.CfnService.KeyValuePairProperty(name="MERLIN_ENV", value=env_name),
                                apprunner.CfnService.KeyValuePairProperty(name="AWS_REGION", value=self.region),
                                apprunner.CfnService.KeyValuePairProperty(
                                    name="MERLIN_INFERENCE_MODE", value="local"
                                ),
                                apprunner.CfnService.KeyValuePairProperty(
                                    name="MERLIN_DATA_LAKE_BUCKET", value=data_stack.landing_bucket.bucket_name
                                ),
                                apprunner.CfnService.KeyValuePairProperty(
                                    name="MERLIN_CURATED_BUCKET", value=data_stack.curated_bucket.bucket_name
                                ),
                                apprunner.CfnService.KeyValuePairProperty(
                                    name="MERLIN_RUNS_TABLE", value=data_stack.runs_table.table_name
                                ),
                                apprunner.CfnService.KeyValuePairProperty(
                                    name="MERLIN_ACTIONS_TABLE", value=data_stack.actions_table.table_name
                                ),
                            ],
                        ),
                    ),
                    authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                        access_role_arn=access_role.role_arn
                    ),
                    auto_deployments_enabled=False,
                ),
                instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
                    cpu="1 vCPU",
                    memory="2 GB",
                    instance_role_arn=instance_role.role_arn,
                ),
                health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                    protocol="HTTP",
                    path="/_stcore/health"
                ),
                service_name=f"merlin-ui-{env_name}",
            )
            # Create CloudFormation output for the service URL
            from aws_cdk import CfnOutput
            CfnOutput(
                self,
                "StreamlitServiceURL",
                value=f"https://{self.ui_service.attr_service_url}",
                description="Public URL for the MERLIN Streamlit UI",
                export_name=f"MerlinUIURL-{env_name}",
            )
