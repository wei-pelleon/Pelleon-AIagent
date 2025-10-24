"""
FastAPI server for VE Chat Agent with streaming support.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from chat_agent_v2 import VEChatAgent
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="VE Agent Chat API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = VEChatAgent()


class ChatMessage(BaseModel):
    message: str
    thread_id: str = "default"


@app.post("/chat/stream")
async def chat_stream(chat: ChatMessage):
    """Stream chat response using Server-Sent Events."""
    
    async def event_generator():
        try:
            async for token in agent.stream_response(chat.message, chat.thread_id):
                # Send each token as an SSE event
                yield {
                    "event": "token",
                    "data": json.dumps({"token": token})
                }
            
            # Send done event
            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"})
            }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "model": "gpt-4o-mini"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "VE Agent Chat API",
        "endpoints": {
            "/chat/stream": "POST - Stream chat responses",
            "/health": "GET - Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting VE Agent Chat Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📝 Docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

