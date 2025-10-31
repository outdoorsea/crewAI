# Testing Guide for CrewAI-Myndy Integration

This guide provides comprehensive testing approaches for the CrewAI-Myndy integration, from basic connectivity to full agent workflows.

## Current Test Status

✅ **Working Components:**
- Tool schema loading (31+ schemas found)
- Myndy core systems (memory, health, finance collections)
- Ollama connectivity (10 models available)
- Basic tool bridge concept
- Memory system (Qdrant, embeddings, collections)

⚠️ **Dependencies Needed:**
- CrewAI packages: `pip install crewai crewai-tools`
- Some models missing: Gemma (installing)

## Testing Levels

### 1. Basic Connectivity Test

**File**: `simple_test.py`

**What it tests:**
- Tool schema loading from myndy
- Myndy core system initialization
- Ollama server connectivity
- Basic bridge concept

**Run:**
```bash
cd /Users/jeremy/crewAI
python simple_test.py
```

**Expected Output:**
```
🧪 Basic Integration Test
==============================
1. Testing tool schemas...
   ✅ Found 31 tool schemas
2. Testing myndy core...
   ✅ Myndy registry: X tools  # After CrewAI install
3. Testing Ollama...
   ✅ Ollama: 10 models available
4. Testing bridge concept...
   ✅ Can load tool: summarize_text

✅ Basic integration components working!
```

### 2. Integration Test (Comprehensive)

**File**: `test_integration.py`

**What it tests:**
- Tool schema compatibility
- Memory system integration
- Tool categorization
- Agent concept validation
- LLM model availability

**Run:**
```bash
cd /Users/jeremy/crewAI
python test_integration.py
```

### 3. Unit Tests (After CrewAI Install)

**Files**: `tests/test_*.py`

**What it tests:**
- Tool bridge functionality
- Agent creation and configuration
- Memory integration components
- Error handling and edge cases

**Run:**
```bash
cd /Users/jeremy/crewAI
pytest tests/ -v
```

### 4. Example Usage Test

**File**: `examples/basic_usage.py`

**What it tests:**
- Full crew creation
- Task definition
- Agent collaboration concepts

**Run:**
```bash
cd /Users/jeremy/crewAI
python examples/basic_usage.py
```

## Installation Steps for Full Testing

### Step 1: Install CrewAI Dependencies

```bash
# Install core CrewAI packages
pip install crewai>=0.28.0
pip install crewai-tools>=0.1.0

# Install supporting packages
pip install langchain>=0.1.0
pip install langchain-community>=0.0.20
```

### Step 2: Install Missing Models

```bash
# Install missing Ollama models
ollama pull gemma

# Verify all models are available
ollama list
```

**Required models:**
- llama3 ✅
- mixtral ✅ 
- phi ✅
- mistral ✅
- gemma ⚠️ (installing)

### Step 3: Verify Myndy Components

```bash
# Test myndy memory system
cd /Users/jeremy/myndy
python -c "from memory.models.components.memory_store import MemoryStore; print('Memory store OK')"

# Test tool registry
python -c "from agents.tools.registry import registry; print(f'Registry: {len(registry._tools)} tools')"
```

## Testing Workflow

### Phase 1: Pre-CrewAI Testing ✅

1. **Basic connectivity** - `simple_test.py` ✅
2. **Myndy integration** - Verify tool loading ✅
3. **Ollama connectivity** - Check models ✅

### Phase 2: Post-CrewAI Installation

1. **Install dependencies**:
   ```bash
   pip install crewai crewai-tools langchain
   ```

2. **Run integration test**:
   ```bash
   python test_integration.py
   ```

3. **Run unit tests**:
   ```bash
   pytest tests/ -v
   ```

### Phase 3: Full Agent Testing

1. **Test agent creation**:
   ```bash
   python examples/basic_usage.py
   ```

2. **Test individual components**:
   ```bash
   python -c "
   from agents import create_memory_librarian
   agent = create_memory_librarian()
   print(f'Agent created: {agent.role}')
   print(f'Tools available: {len(agent.tools)}')
   "
   ```

3. **Test crew functionality**:
   ```bash
   python -c "
   from crews import create_personal_productivity_crew
   crew = create_personal_productivity_crew()
   print('Crew created successfully')
   "
   ```

## Test Scenarios

### Scenario 1: Simple Tool Execution

```python
# Test basic tool bridge
from tools import load_myndy_tools_for_agent
tools = load_myndy_tools_for_agent('memory_librarian')
print(f'Loaded {len(tools)} tools for memory librarian')
```

### Scenario 2: Agent Task Creation

```python
# Test task creation without execution
from crews import create_personal_productivity_crew
crew_manager = create_personal_productivity_crew()
task = crew_manager.create_life_analysis_task('last week')
print(f'Task created: {task.description[:100]}...')
```

### Scenario 3: Memory Integration

```python
# Test memory bridge
from memory import get_memory_bridge
bridge = get_memory_bridge('test_user')
stats = bridge.get_memory_stats()
print(f'Memory available: {stats["available"]}')
```

### Scenario 4: LLM Configuration

```python
# Test LLM setup
from config import get_llm_config
config = get_llm_config()
info = config.get_model_info()
print(f'Models available: {info["available_models"]}')
```

## Troubleshooting Common Issues

### Issue: `No module named 'crewai_tools'`
**Solution**: Install CrewAI dependencies
```bash
pip install crewai crewai-tools
```

### Issue: `Memory system not available`
**Solution**: Check myndy path and imports
```bash
export PYTHONPATH="/Users/jeremy/myndy:$PYTHONPATH"
```

### Issue: `Ollama connection failed`
**Solution**: Start Ollama service
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

### Issue: `Model not found`
**Solution**: Pull missing models
```bash
ollama pull gemma
ollama pull mistral
# etc.
```

## Expected Test Results

### Pre-CrewAI Installation
```
✅ Tool Schemas (31 found)
❌ Myndy Registry (missing crewai_tools)
✅ Ollama Connectivity (10 models)
✅ Tool Bridge Concept
✅ Agent Concept
```

### Post-CrewAI Installation
```
✅ Tool Schemas
✅ Myndy Registry  
✅ Memory System
✅ Tool Bridge
✅ Ollama Connectivity
✅ Agent Creation
✅ Crew Functionality
```

## Performance Benchmarks

**Expected Performance:**
- Tool loading: ~1-2 seconds
- Agent creation: ~500ms each
- Memory operations: <100ms
- Ollama inference: 1-5 seconds per query

## Next Steps After Successful Testing

1. **Create sample workflows**
2. **Test real-world use cases**
3. **Optimize performance**
4. **Add monitoring and logging**
5. **Create user documentation**

## Test Coverage Goals

- [ ] **Tool Bridge**: 90%+ coverage
- [ ] **Agent Creation**: 95%+ coverage  
- [ ] **Memory Integration**: 85%+ coverage
- [ ] **LLM Configuration**: 90%+ coverage
- [ ] **Error Handling**: 80%+ coverage

Run tests with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```