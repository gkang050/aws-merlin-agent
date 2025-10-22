# AWS Deployment Guide for MERLIN

## Quick Deploy (Automated)

```bash
# Run the deployment script
./scripts/deploy_aws.sh demo
```

This will deploy everything automatically. Takes ~15-20 minutes.

---

## Manual Deployment (Step-by-Step)

### Prerequisites ✅

1. **AWS CLI configured**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
```

2. **Verify access**
```bash
aws sts get-caller-identity
# Should show your account ID
```

3. **Set environment variables**
```bash
export AWS_REGION=us-east-1
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export CDK_DEFAULT_REGION=us-east-1
```

---

### Step 1: Install Dependencies

```bash
# Install Python dependencies
poetry install --extras glue

# Verify CDK is available
poetry run cdk --version
```

---

### Step 2: Bootstrap CDK (First Time Only)

```bash
# Bootstrap CDK in your AWS account
poetry run cdk bootstrap -c env=demo

# This creates the CDKToolkit stack
# Only needs to be done once per account/region
```

---

### Step 3: Deploy Data Platform

```bash
# Deploy S3, DynamoDB, Glue, Athena
poetry run cdk deploy -c env=demo MerlinDataPlatformStack-demo --require-approval never

# This creates:
# - S3 buckets (landing, curated, creative)
# - DynamoDB tables (runs, actions)
# - Glue database
# - IAM roles
```

**Expected time**: 2-3 minutes

---

### Step 4: Load Sample Data

```bash
# Load sample sales data into S3
poetry run python scripts/load_sample_data.py --env demo

# This uploads sample data to the landing bucket
```

**Expected time**: 30 seconds

---

### Step 5: Deploy Agent Stack (Without ML)

```bash
# Deploy Lambda, EventBridge (no SageMaker yet)
poetry run cdk deploy -c env=demo MerlinAgentStack-demo --require-approval never

# This creates:
# - Lambda function (agent orchestrator)
# - EventBridge rule (scheduled runs)
# - IAM roles with Bedrock permissions
```

**Expected time**: 3-5 minutes

---

### Step 6: Test the Agent

```bash
# Test locally with AWS credentials
export MERLIN_ENV=demo
export MERLIN_INFERENCE_MODE=local

# Run a test query
poetry run python -c "
from aws_merlin_agent.agent.workflows.agent_plan import MerlinAgentWorkflow
workflow = MerlinAgentWorkflow()
result = workflow.summarize_performance('SKU-001')
print(result['narrative'])
"
```

---

### Step 7: Train ML Model (Optional)

```bash
# Train XGBoost model on sample data
poetry run python -m aws_merlin_agent.models.training.pipeline --env demo

# This:
# - Downloads data from S3
# - Trains XGBoost model
# - Uploads model to S3
# - Registers in DynamoDB
```

**Expected time**: 10-15 minutes

---

### Step 8: Deploy with SageMaker (Optional)

```bash
# Get the model artifact URI from previous step
# It will be printed at the end of training

# Deploy with SageMaker endpoint
poetry run cdk deploy -c env=demo \
  -c forecastModelArtifact=s3://your-bucket/models/demo/demand_forecast/model.json \
  MerlinAgentStack-demo --require-approval never

# This creates:
# - SageMaker model
# - SageMaker endpoint configuration
# - SageMaker endpoint (ml.m5.xlarge)
```

**Expected time**: 5-10 minutes  
**Cost**: ~$50/month for 24/7 endpoint

---

### Step 9: Deploy UI (Optional)

```bash
# Deploy Streamlit UI on AWS App Runner
poetry run cdk deploy -c env=demo -c deployUI=true MerlinAgentStack-demo

# This creates:
# - Docker image in ECR
# - App Runner service
# - Public URL for the UI
```

**Expected time**: 10-15 minutes  
**Cost**: ~$25/month

---

## Verify Deployment

### Check CloudFormation Stacks

```bash
# List all stacks
aws cloudformation list-stacks --query "StackSummaries[?StackStatus=='CREATE_COMPLETE'].StackName"

# Get outputs
aws cloudformation describe-stacks --stack-name MerlinDataPlatformStack-demo --query "Stacks[0].Outputs"
```

### Check S3 Buckets

```bash
# List buckets
aws s3 ls | grep merlin

# Check data
aws s3 ls s3://$(aws cloudformation describe-stacks --stack-name MerlinDataPlatformStack-demo --query "Stacks[0].Outputs[?OutputKey=='LandingBucketOutput'].OutputValue" --output text)/ --recursive
```

### Check DynamoDB Tables

```bash
# List tables
aws dynamodb list-tables | grep merlin

