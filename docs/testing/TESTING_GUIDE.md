# CrewAI Testing Guide

This guide explains how to test CrewAI with Ollama integration using the provided test scripts.

## 🎯 Testing Overview

We've created three levels of tests to verify your CrewAI + Ollama setup:

1. **Quick Test** - Basic functionality check (1-2 minutes)
2. **Basic Test** - Core features testing (5-10 minutes)  
3. **Advanced Test** - Comprehensive feature testing (10-20 minutes)

## 🚀 Getting Started

### Prerequisites

Before running tests, ensure you have:

```bash
# 1. Ollama installed and running
ollama serve

# 2. Required models pulled
ollama pull llama3.2
ollama pull qwen2.5
ollama pull nomic-embed-text

# 3. Dependencies installed
pip install crewai json-repair appdirs chromadb langchain-community requests
```

## 📋 Test Scripts

### 1. Quick Test (`test_crewai_quick.py`)

**Purpose**: Verify basic CrewAI + Ollama integration
**Duration**: 1-2 minutes
**When to use**: First test to run, troubleshooting

```bash
python test_crewai_quick.py
```

**What it tests**:
- ✅ CrewAI imports
- ✅ Agent creation  
- ✅ Task creation
- ✅ Crew execution
- ✅ Basic Ollama communication

**Expected output**:
```
⚡ Quick CrewAI + Ollama Test
===================================
🔍 Checking Prerequisites
✅ Ollama server is running
✅ llama3.2 model available
📦 Testing imports...
✅ CrewAI imports successful
🤖 Creating agent...
✅ Agent created successfully
📋 Creating task...
✅ Task created successfully
👥 Creating crew...
✅ Crew created successfully
🚀 Executing crew...

===================================
📝 RESULT:
Hello from CrewAI with Ollama!
===================================

🎉 Quick test PASSED!
💡 You can now run the full test suite
```

### 2. Basic Test (`test_crewai_basic.py`)

**Purpose**: Test core CrewAI functionality with multiple scenarios
**Duration**: 5-10 minutes
**When to use**: After quick test passes, regular validation

```bash
python test_crewai_basic.py
```

**What it tests**:
- 🤖 Single agent workflows
- 👥 Multi-agent collaboration  
- 🔧 Custom model configuration
- 📊 Different Ollama models
- 🔍 Ollama server status

**Test scenarios**:
1. **Basic Crew**: Simple agent performing research task
2. **Multi-Agent**: Researcher + Writer collaboration
3. **Custom Config**: Using configuration from `config/llm_config.py`

### 3. Advanced Test (`test_crewai_advanced.py`)

**Purpose**: Test advanced CrewAI features and edge cases
**Duration**: 10-20 minutes
**When to use**: Full validation, before production use

```bash
python test_crewai_advanced.py
```

**What it tests**:
- 🔄 Sequential processes
- 🧠 Memory integration
- 🔧 Custom tools
- ⚠️ Error handling
- 🤖 Multiple model comparison

## 📊 Understanding Test Results

### Success Indicators

**Quick Test Success**:
```
🎉 Quick test PASSED!
```

**Basic Test Success**:
```
📊 Test Results: 3/3 tests passed
🎉 All tests passed! CrewAI is working with Ollama!
```

**Advanced Test Success**:
```
📊 Advanced Test Results: 5/5 tests completed
🎉 Most advanced features are working!
```

### Common Issues and Solutions

#### 1. Connection Errors
```
❌ Cannot connect to Ollama server
```
**Solution**:
```bash
# Start Ollama server
ollama serve
```

#### 2. Model Not Found
```
⚠️ llama3.2 model not found
```
**Solution**:
```bash
# Pull the required model
ollama pull llama3.2
```

#### 3. Import Errors
```
❌ Import failed: No module named 'crewai'
```
**Solution**:
```bash
# Install CrewAI and dependencies
pip install crewai json-repair appdirs chromadb
```

#### 4. Memory Errors
```
❌ Memory integration test failed
```
**Solution**:
- Memory features may require additional configuration
- This is often non-critical for basic functionality

#### 5. Custom Tools Errors
```
❌ Custom tools test failed
```
**Solution**:
- Ensure all dependencies are installed
- Check that the agent has proper tool access

## 🔧 Troubleshooting Commands

### Check Ollama Status
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# List available models
ollama list

# Test a model directly
ollama run llama3.2 "Hello, world!"
```

### Check Python Environment
```bash
# Verify CrewAI installation
python -c "import crewai; print('CrewAI installed')"

# Check dependencies
pip list | grep -E "(crewai|langchain|chromadb)"
```

### Reset and Restart
```bash
# Stop Ollama
pkill ollama

# Start fresh
ollama serve

# Re-pull models if needed
ollama pull llama3.2
ollama pull nomic-embed-text
```

## 📈 Performance Expectations

### Typical Response Times

| Test Type | Expected Duration | Notes |
|-----------|------------------|-------|
| Quick Test | 30-120 seconds | Simple single response |
| Basic Test | 3-8 minutes | Multiple agent interactions |
| Advanced Test | 8-20 minutes | Complex workflows |

### Hardware Impact

| RAM | Recommended Models | Expected Performance |
|-----|-------------------|---------------------|
| 8GB | gemma2, phi3 | Fast, basic quality |
| 16GB | llama3.2, qwen2.5:7b | Good balance |
| 32GB+ | qwen2.5:32b, mixtral | Best quality |

## 🎯 Custom Testing

### Create Your Own Test

```python
from crewai import Agent, Task, Crew

# Your custom agent
agent = Agent(
    role="Your Role",
    goal="Your Goal", 
    backstory="Your Backstory",
    llm="ollama/llama3.2"
)

# Your custom task
task = Task(
    description="Your task description",
    expected_output="What you expect",
    agent=agent
)

# Execute
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
print(result)
```

### Test Specific Models

```python
# Test different models for different tasks
models = [
    "ollama/llama3.2",    # General purpose
    "ollama/qwen2.5",     # Advanced reasoning  
    "ollama/gemma2",      # Fast responses
    "ollama/codellama"    # Code tasks
]

for model in models:
    agent = Agent(role="Tester", goal="Test", backstory="Test", llm=model)
    # ... create task and test
```

## 📝 Next Steps

After successful testing:

1. **Develop Custom Crews** - Create agents for your specific use cases
2. **Optimize Model Selection** - Choose appropriate models per agent role
3. **Configure Memory** - Set up persistent memory for long-term projects  
4. **Add Custom Tools** - Integrate with your existing systems
5. **Production Deployment** - Scale for real-world usage

## 🔗 Resources

- **CrewAI Documentation**: [docs.crewai.com](https://docs.crewai.com)
- **Ollama Models**: [ollama.ai/library](https://ollama.ai/library)
- **Setup Guide**: See `OLLAMA_SETUP.md`

---

✅ **Happy Testing!** These tests will help ensure your CrewAI + Ollama setup is working correctly.