from aws_cdk import CfnOutput, RemovalPolicy, Stack, aws_dynamodb as dynamodb, aws_glue as glue, aws_iam as iam, aws_s3 as s3
from constructs import Construct


class DataPlatformStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.env_name = env_name

        self.landing_bucket = s3.Bucket(
            self,
            "LandingBucket",
            bucket_name=None,
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        self.curated_bucket = s3.Bucket(
            self,
            "CuratedBucket",
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        self.creative_bucket = s3.Bucket(
            self,
            "CreativeBucket",
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        self.runs_table = dynamodb.Table(
            self,
            "RunsTable",
            partition_key=dynamodb.Attribute(name="run_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.actions_table = dynamodb.Table(
            self,
            "ActionsTable",
            partition_key=dynamodb.Attribute(name="action_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.glue_database = glue.CfnDatabase(
            self,
            "GlueDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name=f"merlin_{env_name}"
            ),
        )

        self.athena_role = iam.Role(
            self,
            "AthenaExecutionRole",
            assumed_by=iam.ServicePrincipal("athena.amazonaws.com"),
        )
        self.athena_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:ListBucket"],
                resources=[
                    self.curated_bucket.bucket_arn,
                    f"{self.curated_bucket.bucket_arn}/*",
                    self.landing_bucket.bucket_arn,
                    f"{self.landing_bucket.bucket_arn}/*",
                ],
            )
        )

        CfnOutput(self, "LandingBucketOutput", export_name=f"MerlinLandingBucket-{env_name}", value=self.landing_bucket.bucket_name)
        CfnOutput(self, "CuratedBucketOutput", export_name=f"MerlinCuratedBucket-{env_name}", value=self.curated_bucket.bucket_name)
        CfnOutput(self, "CreativeBucketOutput", export_name=f"MerlinCreativeBucket-{env_name}", value=self.creative_bucket.bucket_name)
        CfnOutput(self, "RunsTableOutput", export_name=f"MerlinRunsTable-{env_name}", value=self.runs_table.table_name)
        CfnOutput(self, "ActionsTableOutput", export_name=f"MerlinActionsTable-{env_name}", value=self.actions_table.table_name)
