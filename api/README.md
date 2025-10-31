# CrewAI-Myndy OpenAPI Server

OpenAPI server for the CrewAI-Myndy integration, providing RESTful access to multi-agent workflows through a standardized API interface. Compatible with Open WebUI and other front-end applications.

## Features

### 🤖 Multi-Agent System
- **5 Specialized Agents** with distinct roles and capabilities
- **Memory Librarian** - Knowledge organization and retrieval
- **Research Specialist** - Information gathering and verification
- **Personal Assistant** - Productivity and task management
- **Health Analyst** - Health data analysis and wellness insights
- **Finance Tracker** - Financial analysis and expense tracking

### 🛠️ Tool Integration
- **31+ Myndy Tools** accessible via RESTful API
- **Tool discovery** and metadata endpoints
- **Category-based organization** (memory, research, health, finance)
- **Parameter validation** and error handling

### 🔗 Open WebUI Compatibility
- **OpenAI-compatible endpoints** (`/chat/completions`, `/models`)
- **Agent selection** via model parameter
- **Streaming responses** (optional)
- **Authentication support** (configurable)

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/jeremy/crewAI
pip install -r api/requirements.txt
```

### 2. Start the Server

```bash
# Development server with auto-reload
python api/main.py

# Production server
python api/server.py
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Specification**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/

## API Endpoints

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/status` | System status and metrics |
| GET | `/models` | List available agents (OpenAI-compatible) |

### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/agents` | List all available agents |
| POST | `/agents/{agent_role}/chat` | Chat with specific agent |
| POST | `/chat/completions` | OpenAI-compatible chat endpoint |

### Task Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks` | Create and execute a task |
| GET | `/tasks/{task_id}` | Get task status and results |
| POST | `/crews/execute` | Execute multi-agent crew task |

### Tool Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tools` | List available tools |
| POST | `/tools/execute` | Execute specific tool |

## Open WebUI Integration

### 1. Configuration

Use the provided configuration file:

```bash
cp api/open_webui_config.json /path/to/open-webui/configs/
```

### 2. Add as Custom Model

In Open WebUI admin panel:

1. Go to **Admin Panel > Models**
2. Add custom model with base URL: `http://localhost:8000`
3. Select model type: **OpenAI Compatible**
4. Choose agent: `memory_librarian`, `research_specialist`, etc.

### 3. Agent Selection

Each agent appears as a separate "model" in Open WebUI:

- **memory_librarian** - For knowledge and memory tasks
- **research_specialist** - For research and analysis
- **personal_assistant** - For productivity tasks
- **health_analyst** - For health and wellness
- **finance_tracker** - For financial analysis

## Usage Examples

### Chat with Memory Librarian

```bash
curl -X POST "http://localhost:8000/agents/memory_librarian/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What did I discuss with John last week?",
    "memory_enabled": true
  }'
```

### Execute Life Analysis Task

```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "life_analysis",
    "description": "Analyze my productivity over the last month",
    "priority": "medium"
  }'
```

### OpenAI-Compatible Chat

```bash
curl -X POST "http://localhost:8000/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "research_specialist",
    "messages": [
      {"role": "user", "content": "Research the latest AI developments"}
    ],
    "temperature": 0.7
  }'
```

## Configuration

### Environment Variables

```bash
# Server configuration
export HOST=0.0.0.0
export PORT=8000
export LOG_LEVEL=INFO

# Ollama configuration (inherited from main project)
export OLLAMA_BASE_URL=http://localhost:11434
export MEMEX_DEFAULT_MODEL=llama3

# Optional: Authentication
export API_KEY_REQUIRED=false
export API_KEY=your-secret-key
```

### Agent Models

Each agent uses a specific Ollama model optimized for its role:

- **Memory Librarian**: `llama3` (structured data handling)
- **Research Specialist**: `mixtral` (reasoning and analysis)
- **Personal Assistant**: `gemma` (fast responses)
- **Health Analyst**: `phi` (efficient analysis)
- **Finance Tracker**: `mistral` (numerical data)

## Development

### Project Structure

```
api/
├── main.py                 # Core FastAPI application
├── server.py              # Production server setup
├── models.py              # Pydantic models and schemas
├── openapi_extensions.py  # Open WebUI compatibility
├── open_webui_config.json # Open WebUI configuration
├── requirements.txt       # API-specific dependencies
└── README.md              # This file
```

### Adding New Endpoints

1. Define request/response models in `models.py`
2. Implement endpoint in `main.py`
3. Add to appropriate tag group
4. Update OpenAPI documentation

### Testing

```bash
# Run API tests
pytest api/tests/

# Manual testing with httpx
python -c "
import httpx
response = httpx.get('http://localhost:8000/status')
print(response.json())
"
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r api/requirements.txt

EXPOSE 8000
CMD ["python", "api/server.py"]
```

### Production Considerations

1. **Authentication**: Enable API key authentication for production
2. **Rate Limiting**: Add rate limiting middleware
3. **CORS**: Configure appropriate CORS origins
4. **Logging**: Set up structured logging and monitoring
5. **Health Checks**: Implement comprehensive health checks
6. **SSL/TLS**: Use reverse proxy (nginx) for HTTPS

## Troubleshooting

### Common Issues

**Q: "Tool loader not available"**
A: Ensure myndy system is properly initialized and paths are correct

**Q: "Ollama connection failed"**  
A: Verify Ollama is running on `localhost:11434` with required models

**Q: "Agent creation failed"**
A: Check that all required dependencies are installed and models are available

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python api/server.py
```

### Health Check

```bash
curl http://localhost:8000/status
```

Expected response includes:
- `agents_available: 5`
- `tools_available: 31+`
- `ollama_status: true`

## Contributing

1. Follow FastAPI best practices
2. Add comprehensive tests for new endpoints
3. Update OpenAPI documentation
4. Ensure Open WebUI compatibility
5. Test with real Open WebUI instance

## License

This project inherits the license from the main CrewAI-Myndy integration.