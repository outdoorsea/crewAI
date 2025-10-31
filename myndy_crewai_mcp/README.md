# Myndy CrewAI MCP Server

Model Context Protocol (MCP) server that exposes CrewAI agents and myndy-ai tools to LibreChat and other MCP-compatible clients.

## Overview

This MCP server provides:
- **85+ Tools**: Memory management, calendar, health, finance, research, communication
- **Resources**: Access to memory entities, profiles, documents via `myndy://` URIs
- **Prompts**: Pre-configured agent workflows for common tasks
- **Agents**: 5 specialized AI agents with intelligent routing

## Architecture

```
LibreChat → MCP Server (SSE) → HTTP Tool Bridge → Myndy-AI Backend
```

### Key Features

- **SSE Streaming**: Real-time communication with LibreChat
- **HTTP Tool Bridge**: Preserves existing async/caching infrastructure
- **Zero Changes to Backend**: Myndy-AI remains unchanged
- **Standard Protocol**: Works with any MCP-compatible client

## Quick Start

### Prerequisites

1. **Myndy-AI Backend** running on `http://localhost:8000`
2. **Python 3.10+** with required dependencies
3. **LibreChat** installed (optional, for web interface)

### Installation

```bash
# Navigate to project
cd /Users/jeremy/myndy-core/myndy-crewai

# Install dependencies (if not already installed)
pip install mcp pydantic starlette uvicorn httpx httpx-sse

# Verify installation
python3 -c "from myndy_crewai_mcp.server import MyndyMCPServer; print('✅ Ready')"
```

### Start the Server

```bash
# Start MCP server
python3 start_mcp_server.py

# Server will start on http://localhost:9092
```

### Verify Server

```bash
# Health check
curl http://localhost:9092/health

# Expected response:
# {"status":"healthy","server":"myndy-crewai-mcp"}
```

## Configuration

### Environment Variables

```bash
# Myndy-AI Backend URL
export MYNDY_API_URL="http://localhost:8000"

# MCP Server Settings
export MCP_SERVER_PORT=9092
export MCP_LOG_LEVEL="INFO"
export MCP_DEBUG="false"
export MCP_VERBOSE="false"

# Feature Toggles
export MCP_ENABLE_TOOLS="true"
export MCP_ENABLE_RESOURCES="true"
export MCP_ENABLE_PROMPTS="true"
```

### Configuration File

Edit `myndy_crewai_mcp/config.py` for advanced configuration:

- Transport type (SSE, HTTP, stdio)
- Port and host settings
- Timeout values
- Cache settings
- Security options

## LibreChat Integration

### Setup

1. Copy `librechat.yaml` to your LibreChat installation:
   ```bash
   cp librechat.yaml /path/to/librechat/librechat.yaml
   ```

2. Update the MCP server path in `librechat.yaml`:
   ```yaml
   mcpServers:
     myndy_crewai:
       command: python3
       args:
         - "/path/to/myndy-core/myndy-crewai/start_mcp_server.py"
   ```

3. Restart LibreChat

### Usage in LibreChat

1. Select "Myndy CrewAI" as your model/endpoint
2. Available tools will appear in the tools panel
3. Tools are automatically invoked based on conversation context
4. Resources can be referenced using `myndy://` URIs

## Available Tools

### Current Tools (33 tools from myndy-ai backend)

**Dynamically discovered from backend** - The MCP server automatically discovers and registers all available tools from the myndy-ai backend.

**Tool Categories**:
- **Memory Management** (14 tools): Entity management, conversation analysis, status tracking
- **Time & Date** (4 tools): Current time, date formatting, time calculations, unix timestamps
- **Profile Management** (4 tools): Self-profile, goals, preferences management
- **System Operations** (3 tools): Backup and restore operations
- **Location Services** (2 tools): Location tracking and history
- **Management** (2 tools): Tool approval and management interfaces
- **Journal** (1 tool): Journal management
- **Knowledge** (1 tool): Wikipedia search
- **Projects** (1 tool): Project management
- **Search** (1 tool): Query search

### Full Tool Suite Expansion (when more backend tools are available)

**Memory Management (15+ tools)**
- Entity management
- Conversation analysis
- Memory search
- Knowledge organization

**Calendar & Time (10+ tools)**
- Event management
- Time zone conversion
- Schedule analysis

**Health Analytics (12+ tools)**
- Activity tracking
- Health metrics
- Wellness insights

**Finance Tracking (8+ tools)**
- Expense tracking
- Budget analysis
- Financial insights

**Research & Documents (10+ tools)**
- Document analysis
- Information gathering
- Text processing

**Communication (15+ tools)**
- Email management
- Contact management
- Message processing

**Weather & Location (8+ tools)**
- Weather forecasts
- Location tracking
- Geographic queries

**System Utilities (10+ tools)**
- File operations
- Data processing
- General utilities

## Resources

Resources provide context data via `myndy://` URIs. The MCP server exposes 14 static resources and 5 resource templates for parameterized access.

### Available Resources (14 static)

**Memory Resources** (6):
```
myndy://memory/entities         # All memory entities
myndy://memory/conversations    # Conversation history
myndy://memory/short-term       # Short-term memory entries
myndy://memory/people           # All people in memory
myndy://memory/places           # All places in memory
myndy://memory/events           # All events in memory
```

**Profile Resources** (3):
```
myndy://profile/self            # Self profile with preferences
myndy://profile/goals           # Current goals and objectives
myndy://profile/preferences     # User preferences
```

**Health Resources** (2):
```
myndy://health/metrics          # Health metrics and data
myndy://health/status           # Health status entries
```

**Finance Resources** (2):
```
myndy://finance/transactions    # Financial transactions
myndy://finance/budget          # Budget summary
```

