#!/bin/bash
set -e

echo "🚀 MERLIN AWS Deployment Script"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if environment is provided
ENV=${1:-demo}
echo -e "${BLUE}Deploying to environment: ${ENV}${NC}"
echo ""

# Step 1: Verify AWS credentials
echo -e "${YELLOW}Step 1: Verifying AWS credentials...${NC}"
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_REGION:-us-east-1}
echo -e "${GREEN}✓ AWS Account: ${ACCOUNT_ID}${NC}"
echo -e "${GREEN}✓ Region: ${REGION}${NC}"
echo ""

# Step 2: Set environment variables
echo -e "${YELLOW}Step 2: Setting environment variables...${NC}"
export CDK_DEFAULT_ACCOUNT=$ACCOUNT_ID
export CDK_DEFAULT_REGION=$REGION
export MERLIN_ENV=$ENV
echo -e "${GREEN}✓ Environment variables set${NC}"
echo ""

# Step 3: Install dependencies
echo -e "${YELLOW}Step 3: Installing dependencies...${NC}"
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry not found. Install with: pip install poetry${NC}"
    exit 1
fi
poetry install --extras glue
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Bootstrap CDK (if needed)
echo -e "${YELLOW}Step 4: Bootstrapping CDK...${NC}"
if ! aws cloudformation describe-stacks --stack-name CDKToolkit --region $REGION > /dev/null 2>&1; then
    echo "Bootstrapping CDK for the first time..."
    poetry run cdk bootstrap -c env=$ENV
    echo -e "${GREEN}✓ CDK bootstrapped${NC}"
else
    echo -e "${GREEN}✓ CDK already bootstrapped${NC}"
fi
echo ""

# Step 5: Synthesize CDK stacks
echo -e "${YELLOW}Step 5: Synthesizing CDK stacks...${NC}"
poetry run cdk synth -c env=$ENV
echo -e "${GREEN}✓ Stacks synthesized${NC}"
echo ""

# Step 6: Deploy data platform
echo -e "${YELLOW}Step 6: Deploying data platform (S3, DynamoDB, Glue)...${NC}"
poetry run cdk deploy -c env=$ENV MerlinDataPlatformStack-$ENV --require-approval never
echo -e "${GREEN}✓ Data platform deployed${NC}"
echo ""

# Step 7: Load sample data
echo -e "${YELLOW}Step 7: Loading sample data...${NC}"
poetry run python scripts/load_sample_data.py --env $ENV
echo -e "${GREEN}✓ Sample data loaded${NC}"
echo ""

# Step 8: Train ML model (optional - can take 10-15 minutes)
echo -e "${YELLOW}Step 8: Training ML model (optional)...${NC}"
read -p "Train ML model now? This takes 10-15 minutes. (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    poetry run python -m aws_merlin_agent.models.training.pipeline --env $ENV
    echo -e "${GREEN}✓ Model trained${NC}"
    
    # Get model artifact URI
    MODEL_URI=$(aws s3 ls s3://$(aws cloudformation describe-stacks --stack-name MerlinDataPlatformStack-$ENV --query "Stacks[0].Outputs[?OutputKey=='CuratedBucketOutput'].OutputValue" --output text)/models/$ENV/demand_forecast/ --recursive | sort | tail -n 1 | awk '{print "s3://"$4}')
    echo "Model URI: $MODEL_URI"
    
    # Deploy agent stack with model
    echo -e "${YELLOW}Step 9: Deploying agent stack with ML model...${NC}"
    poetry run cdk deploy -c env=$ENV -c forecastModelArtifact=$MODEL_URI MerlinAgentStack-$ENV --require-approval never
else
    echo "Skipping model training. Deploying agent stack without SageMaker endpoint..."
    # Deploy agent stack without model
    echo -e "${YELLOW}Step 9: Deploying agent stack (Lambda, EventBridge)...${NC}"
    poetry run cdk deploy -c env=$ENV MerlinAgentStack-$ENV --require-approval never
fi
echo -e "${GREEN}✓ Agent stack deployed${NC}"
echo ""

# Step 10: Get outputs
echo -e "${YELLOW}Step 10: Deployment complete! Getting outputs...${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ MERLIN Deployed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get stack outputs
echo "Stack Outputs:"
aws cloudformation describe-stacks --stack-name MerlinDataPlatformStack-$ENV --query "Stacks[0].Outputs" --output table
echo ""
aws cloudformation describe-stacks --stack-name MerlinAgentStack-$ENV --query "Stacks[0].Outputs" --output table 2>/dev/null || echo "Agent stack outputs not available"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo "1. Test the agent: poetry run python -c \"from aws_merlin_agent.agent.workflows.agent_plan import MerlinAgentWorkflow; w = MerlinAgentWorkflow(); print(w.summarize_performance('SKU-001'))\""
echo "2. View logs: aws logs tail /aws/lambda/MerlinAgentStack-$ENV-AgentOrchestrator --follow"
echo "3. Check DynamoDB: aws dynamodb scan --table-name merlin-$ENV-runs --max-items 5"
echo ""
echo -e "${YELLOW}To deploy UI to App Runner:${NC}"
echo "poetry run cdk deploy -c env=$ENV -c deployUI=true MerlinAgentStack-$ENV"
echo ""
echo -e "${GREEN}Deployment complete! 🎉${NC}"
