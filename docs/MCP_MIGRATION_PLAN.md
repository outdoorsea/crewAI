# MCP (Model Context Protocol) Migration Plan

## Executive Summary

Migration of CrewAI-Myndy integration from OpenWebUI Pipeline architecture to Model Context Protocol (MCP) for LibreChat integration.

**Goal**: Standardized, future-proof integration using MCP as the universal AI tool connection protocol.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Comparison](#architecture-comparison)
3. [Migration Phases](#migration-phases)
4. [Implementation Details](#implementation-details)
5. [Testing Strategy](#testing-strategy)
6. [Rollback Plan](#rollback-plan)

---

## Overview

### What is MCP?

Model Context Protocol (MCP) is an open protocol introduced by Anthropic that standardizes how LLMs interact with external tools, data sources, and services. It's the "USB-C of AI" - a universal connection standard.

### Why MCP?

**Current State (OpenWebUI Pipeline):**
- Custom FastAPI server with proprietary endpoints
- Pipeline-specific integration (port 9091)
- Limited to OpenWebUI platform
- Custom valve management and configuration

**Future State (MCP):**
- Standardized protocol following industry specification
- Works with LibreChat, Claude Desktop, VSCode, and any MCP-compatible client
- Leverages official Python SDK
- Universal tool/resource/prompt exposure
- Future-proof architecture

### Core MCP Primitives

1. **Tools** (Model-controlled): Executable functions the LLM can invoke
2. **Resources** (Application-controlled): Data and context (files, memory, schemas)
3. **Prompts** (User-controlled): Templated instructions and workflows

---

## Architecture Comparison

### Current Architecture (OpenWebUI Pipeline)

```
┌─────────────────────────────────────────────────┐
│              OpenWebUI Interface                │
└────────────────┬────────────────────────────────┘
                 │ HTTP (port 9091)
┌────────────────▼────────────────────────────────┐
│          CrewAI Pipeline Server (FastAPI)       │
│  • /chat/completions endpoints                  │
│  • /models endpoint                             │
│  • Custom valve management                      │
│  • Agent routing logic                          │
└────────────────┬────────────────────────────────┘
                 │ HTTP
┌────────────────▼────────────────────────────────┐
│         HTTP Tool Bridge (myndy_bridge.py)      │
│  • AsyncHTTPClient with connection pooling      │
│  • Tool caching and performance optimization    │
│  • 85+ tool HTTP clients                        │
└────────────────┬────────────────────────────────┘
                 │ HTTP (port 8000)
┌────────────────▼────────────────────────────────┐
│           Myndy-AI Backend (FastAPI)            │
│  • /api/v1/tools/execute                        │
│  • Memory management                            │
│  • Vector search (Qdrant)                       │
│  • 85+ tool implementations                     │
└─────────────────────────────────────────────────┘
```

### Proposed MCP Architecture

```
┌─────────────────────────────────────────────────┐
│              LibreChat Interface                │
└────────────────┬────────────────────────────────┘
                 │ MCP Protocol (JSON-RPC 2.0)
                 │ Transport: stdio / SSE / HTTP
┌────────────────▼────────────────────────────────┐
│          CrewAI MCP Server (Python SDK)         │
│                                                  │
│  📦 TOOLS (85+ tools)                           │
│     • Memory management tools                   │
│     • Calendar/time tools                       │
│     • Health analytics tools                    │
│     • Finance tracking tools                    │
│     • Research/document tools                   │
│     • ... (all myndy tools)                     │
│                                                  │
│  📁 RESOURCES (context data)                    │
│     • myndy://memory/entities                   │
│     • myndy://memory/conversations              │
│     • myndy://profile/user                      │
│     • myndy://documents/*                       │
│                                                  │
│  📋 PROMPTS (agent workflows)                   │
│     • Personal Assistant prompt                 │
│     • Memory Librarian prompt                   │
│     • Research Specialist prompt                │
│     • Health Analyst prompt                     │
│     • Finance Tracker prompt                    │
│                                                  │
└────────────────┬────────────────────────────────┘
                 │ HTTP (maintains existing pattern)
┌────────────────▼────────────────────────────────┐
│         HTTP Tool Bridge (myndy_bridge.py)      │
│  • AsyncHTTPClient (reused)                     │
│  • Tool caching (reused)                        │
│  • 85+ tool HTTP clients (reused)               │
└────────────────┬────────────────────────────────┘
                 │ HTTP (port 8000)
┌────────────────▼────────────────────────────────┐
│           Myndy-AI Backend (FastAPI)            │
│  • No changes required                          │
│  • Maintains existing APIs                      │
└─────────────────────────────────────────────────┘
```

**Key Insight**: The HTTP tool bridge and myndy-ai backend remain unchanged. We're only replacing the OpenWebUI Pipeline layer with an MCP server.

---

## Migration Phases

### Phase 1: Foundation Setup (Week 1)

**Tasks:**
1. Install MCP Python SDK: `pip install mcp`
2. Create MCP server project structure
3. Study MCP SDK documentation and examples
4. Design MCP server architecture

**Deliverables:**
- Development environment with MCP SDK
- Architecture design document
- Project structure

### Phase 2: Core MCP Server (Week 1-2)

**Tasks:**
1. Create base MCP server implementation
2. Implement JSON-RPC 2.0 message handling
3. Set up transport layers (stdio, SSE, HTTP)
4. Implement capability negotiation
5. Add logging and error handling

**Deliverables:**
- Functional MCP server skeleton
- Transport layer implementations
- Basic health checks

**Files to Create:**
```
myndy-crewai/
├── mcp/
│   ├── __init__.py
│   ├── server.py              # Main MCP server
│   ├── transport.py           # Transport layer (stdio/SSE/HTTP)
│   ├── tools_provider.py      # Tools implementation
│   ├── resources_provider.py  # Resources implementation
│   ├── prompts_provider.py    # Prompts implementation
│   └── config.py              # MCP server configuration
```

### Phase 3: Tools Migration (Week 2-3)

**Tasks:**
1. Wrap HTTP tool bridge with MCP tool interface
2. Map 85+ myndy tools to MCP tool schema
3. Implement tool execution handlers
4. Add tool parameter validation
5. Implement tool result formatting
6. Preserve async HTTP client and caching

**Key Design Decision**: **Keep the existing HTTP tool bridge** (`myndy_bridge.py`) and wrap it with MCP interface layer.

**Example Tool Mapping:**
```python
# MCP Tool Definition (new layer)
@mcp_server.tool()
async def get_current_time(timezone: str = "UTC") -> str:
    """Get the current time in a specific timezone"""
    # Delegate to existing HTTP tool bridge
    result = await tool_api_client.execute_tool_async(
        tool_name="time.get_current_time",
        parameters={"timezone": timezone}
    )
    return result

# Existing HTTP tool bridge remains unchanged
# myndy_bridge.py continues to handle HTTP communication
```

**Tool Categories to Migrate:**
- Memory management (15+ tools)
- Calendar/scheduling (10+ tools)
- Health analytics (12+ tools)
- Finance tracking (8+ tools)
- Research/documents (10+ tools)
- Communication (email, contacts) (15+ tools)
- Weather/location (8+ tools)
- System utilities (10+ tools)

### Phase 4: Resources Implementation (Week 3)

**Tasks:**
1. Define resource URI schema (`myndy://...`)
2. Implement memory resource providers
3. Implement profile resource providers
4. Implement document resource providers
5. Add resource caching and updates

**Resource URI Design:**
```
myndy://memory/entities         # All entities
myndy://memory/entities/{id}    # Specific entity
myndy://memory/conversations    # Conversation history
myndy://profile/user            # User profile
myndy://documents/{path}        # Document access
myndy://health/metrics          # Health data
myndy://finance/transactions    # Financial data
```

**Example Resource Implementation:**
```python
@mcp_server.resource("myndy://memory/entities")
async def get_entities_resource():
    """Provide all memory entities as context"""
    result = await tool_api_client.execute_tool_async(
        tool_name="memory.list_entities",
        parameters={}
    )
    return {
        "uri": "myndy://memory/entities",
        "name": "Memory Entities",
        "description": "All entities stored in myndy memory",
        "mimeType": "application/json",
        "text": json.dumps(result, indent=2)
    }
```

### Phase 5: Prompts Implementation (Week 3-4)

**Tasks:**
1. Extract agent-specific prompts from existing agents
2. Create prompt templates with variables
3. Implement prompt resolution
4. Add prompt metadata and descriptions

**Prompts to Create:**
- Personal Assistant workflow
- Memory Librarian workflow
- Research Specialist workflow
- Health Analyst workflow
- Finance Tracker workflow
- Shadow Agent analysis workflow

**Example Prompt:**
```python
@mcp_server.prompt()
async def personal_assistant_prompt(task: str = ""):
    """Personal assistant for calendar, email, and time management"""
    return {
        "name": "personal_assistant",
        "description": "Intelligent personal assistant with calendar and communication tools",
        "arguments": [
            {
                "name": "task",
                "description": "The task to help with",
                "required": False
            }
        ],
        "messages": [
            {
                "role": "system",
                "content": f"""You are an expert personal assistant specializing in:
- Calendar and schedule management
- Email processing and drafting
- Contact management
- Time zone conversions
- Weather and location information

Task: {task if task else "Help the user with their request"}

Use the available tools to assist efficiently."""
            }
        ]
    }
```

### Phase 6: LibreChat Integration (Week 4)

**Tasks:**
1. Create `librechat.yaml` configuration
2. Configure MCP server connection
3. Test MCP server with LibreChat
4. Configure agent-specific settings
5. Test tool execution flow
6. Test resource access
7. Test prompt workflows

**LibreChat Configuration:**
```yaml
# librechat.yaml
mcpServers:
  myndy_crewai:
    command: python
    args:
      - "/Users/jeremy/myndy-core/myndy-crewai/mcp/server.py"
    env:
      MYNDY_API_URL: "http://localhost:8000"
      CREWAI_VERBOSE: "true"
    serverInstructions: true
    description: "CrewAI personal AI assistant with memory and 85+ specialized tools"

endpoints:
  custom:
    - name: "Myndy CrewAI"
      apiKey: "user_provided"
      baseURL: "http://localhost:8000"
      models:
        default:
          - "personal_assistant"
          - "memory_librarian"
          - "research_specialist"
          - "health_analyst"
          - "finance_tracker"
      mcpServers:
        - myndy_crewai
```

### Phase 7: Testing & Validation (Week 4-5)

**Tasks:**
1. Unit tests for MCP server components
2. Integration tests with LibreChat
3. Tool execution tests
4. Resource access tests
5. Prompt workflow tests
6. Performance testing
7. Error handling validation
8. Security testing

**Test Coverage:**
- All 85+ tools execute correctly via MCP
- Resources provide accurate context
- Prompts render with proper variables
- Error messages are clear and helpful
- Performance meets or exceeds current system
- Security: proper authentication and authorization

### Phase 8: Documentation & Deployment (Week 5)

**Tasks:**
1. Update architecture documentation
2. Create MCP integration guide
3. Document tool usage patterns
4. Create troubleshooting guide
5. Update CLAUDE.md with MCP guidelines
6. Create deployment instructions
7. Document rollback procedures

**Documentation Files:**
- `docs/MCP_ARCHITECTURE.md`
- `docs/MCP_TOOL_REFERENCE.md`
- `docs/MCP_LIBRECHAT_SETUP.md`
- `docs/MCP_TROUBLESHOOTING.md`

---

## Implementation Details

### Technology Stack

**MCP Components:**
- `mcp` - Official Python SDK
- `pydantic` - Data validation
- `asyncio` - Async operations

**Preserved Components:**
- `myndy_bridge.py` - HTTP tool bridge (no changes)
- `async_http_client.py` - HTTP client (no changes)
- `tool_cache.py` - Caching system (no changes)
- All existing agent definitions (minimal changes)

### Key Design Principles

1. **Minimize Changes**: Reuse existing HTTP tool bridge and caching
2. **Maintain Service Boundaries**: MCP server calls myndy-ai HTTP APIs
3. **Standard Compliance**: Follow MCP specification exactly
4. **Performance**: Preserve async operations and caching
5. **Security**: Maintain authentication and authorization
6. **Testability**: Comprehensive test coverage
7. **Documentation**: Clear, thorough documentation

### Code Structure

```
myndy-crewai/
├── mcp/                          # New MCP server
│   ├── __init__.py
│   ├── server.py                 # Main MCP server
│   ├── transport.py              # Transport layers
│   ├── tools_provider.py         # Tools → MCP tools
│   ├── resources_provider.py     # Memory → MCP resources
│   ├── prompts_provider.py       # Agents → MCP prompts
│   ├── config.py                 # MCP configuration
│   └── schemas.py                # MCP data schemas
│
├── tools/                        # Existing (minimal changes)
│   ├── myndy_bridge.py           # HTTP tool bridge (preserved)
│   ├── async_http_client.py     # HTTP client (preserved)
│   └── tool_cache.py             # Caching (preserved)
│
├── agents/                       # Existing (extract prompts)
│   ├── personal_assistant.py
│   ├── memory_librarian.py
│   ├── research_specialist.py
│   ├── health_analyst.py
│   └── finance_tracker.py
│
├── pipeline/                     # Deprecated (keep for reference)
│   └── server.py                 # OpenWebUI pipeline (old)
│
├── tests/
│   ├── mcp/                      # New MCP tests
│   │   ├── test_server.py
│   │   ├── test_tools.py
│   │   ├── test_resources.py
│   │   └── test_prompts.py
│   └── integration/
│       └── test_librechat_integration.py
│
├── docs/
│   ├── MCP_MIGRATION_PLAN.md    # This document
│   ├── MCP_ARCHITECTURE.md      # MCP system architecture
│   ├── MCP_TOOL_REFERENCE.md    # Tool documentation
│   └── MCP_LIBRECHAT_SETUP.md   # Setup guide
│
└── librechat.yaml                # LibreChat configuration
```

---

## Testing Strategy

### Unit Tests

**MCP Server Core:**
- Transport layer initialization
- Message routing
- Capability negotiation
- Error handling

**Tools Provider:**
- Tool registration
- Parameter validation
- Execution handling
- Result formatting

**Resources Provider:**
- Resource URI resolution
- Context retrieval
- Resource updates
- Caching

**Prompts Provider:**
- Prompt registration
- Variable substitution
- Metadata generation

### Integration Tests

**LibreChat Integration:**
- MCP server connection
- Tool invocation from chat
- Resource access from chat
- Prompt execution
- Multi-turn conversations
- Error recovery

**Myndy-AI Backend Integration:**
- Tool execution via HTTP
- Response formatting
- Timeout handling
- Authentication

### Performance Tests

**Benchmarks:**
- Tool execution latency (target: <500ms)
- Resource retrieval time (target: <200ms)
- Concurrent request handling (target: 50+ concurrent)
- Memory usage (target: <500MB baseline)

**Comparison:**
- Compare with OpenWebUI Pipeline performance
- Ensure no regression in speed
- Validate caching effectiveness

### Security Tests

**Authentication:**
- API key validation
- User authorization
- Resource access control

**Input Validation:**
- Parameter sanitization
- SQL injection prevention
- Command injection prevention

**Data Privacy:**
- Memory data access restrictions
- Profile information protection
- Document access control

---

## Rollback Plan

### Rollback Triggers

1. Critical bugs in MCP implementation
2. Performance degradation >50%
3. Security vulnerabilities discovered
4. LibreChat compatibility issues
5. Data integrity problems

### Rollback Procedure

**Step 1**: Switch LibreChat back to OpenWebUI Pipeline
```yaml
# librechat.yaml
endpoints:
  custom:
    - name: "CrewAI-Myndy"
      baseURL: "http://localhost:9091/v1"
```

**Step 2**: Restart OpenWebUI Pipeline server
```bash
cd /Users/jeremy/myndy-core/myndy-crewai/pipeline
python server.py
```

**Step 3**: Validate functionality
- Test tool execution
- Verify agent routing
- Check memory operations

**Step 4**: Document issues for future resolution

### Gradual Migration Option

**Hybrid Approach:**
- Run both MCP server and OpenWebUI Pipeline simultaneously
- Use different ports (MCP: 9092, Pipeline: 9091)
- Test MCP thoroughly before full cutover
- Keep Pipeline as fallback during testing phase

---

## Success Criteria

### Functional Requirements

✅ All 85+ tools execute correctly via MCP
✅ Resources provide accurate context data
✅ Prompts render with proper variable substitution
✅ LibreChat integration works seamlessly
✅ Multi-turn conversations maintain context
✅ Error messages are clear and actionable

### Performance Requirements

✅ Tool execution latency <500ms (95th percentile)
✅ Resource retrieval <200ms (95th percentile)
✅ Support 50+ concurrent requests
✅ Memory usage <500MB baseline
✅ No performance regression vs. Pipeline

### Quality Requirements

✅ 90%+ test coverage
✅ Zero critical security vulnerabilities
✅ Comprehensive documentation
✅ Clear migration guide
✅ Rollback procedure validated

---

## Timeline

**Week 1**: Foundation Setup + Core MCP Server
**Week 2**: Tools Migration (Phase 3)
**Week 3**: Resources + Prompts (Phase 4-5)
**Week 4**: LibreChat Integration + Testing (Phase 6-7)
**Week 5**: Documentation + Deployment (Phase 8)

**Total Estimated Time**: 5 weeks

---

## Dependencies

### External Dependencies

- `mcp` - MCP Python SDK
- `pydantic>=2.0` - Data validation
- `asyncio` - Async operations
- LibreChat installation

### Internal Dependencies

- Myndy-AI backend must remain running (port 8000)
- Existing HTTP tool bridge preserved
- Agent definitions preserved

### Team Dependencies

- LibreChat setup and configuration
- Testing and validation support
- Documentation review

---

## Risks & Mitigation

### Technical Risks

**Risk**: MCP SDK compatibility issues
**Mitigation**: Test thoroughly in dev environment first

**Risk**: Performance degradation
**Mitigation**: Preserve existing async/caching, benchmark continuously

**Risk**: Tool execution failures
**Mitigation**: Comprehensive error handling and fallbacks

**Risk**: LibreChat integration issues
**Mitigation**: Follow official MCP integration guide, test incrementally

### Process Risks

**Risk**: Timeline delays
**Mitigation**: Phased approach allows partial deployment

**Risk**: Incomplete testing
**Mitigation**: Automated test suite with CI/CD

**Risk**: Documentation gaps
**Mitigation**: Document as you build, review checklist

---

## Next Steps

1. ✅ Create this migration plan document
2. 🚀 Install MCP Python SDK and dependencies
3. 🚀 Create MCP server project structure
4. 🚀 Implement core MCP server skeleton
5. 🚀 Begin tools migration (Phase 3)

---

## Questions & Decisions

### Open Questions

1. **Transport Layer**: Which transport to use initially? (Recommendation: stdio for simplicity)
2. **Authentication**: How to handle API keys in LibreChat? (Recommendation: user_provided)
3. **Deployment**: Docker container or direct Python? (Recommendation: Direct Python initially)
4. **Monitoring**: What metrics to track? (Recommendation: Tool latency, error rates, cache hits)

### Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-07 | Choose MCP over Custom Endpoint | Future-proof, standardized approach |
| 2025-10-07 | Preserve HTTP tool bridge | Minimize changes, maintain architecture |
| 2025-10-07 | Phased migration approach | Reduce risk, enable rollback |

---

## Conclusion

This migration plan provides a comprehensive roadmap for transitioning CrewAI-Myndy from OpenWebUI Pipeline to Model Context Protocol. The phased approach minimizes risk while maximizing the benefits of a standardized integration protocol.

**Key Benefits:**
- ✅ Future-proof architecture using industry standard
- ✅ Works with multiple clients (LibreChat, Claude Desktop, VSCode)
- ✅ Minimal changes to existing codebase
- ✅ Preserves performance optimizations
- ✅ Clear rollback plan

**Next Action**: Begin Phase 1 - Foundation Setup
