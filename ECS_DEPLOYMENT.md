# ECS Deployment Guide

This guide will help you deploy the VE Agent backend to AWS ECS using Fargate.

## Prerequisites

1. **AWS CLI** installed and configured
2. **Docker** installed
3. **OpenAI API Key** set as environment variable

## Step 1: Deploy Infrastructure

First, deploy the ECS infrastructure using CloudFormation:

```bash
export OPENAI_API_KEY='your_openai_api_key_here'
./deploy-ecs-infrastructure.sh
```

This will create:
- ECR repository for Docker images
- VPC with public subnets
- ECS cluster
- Application Load Balancer
- Security groups
- IAM roles

## Step 2: Build and Deploy Application

Once the infrastructure is deployed, build and push the Docker image:

```bash
./ecs-deploy.sh
```

This will:
- Build the Docker image
- Push it to ECR
- Update the ECS service

## Step 3: Get the API URL

After deployment, get the Load Balancer DNS name:

```bash
aws cloudformation describe-stacks \
    --stack-name ve-agent-ecs \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text
```

The API will be available at: `http://<load-balancer-dns>/chat/stream`

## Step 4: Update Frontend Configuration

Update the frontend to use the new API URL:

1. In `ux/src/components/Chat.jsx`, update the API URL:
```javascript
const API_URL = 'http://<load-balancer-dns>/chat/stream';
```

2. Redeploy the frontend to Amplify

## Monitoring

- **ECS Console**: Monitor service health and logs
- **CloudWatch**: View application logs
- **Load Balancer**: Check health checks and metrics

## Troubleshooting

### Service not starting
- Check ECS service events in the console
- Verify the Docker image was pushed successfully
- Check CloudWatch logs for application errors

### Health check failures
- Ensure the application is listening on port 8000
- Verify the `/health` endpoint returns 200 status

### API not responding
- Check security group allows traffic on port 80/8000
- Verify the load balancer target group health
- Check ECS service is running and healthy

## Cleanup

To remove all resources:

```bash
aws cloudformation delete-stack --stack-name ve-agent-ecs
```

This will delete all created resources including the ECR repository.
