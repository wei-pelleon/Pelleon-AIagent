# Value Engineering AI Agent

A comprehensive Value Engineering platform for building materials optimization with AI-powered chat assistance.

## Features

- **Material Optimization**: Compare windows, doors, and appliances with cost-effective alternatives
- **AI Chat Assistant**: Ask questions about your project data using natural language
- **Optimization Strategies**: 4 preset optimization approaches (Functional+Cost, Design+Cost, Lowest Cost, Balanced)
- **Real Product Brands**: Alternatives include actual manufacturer brands and models
- **Professional UI**: Clean, modern interface with collapsible sections and real-time calculations

## Tech Stack

- **Frontend**: React + Vite
- **Backend**: FastAPI + Python
- **AI**: OpenAI GPT-4o-mini with LangChain
- **Deployment**: AWS Amplify (Frontend) + AWS Lambda/ECS (Backend)

## Quick Start

### Local Development

1. **Backend**:
   ```bash
   cd /path/to/VEAgent
   source venv/bin/activate
   python3 agent/chat_server.py
   ```

2. **Frontend**:
   ```bash
   cd ux
   npm install
   npm run dev
   ```

3. **Access**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Environment Setup

1. Copy `env.example` to `.env` and add your API keys:
   ```bash
   cp env.example .env
   ```

2. Required environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `VITE_API_BASE_URL`: Backend API URL (for production)

## Deployment

### AWS Amplify (Frontend)

1. Connect GitHub repository: `https://github.com/wei-pelleon/Pelleon-AIagent`
2. Build settings are configured in `amplify.yml`
3. Environment variables:
   - `VITE_SKIP_AUTH=true`
   - `VITE_API_BASE_URL=https://api.agent.pelleon.com`

### Backend Deployment

The FastAPI backend needs to be deployed separately to AWS (Lambda, ECS, or EC2).

## Project Structure

```
├── agent/                 # Python backend
│   ├── chat_server.py    # FastAPI server
│   ├── chat_agent_v2.py  # LangChain agent
│   ├── data_tools.py     # Data access tools
│   └── ...
├── ux/                   # React frontend
│   ├── src/
│   ├── public/           # Static data files
│   └── package.json
├── data/                 # Project data
│   ├── processed/        # Generated alternatives
│   ├── counts/           # Material counts
│   └── schedule/         # Project schedules
└── rsmeans/             # Cost data
```

## Data Pipeline

1. **Material Matching**: Match project materials to RSMeans cost data
2. **Alternative Generation**: Find cost-effective alternatives
3. **LLM Evaluation**: Score alternatives on functional/design criteria
4. **Optimization**: Calculate optimal selections for different strategies
5. **Product Enhancement**: Add real brand names and models

## Chat Features

The AI chat assistant can answer questions about:
- Material counts and quantities
- Cost analysis and savings
- Alternative comparisons
- Project specifications
- Optimization results

## License

Private - Pelleon AI