# MCP (Model Context Protocol) Migration - TODO

## 📋 **STATUS: IN PROGRESS - Phase 1**

**Goal**: Migrate CrewAI-Myndy integration from OpenWebUI Pipeline to Model Context Protocol (MCP) for LibreChat integration.

**Documentation**: See `docs/MCP_MIGRATION_PLAN.md` for comprehensive migration plan.

---

## 🎯 **Current Priority: Phase 1 - Foundation Setup**

### Phase 1: Foundation Setup (Week 1) - 🚀 IN PROGRESS

- [ ] **1.1** Install MCP Python SDK and dependencies
  - Install: `pip install mcp`
  - Install: `pip install pydantic>=2.0`
  - Verify installation and compatibility

- [ ] **1.2** Create MCP server project structure
  - Create `/mcp/` directory
  - Set up Python package structure
  - Create initial `__init__.py` files

- [ ] **1.3** Study MCP SDK documentation
  - Review official MCP Python SDK docs
  - Study example MCP servers
  - Understand JSON-RPC 2.0 message format
  - Review transport layer options (stdio/SSE/HTTP)

- [ ] **1.4** Design MCP server architecture
  - ✅ Architecture design document created (MCP_MIGRATION_PLAN.md)
  - Map existing tools to MCP tool schema
  - Design resource URI scheme
  - Plan prompt templates

---

## 📅 **Upcoming Phases**

### Phase 2: Core MCP Server (Week 1-2)

- [ ] **2.1** Create base MCP server implementation
  - Implement `mcp/server.py` main server
  - Set up JSON-RPC 2.0 message handling
  - Implement capability negotiation

- [ ] **2.2** Implement transport layers
  - Stdio transport (primary)
  - SSE transport (secondary)
  - HTTP transport (tertiary)

- [ ] **2.3** Add logging and error handling
  - Integrate with existing logging system
  - Implement error response formatting
  - Add debug mode support

- [ ] **2.4** Create MCP configuration system
  - Environment variable configuration
  - Configuration file support
  - Dynamic configuration updates

**Deliverables**: Functional MCP server skeleton with transport layers

---

### Phase 3: Tools Migration (Week 2-3)

- [ ] **3.1** Create MCP tools provider
  - Implement `mcp/tools_provider.py`
  - Wrap existing HTTP tool bridge
  - Preserve async operations and caching

- [ ] **3.2** Migrate tool categories to MCP
  - [ ] Memory management tools (15+ tools)
  - [ ] Calendar/scheduling tools (10+ tools)
  - [ ] Health analytics tools (12+ tools)
  - [ ] Finance tracking tools (8+ tools)
  - [ ] Research/document tools (10+ tools)
  - [ ] Communication tools (15+ tools)
  - [ ] Weather/location tools (8+ tools)
  - [ ] System utility tools (10+ tools)

- [ ] **3.3** Implement tool parameter validation
  - Map parameter schemas to MCP format
  - Add validation logic
  - Implement error responses

- [ ] **3.4** Implement tool result formatting
  - Format tool results for MCP protocol
  - Handle errors and timeouts
  - Add metadata to results

**Deliverables**: All 85+ tools accessible via MCP protocol

---

### Phase 4: Resources Implementation (Week 3)

- [ ] **4.1** Create MCP resources provider
  - Implement `mcp/resources_provider.py`
  - Define resource URI schema (`myndy://...`)

- [ ] **4.2** Implement memory resources
  - `myndy://memory/entities` - All entities
  - `myndy://memory/entities/{id}` - Specific entity
  - `myndy://memory/conversations` - Conversation history

- [ ] **4.3** Implement profile resources
  - `myndy://profile/user` - User profile
  - `myndy://profile/preferences` - User preferences

- [ ] **4.4** Implement document resources
  - `myndy://documents/{path}` - Document access
  - Document metadata and search

- [ ] **4.5** Implement data resources
  - `myndy://health/metrics` - Health data
  - `myndy://finance/transactions` - Financial data

- [ ] **4.6** Add resource caching
  - Cache frequently accessed resources
  - Implement cache invalidation
  - Monitor cache performance

**Deliverables**: Complete resource access via MCP resources

---

### Phase 5: Prompts Implementation (Week 3-4)

- [ ] **5.1** Create MCP prompts provider
  - Implement `mcp/prompts_provider.py`
  - Extract agent prompts from existing code

- [ ] **5.2** Create agent workflow prompts
  - [ ] Personal Assistant prompt
  - [ ] Memory Librarian prompt
  - [ ] Research Specialist prompt
  - [ ] Health Analyst prompt
  - [ ] Finance Tracker prompt
  - [ ] Shadow Agent analysis prompt

- [ ] **5.3** Implement prompt templates
  - Variable substitution
  - Dynamic prompt generation
  - Metadata and descriptions

- [ ] **5.4** Add prompt discovery
  - List available prompts
  - Prompt search and filtering
  - Usage examples

**Deliverables**: Complete prompt system for agent workflows

---

### Phase 6: LibreChat Integration (Week 4)

- [ ] **6.1** Create LibreChat configuration
  - Write `librechat.yaml` configuration file
  - Configure MCP server connection
  - Set up environment variables

- [ ] **6.2** Test MCP server with LibreChat
  - Connect LibreChat to MCP server
  - Test tool invocation
  - Test resource access
  - Test prompt workflows

- [ ] **6.3** Configure agent-specific settings
  - Set up model configurations
  - Configure agent parameters
  - Set up authentication

- [ ] **6.4** Validate integration
  - Test complete user workflows
  - Verify tool execution
  - Check memory persistence
  - Test error handling

**Deliverables**: Working LibreChat integration with MCP server

