#!/bin/bash

# VE Agent ECS Deployment Script
echo "🚀 Deploying VE Agent to AWS ECS..."

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY="ve-agent-backend"
ECS_CLUSTER="ve-agent-cluster"
ECS_SERVICE="ve-agent-service"
ECS_TASK_DEFINITION="ve-agent-task"
STACK_NAME="ve-agent-ecs"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable not set."
    echo "Please set it with: export OPENAI_API_KEY=your_key_here"
    exit 1
fi

# Get ECR URI from CloudFormation stack
ECR_URI=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
    --output text)

if [ -z "$ECR_URI" ]; then
    echo "❌ Could not get ECR URI from CloudFormation stack. Make sure infrastructure is deployed."
    exit 1
fi

echo "📦 Building Docker image..."
docker build -t ${ECR_REPOSITORY} .

echo "🏷️  Tagging image for ECR..."
docker tag ${ECR_REPOSITORY}:latest ${ECR_URI}:latest

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

echo "📤 Pushing image to ECR..."
docker push ${ECR_URI}:latest

echo "🚀 Deploying to ECS..."
aws ecs update-service --cluster ${ECS_CLUSTER} --service ${ECS_SERVICE} --force-new-deployment --region ${AWS_REGION}

echo "✅ Deployment initiated!"
echo "📡 Check the ECS console for deployment status:"
echo "https://${AWS_REGION}.console.aws.amazon.com/ecs/v2/clusters/${ECS_CLUSTER}/services/${ECS_SERVICE}"
