# 🖥️ Pipeline Server Real-Time Logging Guide

Complete guide for running Myndy AI pipeline servers with detailed, real-time logging capabilities.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Server Options](#server-options)
- [Log Levels & Formats](#log-levels--formats)
- [Enhanced Logging Features](#enhanced-logging-features)
- [Real-Time Monitoring](#real-time-monitoring)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

---

## 🚀 Quick Start

### **Recommended: Enhanced Logging Server**
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python pipeline/server_with_logs.py
```

**Result**: Colorful, detailed logs with emojis and timing information.

### **Basic: Simple Server**
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python pipeline/simple_server.py
```

**Result**: Standard logs with basic request information.

---

## 🔧 Server Options

### **Option 1: Enhanced Logging Server** ⭐ **Recommended**

**File**: `server_with_logs.py`

**Features**:
- 🎨 **Colored logs** with emoji indicators
- ⏱️ **Request timing** and performance metrics
- 📊 **Pipeline routing** decisions logged
- 🔍 **Detailed error tracking** with full tracebacks
- 💬 **Chat request analysis** (model, message preview, token counts)

**Command**:
```bash
python pipeline/server_with_logs.py
```

**Sample Output**:
```
🚀 Starting Myndy AI Pipeline with Enhanced Logging
============================================================
📊 Pipeline Type: Simple
🖥️  Real-time logs will appear below...
🌐 Server will be available at: http://localhost:9099
🔗 Add to OpenWebUI: http://localhost:9099
⏹️  Press Ctrl+C to stop
============================================================

🚀 [14:32:15] INFO     __main__              | 🚀 Myndy AI Pipeline server starting up...
📊 [14:32:15] INFO     __main__              | 📊 Pipeline type: simple
🎯 [14:32:15] INFO     __main__              | 🎯 Available models: 6
📋 [14:32:15] INFO     uvicorn               | Uvicorn running on http://0.0.0.0:9099
```

### **Option 2: Simple Server**

**File**: `simple_server.py`

**Features**:
- 📝 **Basic request logging**
- 🔧 **Lightweight** (minimal dependencies)
- ⚡ **Fast startup**

**Command**:
```bash
python pipeline/simple_server.py
```

### **Option 3: Uvicorn with Custom Log Levels**

**Debug Level** (Most Verbose):
```bash
python -m uvicorn pipeline.server_with_logs:app --host 0.0.0.0 --port 9099 --log-level debug
```

**Trace Level** (Everything):
```bash
python -m uvicorn pipeline.server_with_logs:app --host 0.0.0.0 --port 9099 --log-level trace
```

**Info Level** (Standard):
```bash
python -m uvicorn pipeline.server_with_logs:app --host 0.0.0.0 --port 9099 --log-level info
```

### **Option 4: Full Pipeline Server** (Requires All Dependencies)

```bash
python -m uvicorn pipeline.server:app --host 0.0.0.0 --port 9099 --log-level info --reload
```

**Note**: Requires `crewai`, `langchain`, and other ML dependencies installed.

### **Option 5: Production Mode**

```bash
python -m uvicorn pipeline.server_with_logs:app --host 0.0.0.0 --port 9099 --workers 4
```

---

## 📊 Log Levels & Formats

### **Log Levels (Most to Least Verbose)**

| Level | Description | Use Case |
|-------|-------------|----------|
| `TRACE` | Everything including internals | Deep debugging |
| `DEBUG` | Detailed application flow | Development |
| `INFO` | General information | Production monitoring |
| `WARNING` | Potential issues | Problem identification |
| `ERROR` | Actual errors | Error tracking |
| `CRITICAL` | System failures | Emergency response |

### **Enhanced Log Format**

```
🎨 [HH:MM:SS] LEVEL     logger_name           | 📝 message content
```

**Components**:
- **🎨 Emoji**: Visual indicator for log level
- **[HH:MM:SS]**: Precise timestamp
- **LEVEL**: Log level (INFO, DEBUG, etc.)
- **logger_name**: Source component
- **📝 message**: Actual log message with context emoji

### **Log Categories with Emojis**

| Category | Emoji | Description |
|----------|-------|-------------|
| Startup | 🚀 | Server initialization |
| Requests | 📥📤 | HTTP request/response |
| Pipeline | 🎯⚡ | AI processing |
| Models | 📊 | Model operations |
| Chat | 💬 | Conversation handling |
| Errors | ❌🚨 | Error conditions |
| Debug | 🔍 | Debugging information |
| Performance | ⏱️ | Timing metrics |

---

## 🎨 Enhanced Logging Features

### **Request Tracking**

Every HTTP request is logged with:
```
📥 [14:32:30] INFO     __main__              | 📥 POST /v1/chat/completions from 127.0.0.1
💬 [14:32:30] INFO     __main__              | 💬 Processing chat request:
📋 [14:32:30] INFO     __main__              |    🎯 Model: auto
📋 [14:32:30] INFO     __main__              |    📝 Message: Hello Myndy, what's the weather?
📋 [14:32:30] INFO     __main__              |    📊 Message count: 1
⚡ [14:32:30] INFO     __main__              | ⚡ Pipeline processing completed in 0.152s
📤 [14:32:30] INFO     __main__              | 📤 Response length: 245 characters
📤 [14:32:30] INFO     __main__              | 📤 ✅ 200 | 0.158s | /v1/chat/completions
```

### **Performance Metrics**

- **⏱️ Request Duration**: Time from request to response
- **⚡ Pipeline Processing**: Time spent in AI processing
- **📊 Token Counts**: Input/output token usage
- **📤 Response Size**: Character count of responses

### **Error Tracking**

Detailed error information:
```
❌ [14:35:12] ERROR    __main__              | ❌ Error processing chat request: Invalid model specified
📋 [14:35:12] ERROR    __main__              | 📋 Request data: {"model": "invalid", "messages": [...]}
🔍 [14:35:12] ERROR    __main__              | 🔍 Traceback: 
    File "server_with_logs.py", line 123, in chat_completions
    ...
```

### **Pipeline Intelligence**

For full pipeline servers:
```
🎯 [14:33:45] INFO     pipeline              | 🎯 Agent routing for message: "What's the weather?"
📊 [14:33:45] INFO     pipeline              | 📊 Keyword analysis: weather=1, time=0, contact=0
🎯 [14:33:45] INFO     pipeline              | 🎯 Selected agent: personal_assistant (confidence: 0.9)
🔧 [14:33:45] INFO     agent                 | 🔧 Loading tools for personal_assistant
⚡ [14:33:45] INFO     agent                 | ⚡ Executing task with weather tools
```

---

## 🔍 Real-Time Monitoring

### **Terminal Commands for Testing**

While server is running, test in another terminal:

**Test Models Endpoint**:
```bash
curl -s http://localhost:9099/v1/models | jq '.data[] | .name'
```

**Test Chat Endpoint**:
```bash
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Hello Myndy!"}]
  }' | jq '.choices[0].message.content'
```

**Test Different Models**:
```bash
# Memory Librarian
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "memory_librarian",
    "messages": [{"role": "user", "content": "Do you know John Doe?"}]
  }'

# Personal Assistant
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "personal_assistant", 
    "messages": [{"role": "user", "content": "What time is it?"}]
  }'
```

### **Monitoring Performance**

Watch for these metrics in logs:
- **Response times** < 1 second for simple requests
- **Pipeline processing** times
- **Error rates** (should be minimal)
- **Model selection** accuracy

### **Log Filtering**

Filter logs by category:
```bash
# Only show errors
python pipeline/server_with_logs.py 2>&1 | grep "❌\|🚨"

# Only show performance metrics
python pipeline/server_with_logs.py 2>&1 | grep "⚡\|⏱️"

# Only show chat requests
python pipeline/server_with_logs.py 2>&1 | grep "💬"
```

---

## 🛠️ Troubleshooting

### **Common Issues and Solutions**

#### **Issue: No logs appearing**
**Solution**: Check log level and ensure proper terminal output
```bash
python pipeline/server_with_logs.py --log-level debug
```

#### **Issue: Logs too verbose**
**Solution**: Increase log level
```bash
python pipeline/server_with_logs.py --log-level warning
```

#### **Issue: Missing colors/emojis**
**Cause**: Terminal doesn't support ANSI colors
**Solution**: Use basic server or update terminal
```bash
python pipeline/simple_server.py
```

#### **Issue: Server won't start**
**Solution**: Check port availability
```bash
# Check if port is in use
lsof -i :9099

# Use different port
python pipeline/server_with_logs.py --port 9100
```

### **Debug Mode**

Enable maximum logging detail:
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
PYTHONPATH=/Users/jeremy/crewAI:/Users/jeremy/myndy python pipeline/server_with_logs.py --log-level trace
```

### **Log File Output**

Save logs to file while viewing in terminal:
```bash
python pipeline/server_with_logs.py 2>&1 | tee pipeline_logs.txt
```

---

## 📝 Examples

### **Example 1: Basic Monitoring**

**Terminal 1** (Start server):
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python pipeline/server_with_logs.py
```

**Terminal 2** (Send test request):
```bash
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Test message"}]
  }'
```

**Expected Logs**:
```
📥 [15:30:15] INFO     __main__              | 📥 POST /v1/chat/completions from 127.0.0.1
💬 [15:30:15] INFO     __main__              | 💬 Processing chat request:
📋 [15:30:15] INFO     __main__              |    🎯 Model: auto
📋 [15:30:15] INFO     __main__              |    📝 Message: Test message
⚡ [15:30:15] INFO     __main__              | ⚡ Pipeline processing completed in 0.095s
📤 [15:30:15] INFO     __main__              | 📤 ✅ 200 | 0.102s | /v1/chat/completions
```

### **Example 2: OpenWebUI Integration Monitoring**

1. **Start server with logs**:
```bash
python pipeline/server_with_logs.py
```

2. **Add to OpenWebUI**: `http://localhost:9099`

3. **Monitor logs** as you chat in OpenWebUI interface

4. **Watch for**:
   - Model selection decisions
   - Response times
   - Any errors or warnings

### **Example 3: Performance Testing**

**Load Testing Script**:
```bash
# Create test script
cat > test_performance.sh << 'EOF'
#!/bin/bash
echo "🚀 Testing pipeline performance..."
for i in {1..10}; do
  echo "Request $i:"
  time curl -s -X POST http://localhost:9099/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"auto\",\"messages\":[{\"role\":\"user\",\"content\":\"Test $i\"}]}" \
    > /dev/null
done
EOF

chmod +x test_performance.sh
./test_performance.sh
```

**Monitor logs** for performance patterns and bottlenecks.

### **Example 4: Error Simulation**

Test error handling:
```bash
# Invalid model
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"invalid_model","messages":[{"role":"user","content":"test"}]}'

# Malformed request
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"invalid":"json"}'
```

**Watch logs** for error handling and recovery.

---

## 🎯 Best Practices

### **Development**
- Use **enhanced logging server** for development
- Set log level to **DEBUG** for detailed information
- Monitor **performance metrics** regularly

### **Production**
- Use **INFO** log level for production
- Implement **log rotation** for long-running servers
- Monitor **error rates** and **response times**

### **Debugging**
- Use **TRACE** level for complex issues
- Enable **error tracking** with full stack traces
- Test with **curl commands** for isolated debugging

---

## 🚀 Quick Reference

### **Start Commands**
```bash
# Enhanced logging (recommended)
python pipeline/server_with_logs.py

# Simple logging
python pipeline/simple_server.py

# Debug mode
python pipeline/server_with_logs.py --log-level debug

# Different port
python pipeline/server_with_logs.py --port 9100
```

### **Test Commands**
```bash
# Test models
curl http://localhost:9099/v1/models

# Test chat
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"test"}]}'
```

### **Monitoring Commands**
```bash
# Filter errors only
python pipeline/server_with_logs.py 2>&1 | grep "❌"

# Save logs to file
python pipeline/server_with_logs.py 2>&1 | tee logs.txt

# Check if running
curl -s http://localhost:9099/ | jq '.status'
```

---

**🎉 You're now ready to run Myndy AI pipeline servers with comprehensive, real-time logging!**

The enhanced logging system provides complete visibility into your pipeline's operation, making development, debugging, and monitoring much easier.