**Document Resources** (1):
```
myndy://documents/list          # Document listing
```

### Resource Templates (5 parameterized)

```
myndy://memory/entities/{entity_id}             # Specific entity by ID
myndy://memory/conversations/{conversation_id}  # Specific conversation
myndy://memory/people/{person_id}               # Specific person by ID
myndy://memory/places/{place_id}                # Specific place by ID
myndy://documents/{path}                        # Specific document by path
```

### Resource Usage

Resources are accessed via the MCP protocol's `read_resource` method. LibreChat and other MCP clients can request resource data by URI, and the server will fetch the latest data from the myndy-ai backend.

## Prompts

Pre-configured agent workflow templates for common tasks. The MCP server provides 16 prompts across 5 specialized agent personas.

### Available Prompts (16 total)

**Personal Assistant** (3 prompts):
- `personal_assistant` - General personal assistant tasks
- `schedule_management` - Manage calendar events
- `time_query` - Query time in different timezones

**Memory Librarian** (4 prompts):
- `memory_librarian` - General memory operations
- `memory_search` - Search through memory entities
- `entity_management` - Manage entities (people, places, events)
- `conversation_analysis` - Extract entities from conversations

**Research Specialist** (3 prompts):
- `research_specialist` - General research tasks
- `information_gathering` - Targeted research on topics
- `document_analysis` - Analyze and extract from documents

**Health Analyst** (3 prompts):
- `health_analyst` - General health analysis
- `health_metrics` - Analyze specific health metrics
- `wellness_insights` - Generate wellness recommendations

**Finance Tracker** (3 prompts):
- `finance_tracker` - General finance tracking
- `expense_tracking` - Track and analyze expenses
- `budget_analysis` - Analyze budget and spending patterns

### Prompt Usage

Prompts are accessed via the MCP protocol's `get_prompt` method. Each prompt accepts optional arguments to customize the workflow:

```javascript
// Example: Get personal assistant prompt
const result = await mcpClient.getPrompt("personal_assistant", {
  task: "Check my schedule for today"
});

// Result contains system and user messages for LLM initialization
// result.messages = [
//   {role: "system", content: "You are a Personal Assistant AI..."},
//   {role: "user", content: "Check my schedule for today"}
// ]
```

Prompts provide pre-configured agent personas with appropriate tools and capabilities, reducing setup time for common workflows.

## Development

### Project Structure

```
myndy_crewai_mcp/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── schemas.py               # MCP data schemas
├── server.py                # Core MCP server
├── main.py                  # Server entry point
├── tools_provider.py        # Tools integration
├── resources_provider.py    # Resources (TODO)
├── prompts_provider.py      # Prompts (TODO)
└── README.md               # This file
```

### Testing

```bash
# Test server import
python3 -c "from myndy_crewai_mcp.server import MyndyMCPServer; print('✅ OK')"

# Test tools provider
python3 -c "
import asyncio
from myndy_crewai_mcp.config import get_config
from myndy_crewai_mcp.tools_provider import ToolsProvider

async def test():
    config = get_config()
    provider = ToolsProvider(config)
    await provider.initialize()
    print(f'✅ {provider.get_tool_count()} tools registered')

asyncio.run(test())
"

# Test full server startup
python3 start_mcp_server.py
```

### Logs

Logs are written to:
- Console (INFO level by default)
- Optional log file (configure in `config.py`)

Enable debug logging:
```bash
export MCP_DEBUG="true"
export MCP_LOG_LEVEL="DEBUG"
```

## Troubleshooting

### Server won't start

1. Check Myndy-AI backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check port availability:
   ```bash
   lsof -i :9092
   ```

3. Check logs for errors:
   ```bash
   python3 start_mcp_server.py 2>&1 | tee mcp_server.log
   ```

### Tools not appearing in LibreChat

1. Verify server is running:
   ```bash
   curl http://localhost:9092/health
   ```

2. Check LibreChat MCP configuration in `librechat.yaml`

3. Restart LibreChat after configuration changes

### Tool execution fails

1. Check Myndy-AI backend connectivity
2. Verify tool parameters match schema
3. Check MCP server logs for errors

## Documentation

- **Migration Plan**: `../docs/MCP_MIGRATION_PLAN.md`
- **Architecture**: See migration plan for complete architecture
- **TODO**: `../TODO.md` for current development status
- **Setup Complete**: `../MCP_SETUP_COMPLETE.md` for implementation summary

## Status

**Phase 1-5 Complete ✅:**
- ✅ MCP SDK installed
- ✅ Configuration system
- ✅ Data schemas
- ✅ SSE streaming server
- ✅ Tools provider with HTTP bridge
- ✅ LibreChat configuration
- ✅ Basic testing complete
- ✅ Dynamic tool discovery from backend
- ✅ 33 tools registered and tested
- ✅ Tool execution working via HTTP bridge
- ✅ Resources provider implementation
- ✅ myndy:// URI scheme for resources
- ✅ 14 resources registered (memory, profile, health, finance, documents)
- ✅ 5 resource templates defined
- ✅ Resource access tested and working
- ✅ Prompts provider implementation
- ✅ 16 prompts across 5 agent categories
- ✅ Dynamic message building system
- ✅ Prompt templates tested and working
- ✅ All MCP primitives implemented (tools, resources, prompts)
- ✅ Comprehensive test scripts created
- ✅ Documentation complete

**Phase 6-8 TODO:**
- LibreChat integration testing
- Complete testing suite
- Performance optimization
- Production deployment guide

## Support

For issues or questions:
1. Check `../docs/MCP_MIGRATION_PLAN.md` for architecture details
2. Review `../TODO.md` for current development status
3. Check server logs for error messages
4. See `../MCP_SETUP_COMPLETE.md` for setup summary

## License

MIT License - Part of Myndy Core project
