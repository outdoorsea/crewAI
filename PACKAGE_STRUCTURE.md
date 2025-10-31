# Myndy-Core CrewAI Package Structure

This document describes the refactored Python package structure for the myndy-crewai integration.

## Package Structure

```
myndy-crewai/
├── pyproject.toml                    # Package configuration
├── README.md                         # Main documentation
├── src/                             # Source code (Python package standard)
│   ├── crewai/                      # Standard CrewAI framework
│   │   └── ...                      # (Inherited from upstream CrewAI)
│   └── myndy_crewai/                # Our custom myndy-core integration
│       ├── __init__.py              # Main package exports
│       ├── agents/                  # Specialized agents
│       │   ├── __init__.py          # Agent exports
│       │   ├── personal_assistant.py
│       │   ├── enhanced_shadow_agent.py
│       │   └── context_manager.py
│       ├── tools/                   # HTTP bridge and tool integration
│       │   ├── __init__.py          # Tool exports
│       │   ├── myndy_bridge.py      # Main HTTP bridge
│       │   └── shadow_agent_http_tools.py
│       ├── config/                  # Configuration management
│       │   ├── __init__.py          # Config exports
│       │   ├── llm_config.py        # LLM configuration
│       │   └── env_config.py        # Environment variables
│       ├── pipeline/                # OpenWebUI pipeline integration
│       │   ├── __init__.py          # Pipeline exports
│       │   ├── crewai_myndy_pipeline.py  # Main pipeline
│       │   ├── server.py            # FastAPI server
│       │   └── openwebui_pipeline.py     # OpenWebUI specific
│       └── api/                     # API components
│           ├── __init__.py          # API exports
│           ├── valve_manager.py     # Enhanced valve management
│           └── agent_router.py      # Agent routing logic
├── agents/                          # Legacy agent definitions (backward compatibility)
├── tools/                           # Legacy tool definitions (backward compatibility)
├── config/                          # Legacy config (backward compatibility)
├── pipeline/                        # Legacy pipeline (backward compatibility)
├── api/                            # Legacy API (backward compatibility)
├── tests/                          # Test suite
└── docs/                           # Documentation
```

## Key Changes

### 1. **Standard Python Package Structure**
- All source code moved to `src/` directory following Python packaging best practices
- Proper package hierarchy with `__init__.py` files
- Clear separation between upstream CrewAI and myndy-core customizations

### 2. **Package Identity**
- **Name**: `myndy-crewai` (was `crewai`)
- **Version**: `0.1.0` (our versioning)
- **Author**: Jeremy (was Joao Moura)
- **URLs**: Point to myndy-core repository

### 3. **Entry Points**
- **Script**: `myndy-crewai` command launches the pipeline server
- **Target**: `myndy_crewai.pipeline.server:main`

### 4. **Import Structure**

#### Core Exports (from `myndy_crewai`)
```python
from myndy_crewai import (
    Pipeline,                    # Main pipeline orchestrator
    create_personal_assistant,   # Primary agent
    create_enhanced_shadow_agent, # Behavioral analysis agent
    MyndyBridge,                # HTTP bridge to myndy-ai
    LLMConfig,                  # LLM configuration
    EnvConfig                   # Environment management
)
```

#### Legacy Compatibility
```python
# Still works for backward compatibility
from myndy_crewai.agents import create_memory_librarian  # Legacy agents
from myndy_crewai.tools import load_myndy_tools_for_agent  # Legacy functions
```

### 5. **Dual Architecture Support**
- **Current**: 2 agents (Personal Assistant + Shadow Agent)
- **Legacy**: 6 agents (maintained for compatibility but deprecated)
- **Migration Path**: Clear deprecation warnings and migration guides

## Installation

### Development Installation
```bash
cd /Users/jeremy/myndy-core/crewAI
pip install -e .
```

### Production Installation (when published)
```bash
pip install myndy-crewai
```

## Usage

### Command Line
```bash
# Start the pipeline server
myndy-crewai

# Or directly
python -m myndy_crewai.pipeline.server
```

### Python API
```python
import myndy_crewai

# Create and run pipeline
pipeline = myndy_crewai.Pipeline()
response = pipeline.pipe(
    user_message="Hello",
    model_id="auto",
    messages=[],
    body={}
)
```

## Benefits

### 1. **Standards Compliance**
- Follows PEP 518 and modern Python packaging standards
- Proper source layout with `src/` directory
- Standard build system using `hatchling`

### 2. **Clear Separation**
- Upstream CrewAI code remains isolated in `src/crewai/`
- Our customizations clearly defined in `src/myndy_crewai/`
- Easy to track changes and updates

### 3. **Import Safety**
- Proper package structure prevents import conflicts
- Clear namespace separation
- Lazy imports to avoid circular dependencies

### 4. **Maintainability**
- Legacy code maintained for backward compatibility
- Clear migration path for deprecation
- Modular structure allows easy testing and development

### 5. **Distribution Ready**
- Package can be built and distributed via PyPI
- Proper dependencies and optional dependencies
- Development dependencies clearly separated

## Migration from Legacy Structure

### For Developers
1. Update imports from root-level modules to `myndy_crewai.*`
2. Use new standardized agent creation functions
3. Migrate to new valve management system
4. Update CI/CD to use new package structure

### For Users  
1. Install new package: `pip install myndy-crewai`
2. Update import statements in code
3. Use new CLI command: `myndy-crewai` instead of custom scripts
4. Configure via new valve management system

## Testing

```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/myndy_crewai/

# Run with coverage
pytest --cov=myndy_crewai
```

## Future Enhancements

1. **Continuous Integration**: Setup GitHub Actions for automated testing
2. **Documentation**: Automated API documentation generation
3. **Publishing**: PyPI distribution for easy installation
4. **Versioning**: Semantic versioning with automated releases
5. **Type Checking**: Full mypy compatibility with type annotations