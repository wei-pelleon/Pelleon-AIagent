/**
 * AWS Cognito Configuration
 * 
 * To use this, you need to:
 * 1. Create a Cognito User Pool in AWS Console
 * 2. Create an App Client in your User Pool
 * 3. Replace the values below with your actual Cognito settings
 * 4. Optionally use environment variables for production
 */

const cognitoConfig = {
  // Replace with your AWS region (e.g., 'us-east-1', 'us-west-2')
  region: process.env.VITE_COGNITO_REGION || 'us-east-1',
  
  // Replace with your User Pool ID (found in AWS Cognito Console)
  // Format: us-east-1_xxxxxxxxx
  userPoolId: process.env.VITE_COGNITO_USER_POOL_ID || 'YOUR_USER_POOL_ID',
  
  // Replace with your App Client ID (found in App clients tab)
  // Format: xxxxxxxxxxxxxxxxxxxxxxxxxxxx
  userPoolWebClientId: process.env.VITE_COGNITO_CLIENT_ID || 'YOUR_APP_CLIENT_ID',
}

export default cognitoConfig


