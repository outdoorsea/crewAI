# 🛠️ Dependency Installation Solutions

This guide provides multiple approaches to resolve the `ModuleNotFoundError: No module named 'fastapi'` error and get your Myndy AI pipeline running.

## 🚨 Problem Summary

You encountered:
```
File "/Users/jeremy/crewAI/pipeline/server_verbose.py", line 15, in <module>
    from fastapi import FastAPI
ModuleNotFoundError: No module named 'fastapi'
```

**Root Cause**: The virtual environment had broken paths pointing to the old "myndy" directory.

## ✅ Solution 1: Simple Server (Working Now!)

**Status**: ✅ **WORKING** - Server is running on `http://localhost:9099`

```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python pipeline/simple_server.py
```

**Features**:
- ✅ Basic FastAPI server with OpenWebUI compatibility
- ✅ 6 available models (Auto + 5 agents)
- ✅ Simple keyword-based routing
- ✅ Lightweight - no heavy ML dependencies required
- ✅ Works immediately with existing setup

**Test it**:
```bash
curl http://localhost:9099/v1/models
```

## 🚀 Solution 2: Full Installation (Recommended)

For complete functionality, install all dependencies:

### Step 1: Install Core Dependencies
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
pip install crewai langchain
```

### Step 2: Install Optional Heavy Dependencies (one at a time)
```bash
# Vector search (optional)
pip install qdrant-client

# Advanced text processing (optional)
pip install sentence-transformers

# Additional tools (optional)
pip install torch scikit-learn scipy
```

### Step 3: Run Full Server
```bash
python -m uvicorn server:app --host 0.0.0.0 --port 9099
```

## 🐳 Solution 3: Docker (Isolated Environment)

Avoid dependency conflicts completely:

### Create Dockerfile
```dockerfile
# In /Users/jeremy/crewAI/pipeline/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 9099

CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9099"]
```

### Build and Run
```bash
cd /Users/jeremy/crewAI/pipeline
docker build -t myndy-pipeline .
docker run -d -p 9099:9099 myndy-pipeline
```

## 🎯 Solution 4: Progressive Installation

Install dependencies gradually as needed:

### Phase 1: Basic Web Server (✅ Done)
```bash
pip install fastapi uvicorn pydantic
```

### Phase 2: Add CrewAI
```bash
pip install crewai
```

### Phase 3: Add Vector Search
```bash
pip install qdrant-client
```

### Phase 4: Add ML Capabilities
```bash
pip install sentence-transformers torch
```

## 🔧 Quick Start Commands

### Option A: Use Simple Server (Working Now)
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python pipeline/simple_server.py
```
**Then add `http://localhost:9099` to OpenWebUI pipelines**

### Option B: Install Full Dependencies
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
pip install crewai langchain sentence-transformers qdrant-client
python -m uvicorn server:app --port 9099
```

### Option C: Terminal Interface (No Web Server)
```bash
cd /Users/jeremy/crewAI/pipeline
source ../venv/bin/activate
python terminal_runner.py
```

## 🧪 Test Your Installation

### Test 1: Basic Server
```bash
curl http://localhost:9099/v1/models
```

### Test 2: Chat Request
```bash
curl -X POST http://localhost:9099/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Hello Myndy"}]
  }'
```

### Test 3: Import Test
```bash
cd /Users/jeremy/crewAI
source venv/bin/activate
python -c "from crewai_myndy_pipeline import Pipeline; print('✅ Full pipeline works')"
```

## 🐛 Troubleshooting

### Issue: Virtual Environment Broken
**Solution**: Created fresh venv in `/Users/jeremy/crewAI/venv`

### Issue: Heavy Dependencies Fail
**Solution**: Use `simple_server.py` which works without ML libraries

### Issue: Port Already in Use
**Solution**: Use different port: `--port 9100`

### Issue: Import Errors
**Solution**: Check paths and ensure Myndy is at `/Users/jeremy/myndy`

## 📊 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| ✅ Simple Server | Working | Running on port 9099 |
| ✅ FastAPI | Installed | Core web framework |
| ✅ Virtual Environment | Fixed | Clean `/Users/jeremy/crewAI/venv` |
| ⏳ Full Pipeline | Pending | Requires CrewAI installation |
| ⏳ ML Dependencies | Optional | For advanced features |

## 🎉 Next Steps

1. **Immediate Use**: The simple server is running and ready to use with OpenWebUI
2. **Add to OpenWebUI**: Go to Admin Settings > Pipelines, add `http://localhost:9099`
3. **Test Basic Functionality**: Try asking questions to see routing in action
4. **Upgrade Gradually**: Install additional dependencies as needed

## 💡 Pro Tips

- **Start Simple**: Use the working simple server, then upgrade
- **Install Incrementally**: Add dependencies one at a time to isolate issues
- **Use Docker**: For production, containerize to avoid dependency conflicts
- **Monitor Resources**: ML dependencies are resource-intensive
- **Keep Simple Server**: Always have a fallback option

---

**🚀 Your Myndy AI pipeline is now running and ready to use!**