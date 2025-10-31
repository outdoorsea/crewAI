# MCP Migration Documentation Index

## Overview

This document serves as the central navigation hub for all documentation related to the Model Context Protocol (MCP) server implementation in the Myndy-CrewAI project.

**Migration Status**: ✅ **Phases 1-5 Complete** (62.5% of planned work)

## Quick Links

### Essential Documents
- **[MCP Migration Complete Summary](MCP_MIGRATION_COMPLETE.md)** - Executive summary of the entire migration project
- **[LibreChat Integration Guide](LIBRECHAT_INTEGRATION_GUIDE.md)** - Complete guide for integrating with LibreChat
- **[Test Suite Guide](TEST_SUITE_GUIDE.md)** - Comprehensive testing documentation
- **[MCP Server README](myndy_crewai_mcp/README.md)** - Quick start and API reference

### Phase Documentation
- **[Phase 1-2: Setup & Architecture](MCP_SETUP_COMPLETE.md)** - Initial setup and configuration
- **[Phase 3: Tools Implementation](MCP_PHASE3_COMPLETE.md)** - Dynamic tool discovery and HTTP bridge
- **[Phase 4: Resources Implementation](MCP_PHASE4_COMPLETE.md)** - Resources and myndy:// URI scheme
- **[Phase 5: Prompts Implementation](MCP_PHASE5_COMPLETE.md)** - Agent workflow templates

### Technical Documentation
- **[Migration Plan](docs/MCP_MIGRATION_PLAN.md)** - Original 8-phase migration plan
- **[Configuration Guide](myndy_crewai_mcp/config.py)** - Server configuration options
- **[Schemas Reference](myndy_crewai_mcp/schemas.py)** - MCP data schemas

### Testing & Validation
- **[Tool Registration Test](test_tool_registration.py)** - Verify tool discovery
- **[Tool Execution Test](test_tool_execution.py)** - Test tool execution via HTTP
- **[Resource Access Test](test_resource_access.py)** - Test resource URIs
- **[Prompts Test](test_prompts.py)** - Test prompt generation

## Documentation by Topic

### For Users

#### Getting Started
1. Read [MCP Server README](myndy_crewai_mcp/README.md) for quick start
2. Review [LibreChat Integration Guide](LIBRECHAT_INTEGRATION_GUIDE.md) for LibreChat setup
3. Run test scripts to verify installation

#### Using the MCP Server
- **Tools**: 33 tools dynamically discovered from myndy-ai backend
- **Resources**: 14 resources accessible via `myndy://` URIs
- **Prompts**: 16 agent workflow templates across 5 personas

