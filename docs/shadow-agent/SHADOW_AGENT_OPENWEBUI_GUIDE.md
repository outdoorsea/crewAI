# 🔮 Shadow Agent in OpenWebUI - Complete Setup Guide

## 🎯 Overview

The Shadow Agent runs **automatically in the background** during every conversation in OpenWebUI, silently observing and learning your behavioral patterns. You don't interact with it directly - it works behind the scenes to enhance all other agents.

## ✅ **Current Status: Ready to Use!**

The Shadow Agent is **already integrated** and working automatically in the OpenWebUI pipeline.

## 🚀 **Quick Start - Running Shadow Agent in OpenWebUI**

### Step 1: Start the Myndy-AI Backend (Required)

The Shadow Agent needs the myndy-ai FastAPI server running to store behavioral observations:

```bash
# Navigate to myndy-ai directory
cd /Users/jeremy/myndy-core/myndy-ai

# Start the FastAPI server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Keep this running in background or separate terminal
```

### Step 2: Start the CrewAI Pipeline Server

```bash
# Navigate to pipeline directory
cd /Users/jeremy/myndy-core/crewAI/pipeline

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the OpenWebUI pipeline server
python -m uvicorn server:app --host 0.0.0.0 --port 9099
```

### Step 3: Add Pipeline to OpenWebUI

1. **Open OpenWebUI** in your browser
2. **Go to Settings** → **Pipelines**
3. **Add Pipeline URL**: `http://localhost:9099`
4. **Click "Add Pipeline"**

### Step 4: Use Any Agent - Shadow Agent Observes Automatically

The Shadow Agent works silently in the background for **every conversation** with any agent:

```
🧠 Myndy AI v0.1 (Auto-routing + Shadow observation)
🎯 Memory Librarian (+ Shadow observation)
🎯 Research Specialist (+ Shadow observation)  
🎯 Personal Assistant (+ Shadow observation)
🎯 Health Analyst (+ Shadow observation)
🎯 Finance Tracker (+ Shadow observation)
```

## 🔮 **How Shadow Agent Works Automatically**

### Silent Background Operation

1. **Every Message**: Shadow Agent observes your message and the agent's response
2. **Pattern Analysis**: Analyzes communication style, topics, emotions, timing
3. **Storage**: Stores insights via myndy-ai memory APIs (journal entries, status updates, facts)
4. **Learning**: Builds behavioral patterns and personality model over time

### What It Observes

```yaml
Communication Styles: concise, detailed, polite, urgent, casual
Message Types: question, request, appreciation, scheduling, general  
Topics: health, finance, work, calendar, personal, technology, weather
Emotions: happy, frustrated, confused, excited, worried, neutral
Timing: Time of day, urgency levels, complexity preferences
```

### Where Data Is Stored

- **Journal Entries**: Detailed behavioral observations
- **Status Updates**: Current behavioral patterns
- **Facts**: Long-term preference learning
- **All via HTTP APIs**: No direct database access, follows service architecture

## 📊 **Viewing Shadow Agent Insights**

### Option 1: Direct API Queries

```bash
# Get behavioral insights
curl http://localhost:8000/api/v1/memory/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-12345" \
  -d '{"query": "Shadow Agent Observation", "limit": 10}'

# Get status history
curl http://localhost:8000/api/v1/status/history \
  -H "X-API-Key: dev-api-key-12345"
```

### Option 2: Use Memory Librarian in OpenWebUI

Simply ask the Memory Librarian:
```
"What behavioral patterns have you observed about me?"
"Show me my communication preferences"  
"What topics do I discuss most often?"
"Analyze my interaction patterns"
```

### Option 3: Python Test Script

```bash
cd /Users/jeremy/myndy-core/crewAI
python test_shadow_agent_integration.py
```

## 🔧 **Advanced Configuration**

### Enable Debug Mode

To see detailed Shadow Agent logging:

```bash
# Set environment variable
export MYNDY_VERBOSE=true

# Or modify pipeline valves in OpenWebUI:
# Settings → Pipelines → Myndy AI → Configure
# Set debug_mode: true
```

### Customize API Settings

Edit the Shadow Agent configuration in `agents/mvp_shadow_agent.py`:

