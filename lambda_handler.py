import json
import os
import sys
from mangum import Mangum
from agent.chat_server import app

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create the ASGI handler
handler = Mangum(app, lifespan="off")
