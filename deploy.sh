#!/bin/bash

# VE Agent Deployment Script
echo "🚀 Deploying VE Agent to AWS..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check if Serverless Framework is installed
if ! command -v serverless &> /dev/null; then
    echo "📦 Installing Serverless Framework..."
    npm install -g serverless
fi

# Check if Node.js dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable not set."
    echo "Please set it with: export OPENAI_API_KEY=your_key_here"
    exit 1
fi

# Deploy to AWS Lambda
echo "☁️  Deploying backend to AWS Lambda..."
serverless deploy --stage prod

if [ $? -eq 0 ]; then
    echo "✅ Backend deployed successfully!"
    echo "📡 API Gateway URL will be shown above."
    echo ""
    echo "🔧 Next steps:"
    echo "1. Copy the API Gateway URL"
    echo "2. Update VITE_API_BASE_URL in Amplify environment variables"
    echo "3. Redeploy the frontend"
else
    echo "❌ Deployment failed. Check the logs above."
    exit 1
fi
