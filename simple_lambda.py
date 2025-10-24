import json
import os

def handler(event, context):
    """Simple Lambda handler for testing."""
    
    # Get the HTTP method and path
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    
    if path == '/health':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({'status': 'healthy'})
        }
    
    elif path == '/chat/stream' and http_method == 'POST':
        # Simple chat response
        try:
            body = json.loads(event.get('body', '{}'))
            message = body.get('message', 'Hello')
            
            response = f"Echo: {message}"
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({'response': response})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': str(e)})
            }
    
    else:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'VE Agent API',
                'endpoints': {
                    '/chat/stream': 'POST - Chat endpoint',
                    '/health': 'GET - Health check'
                }
            })
        }
