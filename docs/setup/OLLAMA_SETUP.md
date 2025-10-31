# CrewAI with Ollama Setup Guide

This guide explains how to configure CrewAI to use Ollama instead of OpenAI for local LLM inference.

## 🎯 Overview

We've configured CrewAI to use Ollama as the default LLM provider instead of OpenAI. This provides:
- **Local inference** - No API keys required
- **Privacy** - Data stays on your machine
- **Cost-effective** - No per-token charges
- **Offline capability** - Works without internet

## 📋 Prerequisites

- Python 3.10+ (note: CrewAI 0.28+ requires Python <3.13)
- At least 8GB RAM (16GB+ recommended for larger models)
- 20GB+ free disk space for models

## 🔧 Installation Steps

### 1. Install Ollama

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download from [ollama.ai](https://ollama.ai/download/windows)

### 2. Start Ollama Service

```bash
ollama serve
```

This starts Ollama on `http://localhost:11434`

### 3. Install Required Dependencies

```bash
# Core dependencies
pip install json-repair appdirs chromadb langchain-community

# Optional: Install CrewAI if not already installed
pip install crewai>=0.11.2
```

### 4. Pull Required Models

#### Language Models
```bash
# Primary model (default)
ollama pull llama3.2

# Additional recommended models
ollama pull qwen2.5          # Strong reasoning
ollama pull gemma2           # Fast responses  
ollama pull phi3             # Efficient analysis
ollama pull mixtral          # Good with numbers
ollama pull codellama        # Code generation
ollama pull deepseek-coder   # Advanced coding
```

#### Embedding Model
```bash
ollama pull nomic-embed-text
```

## 🚀 Configuration Changes Made

### 1. Default Provider Changed
- **File**: `src/crewai/cli/constants.py`
- **Change**: Ollama moved to first position in `PROVIDERS` list
- **Default model**: Changed from `gpt-4o-mini` to `ollama/llama3.2`

### 2. Ollama Models Added
```python
"ollama": [
    "ollama/llama3.2",
    "ollama/llama3.1", 
    "ollama/llama3.1:8b",
    "ollama/llama3.1:70b",
    "ollama/qwen2.5",
    "ollama/qwen2.5:7b",
    "ollama/qwen2.5:14b", 
    "ollama/qwen2.5:32b",
    "ollama/mistral",
    "ollama/mixtral",
    "ollama/codellama",
    "ollama/deepseek-coder",
    "ollama/phi3"
]
```

### 3. Environment Variables
- **File**: `src/crewai/cli/constants.py`
- **Change**: Ollama configuration prioritized with `http://localhost:11434`

### 4. Embedding Functions Updated
- **Files**: 
  - `src/crewai/utilities/embedding_configurator.py`
  - `src/crewai/knowledge/storage/knowledge_storage.py` 
  - `src/crewai/memory/storage/rag_storage.py`
- **Change**: Default embedding changed from OpenAI to Ollama's `nomic-embed-text`

### 5. Custom LLM Configuration
- **File**: `config/llm_config.py`
- **Changes**:
  - Default model: `llama3.2`
  - Updated model assignments per agent role
  - Removed OpenAI fallback references

## 📝 Usage Examples

### Basic CrewAI with Ollama

```python
from crewai import Agent, Task, Crew

# Create agent with Ollama (default)
agent = Agent(
    role="Research Assistant",
    goal="Analyze data and provide insights",
    backstory="An AI assistant specializing in research",
    llm="ollama/llama3.2",  # Explicitly specify Ollama model
    verbose=True
)

# Create task
task = Task(
    description="Analyze the latest trends in AI technology",
    expected_output="A comprehensive report on AI trends",
    agent=agent
)

# Create and run crew
crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)

result = crew.kickoff()
```

### Using Different Models per Agent

```python
from config.llm_config import get_agent_llm

# Get optimized LLM for specific agent roles
research_llm = get_agent_llm("research_specialist")  # Uses qwen2.5
assistant_llm = get_agent_llm("personal_assistant")  # Uses gemma2
finance_llm = get_agent_llm("finance_tracker")       # Uses mixtral
```

### Custom Ollama Configuration

```python
from crewai import Agent

agent = Agent(
    role="Code Reviewer",
    goal="Review and improve code quality",
    backstory="Senior software engineer",
    llm="ollama/codellama",  # Use CodeLlama for coding tasks
    verbose=True
)
```

## 🔍 Verification

Test your setup with:

```bash
cd /path/to/crewai
python simple_ollama_test.py
```

Expected output:
```
🚀 Simple Ollama Configuration Test
========================================
🔧 Testing constants configuration...
✅ Default model: ollama/llama3.2
✅ Primary provider: ollama
✅ Ollama models: 13

🔧 Testing custom config...
✅ Default model: llama3.2
✅ Ollama URL: http://localhost:11434
✅ Available models: 9

📊 Results: 2/2 tests passed
🎉 Configuration looks good!
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Connection refused" errors**
   - Ensure Ollama is running: `ollama serve`
   - Check if port 11434 is available

2. **"Model not found" errors**
   - Pull the required model: `ollama pull llama3.2`
   - Verify available models: `ollama list`

3. **Import errors**
   - Install missing dependencies: `pip install json-repair appdirs chromadb`

4. **Memory issues**
   - Use smaller models like `phi3` or `gemma2`
   - Reduce context window in model configuration

### Performance Optimization

1. **Model Selection by Use Case**:
   - **General tasks**: `llama3.2`
   - **Reasoning/Analysis**: `qwen2.5`
   - **Fast responses**: `gemma2`
   - **Code tasks**: `codellama` or `deepseek-coder`
   - **Math/Finance**: `mixtral`

2. **Hardware Recommendations**:
   - **8GB RAM**: Use 7B parameter models (gemma2, phi3)
   - **16GB RAM**: Use 8B-14B parameter models (llama3.2, qwen2.5:7b)
   - **32GB+ RAM**: Use larger models (mixtral, qwen2.5:32b)

## 🔒 Environment Variables

Optional environment variables for customization:

```bash
# Ollama server URL (default: http://localhost:11434)
export OLLAMA_BASE_URL="http://localhost:11434"

# Default model for myndy integration
export MEMEX_DEFAULT_MODEL="llama3.2"

# Disable OpenAI entirely (optional)
unset OPENAI_API_KEY
```

## 📊 Model Comparison

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `gemma2` | 2B-9B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Quick responses |
| `phi3` | 3.8B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Analysis tasks |
| `llama3.2` | 3B-11B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | General purpose |
| `qwen2.5` | 7B-72B | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Complex reasoning |
| `mixtral` | 8x7B | ⭐⭐ | ⭐⭐⭐⭐⭐ | Math/specialized |
| `codellama` | 7B-34B | ⭐⭐⭐ | ⭐⭐⭐⭐ | Code generation |

## 📚 Next Steps

1. **Test with Real Workflows**: Try running your existing CrewAI scripts
2. **Optimize Model Selection**: Choose appropriate models for each agent role
3. **Monitor Performance**: Adjust models based on speed vs quality needs
4. **Scale Up**: Consider GPU acceleration for larger models

## 🤝 Support

- **Ollama Documentation**: [ollama.ai/docs](https://ollama.ai/docs)
- **CrewAI Documentation**: [docs.crewai.com](https://docs.crewai.com)
- **Model Repository**: [ollama.ai/library](https://ollama.ai/library)

---

✅ **Setup Complete!** Your CrewAI is now configured to use Ollama for local, private LLM inference.