# Scan runs table
aws dynamodb scan --table-name merlin-demo-runs --max-items 5
```

### Check Lambda Function

```bash
# List functions
aws lambda list-functions | grep -i merlin

# View logs
aws logs tail /aws/lambda/MerlinAgentStack-demo-AgentOrchestrator --follow
```

### Test Bedrock Access

```bash
# Test Nova Pro access
aws bedrock list-foundation-models --region us-east-1 | grep nova

# If empty, request access in AWS Console:
# Bedrock → Model access → Request access to Nova models
```

---

## Invoke the Agent

### Via Lambda

```bash
# Invoke the agent Lambda function
aws lambda invoke \
  --function-name $(aws lambda list-functions --query "Functions[?contains(FunctionName, 'AgentOrchestrator')].FunctionName" --output text) \
  --payload '{"detail": {"sku": "SKU-001"}}' \
  response.json

# View response
cat response.json | jq .
```

### Via Python

```bash
# Run locally with AWS credentials
poetry run python << 'EOF'
from aws_merlin_agent.agent.workflows.agent_plan import MerlinAgentWorkflow

workflow = MerlinAgentWorkflow()

# Test performance summary
result = workflow.summarize_performance('SKU-001')
print("Narrative:", result['narrative'])

# Test forecast
forecast = workflow.forecast(sku='SKU-001')
print("Forecast:", forecast)
EOF
```

---

## Cost Breakdown

### Minimal Deployment (No SageMaker)
- Lambda: ~$5/month (1M requests)
- S3: ~$5/month (100GB)
- DynamoDB: ~$5/month (on-demand)
- Bedrock: ~$10-20/month (light usage)
- **Total**: ~$25-35/month

### Full Deployment (With SageMaker)
- Above costs: ~$25-35/month
- SageMaker Endpoint: ~$50/month (ml.m5.xlarge 24/7)
- **Total**: ~$75-85/month

### With UI (App Runner)
- Above costs: ~$75-85/month
- App Runner: ~$25/month
- **Total**: ~$100-110/month

---

## Cleanup

### Delete Everything

```bash
# Delete agent stack
poetry run cdk destroy -c env=demo MerlinAgentStack-demo

# Delete data platform stack
poetry run cdk destroy -c env=demo MerlinDataPlatformStack-demo

# Verify deletion
aws cloudformation list-stacks | grep merlin
```

### Delete Specific Resources

```bash
# Stop SageMaker endpoint (saves $50/month)
aws sagemaker delete-endpoint --endpoint-name merlin-demo-demand-forecast

# Empty and delete S3 buckets
aws s3 rm s3://bucket-name --recursive
aws s3 rb s3://bucket-name

# Delete DynamoDB tables
aws dynamodb delete-table --table-name merlin-demo-runs
aws dynamodb delete-table --table-name merlin-demo-actions
```

---

## Troubleshooting

### CDK Bootstrap Fails

```bash
# Check if already bootstrapped
aws cloudformation describe-stacks --stack-name CDKToolkit

# If exists, skip bootstrap
# If not, ensure you have permissions to create CloudFormation stacks
```

### Bedrock Access Denied

```bash
# Request model access in AWS Console
# 1. Go to Amazon Bedrock
# 2. Click "Model access" in sidebar
# 3. Click "Request model access"
# 4. Select: Nova Pro, Claude 3 Sonnet
# 5. Submit request
# 6. Wait 5-10 minutes for approval
```

### Lambda Timeout

```bash
# Increase timeout in infra/stacks/agent_stack.py
# Change: timeout=Duration.minutes(5)
# To: timeout=Duration.minutes(10)

# Redeploy
poetry run cdk deploy -c env=demo MerlinAgentStack-demo
```

### SageMaker Endpoint Creation Fails

```bash
# Check service quotas
aws service-quotas get-service-quota \
  --service-code sagemaker \
  --quota-code L-D9B0B7F4

# Request increase if needed
```

### High Costs

```bash
# Stop SageMaker endpoint when not in use
aws sagemaker delete-endpoint --endpoint-name merlin-demo-demand-forecast

# Use local inference mode instead
export MERLIN_INFERENCE_MODE=local
```

---

## Next Steps

1. ✅ Deploy infrastructure
2. ✅ Test agent locally
3. ✅ Train ML model
4. ✅ Deploy with SageMaker
5. ✅ Deploy UI (optional)
6. ✅ Monitor costs
7. ✅ Set up CloudWatch alarms

For questions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) or open an issue.
