# CrewAI-Myndy Integration

A comprehensive integration between CrewAI and the Myndy ecosystem, enabling powerful multi-agent workflows with access to 530+ specialized tools and sophisticated memory management.

## Overview

This project bridges the gap between CrewAI's multi-agent orchestration capabilities and Myndy's extensive personal productivity ecosystem. The integration provides:

- **5 Specialized Agents** with distinct roles and capabilities
- **530+ Production-Ready Tools** from the Myndy ecosystem
- **Sophisticated Memory System** for persistent context and knowledge
- **Ollama LLM Integration** for local, private AI inference
- **Comprehensive Tool Bridge** for seamless interoperability

## Architecture

### Agents

| Agent | Role | Primary Tools | LLM Model |
|-------|------|---------------|-----------|
| **Memory Librarian** | Entity organization, knowledge retrieval | Memory, conversation, profile tools | Llama3 |
| **Research Specialist** | Information gathering, fact verification | Search, document processing, analysis tools | Mixtral |
| **Personal Assistant** | Calendar, email, task management | Calendar, email, contact, project tools | Gemma |
| **Health Analyst** | Health data analysis, wellness insights | Health, fitness, activity tracking tools | Phi |
| **Finance Tracker** | Financial analysis, expense tracking | Finance, transaction, budget tools | Mistral |
| **🔮 Shadow Agent** | Behavioral intelligence, silent observation | Behavioral analysis, pattern recognition tools | Llama3.2 |

### Tool Categories

- **🔮 Behavioral Intelligence**: 4+ tools for behavioral analysis, pattern recognition, personality modeling
- **Memory & Knowledge**: 80+ tools for entity management, conversation history, knowledge graphs
- **Research & Analysis**: 150+ tools for web search, document processing, fact verification
- **Personal Productivity**: 100+ tools for calendar, email, contacts, project management
- **Health & Wellness**: 60+ tools for health data integration (iOS HealthKit, Oura, Peloton)
- **Financial Management**: 50+ tools for expense tracking, budget analysis, financial planning

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the crewAI directory
cd /Users/jeremy/crewAI

# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running with required models
ollama pull llama3
ollama pull mixtral
ollama pull gemma
ollama pull phi
ollama pull mistral
```

### 2. Basic Usage

```python
from crews import create_personal_productivity_crew

# Create the crew
crew_manager = create_personal_productivity_crew(verbose=True)

# Create a comprehensive life analysis task
task = crew_manager.create_life_analysis_task("last 30 days")

# Execute the task
result = crew_manager.execute_task(task)
print(result)
```

### 3. Individual Agent Usage

```python
from agents import create_memory_librarian, create_research_specialist

# Create specific agents
librarian = create_memory_librarian()
researcher = create_research_specialist()

# Use agent tools
tools = librarian.tools
print(f"Memory Librarian has {len(tools)} tools available")
```

## Key Features

### 🧠 Memory Integration

- **Persistent Context**: All agent interactions stored in Myndy memory system
- **Cross-Agent Memory Sharing**: Agents can access each other's findings
- **Entity Relationship Mapping**: Comprehensive knowledge graph maintenance
- **Conversation History**: Full context preservation across sessions

### 🔧 Tool Bridge

- **530+ Tools Available**: Direct access to entire Myndy tool ecosystem
- **Automatic Schema Conversion**: Seamless OpenAI function calling compatibility
- **Category-Based Assignment**: Tools intelligently assigned by agent role
- **Dynamic Loading**: Tools loaded on-demand for optimal performance

### 🤖 Agent Collaboration

- **Sequential Workflows**: Coordinated multi-step task execution
- **Parallel Processing**: Independent analysis by multiple agents
- **Delegation Support**: Agents can request specialized analysis from others
- **Consensus Building**: Collaborative decision-making on complex issues

### 🔒 Privacy & Security

- **Local LLM Inference**: All AI processing via Ollama (no external API calls)
- **Sensitive Data Isolation**: Finance and health agents operate with restricted delegation
- **User Data Separation**: Complete isolation between different users
- **Audit Trails**: Full logging of all agent interactions and tool usage

## Example Workflows

### Comprehensive Life Analysis

```python
# Analyze all aspects of personal life
task = crew_manager.create_life_analysis_task("last quarter")

