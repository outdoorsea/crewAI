# 💻 Terminal Interface Guide

Complete guide for using Myndy AI pipeline servers directly from the command line with real-time logging and interactive features.

## 📋 Table of Contents

- [Overview](#overview)
- [Server Options](#server-options)
- [Interactive Terminal Interface](#interactive-terminal-interface)
- [Single Command Execution](#single-command-execution)
- [Batch Processing](#batch-processing)
- [Real-Time Monitoring](#real-time-monitoring)
- [Advanced Usage](#advanced-usage)
- [Examples](#examples)

---

## 🔍 Overview

The Myndy AI pipeline provides multiple ways to interact with your AI agents directly from the terminal:

1. **🖥️ Server Mode**: Run as a web server with real-time logs
2. **💬 Interactive Mode**: Chat directly in terminal
3. **⚡ Single Commands**: Execute one-off queries
4. **📝 Batch Mode**: Process multiple commands from files

---

## 🖥️ Server Options

### **Option 1: Enhanced Logging Server** ⭐ **Recommended**

**Purpose**: Run as web server with detailed, colorful logs

**Command**:
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python pipeline/server_with_logs.py
```

**Features**:
- 🎨 **Colorful logs** with emojis
- ⏱️ **Performance metrics** for each request
- 🔍 **Detailed error tracking**
- 💬 **Chat request analysis**
- 📊 **Model selection insights**

**Output Example**:
```
🚀 Starting Myndy AI Pipeline with Enhanced Logging
============================================================
📊 Pipeline Type: Simple
🖥️  Real-time logs will appear below...
🌐 Server will be available at: http://localhost:9099
🔗 Add to OpenWebUI: http://localhost:9099
⏹️  Press Ctrl+C to stop
============================================================

🚀 [14:32:15] INFO     __main__              | 🚀 Pipeline server starting up...
📊 [14:32:15] INFO     __main__              | 📊 Available models: 6
📋 [14:32:15] INFO     uvicorn               | Uvicorn running on http://0.0.0.0:9099

# When requests come in:
📥 [14:32:30] INFO     __main__              | 📥 POST /v1/chat/completions from 127.0.0.1
💬 [14:32:30] INFO     __main__              | 💬 Processing: "What's the weather?"
🎯 [14:32:30] INFO     __main__              | 🎯 Selected: personal_assistant
⚡ [14:32:30] INFO     __main__              | ⚡ Completed in 0.152s
📤 [14:32:30] INFO     __main__              | 📤 ✅ 200 | Response: 245 chars
```

### **Option 2: Simple Server**

**Purpose**: Basic web server with minimal logging

**Command**:
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python pipeline/simple_server.py
```

**Features**:
- 📝 **Basic request logging**
- ⚡ **Fast startup**
- 🔧 **Minimal dependencies**

### **Option 3: Uvicorn with Custom Levels**

**Debug Mode** (Most Verbose):
```bash
python -m uvicorn pipeline.server_with_logs:app --host 0.0.0.0 --port 9099 --log-level debug --reload
```

**Production Mode**:
```bash
python -m uvicorn pipeline.server_with_logs:app --host 0.0.0.0 --port 9099 --log-level info
```

---

## 💬 Interactive Terminal Interface

### **Purpose**: Chat directly with Myndy AI in terminal

**Command**:
```bash
cd /Users/jeremy/crewAI/pipeline
source ../venv/bin/activate
python terminal_runner.py
```

### **Features**:
- 🎯 **Model selection** (auto or specific agent)
- 💬 **Continuous conversation** with history
- 🔄 **Model switching** during chat
- 🗑️ **History clearing**
- ⌨️ **Easy commands**: `quit`, `clear`, `switch`

### **Sample Session**:
```bash
$ python terminal_runner.py

🧠 Myndy AI Terminal Interface
==================================================
Available models:
  1. 🧠 Myndy AI v0.1
  2. 🎯 Memory Librarian
  3. 🎯 Research Specialist
  4. 🎯 Personal Assistant
  5. 🎯 Health Analyst
  6. 🎯 Finance Tracker

Select model (1-6, or 'auto' for intelligent routing): auto

🎯 Using: 🧠 Myndy AI v0.1
💬 Start chatting! (Type 'quit' to exit, 'clear' to clear history, 'switch' to change model)
--------------------------------------------------

👤 You: What's the weather in San Francisco?
🤔 Thinking...
🤖 Myndy: 🤖 **Personal Assistant** (Myndy AI)
**Routing:** Selected Personal Assistant based on pattern matching (score: 3)

**Response:** 🗓️ **Personal Assistant**: I would help with weather information for San Francisco.

👤 You: Do you know John Doe?
🤔 Thinking...
🤖 Myndy: 🤖 **Memory Librarian** (Myndy AI)
**Routing:** Selected Memory Librarian based on pattern matching (score: 2)

**Response:** 📚 **Memory Search**: I would search for John Doe in your contacts and knowledge base.

👤 You: switch
Select model (1-6, or 'auto' for intelligent routing): 2
🎯 Switched to: 🎯 Memory Librarian

👤 You: Search for contacts
🤔 Thinking...
🤖 Myndy: 🎯 **Memory Librarian** (Direct selection)
**Response:** 📚 **Memory Search**: I would search your contact database for stored information.

👤 You: clear
🗑️  Conversation history cleared!

👤 You: quit
👋 Goodbye!
```

### **Interactive Commands**:

| Command | Action |
|---------|---------|
| `quit`, `exit`, `q` | Exit the program |
| `clear` | Clear conversation history |
| `switch` | Change to different model |
| Normal text | Send message to AI |

---

## ⚡ Single Command Execution

### **Purpose**: Execute one-off queries quickly

**Basic Usage**:
```bash
cd /Users/jeremy/crewAI/pipeline
source ../venv/bin/activate
python single_command.py "Your message here"
```

### **With Specific Model**:
```bash
python single_command.py "Your message here" model_name
```

### **Examples**:

**Auto-routing**:
```bash
python single_command.py "What's the weather like?"
```
Output:
```
🧠 Myndy AI Processing: What's the weather like?
🎯 Using model: auto
--------------------------------------------------
🤖 Response: 🤖 **Personal Assistant** (Myndy AI)
**Routing:** Selected Personal Assistant based on pattern matching (score: 3)
**Response:** I would help with weather information...
```

**Specific Agent**:
```bash
python single_command.py "Search for John Doe" memory_librarian
```
Output:
```
🧠 Myndy AI Processing: Search for John Doe
🎯 Using model: memory_librarian
--------------------------------------------------
🤖 Response: 🎯 **Memory Librarian** (Direct selection)
**Response:** I would search for John Doe in your contacts...
```

**Multiple Quick Commands**:
```bash
# Weather query
python single_command.py "Current weather in NYC"

# Contact search
python single_command.py "Find Sarah Chen" memory_librarian

# Financial query
python single_command.py "Track my expenses" finance_tracker

# Health query
python single_command.py "Analyze my sleep patterns" health_analyst

# Research query
python single_command.py "Research AI trends" research_specialist
```

---

## 📝 Batch Processing

### **Purpose**: Process multiple commands from files or interactively

**Interactive Mode**:
```bash
cd /Users/jeremy/crewAI/pipeline
source ../venv/bin/activate
python batch_processor.py
```

**From File**:
```bash
python batch_processor.py -i commands.txt -o results.json
```

### **Creating Command Files**:

**Example commands.txt**:
```
# Weather queries
What's the weather in San Francisco?
Check weather in New York
Temperature in London today

# Contact searches  
Do you know John Doe?
Find Sarah Chen's contact info
Search for contacts at Google

# Research requests
Research latest AI developments
Analyze current tech trends
Summarize blockchain news

# Financial queries
Track my spending this month
Budget analysis for Q4
Recent expense patterns
```

### **Running Batch Processing**:

**Step 1**: Create command file
```bash
cat > my_commands.txt << 'EOF'
What time is it?
Do you know Jeremy?
Research Python frameworks
Track my expenses
Check my health data
EOF
```

**Step 2**: Process commands
```bash
python batch_processor.py -i my_commands.txt -o my_results.json
```

**Sample Output**:
```
[1] Processing: What time is it?
✅ Response: 🤖 **Personal Assistant** (Myndy AI)...

[2] Processing: Do you know Jeremy?
✅ Response: 🤖 **Memory Librarian** (Myndy AI)...

[3] Processing: Research Python frameworks
✅ Response: 🤖 **Research Specialist** (Myndy AI)...

[4] Processing: Track my expenses
✅ Response: 🤖 **Finance Tracker** (Myndy AI)...

[5] Processing: Check my health data
✅ Response: 🤖 **Health Analyst** (Myndy AI)...

💾 Results saved to: my_results.json
🎉 Processed 5 commands
```

**Step 3**: View results
```bash
cat my_results.json | jq '.[] | {command: .command, success: .success}'
```

---

## 🔍 Real-Time Monitoring

### **Monitoring Server Performance**

**Terminal 1** (Start server with logs):
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python pipeline/server_with_logs.py
```

**Terminal 2** (Send test requests):
```bash
# Test basic functionality
curl -s http://localhost:9099/v1/models | jq '.data[].name'

# Test different agents
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Weather test"}]}' \
  | jq '.choices[0].message.content'

# Monitor specific agent
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"memory_librarian","messages":[{"role":"user","content":"Contact search test"}]}'
```

**Terminal 1 will show**:
```
📥 [15:30:15] INFO     __main__              | 📥 GET /v1/models from 127.0.0.1
📋 [15:30:15] INFO     __main__              | 📋 Models endpoint accessed
📤 [15:30:15] INFO     __main__              | 📤 ✅ 200 | 0.003s | /v1/models

📥 [15:30:20] INFO     __main__              | 📥 POST /v1/chat/completions from 127.0.0.1
💬 [15:30:20] INFO     __main__              | 💬 Processing chat request:
📋 [15:30:20] INFO     __main__              |    🎯 Model: auto
📋 [15:30:20] INFO     __main__              |    📝 Message: Weather test
⚡ [15:30:20] INFO     __main__              | ⚡ Pipeline processing completed in 0.095s
📤 [15:30:20] INFO     __main__              | 📤 ✅ 200 | 0.102s | /v1/chat/completions
```

### **Performance Testing**

**Load Testing Script**:
```bash
cat > test_load.sh << 'EOF'
#!/bin/bash
echo "🚀 Load testing Myndy AI pipeline..."
echo "Starting $(date)"

for i in {1..20}; do
  echo -n "Request $i: "
  start_time=$(date +%s.%N)
  
  response=$(curl -s -X POST http://localhost:9099/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"auto\",\"messages\":[{\"role\":\"user\",\"content\":\"Load test $i\"}]}")
  
  end_time=$(date +%s.%N)
  duration=$(echo "$end_time - $start_time" | bc)
  
  if echo "$response" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
    echo "✅ ${duration}s"
  else
    echo "❌ Failed"
  fi
  
  sleep 0.1
done

echo "Completed $(date)"
EOF

chmod +x test_load.sh
./test_load.sh
```

---

## 🔧 Advanced Usage

### **Environment Variables**

Set environment variables for customization:
```bash
export MYNDY_PATH="/Users/jeremy/myndy"
export PIPELINE_PORT="9099"
export LOG_LEVEL="DEBUG"
export PIPELINE_MODE="development"

python pipeline/server_with_logs.py
```

### **Custom Configuration**

Create custom pipeline config:
```bash
cat > pipeline_config.json << 'EOF'
{
  "server": {
    "host": "0.0.0.0",
    "port": 9099,
    "log_level": "INFO"
  },
  "pipeline": {
    "type": "enhanced",
    "myndy_path": "/Users/jeremy/myndy",
    "enable_caching": true,
    "enable_metrics": true
  },
  "agents": {
    "default_model": "auto",
    "timeout": 30,
    "max_retries": 3
  }
}
EOF

# Use config (if pipeline supports it)
python pipeline/server_with_logs.py --config pipeline_config.json
```

### **Logging to Files**

**Save all logs to file**:
```bash
python pipeline/server_with_logs.py 2>&1 | tee pipeline_$(date +%Y%m%d_%H%M%S).log
```

**Filter specific log types**:
```bash
# Only errors
python pipeline/server_with_logs.py 2>&1 | grep "❌\|🚨" | tee errors.log

# Only performance metrics
python pipeline/server_with_logs.py 2>&1 | grep "⚡\|⏱️" | tee performance.log

# Only chat interactions
python pipeline/server_with_logs.py 2>&1 | grep "💬" | tee conversations.log
```

### **Health Checking**

**Create health check script**:
```bash
cat > health_check.sh << 'EOF'
#!/bin/bash
echo "🏥 Myndy AI Pipeline Health Check"
echo "================================"

# Check if server is running
if curl -s http://localhost:9099/ > /dev/null; then
  echo "✅ Server: Running"
  
  # Check models endpoint
  models=$(curl -s http://localhost:9099/v1/models | jq '.data | length')
  echo "✅ Models: $models available"
  
  # Test chat endpoint
  response=$(curl -s -X POST http://localhost:9099/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"auto","messages":[{"role":"user","content":"health check"}]}')
  
  if echo "$response" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
    echo "✅ Chat: Working"
  else
    echo "❌ Chat: Failed"
  fi
  
  # Check response time
  start_time=$(date +%s.%N)
  curl -s http://localhost:9099/ > /dev/null
  end_time=$(date +%s.%N)
  response_time=$(echo "$end_time - $start_time" | bc)
  echo "⏱️  Response Time: ${response_time}s"
  
else
  echo "❌ Server: Not running"
  echo "💡 Start with: python pipeline/server_with_logs.py"
fi
EOF

chmod +x health_check.sh
./health_check.sh
```

---

## 📋 Examples

### **Example 1: Development Workflow**

**Start development server**:
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python pipeline/server_with_logs.py --log-level debug
```

**Test in another terminal**:
```bash
# Quick functionality test
python pipeline/single_command.py "Hello Myndy"

# Interactive testing
python pipeline/terminal_runner.py

# Batch testing
echo -e "Test 1\nTest 2\nTest 3" | python pipeline/batch_processor.py
```

### **Example 2: Production Monitoring**

**Start production server**:
```bash
python pipeline/server_with_logs.py --log-level info 2>&1 | tee production.log
```

**Monitor in real-time**:
```bash
# Watch error logs
tail -f production.log | grep "❌\|🚨"

# Monitor performance
tail -f production.log | grep "⚡" | while read line; do
  echo "$line" | grep -o "[0-9]\+\.[0-9]\+s"
done
```

### **Example 3: Testing All Agents**

**Create comprehensive test**:
```bash
cat > test_all_agents.txt << 'EOF'
# Test auto-routing
What's the weather in San Francisco?
Do you know John Doe?
Research AI trends
Track my expenses
Check my health data

# Test specific agents
Personal assistant: What time is it?
Memory librarian: Search for contacts
Research specialist: Analyze this topic
Health analyst: Review my fitness
Finance tracker: Show spending patterns
EOF

python pipeline/batch_processor.py -i test_all_agents.txt -o agent_test_results.json
```

### **Example 4: Performance Benchmarking**

**Benchmark script**:
```bash
cat > benchmark.sh << 'EOF'
#!/bin/bash
echo "🚀 Myndy AI Performance Benchmark"
echo "================================="

models=("auto" "memory_librarian" "personal_assistant" "research_specialist" "health_analyst" "finance_tracker")
requests_per_model=5

for model in "${models[@]}"; do
  echo "Testing model: $model"
  total_time=0
  
  for i in $(seq 1 $requests_per_model); do
    start_time=$(date +%s.%N)
    
    curl -s -X POST http://localhost:9099/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"Benchmark test $i\"}]}" > /dev/null
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    total_time=$(echo "$total_time + $duration" | bc)
    
    echo "  Request $i: ${duration}s"
  done
  
  avg_time=$(echo "scale=3; $total_time / $requests_per_model" | bc)
  echo "  Average: ${avg_time}s"
  echo
done
EOF

chmod +x benchmark.sh
./benchmark.sh
```

---

## 🎯 Quick Reference

### **Starting Servers**
```bash
# Enhanced logging (recommended)
python pipeline/server_with_logs.py

# Simple server  
python pipeline/simple_server.py

# Debug mode
python pipeline/server_with_logs.py --log-level debug

# Different port
python pipeline/server_with_logs.py --port 9100
```

### **Terminal Interfaces**
```bash
# Interactive chat
python pipeline/terminal_runner.py

# Single command
python pipeline/single_command.py "message"

# Batch processing
python pipeline/batch_processor.py -i input.txt -o output.json
```

### **Testing Commands**
```bash
# Health check
curl http://localhost:9099/

# List models
curl http://localhost:9099/v1/models

# Send chat message
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"test"}]}'
```

### **Monitoring**
```bash
# Save logs to file
python pipeline/server_with_logs.py 2>&1 | tee logs.txt

# Filter errors only
python pipeline/server_with_logs.py 2>&1 | grep "❌"

# Check if running
pgrep -f "server_with_logs.py"
```

---

**🎉 You're now equipped with comprehensive terminal interface capabilities for Myndy AI!**

Choose the interface that best fits your workflow - from real-time server monitoring to quick command execution to interactive conversations.