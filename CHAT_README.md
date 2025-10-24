# VE Agent Chat Interface

An AI-powered chat assistant that can answer questions about your Value Engineering project data.

## Architecture

### Backend (Python)
- **LangGraph**: Multi-agent architecture with memory
- **Tools**: 14 data tools (each table is a tool)
- **LLM**: OpenAI GPT-4-mini for intelligent responses
- **Streaming**: Token-by-token streaming via SSE

### Frontend (React)
- **Position**: Fixed panel on the right side
- **Collapsible**: Click to expand/collapse
- **Streaming UI**: Shows tokens as they arrive
- **Beautiful**: Elegant chat bubbles and animations

## Quick Start

### 1. Set OpenAI API Key

```bash
# Option A: Environment variable
export OPENAI_API_KEY='your-api-key-here'

# Option B: Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 2. Start Backend Server

```bash
./start_chat_server.sh
```

This starts the API server on **http://localhost:8000**

### 3. Start Frontend (if not running)

```bash
cd ux
npm run dev
```

Frontend runs on **http://localhost:3000**

### 4. Use the Chat

1. Open http://localhost:3000
2. Look for the **💬 AI Assistant** panel on the right
3. Click to expand if collapsed
4. Type your question and press Enter!

## Example Questions

### About Costs
- "What's the total cost for all windows?"
- "How much can we save on doors?"
- "What are the most expensive appliances?"

### About Materials
- "List all window types and their quantities"
- "What doors are used in 2-bedroom units?"
- "Show me all exterior doors"

### About Alternatives
- "What alternatives exist for window W2?"
- "Which windows have the best cost reduction?"
- "Compare functional vs design scores for doors"

### About the Project
- "How many apartment units are in the building?"
- "What's the total leasable area?"
- "Show me the unit mix breakdown"

## Available Data Tools

The AI assistant has access to 14 data tools:

### Project Data
1. `get_apartment_specs` - Unit types, areas, floor distributions
2. `get_total_areas` - Building area calculations

### Windows
3. `get_window_schedule` - Window specifications
4. `get_window_counts` - Window quantities by facade
5. `get_matched_windows` - Windows with RSMeans costs
6. `get_window_alternatives` - Strategic alternatives with scores

### Doors
7. `get_door_schedule` - Door specifications
8. `get_door_counts` - Door quantities by unit
9. `get_matched_doors` - Doors with RSMeans costs
10. `get_door_alternatives` - Alternatives with scores

### Appliances
11. `get_appliance_counts` - Appliance specifications and quantities
12. `get_matched_appliances` - Appliances with costs

### RSMeans Database
13. `get_rsmeans_windows` - RSMeans window pricing
14. `get_rsmeans_doors` - RSMeans door pricing

## Features

### Multi-Agent Architecture
- Agent automatically selects which tools to use
- Can combine data from multiple sources
- Maintains conversation context

### Memory & Checkpointing
- Remembers previous questions in the session
- Can reference earlier parts of the conversation
- Thread-based conversation tracking

### Streaming Responses
- Tokens appear one at a time (like ChatGPT)
- Smooth, real-time experience
- Visual typing indicator while thinking

### Beautiful UI
- Collapsible side panel
- User messages in purple bubbles (right-aligned)
- AI messages in white bubbles (left-aligned)
- Smooth animations
- Auto-scroll to latest message

## Technical Details

### Backend API Endpoints

**POST /chat/stream**
- Streams response using Server-Sent Events (SSE)
- Body: `{ "message": "your question", "thread_id": "session-1" }`
- Returns: Stream of tokens

**GET /health**
- Health check
- Returns: `{ "status": "ok", "model": "gpt-4o-mini" }`

### How It Works

```
User Question
    ↓
Frontend (React)
    ↓ POST /chat/stream
Backend (FastAPI)
    ↓
LangGraph Agent
    ↓
Calls Data Tools
    ↓
OpenAI GPT-4-mini
    ↓
Streams Response ← ← ← Token by token
    ↓
Frontend displays each token
```

## Troubleshooting

### "Error connecting to chat server"
**Solution**: Make sure backend is running on port 8000
```bash
./start_chat_server.sh
```

### "OpenAI API key not set"
**Solution**: Set your API key
```bash
export OPENAI_API_KEY='sk-...'
```

### Chat not visible
**Solution**: Look for the chat panel on the far right, click the toggle if collapsed

### Slow responses
- First response may be slower (loading data)
- Subsequent responses are faster (cached)
- Complex queries take longer

## Development

### Test Backend Directly

```bash
cd agent
python3 chat_agent.py
```

### Test API Endpoint

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "How many windows are there?", "thread_id": "test"}'
```

### View API Docs

Open http://localhost:8000/docs for interactive API documentation

## Production Deployment

### Backend
```bash
# Use gunicorn or similar
gunicorn agent.chat_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
Build and deploy the React app with the backend URL:
```bash
cd ux
VITE_API_URL=https://your-backend.com npm run build
```

## Security Notes

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Implement authentication** for production
4. **Rate limit** the chat endpoint
5. **Validate** all user inputs

## Future Enhancements

- [ ] Voice input
- [ ] Export chat history
- [ ] Share conversations
- [ ] Suggested questions
- [ ] Data visualization in chat
- [ ] Multi-language support

---

**Enjoy your AI-powered Value Engineering assistant!** 🤖💰


