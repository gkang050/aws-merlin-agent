#!/bin/bash
set -e

echo "🚀 Deploying MERLIN UI to AWS App Runner"
echo "========================================="
echo ""

# Set environment
export AWS_REGION=${AWS_REGION:-us-east-1}
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export CDK_DEFAULT_REGION=$AWS_REGION
export MERLIN_ENV=demo

echo "📦 Account: $CDK_DEFAULT_ACCOUNT"
echo "🌍 Region: $AWS_REGION"
echo ""

echo "🔨 Deploying UI to AWS App Runner..."
echo "This will take 10-15 minutes..."
echo ""

poetry run cdk deploy -c env=demo -c deployUI=true MerlinAgentStack-demo --require-approval never

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Getting your public URL..."
aws cloudformation describe-stacks \
  --stack-name MerlinAgentStack-demo \
  --query "Stacks[0].Outputs[?OutputKey=='StreamlitServiceURL'].OutputValue" \
  --output text

echo ""
echo "📝 Share this URL with judges!"
echo ""
echo "💰 Cost: ~$25/month"
echo "🗑️  To delete: poetry run cdk destroy -c env=demo MerlinAgentStack-demo"
echo ""
