/**
 * Authentication Service using AWS Cognito
 */
import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
} from 'amazon-cognito-identity-js'
import cognitoConfig from '../config/cognito'

// Create User Pool (only if config is valid)
let userPool = null
try {
  if (cognitoConfig.userPoolId && cognitoConfig.userPoolId !== 'YOUR_USER_POOL_ID') {
    userPool = new CognitoUserPool({
      UserPoolId: cognitoConfig.userPoolId,
      ClientId: cognitoConfig.userPoolWebClientId,
    })
  }
} catch (err) {
  console.warn('Cognito not configured:', err)
}

class AuthService {
  /**
   * Sign in user
   */
  signIn(username, password) {
    if (!userPool) {
      return Promise.reject(new Error('Cognito not configured. Please set up AWS Cognito or use development mode.'))
    }

    return new Promise((resolve, reject) => {
      const authenticationDetails = new AuthenticationDetails({
        Username: username,
        Password: password,
      })

      const cognitoUser = new CognitoUser({
        Username: username,
        Pool: userPool,
      })

      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: (result) => {
          console.log('Login successful')
          resolve({
            accessToken: result.getAccessToken().getJwtToken(),
            idToken: result.getIdToken().getJwtToken(),
            refreshToken: result.getRefreshToken().getToken(),
            user: result.getIdToken().payload,
          })
        },
        onFailure: (err) => {
          console.error('Login failed:', err)
          reject(err)
        },
        newPasswordRequired: (userAttributes, requiredAttributes) => {
          // Handle new password required
          reject(new Error('New password required'))
        },
      })
    })
  }

  /**
   * Sign out user
   */
  signOut() {
    const cognitoUser = userPool.getCurrentUser()
    if (cognitoUser) {
      cognitoUser.signOut()
    }
  }

  /**
   * Get current authenticated user
   */
  getCurrentUser() {
    if (!userPool) {
      return Promise.reject(new Error('Cognito not configured'))
    }

    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser()

      if (!cognitoUser) {
        reject(new Error('No user found'))
        return
      }

      cognitoUser.getSession((err, session) => {
        if (err) {
          reject(err)
          return
        }

        if (!session.isValid()) {
          reject(new Error('Session is not valid'))
          return
        }

        cognitoUser.getUserAttributes((err, attributes) => {
          if (err) {
            reject(err)
            return
          }

          const userData = {}
          attributes.forEach((attr) => {
            userData[attr.Name] = attr.Value
          })

          resolve({
            username: cognitoUser.getUsername(),
            attributes: userData,
            session: session,
          })
        })
      })
    })
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    if (!userPool) {
      return Promise.resolve(false)
    }

    const cognitoUser = userPool.getCurrentUser()
    if (!cognitoUser) {
      return Promise.resolve(false)
    }

    return new Promise((resolve) => {
      cognitoUser.getSession((err, session) => {
        if (err || !session.isValid()) {
          resolve(false)
        } else {
          resolve(true)
        }
      })
    })
  }
}

export default new AuthService()