#### Troubleshooting
- Check [LibreChat Integration Guide - Troubleshooting](LIBRECHAT_INTEGRATION_GUIDE.md#troubleshooting)
- Review [Test Suite Guide - Debugging](TEST_SUITE_GUIDE.md#debugging-tests)
- Check server logs: `/tmp/mcp_server.log`

### For Developers

#### Architecture & Design
- [MCP Migration Complete](MCP_MIGRATION_COMPLETE.md#architecture) - System architecture overview
- [Migration Plan](docs/MCP_MIGRATION_PLAN.md) - Original design decisions
- [MCP Server README](myndy_crewai_mcp/README.md#architecture) - Component architecture

#### Implementation Details
- **Tools Provider**: [Phase 3 Documentation](MCP_PHASE3_COMPLETE.md)
  - Dynamic tool discovery from backend
  - HTTP bridge implementation
  - Tool schema conversion
  - Error handling and fallbacks

- **Resources Provider**: [Phase 4 Documentation](MCP_PHASE4_COMPLETE.md)
  - myndy:// URI scheme design
  - Category-based resource routing
  - Resource templates for parameterized access
  - Backend API integration

- **Prompts Provider**: [Phase 5 Documentation](MCP_PHASE5_COMPLETE.md)
  - Agent persona definitions
  - Dynamic message building
  - Argument handling
  - Workflow templates

#### Testing
- [Test Suite Guide](TEST_SUITE_GUIDE.md) - Complete testing documentation
- Unit tests: Test individual components
- Integration tests: Test full workflows
- Performance tests: Benchmark tool execution

#### Extending the Server
- **Adding Tools**: Tools are automatically discovered from myndy-ai backend
- **Adding Resources**: Edit `myndy_crewai_mcp/resources_provider.py`
- **Adding Prompts**: Edit `myndy_crewai_mcp/prompts_provider.py`
- **Configuration**: Edit `myndy_crewai_mcp/config.py`

### For DevOps

#### Deployment
- [MCP Server README - Quick Start](myndy_crewai_mcp/README.md#quick-start)
- [LibreChat Integration - Installation](LIBRECHAT_INTEGRATION_GUIDE.md#installation-steps)
- Environment variables and configuration options

#### Monitoring
- Health endpoint: `http://localhost:9092/health`
- Metrics endpoint: `http://localhost:9092/metrics` (if implemented)
- Log file: `/tmp/mcp_server.log`

#### Performance
- [Migration Complete - Performance](MCP_MIGRATION_COMPLETE.md#performance-metrics)
- Connection pooling: 100 total connections, 30 per host
- Async operations throughout
- Tool execution benchmarks: < 1 second for most tools

## Documentation by Phase

### Phase 1-2: Foundation (Complete ✅)
**Goal**: Setup MCP SDK and basic server structure

**Documentation**:
- [MCP Setup Complete](MCP_SETUP_COMPLETE.md)
- [MCP Server README - Installation](myndy_crewai_mcp/README.md#installation)

**Key Achievements**:
- MCP SDK installed and configured
- Basic server structure with SSE streaming
- Configuration system implemented
- Health check endpoint functional

### Phase 3: Tools (Complete ✅)
**Goal**: Dynamic tool discovery and execution via HTTP bridge

**Documentation**:
- [Phase 3 Complete](MCP_PHASE3_COMPLETE.md)
- [Tool Registration Test](test_tool_registration.py)
- [Tool Execution Test](test_tool_execution.py)

**Key Achievements**:
- 33 tools registered (52 discovered, 19 duplicates skipped)
- HTTP bridge with connection pooling
- Tool schema conversion (Myndy → MCP)
- All tool tests passing (4/4)

### Phase 4: Resources (Complete ✅)
**Goal**: Expose myndy-ai data via myndy:// URI scheme

**Documentation**:
- [Phase 4 Complete](MCP_PHASE4_COMPLETE.md)
- [Resource Access Test](test_resource_access.py)

**Key Achievements**:
- 14 resources registered (memory, profile, health, finance, documents)
- 5 resource templates for parameterized access
- myndy:// URI scheme with category routing
- All resource tests passing (5/5)

### Phase 5: Prompts (Complete ✅)
**Goal**: Pre-configured agent workflow templates

**Documentation**:
- [Phase 5 Complete](MCP_PHASE5_COMPLETE.md)
- [Prompts Test](test_prompts.py)

**Key Achievements**:
- 16 prompts across 5 agent categories
- Dynamic message building system
- Agent persona definitions
- All prompt tests passing (7/7)

### Phase 6: LibreChat Integration (Pending ⏳)
**Goal**: End-to-end testing with LibreChat client

**Documentation**:
- [LibreChat Integration Guide](LIBRECHAT_INTEGRATION_GUIDE.md) (preparation complete)

**Remaining Work**:
- Install LibreChat
- Configure LibreChat with MCP server
- Test tools, resources, and prompts from UI
- Document real-world integration issues

### Phase 7: Testing & Validation (Partial ✅)
**Goal**: Comprehensive test coverage

**Documentation**:
- [Test Suite Guide](TEST_SUITE_GUIDE.md)

**Current Status**:
- 4 test scripts created and passing
- Unit test recommendations documented
- Integration test recommendations documented
- Performance test recommendations documented

**Remaining Work**:
- Implement recommended unit tests
- Implement integration tests
- Performance benchmarking
- Security testing

### Phase 8: Production Deployment (Pending ⏳)
**Goal**: Production-ready deployment

**Documentation**:
- Deployment guide (to be created)
- Monitoring guide (to be created)

**Remaining Work**:
- Production deployment guide
- Monitoring and alerting setup
- Backup and recovery procedures
- Performance tuning guide

## MCP Server Capabilities

### Tools (33 total)
**Categories**: Memory (14), Time (4), Profile (4), System (3), Location (2), Management (2), Journal (1), Knowledge (1), Projects (1), Search (1)

**Full list**: See [Phase 3 Complete](MCP_PHASE3_COMPLETE.md#tool-categories)

### Resources (14 static + 5 templates)
**Categories**: Memory (6), Profile (3), Health (2), Finance (2), Documents (1)

**URIs**:
```
myndy://memory/entities
myndy://memory/conversations
myndy://memory/short-term
myndy://memory/people
myndy://memory/places
myndy://memory/events
myndy://profile/self
myndy://profile/goals
myndy://profile/preferences
myndy://health/metrics
myndy://health/status
myndy://finance/transactions
myndy://finance/budget
myndy://documents/list
```

**Templates**:
```
myndy://memory/entities/{entity_id}
myndy://memory/conversations/{conversation_id}
myndy://memory/people/{person_id}
myndy://memory/places/{place_id}
myndy://documents/{path}
```

**Full details**: See [Phase 4 Complete](MCP_PHASE4_COMPLETE.md#resources)

### Prompts (16 total)
**Agent Categories**:
- Personal Assistant (3 prompts)
- Memory Librarian (4 prompts)
- Research Specialist (3 prompts)
- Health Analyst (3 prompts)
- Finance Tracker (3 prompts)

**Prompts**:
```
personal_assistant, schedule_management, time_query
memory_librarian, memory_search, entity_management, conversation_analysis
research_specialist, information_gathering, document_analysis
health_analyst, health_metrics, wellness_insights
finance_tracker, expense_tracking, budget_analysis
```

**Full details**: See [Phase 5 Complete](MCP_PHASE5_COMPLETE.md#agent-workflow-prompts)

## Integration Points

### Myndy-AI Backend
**Connection**: HTTP REST API at `http://localhost:8000`
**Endpoints Used**:
- `/api/v1/tools/` - Tool discovery
- `/api/v1/tools/execute` - Tool execution
- `/api/v1/memory/*` - Memory operations
- `/api/v1/profile/*` - Profile operations
- `/api/v1/health/*` - Health data
- `/api/v1/finance/*` - Finance data

### LibreChat Client
**Connection**: SSE (Server-Sent Events) transport
**Protocol**: JSON-RPC 2.0 over SSE
**Port**: 9092 (configurable)
**Format**: MCP standard protocol

### Other MCP Clients
**Supported**: Any MCP-compatible client (Claude Desktop, etc.)
**Protocol**: Standard MCP protocol
**Transport**: SSE, HTTP, or stdio (configurable)

## Common Tasks

### Start the MCP Server
```bash
cd /Users/jeremy/myndy-core/myndy-crewai
python3 start_mcp_server.py
```

### Run All Tests
```bash
# Individual tests
python3 test_tool_registration.py
python3 test_tool_execution.py
python3 test_resource_access.py
python3 test_prompts.py

# Or create test runner (see Test Suite Guide)
./run_all_tests.sh
```

### Check Server Health
```bash
curl http://localhost:9092/health
```

### Debug Issues
```bash
# Enable debug logging
export MCP_DEBUG="true"
export MCP_LOG_LEVEL="DEBUG"

# Check logs
tail -f /tmp/mcp_server.log
```

### Integrate with LibreChat
See [LibreChat Integration Guide](LIBRECHAT_INTEGRATION_GUIDE.md) for complete instructions.

## Known Issues

### Tool Duplicates
**Issue**: Backend returns 52 tools but 19 are duplicates
**Status**: Handled in MCP server (duplicate detection)
**Impact**: None - server correctly registers 33 unique tools
**Reference**: [Phase 3 Complete - Duplicate Tools](MCP_PHASE3_COMPLETE.md#duplicate-tools)

### Limited Finance/Document Support
**Issue**: Backend has limited finance and document APIs
**Status**: Placeholder handlers implemented
**Impact**: Some resources return limited data
**Reference**: [Phase 4 Complete - Known Limitations](MCP_PHASE4_COMPLETE.md#known-limitations)

## Performance Metrics

- **Server Startup**: < 5 seconds
- **Tool Registration**: < 1 second for 33 tools
- **Tool Execution**: < 1 second for most tools (varies by backend)
- **Resource Access**: < 500ms for most resources
- **Prompt Generation**: < 100ms (instant, no backend calls)

**Full metrics**: See [Migration Complete - Performance](MCP_MIGRATION_COMPLETE.md#performance-metrics)

## Success Criteria

All Phase 1-5 success criteria achieved:

✅ MCP SDK properly integrated
✅ Server accepts and responds to MCP protocol messages
✅ Tools dynamically discovered from backend
✅ All tool tests passing (100%)
✅ Resources accessible via myndy:// URIs
✅ All resource tests passing (100%)
✅ Prompts generate proper messages
✅ All prompt tests passing (100%)
✅ Zero changes to myndy-ai backend
✅ HTTP bridge preserves existing infrastructure
✅ Comprehensive documentation created

**Full criteria**: See [Migration Complete - Success Criteria](MCP_MIGRATION_COMPLETE.md#success-criteria)

## Next Steps

### For Immediate Use
1. Start MCP server: `python3 start_mcp_server.py`
2. Verify health: `curl http://localhost:9092/health`
3. Run tests to confirm functionality
4. Review [LibreChat Integration Guide](LIBRECHAT_INTEGRATION_GUIDE.md) for next steps

### For Development
1. Review [Migration Complete](MCP_MIGRATION_COMPLETE.md) for architecture understanding
2. Check [Test Suite Guide](TEST_SUITE_GUIDE.md) for testing patterns
3. See phase documentation for implementation details
4. Extend server by adding resources or prompts

### For Production
1. Complete Phase 6: LibreChat integration testing
2. Implement recommended additional tests (Phase 7)
3. Create production deployment guide (Phase 8)
4. Setup monitoring and alerting
5. Configure backup and recovery

## Support & Feedback

**Issues**: Report technical issues in project issue tracker
**Questions**: Review documentation index or check specific phase docs
**Contributions**: Follow existing patterns in phase documentation

---

## Document History

**Created**: October 7, 2025
**Last Updated**: October 7, 2025
**Version**: 1.0
**Status**: Phase 1-5 documentation complete

**Maintainers**: Jeremy (project owner)
**Contributors**: Claude (Sonnet 4.5) - Implementation and documentation

---

**This index is maintained as new phases are completed and documentation is added.**
