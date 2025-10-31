# LibreChat Integration Guide

## Overview

This guide explains how to integrate the Myndy CrewAI MCP Server with LibreChat, enabling access to 33 AI tools, 14 data resources, and 16 agent workflow prompts through LibreChat's chat interface.

## Prerequisites

### Required Software

1. **Myndy-AI Backend** (already running)
   - URL: `http://localhost:8000`
   - Status: Should be running and accessible

2. **Myndy CrewAI MCP Server** (already configured)
   - Location: `/Users/jeremy/myndy-core/myndy-crewai/`
   - Port: 9092
   - Start command: `python3 start_mcp_server.py`

3. **LibreChat** (to be installed)
   - Repository: https://github.com/danny-avila/LibreChat
   - Requirements: Node.js 18+, MongoDB, Redis (optional)

### System Requirements

- **OS**: macOS, Linux, or Windows with WSL
- **Python**: 3.10+
- **Node.js**: 18.x or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for LibreChat + dependencies

## Installation Steps

### 1. Install LibreChat

```bash
# Clone LibreChat repository
cd ~/projects
git clone https://github.com/danny-avila/LibreChat.git
cd LibreChat

# Install dependencies
npm install

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file:

```bash
# LibreChat Core Settings
APP_TITLE="Myndy AI Assistant"
PORT=3080
HOST=localhost

# MongoDB (required)
MONGO_URI=mongodb://127.0.0.1:27017/LibreChat

# Redis (optional, for caching)
REDIS_URI=redis://localhost:6379

# MCP Server Configuration
MCP_ENABLED=true
MCP_SERVER_URL=http://localhost:9092