```python
# Change API endpoint
myndy_api_base_url = "http://localhost:8000"  # Default

# Modify headers for authentication
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key",  # Update if needed
    "User-Agent": "MVP-Shadow-Agent/1.0"
}
```

## 🧪 **Testing Shadow Agent Operation**

### Verify It's Working

1. **Start both servers** (myndy-ai on :8000, pipeline on :9099)
2. **Have a conversation** in OpenWebUI with any agent
3. **Check logs** for Shadow Agent activity:

```bash
# Look for these log messages in pipeline terminal:
# "🔮 MVP Shadow Agent initialized for behavioral observation"
# "🔮 Shadow observation completed for session [session_id]"
```

4. **Query stored observations**:

```bash
# Check if behavioral data was stored
curl http://localhost:8000/api/v1/memory/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-12345" \
  -d '{"query": "behavioral observation", "limit": 5}'
```

### Sample Test Conversation

Try these messages to generate different behavioral patterns:

```
1. "What's the weather like today?" (casual, weather topic)
2. "Please help me schedule a meeting for tomorrow at 2pm" (polite, scheduling)
3. "Can you analyze my spending patterns this month?" (request, finance)
4. "I'm feeling stressed about my health goals" (emotional, health)
```

Each message will trigger Shadow Agent analysis and storage.

## 🛠️ **Troubleshooting**

### Common Issues

#### 1. Shadow Agent Not Observing
**Symptoms**: No behavioral logs, no stored observations
**Solutions**:
- Ensure myndy-ai server is running on port 8000
- Check API authentication (X-API-Key header)
- Verify Shadow Agent initialization in pipeline logs

#### 2. API Connection Errors
**Symptoms**: HTTP 401/500 errors in logs
**Solutions**:
```bash
# Test myndy-ai server directly
curl http://localhost:8000/api/v1/health

# Check API key in Shadow Agent code
grep -n "api.*key" agents/mvp_shadow_agent.py
```

#### 3. No Behavioral Data Stored
**Symptoms**: Observations run but no data in memory
**Solutions**:
- Check myndy-ai memory system is properly initialized
- Verify Qdrant is running (if using vector storage)
- Test memory APIs directly

### Debug Commands

```bash
# Test Shadow Agent standalone
cd /Users/jeremy/myndy-core/crewAI
python -c "
from agents.mvp_shadow_agent import create_mvp_shadow_agent
agent = create_mvp_shadow_agent()
result = agent.observe_conversation(
    'Hello', 'Hi there!', 'personal_assistant', 'test_123'
)
print('Shadow Agent Result:', result)
"

# Check pipeline integration
python -c "
from pipeline.crewai_myndy_pipeline import Pipeline
p = Pipeline()
print('Shadow Agent Available:', p.mvp_shadow_agent is not None)
"
```

## 📈 **Behavioral Learning Over Time**

### What to Expect

- **First few conversations**: Basic pattern recognition
- **After 10+ interactions**: Communication style preferences emerge
- **After 50+ interactions**: Topic interests and behavioral consistency
- **After 100+ interactions**: Predictive insights and personality modeling

### Privacy Controls

- **All data stays local** in your myndy-ai instance
- **No external tracking** or data sharing
- **User control** over behavioral data via memory APIs
- **Granular deletion** of observations if needed

## 🎯 **Next Steps**

1. **Start using OpenWebUI** - Shadow Agent works automatically
2. **Have natural conversations** - Let it learn your patterns
3. **Check insights periodically** - Ask Memory Librarian about your patterns
4. **Advanced features** - See `SHADOW_AGENT_MAPPING.md` for roadmap

---

## 🔮 **The Shadow Agent Experience**

**You won't notice the Shadow Agent working** - that's the point! It operates silently, learning from every interaction to make all your AI agents more personalized and effective over time.

**Every conversation teaches it more about:**
- How you prefer to communicate
- What topics interest you most  
- Your emotional patterns and triggers
- Optimal timing for different requests
- Your goals and behavioral consistency

**The result**: AI agents that understand you better and provide increasingly personalized assistance.

**Ready to start?** Just use OpenWebUI normally - your Shadow Agent is already watching, learning, and growing smarter with every conversation! 🔮✨