# Results include:
# - Health metrics and trends (Health Analyst)
# - Financial health review (Finance Tracker)  
# - Productivity analysis (Personal Assistant)
# - Key relationships and events (Memory Librarian)
# - External context validation (Research Specialist)
```

### Research Project

```python
# Deep research with personal context
task = crew_manager.create_research_project_task(
    topic="Investment strategies for tech professionals",
    depth="comprehensive"
)

# Results include:
# - Market research and analysis (Research Specialist)
# - Personal financial context (Finance Tracker)
# - Relevant past experiences (Memory Librarian)
# - Implementation timeline (Personal Assistant)
```

### Health Optimization

```python
# Data-driven health improvement
task = crew_manager.create_health_optimization_task("cardiovascular fitness")

# Results include:
# - Current health data analysis (Health Analyst)
# - Budget for health investments (Finance Tracker)
# - Schedule optimization for workouts (Personal Assistant)
# - Past successful health initiatives (Memory Librarian)
```

## Project Structure

```
crewAI/
├── agents/                 # Specialized agent definitions
├── tools/                  # Tool bridge and adapters
├── crews/                  # Crew configurations
├── config/                 # LLM and system configuration
├── memory/                 # Memory system integration
├── tests/                  # Comprehensive test suite
├── examples/               # Usage examples
├── requirements.txt        # Dependencies
├── TODO.md                # Implementation roadmap
├── tool_analysis.md       # Tool compatibility analysis
└── agent_architecture.md  # Agent design documentation
```

## Configuration

### Environment Variables

```bash
# Ollama configuration
export OLLAMA_BASE_URL="http://localhost:11434"
export MEMEX_DEFAULT_MODEL="llama3"

# Optional: OpenAI fallback
export OPENAI_API_KEY="your_key_here"
```

## 🔮 Shadow Agent - Behavioral Intelligence

The Shadow Agent MVP provides behavioral intelligence capabilities that work silently in the background:

### Key Features
- **Silent Observation**: Analyzes all conversations without user interference
- **Pattern Recognition**: Identifies communication styles, preferences, and behavioral patterns
- **Memory Integration**: Stores insights via myndy-ai memory APIs
- **Personality Modeling**: Generates behavioral summaries and insights over time
- **OpenWebUI Integration**: Automatically observes all pipeline conversations

### Usage

```python
from agents.mvp_shadow_agent import create_mvp_shadow_agent

# Create Shadow Agent
shadow_agent = create_mvp_shadow_agent()

# Observe a conversation (automatic in pipeline)
observation = shadow_agent.observe_conversation(
    user_message="What's the weather like today?",
    agent_response="It's sunny and 72°F in your area.",
    agent_type="personal_assistant",
    session_id="session_123"
)

# Get behavioral insights
insights = shadow_agent.get_behavioral_insights()
summary = shadow_agent.generate_personality_summary()
```

### Behavioral Analysis
- **Communication Styles**: concise, detailed, polite, urgent, casual
- **Message Types**: question, request, appreciation, scheduling, general
- **Topic Interests**: health, finance, work, calendar, personal, technology, weather
- **Emotional Indicators**: happy, frustrated, confused, excited, worried, neutral

See `SHADOW_AGENT_MVP_GUIDE.md` for complete documentation.

## Complex Multi-Agent Workflows

**NEW**: The CrewAI integration supports sophisticated multi-agent workflows for complex processes!

### Quick Start with Complex Workflows

```bash
# Run demonstrations of different workflow patterns
cd /Users/jeremy/myndy-core/myndy-crewai

# Sequential workflow (agents build on each other)
python examples/complex_workflow_demo.py 1

# Parallel workflow (agents work simultaneously)
python examples/complex_workflow_demo.py 2

# Collaborative workflow (agents delegate tasks)
python examples/complex_workflow_demo.py 3

# Adaptive workflow (routes change based on results)
python examples/complex_workflow_demo.py 4

# Complex goal planning (multi-phase with validation)
python examples/complex_workflow_demo.py 5

