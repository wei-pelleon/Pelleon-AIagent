#!/bin/bash

# Deploy ECS Infrastructure
echo "🏗️  Deploying ECS Infrastructure..."

# Configuration
STACK_NAME="ve-agent-ecs"
REGION="us-east-1"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable not set."
    echo "Please set it with: export OPENAI_API_KEY=your_key_here"
    exit 1
fi

echo "📋 Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file ecs-infrastructure.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides OpenAIAPIKey=${OPENAI_API_KEY} \
    --capabilities CAPABILITY_IAM \
    --region ${REGION}

if [ $? -eq 0 ]; then
    echo "✅ Infrastructure deployed successfully!"
    
    # Get the ECR repository URI
    ECR_URI=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --region ${REGION} \
        --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
        --output text)
    
    echo "📦 ECR Repository URI: ${ECR_URI}"
    echo ""
    echo "Next steps:"
    echo "1. Build and push Docker image: ./ecs-deploy.sh"
    echo "2. Get Load Balancer DNS: aws cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[0].Outputs[?OutputKey==\`LoadBalancerDNS\`].OutputValue' --output text"
else
    echo "❌ Infrastructure deployment failed!"
    exit 1
fi
