#!/bin/bash
set -e

echo "🚀 MERLIN AWS Deployment"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Verify AWS credentials
echo -e "${BLUE}Step 1: Verifying AWS credentials...${NC}"
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_REGION:-us-east-1}
echo -e "${GREEN}✓ Account: ${ACCOUNT_ID}${NC}"
echo -e "${GREEN}✓ Region: ${REGION}${NC}"
echo ""

# Step 2: Set environment variables
echo -e "${BLUE}Step 2: Setting environment variables...${NC}"
export CDK_DEFAULT_ACCOUNT=$ACCOUNT_ID
export CDK_DEFAULT_REGION=$REGION
export MERLIN_ENV=demo
export AWS_REGION=$REGION
echo -e "${GREEN}✓ Environment configured${NC}"
echo ""

# Step 3: Install dependencies
echo -e "${BLUE}Step 3: Installing dependencies...${NC}"
poetry install --extras glue > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Bootstrap CDK
echo -e "${BLUE}Step 4: Bootstrapping CDK...${NC}"
if aws cloudformation describe-stacks --stack-name CDKToolkit --region $REGION > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CDK already bootstrapped${NC}"
else
    poetry run cdk bootstrap -c env=demo
    echo -e "${GREEN}✓ CDK bootstrapped${NC}"
fi
echo ""

# Step 5: Deploy data platform
echo -e "${BLUE}Step 5: Deploying data platform (S3, DynamoDB, Glue)...${NC}"
poetry run cdk deploy -c env=demo MerlinDataPlatformStack-demo --require-approval never
echo -e "${GREEN}✓ Data platform deployed${NC}"
echo ""

# Step 6: Deploy agent stack
echo -e "${BLUE}Step 6: Deploying agent stack (Lambda, EventBridge)...${NC}"
poetry run cdk deploy -c env=demo MerlinAgentStack-demo --require-approval never
echo -e "${GREEN}✓ Agent stack deployed${NC}"
echo ""

# Step 7: Load sample data
echo -e "${BLUE}Step 7: Loading sample data...${NC}"
export MERLIN_ENV=demo
poetry run python scripts/load_sample_data.py
echo -e "${GREEN}✓ Sample data loaded${NC}"
echo ""

# Step 8: Test deployment
echo -e "${BLUE}Step 8: Testing deployment...${NC}"
poetry run python scripts/test_agent.py
echo ""

# Step 9: Show outputs
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${BLUE}📊 Stack Outputs:${NC}"
aws cloudformation describe-stacks --stack-name MerlinDataPlatformStack-demo --query "Stacks[0].Outputs" --output table
echo ""

echo -e "${BLUE}🪣 S3 Buckets:${NC}"
aws s3 ls | grep merlin
echo ""

echo -e "${BLUE}📋 DynamoDB Tables:${NC}"
aws dynamodb list-tables | grep merlin
echo ""

echo -e "${BLUE}⚡ Lambda Functions:${NC}"
aws lambda list-functions --query "Functions[?contains(FunctionName, 'Merlin')].FunctionName" --output text
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test locally: poetry run streamlit run src/aws_merlin_agent/ui/chat_app.py"
echo "2. View logs: aws logs tail /aws/lambda/\$(aws lambda list-functions --query \"Functions[?contains(FunctionName, 'Merlin')].FunctionName\" --output text) --follow"
echo "3. Check costs: aws ce get-cost-and-usage --time-period Start=\$(date -u -d '7 days ago' +%Y-%m-%d),End=\$(date -u +%Y-%m-%d) --granularity DAILY --metrics BlendedCost"
echo ""

echo -e "${GREEN}🎉 MERLIN is deployed and ready!${NC}"
echo ""
echo -e "${YELLOW}Estimated monthly cost: \$25-35 (without SageMaker)${NC}"
echo ""