# API Keys (if using cloud models)
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Local Model Configuration (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Configure LibreChat for MCP

Copy the provided `librechat.yaml` to LibreChat directory:

```bash
# From myndy-crewai directory
cp librechat.yaml ~/projects/LibreChat/librechat.yaml
```

Or create a new `librechat.yaml` in LibreChat root:

```yaml
version: 1.1.0

# MCP Server Configuration
mcpServers:
  myndy_crewai:
    # Server command - adjust path to match your installation
    command: python3
    args:
      - "/Users/jeremy/myndy-core/myndy-crewai/start_mcp_server.py"

    # Environment variables for MCP server
    env:
      MYNDY_API_URL: "http://localhost:8000"
      MCP_LOG_LEVEL: "INFO"
      MCP_DEBUG: "false"
      MCP_VERBOSE: "false"

    # Server metadata
    description: "Myndy CrewAI MCP Server with 33 tools, 14 resources, and 16 agent prompts"
    serverInstructions: true

# Custom Endpoint Configuration
endpoints:
  custom:
    - name: "Myndy AI"
      apiKey: "user_provided"
      baseURL: "http://localhost:9092"

      # Available models (agent personas)
      models:
        default:
          - "myndy-assistant"
          - "myndy-memory"
          - "myndy-research"
          - "myndy-health"
          - "myndy-finance"

      # UI Settings
      titleConvo: true
      summarize: false
      modelDisplayLabel: "Myndy AI Agent"

      # MCP Integration
      mcpServers:
        - myndy_crewai

# Interface Configuration
interface:
  tools:
    mcp: true  # Enable MCP tools in UI

  privacyPolicy:
    externalUrl: ""
    openNewTab: false

# Model Specifications
modelSpecs:
  enforce: false
  prioritize: true
  list:
    - name: "myndy-assistant"
      label: "Personal Assistant"
      description: "Calendar, email, weather, time management"
      preset: "myndy-ai"

    - name: "myndy-memory"
      label: "Memory Librarian"
      description: "Entity management, memory search, knowledge"
      preset: "myndy-ai"

    - name: "myndy-research"
      label: "Research Specialist"
      description: "Information gathering, document analysis"
      preset: "myndy-ai"

    - name: "myndy-health"
      label: "Health Analyst"
      description: "Health data analysis, wellness insights"
      preset: "myndy-ai"

    - name: "myndy-finance"
      label: "Finance Tracker"
      description: "Expense tracking, budget management"
      preset: "myndy-ai"
```

### 4. Start Required Services

**Terminal 1: Start Myndy-AI Backend** (if not running)
```bash
cd /Users/jeremy/myndy-core/myndy-ai
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2: Start MCP Server**
```bash
cd /Users/jeremy/myndy-core/myndy-crewai
python3 start_mcp_server.py
```

**Terminal 3: Start MongoDB** (if not running)
```bash
# macOS with Homebrew
brew services start mongodb-community

# Linux
sudo systemctl start mongodb

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Terminal 4: Start LibreChat**
```bash
cd ~/projects/LibreChat
npm run backend
```

**Terminal 5: Start LibreChat Frontend** (in development)
```bash
cd ~/projects/LibreChat
npm run frontend
```

### 5. Verify Installation

1. **Check MCP Server Health**:
   ```bash
   curl http://localhost:9092/health
   # Expected: {"status":"healthy","server":"myndy-crewai-mcp"}
   ```

2. **Check Myndy-AI Backend**:
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status":"healthy"}
   ```

3. **Access LibreChat**:
   - Open browser: `http://localhost:3080`
   - Create account or login
   - Should see "Myndy AI" in model selection

## Using MCP Features in LibreChat

### 1. Selecting Agent Personas

In LibreChat chat interface:

1. Click on model selector dropdown
2. Look for "Myndy AI Agent" or custom endpoint
3. Choose agent persona:
   - **Personal Assistant**: For scheduling, emails, time queries
   - **Memory Librarian**: For memory operations, entity management
   - **Research Specialist**: For research and document analysis
   - **Health Analyst**: For health data and wellness insights
   - **Finance Tracker**: For expense tracking and budgets

### 2. Using Tools

Tools are invoked automatically based on conversation context:

**Example Conversations**:

```
User: "What time is it in Tokyo?"
→ MCP Server executes get_current_time tool
→ Returns current time in Asia/Tokyo timezone

User: "Search my memory for people named John"
→ MCP Server executes search_memory tool
→ Returns matching people entities

User: "Show me my schedule for tomorrow"
→ MCP Server executes calendar tools
→ Returns schedule information
```

**Manual Tool Invocation** (if supported):
```
User: "/tool get_current_time timezone=America/New_York"
→ Directly invokes tool with parameters
```

### 3. Accessing Resources

Resources provide context data via `myndy://` URIs:

**Example Requests**:

```
User: "What's in my memory?"
→ Agent accesses myndy://memory/entities resource
→ Returns all memory entities

User: "Show me my profile"
→ Agent accesses myndy://profile/self resource
→ Returns user profile data

User: "What are my current goals?"
→ Agent accesses myndy://profile/goals resource
→ Returns goal list
```

### 4. Using Prompts

Prompts initialize conversations with pre-configured agent workflows:

**Available Prompts**:

1. **Personal Assistant Prompts**:
   - `personal_assistant` - General PA tasks
   - `schedule_management` - Calendar operations
   - `time_query` - Time and timezone queries

2. **Memory Librarian Prompts**:
   - `memory_search` - Search memory
   - `entity_management` - Manage entities
   - `conversation_analysis` - Extract insights

3. **Research Specialist Prompts**:
   - `research_specialist` - Research tasks
   - `information_gathering` - Topic research
   - `document_analysis` - Analyze documents

4. **Health Analyst Prompts**:
   - `health_metrics` - Analyze metrics
   - `wellness_insights` - Wellness recommendations

5. **Finance Tracker Prompts**:
   - `expense_tracking` - Track expenses
   - `budget_analysis` - Analyze budget

**Using Prompts** (if LibreChat UI supports):
```
1. Click "Use Prompt" or "Load Template"
2. Select agent category (e.g., "Personal Assistant")
3. Choose specific prompt (e.g., "schedule_management")
4. Fill in arguments (e.g., action: "view", date: "tomorrow")
5. Prompt initializes conversation with pre-configured context
```

## Configuration Options

### MCP Server Configuration

Edit environment variables before starting MCP server:

```bash
# Set Myndy API URL
export MYNDY_API_URL="http://localhost:8000"

# Set MCP Server Port (default: 9092)
export MCP_SERVER_PORT="9092"

# Enable debug logging
export MCP_DEBUG="true"
export MCP_LOG_LEVEL="DEBUG"

# Feature toggles
export MCP_ENABLE_TOOLS="true"
export MCP_ENABLE_RESOURCES="true"
export MCP_ENABLE_PROMPTS="true"

# Start server
python3 start_mcp_server.py
```

### LibreChat Configuration

Edit `librechat.yaml` to customize:

```yaml
# Add more model options
models:
  default:
    - "myndy-assistant"
    - "myndy-memory"
    - "myndy-research"
    - "myndy-health"
    - "myndy-finance"
    - "gpt-4"  # Mix with cloud models

# Customize interface
interface:
  tools:
    mcp: true
    fileUploads: true
  features:
    conversationHistory: true
    messageSearch: true
```

## Troubleshooting

### MCP Server Issues

**Problem**: MCP server won't start
```bash
# Check if port is in use
lsof -i :9092

# Check logs
tail -f /tmp/mcp_server.log

# Verify Python packages
pip list | grep mcp
```

**Problem**: Tools not appearing in LibreChat
```bash
# Verify tools are registered
curl http://localhost:9092/health

# Check MCP server logs
tail -f /tmp/mcp_server.log | grep "Tools"

# Restart MCP server
pkill -f start_mcp_server.py
python3 start_mcp_server.py
```

### LibreChat Issues

**Problem**: LibreChat won't start
```bash
# Check MongoDB is running
mongo --eval "db.version()"

# Check LibreChat logs
npm run backend 2>&1 | tee librechat.log

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Problem**: MCP features not showing
```bash
# Verify librechat.yaml is in correct location
ls -la librechat.yaml

# Check LibreChat config loading
grep -r "mcpServers" logs/

# Restart LibreChat
npm run backend
```

### Connection Issues

**Problem**: MCP server can't reach Myndy-AI
```bash
# Test connectivity
curl http://localhost:8000/health

# Check firewall
sudo lsof -i :8000

# Verify API URL in MCP config
env | grep MYNDY_API_URL
```

**Problem**: LibreChat can't reach MCP server
```bash
# Test SSE endpoint
curl http://localhost:9092/sse

# Check CORS settings
curl -H "Origin: http://localhost:3080" http://localhost:9092/health

# Verify MCP server is accessible
telnet localhost 9092
```

## Testing Integration

### 1. Test Tool Execution

```bash
# From myndy-crewai directory
python3 test_tool_execution.py
```

Expected: All tools execute successfully

### 2. Test Resource Access

```bash
python3 test_resource_access.py
```

Expected: All resources accessible

### 3. Test Prompts

```bash
python3 test_prompts.py
```

Expected: All prompts return correct messages

### 4. End-to-End Test in LibreChat

1. **Start Conversation**:
   - Open LibreChat
   - Select "Myndy AI" endpoint
   - Choose "Personal Assistant" model

2. **Test Tool Execution**:
   ```
   User: "What time is it in London?"
   Expected: Tool executes, returns current time in Europe/London
   ```

3. **Test Memory Access**:
   ```
   User: "What do you know about me?"
   Expected: Agent accesses profile resource, returns user data
   ```

4. **Test Agent Switching**:
   - Switch to "Memory Librarian"
   - Ask: "Search my memory for people I know"
   - Expected: Memory search executes, returns results

5. **Test Multi-Turn Conversation**:
   ```
   User: "Schedule a meeting for tomorrow at 2pm"
   Agent: Uses schedule_management prompt and tools

   User: "Actually, make it 3pm"
   Agent: Updates schedule using context
   ```

## Performance Optimization

### MCP Server

```bash
# Increase worker processes (if using production server)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker myndy_crewai_mcp.main:app

# Enable caching
export MCP_ENABLE_CACHE="true"
export MCP_CACHE_TTL="300"  # 5 minutes

# Optimize connection pooling
export HTTP_POOL_SIZE="100"
export HTTP_POOL_PER_HOST="30"
```

### LibreChat

```yaml
# In librechat.yaml
cache:
  type: "redis"
  options:
    host: "localhost"
    port: 6379
    ttl: 300

# Rate limiting
rateLimits:
  fileUploads:
    ipMax: 100
    userMax: 50
```

## Security Considerations

### MCP Server Security

1. **Authentication** (if needed):
   ```bash
   export MCP_API_KEY="your-secret-key"
   ```

2. **CORS Configuration**:
   ```python
   # In config.py
   cors_allowed_origins = ["http://localhost:3080"]
   ```

3. **Input Validation**:
   - All tool parameters validated via Pydantic
   - Resource URIs validated before access
   - Prompt arguments sanitized

### LibreChat Security

1. **User Authentication**: Enable in `.env`
   ```bash
   ALLOW_REGISTRATION=true
   SESSION_SECRET="your-secret-key-here"
   ```

2. **API Rate Limiting**: Configure in `librechat.yaml`

3. **Data Privacy**:
   - All Myndy data stays on local server
   - No external API calls unless configured
   - User data isolated by session

## Advanced Configuration

### Custom Tools

To add custom tools to MCP server:

1. Add tool to myndy-ai backend
2. MCP server auto-discovers via `/api/v1/tools/` endpoint
3. Restart MCP server
4. Tool available in LibreChat

### Custom Resources

To add custom resources:

1. Edit `myndy_crewai_mcp/resources_provider.py`
2. Add resource definition and handler
3. Restart MCP server
4. Resource available via `myndy://` URI

### Custom Prompts

To add custom prompts:

1. Edit `myndy_crewai_mcp/prompts_provider.py`
2. Add prompt definition and message builder
3. Restart MCP server
4. Prompt available in LibreChat

## Monitoring and Logs

### Log Locations

```bash
# MCP Server logs
tail -f /tmp/mcp_server.log

# Myndy-AI logs
tail -f ~/myndy-core/myndy-ai/logs/app.log

# LibreChat logs
tail -f ~/projects/LibreChat/logs/error.log
```

### Health Checks

```bash
# Automated health monitoring script
while true; do
  echo "=== Health Check $(date) ==="
  echo "MCP Server:"
  curl -s http://localhost:9092/health | jq
  echo "Myndy-AI:"
  curl -s http://localhost:8000/health | jq
  echo "LibreChat:"
  curl -s http://localhost:3080/api/health | jq
  sleep 60
done
```

### Metrics

```bash
# MCP Server metrics
curl http://localhost:9092/metrics

# Shows:
# - Tool execution count
# - Resource access count
# - Prompt invocation count
# - Average response time
# - Error rate
```

## Support and Resources

### Documentation

- **MCP Migration Plan**: `docs/MCP_MIGRATION_PLAN.md`
- **Phase Completion Docs**:
  - `MCP_PHASE3_COMPLETE.md` (Tools)
  - `MCP_PHASE4_COMPLETE.md` (Resources)
  - `MCP_PHASE5_COMPLETE.md` (Prompts)
- **README**: `myndy_crewai_mcp/README.md`

### Testing Scripts

- `test_tool_execution.py` - Test tool execution
- `test_resource_access.py` - Test resource access
- `test_prompts.py` - Test prompt generation
- `test_tool_registration.py` - Test tool discovery

### Getting Help

1. Check logs first
2. Review troubleshooting section
3. Run test scripts to isolate issues
4. Check MCP server health endpoint
5. Verify all services are running

## Next Steps

After successful integration:

1. **Explore Tools**: Try different tool combinations
2. **Test Agents**: Switch between agent personas
3. **Use Resources**: Access your personal data
4. **Try Prompts**: Use pre-configured workflows
5. **Customize**: Add your own tools, resources, prompts
6. **Monitor**: Set up health checks and logging
7. **Optimize**: Tune performance based on usage

## Conclusion

This integration guide provides everything needed to connect LibreChat with the Myndy CrewAI MCP Server. The setup enables access to 33 AI tools, 14 data resources, and 16 agent workflow prompts through a modern chat interface.

For issues or questions, refer to the troubleshooting section or review the phase completion documentation for detailed technical information.

---

**Last Updated**: October 7, 2025
**MCP Server Version**: 0.1.0
**LibreChat Compatibility**: 1.1.0+
