# 🤖 Enhanced CrewAI-Myndy Integration

**Intelligent Agent Routing + Conversation Analysis + Open WebUI Integration**

This enhanced version analyzes your conversations and automatically selects the most appropriate agent to handle each request, eliminating the need to manually choose between agents.

## 🎯 What's New

### ✨ Intelligent Agent Routing
- **Auto-selects** the best agent based on conversation analysis
- **Confidence scoring** ensures optimal agent selection
- **Conversation context** improves routing decisions over time
- **Multi-agent collaboration** suggestions for complex tasks
- **Real-time reasoning** shows why each agent was selected

### 🧠 How It Works

1. **Message Analysis**: Your message is analyzed for keywords, intent, and complexity
2. **Agent Scoring**: Each agent is scored based on relevance to your request
3. **Context Consideration**: Recent conversation history influences selection
4. **Intelligent Selection**: The best agent is automatically chosen
5. **Transparent Reasoning**: You see exactly why that agent was selected

## 🚀 Quick Start

### Step 1: Start the Enhanced Server

```bash
cd /Users/jeremy/crewAI
python api/enhanced_server.py
```

Server will be available at: `http://localhost:8001`

### Step 2: Configure Open WebUI

1. **Add Custom Model**:
   - Base URL: `http://localhost:8001`
   - Model Type: OpenAI Compatible
   - API Key: (leave empty)

2. **Select Routing Mode**:
   - **`auto`** - Intelligent automatic agent selection (recommended)
   - **Individual agents** - Manual selection (memory_librarian, research_specialist, etc.)

## 💬 Usage Examples

### Automatic Agent Selection (Recommended)

**Model**: `auto`

```
User: "Help me organize my meeting notes and remember key action items"

System: 🤖 Memory Librarian (Auto-selected)
Routing Analysis: Selected Memory Librarian (confidence: 0.11) | Keywords: remember, notes, organize | Task: moderate

Response: I'm the Memory Librarian, automatically selected to help you organize and remember information...
```

```
User: "Analyze my sleep patterns and suggest improvements"

System: 🤖 Health Analyst (Auto-selected) 
Routing Analysis: Selected Health Analyst (confidence: 0.04) | Keywords: sleep, improvement | Task: moderate

Response: I'm the Health Analyst, selected to help with your wellness optimization...
```

```
User: "How much did I spend on groceries this month?"

System: 🤖 Finance Tracker (Auto-selected)
Routing Analysis: Selected Finance Tracker (confidence: 0.15) | Keywords: spend, month | Task: simple

Response: I'm the Finance Tracker, here to help with your spending analysis...
```

## 🎭 Available Agents

| Agent | Triggers | Best For |
|-------|----------|---------|
| **Memory Librarian** | remember, recall, organize, notes, history | Knowledge organization, entity relationships |
| **Research Specialist** | research, analyze, investigate, trends, facts | Information gathering, analysis |
| **Personal Assistant** | schedule, calendar, meeting, email, task | Productivity, time management |
| **Health Analyst** | health, fitness, sleep, exercise, wellness | Health optimization, activity tracking |
| **Finance Tracker** | money, budget, spend, expense, financial | Budget analysis, expense tracking |

## 🔧 Advanced Features

### Multi-Agent Collaboration

For complex requests, the system suggests collaboration:

```
User: "I need a comprehensive analysis of my life - health, finances, and productivity"

System: 🤖 Research Specialist (Auto-selected)
Routing Analysis: Selected Research Specialist (confidence: 0.05) | Keywords: analysis, comprehensive | Task: moderate
Collaboration Suggested: Health Analyst, Finance Tracker for comprehensive approach
```

### Conversation Context

The system remembers your conversation:
- Recent agent usage influences future selections
- Conversation history provides context for routing
- Session tracking maintains context across messages

### Confidence Scoring

- **High (>0.6)**: Very confident in agent selection
- **Medium (0.3-0.6)**: Good match, may suggest collaboration
- **Low (<0.3)**: Uncertain, fallback to Memory Librarian

