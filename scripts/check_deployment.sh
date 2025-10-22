#!/bin/bash

echo "🔍 Checking MERLIN Deployment Status..."
echo "========================================"
echo ""

# Check CloudFormation stacks
echo "📦 CloudFormation Stacks:"
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query "StackSummaries[?contains(StackName, 'Merlin')].{Name:StackName,Status:StackStatus}" --output table

echo ""
echo "🪣 S3 Buckets:"
aws s3 ls | grep merlin

echo ""
echo "📋 DynamoDB Tables:"
aws dynamodb list-tables | grep merlin

echo ""
echo "⚡ Lambda Functions:"
aws lambda list-functions --query "Functions[?contains(FunctionName, 'Merlin')].FunctionName" --output table

echo ""
echo "✅ Check complete!"
