# VE Agent Deployment Guide

This guide will help you deploy the Value Engineering AI Agent to AWS.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Node.js** (v16 or higher)
4. **Python** (v3.9 or higher)

## Step 1: AWS CLI Setup

```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region (us-east-1)
```

## Step 2: Install Dependencies

```bash
# Install Serverless Framework globally
npm install -g serverless

# Install project dependencies
npm install
```

## Step 3: Set Environment Variables

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your_actual_openai_api_key_here"
```

## Step 4: Deploy Backend to AWS Lambda

```bash
# Run the deployment script
./deploy.sh
```

This will:
- Deploy the FastAPI backend to AWS Lambda
- Create an API Gateway endpoint
- Return the API Gateway URL

## Step 5: Deploy Frontend to AWS Amplify

### Option A: Using AWS Console (Recommended)

1. **Go to AWS Amplify Console**: https://console.aws.amazon.com/amplify/
2. **Click "New app" → "Host web app"**
3. **Connect to GitHub**:
   - Repository: `wei-pelleon/Pelleon-AIagent`
   - Branch: `main`
4. **Build settings**: Auto-detected from `amplify.yml`
5. **Environment variables**:
   ```
   VITE_SKIP_AUTH=true
   VITE_API_BASE_URL=https://your-api-gateway-url.amazonaws.com/prod
   ```
6. **Deploy**

### Option B: Using AWS CLI

```bash
# Create Amplify app
aws amplify create-app --name "ve-agent" --repository "https://github.com/wei-pelleon/Pelleon-AIagent"

# Add environment variables
aws amplify update-app --app-id YOUR_APP_ID --environment-variables VITE_SKIP_AUTH=true,VITE_API_BASE_URL=https://your-api-gateway-url.amazonaws.com/prod
```

## Step 6: Configure Custom Domain

### Route 53 Setup

1. **Go to Route 53 Console**: https://console.aws.amazon.com/route53/
2. **Create/Update CNAME record**:
   ```
   Name: agent.pelleon.com
   Type: CNAME
   Value: [Amplify domain from step 5]
   TTL: 300
   ```

### Amplify Domain Configuration

1. **In Amplify Console** → Your app → **Domain management**
2. **Add domain**: `agent.pelleon.com`
3. **Configure SSL certificate** (auto-generated)
4. **Update DNS records** as instructed

## Step 7: Update Frontend API URL

After backend deployment, update the frontend:

1. **Copy the API Gateway URL** from the deployment output
2. **Update Amplify environment variables**:
   ```
   VITE_API_BASE_URL=https://your-actual-api-gateway-url.amazonaws.com/prod
   ```
3. **Redeploy the frontend**

## Verification

1. **Frontend**: Visit `https://agent.pelleon.com`
2. **Backend API**: Test `https://your-api-gateway-url.amazonaws.com/prod/health`
3. **Chat functionality**: Try asking questions in the chat interface

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure API Gateway has CORS enabled
2. **Environment Variables**: Verify all required env vars are set
3. **API Key**: Ensure OpenAI API key is valid and has sufficient credits
4. **Domain**: Check DNS propagation (can take up to 48 hours)

### Logs

```bash
# View Lambda logs
serverless logs -f chat --stage prod

# View Amplify build logs
# Go to Amplify Console → Your app → Build history
```

## Cost Optimization

- **Lambda**: Pay per request (very cost-effective for low traffic)
- **API Gateway**: Pay per API call
- **Amplify**: Free tier includes 1000 build minutes/month
- **Route 53**: $0.50/month per hosted zone

## Security

- API keys are stored as environment variables (not in code)
- CORS is configured for your domain only
- HTTPS enforced for all communications

## Monitoring

- **CloudWatch**: Monitor Lambda function performance
- **Amplify Console**: Monitor frontend deployments
- **API Gateway**: Monitor API usage and errors