# Run all demonstrations
python examples/complex_workflow_demo.py all
```

### Workflow Patterns Supported

1. **Sequential** - Agents build on previous results (planning, analysis)
2. **Parallel** - Multiple agents work simultaneously (comprehensive analysis)
3. **Collaborative** - Agents delegate subtasks (complex research)
4. **Adaptive** - Workflow changes based on results (smart routing)
5. **Multi-Stage Pipelines** - Validation checkpoints (quality control)
6. **Continuous Monitoring** - Ongoing oversight (alerts on issues)

### Example: Health Improvement Plan

```python
from crews import create_personal_productivity_crew

crew = create_personal_productivity_crew()

# Sequential workflow: Health → Research → Finance → Schedule
task = crew.create_health_optimization_task("cardiovascular fitness")
result = crew.execute_task(task)

# Result includes contributions from all relevant agents
# working together to create a comprehensive plan
```

### Real-World Applications

- **Major Decisions**: Job changes, home purchases, relocations
- **Goal Planning**: Marathon training, career development, health goals
- **Life Reviews**: Weekly/monthly comprehensive analysis
- **Optimization**: Sleep quality, productivity, financial health
- **Monitoring**: Continuous health, finance, productivity oversight

See **COMPLEX_AGENT_WORKFLOWS_GUIDE.md** for complete documentation!

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_tool_bridge.py -v
pytest tests/test_agents.py -v
pytest tests/test_memory_integration.py -v

# Test Shadow Agent integration
python test_shadow_agent_integration.py

# Test complex workflows
python examples/complex_workflow_demo.py all
```

## MCP Server Integration

**NEW**: Model Context Protocol (MCP) server implementation complete! The MCP server exposes myndy-ai capabilities to LibreChat and other MCP-compatible clients.

### MCP Server Features

- **33 Tools**: Dynamic discovery and execution via HTTP bridge
- **14 Resources**: Access to memory, profile, health, finance, and documents via `myndy://` URIs
- **16 Prompts**: Pre-configured agent workflows across 5 specialized personas
- **SSE Streaming**: Real-time communication with MCP clients
- **Zero Backend Changes**: Preserves existing myndy-ai architecture

### Quick Start - MCP Server

```bash
# Start the MCP server
cd /Users/jeremy/myndy-core/myndy-crewai
python3 start_mcp_server.py

# Server runs on http://localhost:9092
# Health check: curl http://localhost:9092/health
```

### MCP Documentation

- **Quick Start**: See `myndy_crewai_mcp/README.md`
- **LibreChat Integration**: See `LIBRECHAT_INTEGRATION_GUIDE.md`
- **Testing Guide**: See `TEST_SUITE_GUIDE.md`
- **Complete Migration Summary**: See `MCP_MIGRATION_COMPLETE.md`
- **Phase Documentation**: See `MCP_PHASE3_COMPLETE.md`, `MCP_PHASE4_COMPLETE.md`, `MCP_PHASE5_COMPLETE.md`

### MCP vs CrewAI Integration

| Feature | MCP Server | CrewAI Integration |
|---------|-----------|-------------------|
| **Purpose** | Standard protocol for LLM tool access | Multi-agent orchestration |
| **Client** | LibreChat, Claude Desktop, any MCP client | OpenWebUI, direct Python usage |
| **Tools** | 33 core tools via HTTP | 530+ tools via bridge |
| **Interface** | JSON-RPC 2.0 over SSE | Python API |
| **Agents** | 5 prompt templates | 5 full agents with LLMs |
| **Use Case** | Chat interface integration | Complex multi-agent workflows |

Both integrations work with the same myndy-ai backend and can be used simultaneously.

## Status

✅ **Completed**:
- Core architecture, tool bridge, agent definitions, memory integration
- **MCP Server (Phases 1-5)**: Tools, resources, prompts fully implemented and tested
- Shadow Agent MVP with behavioral intelligence
- Comprehensive testing framework and documentation

🔄 **In Progress**:
- MCP Phase 6: LibreChat integration testing
- Additional test coverage implementation

📋 **Next**:
- MCP Phase 7-8: Performance optimization, production deployment
- Full integration testing with LibreChat
- Example implementations and user guides

---

**Note**: This integration requires a properly configured Myndy environment and Ollama installation. For MCP server, see `MCP_MIGRATION_COMPLETE.md` for complete implementation details. See `TODO.md` for development roadmap.