## 📊 API Endpoints

### Chat Endpoints
| Endpoint | Method | Description |
|----------|--------|-----------|
| `/chat/completions` | POST | OpenAI-compatible chat with intelligent routing |
| `/models` | GET | List available models (includes `auto` model) |

### Routing Endpoints
| Endpoint | Method | Description |
|----------|--------|-----------|
| `/routing/test` | GET | Test routing with sample messages |
| `/agents` | GET | List agents with routing information |
| `/sessions` | GET | View active conversation sessions |

### System Endpoints
| Endpoint | Method | Description |
|----------|--------|-----------|
| `/` | GET | Health check |
| `/status` | GET | System status with routing info |
| `/docs` | GET | API documentation |

## 🧪 Testing the Router

Test intelligent routing directly:

```bash
# Test routing logic
curl http://localhost:8001/routing/test

# Test auto model
curl -X POST http://localhost:8001/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Help me plan my workout routine"}]
  }'
```

## 🎯 Sample Routing Results

**Real test results from the system:**

```json
{
  "message": "Help me organize my notes from last week's meetings",
  "selected_agent": "memory_librarian",
  "confidence": 0.06,
  "reasoning": "Selected Memory Librarian | Keywords: notes, organize | Task: moderate"
}

{
  "message": "Schedule a meeting with John for tomorrow at 2 PM", 
  "selected_agent": "personal_assistant",
  "confidence": 0.05,
  "reasoning": "Selected Personal Assistant | Keywords: schedule, meeting | Task: moderate"
}

{
  "message": "Analyze my sleep patterns and suggest improvements",
  "selected_agent": "health_analyst", 
  "confidence": 0.04,
  "reasoning": "Selected Health Analyst | Keywords: sleep, improvement | Task: moderate"
}
```

## 🔄 Fallback Behavior

If routing fails:
1. **Fallback Agent**: Memory Librarian (most general purpose)
2. **Error Handling**: Graceful degradation to manual selection
3. **Logging**: All routing decisions are logged for debugging

## ⚙️ Configuration

### Environment Variables

```bash
# Optional: Enable debug logging
export LOG_LEVEL=DEBUG

# Optional: Custom port
export PORT=8001
```

### Custom Keywords

The routing system can be extended by modifying `/api/agent_router.py`:

```python
# Add custom keywords for better routing
keywords=[
    "your", "custom", "keywords", "here"
]
```

## 🚀 Production Deployment

### Docker

```yaml
version: '3.8'
services:
  enhanced-crewai-api:
    build: .
    ports:
      - "8001:8001"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./myndy:/myndy:ro
      
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OPENAI_API_BASE_URL=http://enhanced-crewai-api:8001
    depends_on:
      - enhanced-crewai-api
```

### Open WebUI Integration

1. **Add Model**: `http://localhost:8001` as OpenAI-compatible
2. **Select Model**: Choose `auto` for intelligent routing
3. **Chat**: Start chatting - the system automatically picks the right agent

## 🎁 Benefits

### ✅ For Users
- **No decision fatigue** - system picks the right agent
- **Faster interaction** - no need to switch between agents
- **Better results** - agents are matched to expertise areas
- **Transparent reasoning** - see why each agent was chosen

### ✅ For Developers  
- **OpenAI compatibility** - works with existing tools
- **Extensible routing** - easy to add new agents/keywords
- **Session management** - conversation context preserved
- **Rich API** - detailed routing information available

## 🔮 Future Enhancements

- **Learning from feedback** - improve routing based on user satisfaction
- **Tool-aware routing** - select agents based on available tools
- **Collaborative workflows** - orchestrated multi-agent tasks
- **User preferences** - learn individual user patterns

## 🎯 Ready to Use!

1. **Start**: `python api/enhanced_server.py`
2. **Open WebUI**: Add `http://localhost:8001` as OpenAI model
3. **Select**: Use `auto` model for intelligent routing
4. **Chat**: Let the system pick the perfect agent for each task!

---

**The future of AI assistance is here - intelligent, contextual, and effortless! 🚀**