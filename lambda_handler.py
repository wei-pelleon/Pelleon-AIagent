import json
import os
import sys
from mangum import Mangum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from agent.chat_agent_simple_lambda import get_agent

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create FastAPI app
app = FastAPI(title="VE Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str

@app.get("/")
async def root():
    return {
        "message": "VE Agent Chat API",
        "endpoints": {
            "/chat/stream": "POST - Stream chat responses",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat/stream")
async def chat_stream(request: ChatMessage):
    """Stream chat responses."""
    
    def generate_response():
        try:
            agent = get_agent()
            response = agent.chat(request.message)
            
            # Stream the response token by token
            words = response.split()
            for i, word in enumerate(words):
                token = word + (" " if i < len(words) - 1 else "")
                yield {
                    "event": "token",
                    "data": json.dumps({"token": token})
                }
            
            # Send completion event
            yield {
                "event": "complete", 
                "data": json.dumps({"status": "completed"})
            }
            
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(generate_response())

# Create the ASGI handler
handler = Mangum(app, lifespan="off")
