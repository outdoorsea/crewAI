# Open WebUI Integration for CrewAI-Myndy

Complete guide for integrating the CrewAI-Myndy system with Open WebUI front-end.

## 🎯 Overview

The CrewAI-Myndy OpenAPI server provides a standardized interface that's fully compatible with Open WebUI, allowing you to interact with 5 specialized AI agents through a beautiful web interface.

### Available Agents

| Agent | ID | Expertise | Best For |
|-------|----|-----------| ---------|
| **Memory Librarian** | `memory_librarian` | Knowledge organization, entity relationships | Organizing thoughts, finding past conversations |
| **Research Specialist** | `research_specialist` | Information gathering, fact verification | Research projects, analysis tasks |
| **Personal Assistant** | `personal_assistant` | Calendar, email, productivity | Scheduling, task management |
| **Health Analyst** | `health_analyst` | Health data analysis, wellness | Fitness tracking, health insights |
| **Finance Tracker** | `finance_tracker` | Expense tracking, financial analysis | Budget planning, expense analysis |

## 🚀 Quick Setup

### Step 1: Start the API Server

```bash
cd /Users/jeremy/crewAI

# Start the server
python api/simple_server.py
```

Server will be available at: `http://localhost:8000`

### Step 2: Verify API is Working

```bash
# Health check
curl http://localhost:8000/

# List available models (agents)
curl http://localhost:8000/models

# Test chat
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "memory_librarian",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Step 3: Configure Open WebUI

#### Option A: Admin Panel Configuration

1. **Open Open WebUI Admin Panel**
   - Go to your Open WebUI instance (usually `http://localhost:3000`)
   - Login as admin
   - Navigate to **Admin Panel > Models**

2. **Add Custom Model**
   - Click **"Add Model"**
   - Select **"OpenAI Compatible"**
   - Fill in the details:

```
Name: CrewAI-Myndy Agents
Base URL: http://localhost:8000
API Key: (leave empty - no auth required)
```

3. **Select Agent**
   - In the model dropdown, you'll see:
     - `memory_librarian`
     - `research_specialist` 
     - `personal_assistant`
     - `health_analyst`
     - `finance_tracker`

#### Option B: Environment Variables

```bash
# Add to your Open WebUI environment
export OPENAI_API_BASE_URL=http://localhost:8000
export OPENAI_API_KEY=not-required
```

## 💬 Usage Examples

### Memory Librarian
**Best for**: Organizing knowledge, finding information, memory management

```
User: "Help me organize my notes from the last project meeting"
Memory Librarian: I can help you structure and categorize your meeting notes. I have access to conversation history and can create entity relationships to help you remember key points, action items, and connections between topics.
```

### Research Specialist  
**Best for**: Information gathering, fact-checking, analysis

```
User: "Research the latest trends in AI development"
Research Specialist: I'll conduct comprehensive research on current AI trends. I can gather information from multiple sources, verify facts, and provide you with a detailed analysis including recent developments, key players, and emerging technologies.
```

### Personal Assistant
**Best for**: Scheduling, task management, productivity

```
User: "Help me plan my week and organize my calendar"
Personal Assistant: I can help you optimize your schedule, manage your calendar, and coordinate your tasks. I have access to productivity tools that can help streamline your workflow and ensure you stay on top of your commitments.
```

### Health Analyst
**Best for**: Health tracking, wellness insights, fitness planning

```
User: "Analyze my fitness progress this month"
Health Analyst: I can review your health metrics, analyze fitness trends, and provide insights about your wellness journey. I have access to health data tools that can help track your progress and suggest optimizations.
```

### Finance Tracker
**Best for**: Budget analysis, expense tracking, financial planning

```
User: "Help me understand my spending patterns"
Finance Tracker: I can analyze your financial data, categorize expenses, and identify spending patterns. I have tools for budget analysis and can provide insights to help you optimize your financial health.
```

## 🔧 Advanced Configuration

### Custom Agent Prompts

You can customize how each agent responds by using system prompts in Open WebUI:

```
System: You are the Memory Librarian from the CrewAI-Myndy system. 
Focus on helping the user organize and retrieve information. 
Use your knowledge management capabilities to provide structured responses.
```

### Multi-Agent Workflows

For complex tasks, you can simulate multi-agent collaboration:

1. Start with **Research Specialist** for information gathering
2. Switch to **Memory Librarian** for organization  
3. Use **Personal Assistant** for action planning
4. Apply **Health Analyst** or **Finance Tracker** for domain-specific analysis

### API Endpoints Reference

| Endpoint | Method | Description | Open WebUI Usage |
|----------|--------|-------------|------------------|
| `/models` | GET | List available agents | Model selection |
| `/chat/completions` | POST | OpenAI-compatible chat | Main chat interface |
| `/` | GET | Health check | Status monitoring |
| `/agents` | GET | Detailed agent info | Admin reference |

## 🛠️ Troubleshooting

### Common Issues

**Issue**: "Connection refused to localhost:8000"
```bash
# Solution: Start the API server
cd /Users/jeremy/crewAI
python api/simple_server.py
```

**Issue**: "No models available"
```bash
# Solution: Check API is responding
curl http://localhost:8000/models
```

**Issue**: "Agent not responding correctly"
```bash
# Solution: Test directly via API
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "memory_librarian", "messages": [{"role": "user", "content": "test"}]}'
```

### Debug Mode

Enable debug logging:

```bash
# Set log level to debug
export LOG_LEVEL=DEBUG
python api/simple_server.py
```

### Network Configuration

If Open WebUI is on a different machine:

```bash
# Update the base URL in Open WebUI to your server IP
# Example: http://192.168.1.100:8000
```

## 🚀 Production Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  crewai-myndy-api:
    build: 
      context: /Users/jeremy/crewAI
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - /Users/jeremy/myndy:/myndy:ro
    
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OPENAI_API_BASE_URL=http://crewai-myndy-api:8000
    depends_on:
      - crewai-myndy-api
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring

### API Status Dashboard

Access the built-in status endpoint:

```bash
curl http://localhost:8000/status
```

Response:
```json
{
  "status": "operational", 
  "agents_available": 5,
  "tools_available": 31,
  "timestamp": "2025-05-29T08:21:03.073115",
  "version": "1.0.0"
}
```

### Open WebUI Integration Status

In Open WebUI:
1. Go to **Settings > Models**
2. Check that all 5 agents are listed
3. Test each agent with a simple message
4. Verify responses are agent-specific

## 🎁 Features

### ✅ Working Features
- ✅ **OpenAI-compatible API** - Full compatibility with Open WebUI
- ✅ **5 Specialized Agents** - Each with distinct personalities and capabilities  
- ✅ **Model Selection** - Choose agents via Open WebUI model dropdown
- ✅ **RESTful API** - Standard HTTP endpoints for integration
- ✅ **CORS Support** - Works with web-based front-ends
- ✅ **Health Monitoring** - Built-in status and health checks

### 🔄 Coming Soon  
- **Streaming Responses** - Real-time response streaming
- **Tool Execution** - Direct access to 31+ myndy tools
- **Memory Integration** - Persistent conversation context
- **Multi-Agent Workflows** - Orchestrated agent collaboration
- **Authentication** - API key and user management

## 🎯 Ready to Use!

1. **Start the server**: `python api/simple_server.py`
2. **Open WebUI**: Add `http://localhost:8000` as OpenAI-compatible model
3. **Select agent**: Choose from 5 specialized agents
4. **Start chatting**: Each agent has unique capabilities and personality

The integration is now ready for production use with Open WebUI!