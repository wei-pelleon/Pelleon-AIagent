# AWS Cognito Setup Guide

## Overview

The VE Agent UI uses AWS Cognito for secure authentication. Follow these steps to set it up.

## 1. Create AWS Cognito User Pool

### Step 1: Go to AWS Console
1. Log in to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **Cognito** service
3. Click **Create user pool**

### Step 2: Configure Sign-in Experience
1. **Sign-in options**: Select **Username** or **Email** (recommended: Email)
2. Click **Next**

### Step 3: Configure Security Requirements
1. **Password policy**: Use default or customize
2. **Multi-factor authentication**: Optional (recommended: Optional MFA)
3. Click **Next**

### Step 4: Configure Sign-up Experience
1. **Self-registration**: Enable if you want users to sign up
2. **Attributes**: Select required attributes (email recommended)
3. Click **Next**

### Step 5: Configure Message Delivery
1. **Email provider**: Use **Cognito** (for testing) or **SES** (for production)
2. Click **Next**

### Step 6: Integrate Your App
1. **User pool name**: e.g., `ve-agent-users`
2. **App client name**: e.g., `ve-agent-web`
3. **Client secret**: Select **Don't generate a client secret** (for web apps)
4. Click **Next**

### Step 7: Review and Create
1. Review all settings
2. Click **Create user pool**

## 2. Get Your Configuration Values

After creating the user pool:

### Get User Pool ID
1. In Cognito console, click on your user pool
2. Copy the **User pool ID** (format: `us-east-1_xxxxxxxxx`)

### Get App Client ID
1. Click **App integration** tab
2. Scroll down to **App clients**
3. Click on your app client
4. Copy the **Client ID** (format: `xxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### Get Region
Your AWS region from the URL (e.g., `us-east-1`, `us-west-2`)

## 3. Configure the App

### Option A: Using .env file (Recommended)

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and replace the values:
```bash
VITE_COGNITO_REGION=us-east-1
VITE_COGNITO_USER_POOL_ID=us-east-1_abcd1234
VITE_COGNITO_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j1k2l3m
```

3. Restart the dev server:
```bash
npm run dev
```

### Option B: Hardcode in cognito.js

Edit `src/config/cognito.js`:
```javascript
const cognitoConfig = {
  region: 'us-east-1',
  userPoolId: 'us-east-1_abcd1234',
  userPoolWebClientId: '1a2b3c4d5e6f7g8h9i0j1k2l3m',
}
```

## 4. Create Test Users

### In AWS Console:
1. Go to your User Pool
2. Click **Users** tab
3. Click **Create user**
4. Enter:
   - **Username**: testuser
   - **Email**: test@example.com
   - **Temporary password**: TempPass123!
5. Click **Create user**

### First Login:
1. User will need to change password on first login
2. Use the temporary password
3. Set a new permanent password

## 5. Test Authentication

1. Refresh the app: http://localhost:3000
2. You should see the login page
3. Enter credentials
4. Click **Sign In**
5. If successful, you'll see the VE Agent dashboard

## Troubleshooting

### "No user pool ID provided"
- Check that `.env` file exists and has correct values
- Restart dev server after creating `.env`

### "User does not exist"
- Make sure you created a user in Cognito console
- Check username is correct (case-sensitive)

### "Incorrect username or password"
- Check password is correct
- If first login, use temporary password

### "Network error"
- Check AWS region is correct
- Verify User Pool ID and Client ID are correct
- Check internet connection

## Security Notes

1. **Never commit `.env`** to version control (already in .gitignore)
2. **Use environment variables** for production deployments
3. **Enable MFA** for production user pools
4. **Use SES** for production email delivery
5. **Set up password policies** appropriate for your security requirements

## Production Deployment

For production, use environment variables:
```bash
# On your hosting platform (Vercel, Netlify, etc.)
VITE_COGNITO_REGION=us-east-1
VITE_COGNITO_USER_POOL_ID=your-prod-pool-id
VITE_COGNITO_CLIENT_ID=your-prod-client-id
```

## Alternative: Skip Authentication for Development

To test without Cognito temporarily, you can bypass authentication:

Edit `src/App.jsx` and set:
```javascript
const [isAuthenticated, setIsAuthenticated] = useState(true)  // Change to true
const [checkingAuth, setCheckingAuth] = useState(false)       // Change to false
```

**Note**: This is ONLY for development testing. Remove before production!

---

Need help? Check the [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)