---

### Phase 7: Testing & Validation (Week 4-5)

- [ ] **7.1** Unit tests for MCP server
  - Test transport layers
  - Test message routing
  - Test capability negotiation

- [ ] **7.2** Unit tests for providers
  - Test tools provider
  - Test resources provider
  - Test prompts provider

- [ ] **7.3** Integration tests
  - Test LibreChat integration
  - Test tool execution flow
  - Test resource access
  - Test prompt execution

- [ ] **7.4** Performance testing
  - Benchmark tool execution latency
  - Benchmark resource retrieval time
  - Test concurrent request handling
  - Monitor memory usage

- [ ] **7.5** Security testing
  - Validate authentication
  - Test input validation
  - Check data privacy controls

- [ ] **7.6** Comparison testing
  - Compare with OpenWebUI Pipeline performance
  - Validate no regression
  - Document improvements

**Deliverables**: Comprehensive test suite with 90%+ coverage

---

### Phase 8: Documentation & Deployment (Week 5)

- [ ] **8.1** Architecture documentation
  - Write `MCP_ARCHITECTURE.md`
  - Document system design
  - Create architecture diagrams

- [ ] **8.2** Tool reference documentation
  - Write `MCP_TOOL_REFERENCE.md`
  - Document all 85+ tools
  - Add usage examples

- [ ] **8.3** Setup guide
  - Write `MCP_LIBRECHAT_SETUP.md`
  - Installation instructions
  - Configuration guide
  - Troubleshooting section

- [ ] **8.4** Update project documentation
  - Update `CLAUDE.md` with MCP guidelines
  - Update architecture documentation
  - Add MCP integration patterns

- [ ] **8.5** Create deployment guide
  - Deployment procedures
  - Environment configuration
  - Monitoring and logging setup

- [ ] **8.6** Document rollback procedures
  - Rollback triggers
  - Step-by-step rollback process
  - Validation checklist

**Deliverables**: Complete documentation suite

---

## 🎯 **Success Criteria**

### Functional Requirements
- ✅ All 85+ tools execute correctly via MCP
- ✅ Resources provide accurate context data
- ✅ Prompts render with proper variable substitution
- ✅ LibreChat integration works seamlessly
- ✅ Multi-turn conversations maintain context
- ✅ Error messages are clear and actionable

### Performance Requirements
- ✅ Tool execution latency <500ms (95th percentile)
- ✅ Resource retrieval <200ms (95th percentile)
- ✅ Support 50+ concurrent requests
- ✅ Memory usage <500MB baseline
- ✅ No performance regression vs. Pipeline

### Quality Requirements
- ✅ 90%+ test coverage
- ✅ Zero critical security vulnerabilities
- ✅ Comprehensive documentation
- ✅ Clear migration guide
- ✅ Rollback procedure validated

---

## 📊 **Project Status**

### Timeline
- **Week 1**: Foundation Setup + Core MCP Server (Phase 1-2)
- **Week 2**: Tools Migration (Phase 3)
- **Week 3**: Resources + Prompts (Phase 4-5)
- **Week 4**: LibreChat Integration + Testing (Phase 6-7)
- **Week 5**: Documentation + Deployment (Phase 8)

**Total Estimated Time**: 5 weeks

### Progress
- **Phase 1**: 🚀 IN PROGRESS (25% complete)
- **Phase 2**: ⏸️ NOT STARTED
- **Phase 3**: ⏸️ NOT STARTED
- **Phase 4**: ⏸️ NOT STARTED
- **Phase 5**: ⏸️ NOT STARTED
- **Phase 6**: ⏸️ NOT STARTED
- **Phase 7**: ⏸️ NOT STARTED
- **Phase 8**: ⏸️ NOT STARTED

---

## 🔗 **Related Documentation**

- **Migration Plan**: `docs/MCP_MIGRATION_PLAN.md` (comprehensive plan)
- **Architecture**: To be created in Phase 8
- **Tool Reference**: To be created in Phase 8
- **Setup Guide**: To be created in Phase 8

---

## 🚨 **Important Notes**

### Preserved Components (No Changes Required)
- `tools/myndy_bridge.py` - HTTP tool bridge
- `tools/async_http_client.py` - HTTP client
- `tools/tool_cache.py` - Caching system
- `agents/` - Agent definitions (minimal changes)
- Myndy-AI backend (no changes)

### Deprecated Components (Keep for Reference)
- `pipeline/server.py` - OpenWebUI Pipeline (will be replaced by MCP)

### Key Design Principles
1. **Minimize Changes**: Reuse existing HTTP tool bridge and caching
2. **Maintain Service Boundaries**: MCP server calls myndy-ai HTTP APIs
3. **Standard Compliance**: Follow MCP specification exactly
4. **Performance**: Preserve async operations and caching
5. **Security**: Maintain authentication and authorization

---

## 📝 **Decision Log**

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-07 | Choose MCP over Custom Endpoint | Future-proof, standardized approach |
| 2025-10-07 | Preserve HTTP tool bridge | Minimize changes, maintain architecture |
| 2025-10-07 | Phased migration approach | Reduce risk, enable rollback |
| 2025-10-07 | Use stdio transport initially | Simplicity and LibreChat compatibility |

---

## 🎯 **Next Immediate Actions**

1. Install MCP Python SDK: `pip install mcp`
2. Create MCP project structure: `mkdir -p mcp && touch mcp/__init__.py`
3. Study MCP Python SDK examples and documentation
4. Begin implementing core MCP server in `mcp/server.py`

---

**Last Updated**: 2025-10-07
**Status**: Phase 1 - Foundation Setup (IN PROGRESS)
