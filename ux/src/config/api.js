// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://ve-agent-alb-1735797675.us-east-1.elb.amazonaws.com'

export const API_ENDPOINTS = {
  CHAT_STREAM: `${API_BASE_URL}/chat/stream`,
  HEALTH: `${API_BASE_URL}/health`
}

export default API_ENDPOINTS
