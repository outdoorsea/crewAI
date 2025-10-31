# 🚀 Myndy AI Pipeline - OpenWebUI Integration

## ✅ Pipeline Setup Complete

Your Myndy AI pipeline is now ready for OpenWebUI integration with enhanced terminal logging!

## 📋 Integration Options

### Option 1: Direct Pipeline Upload (Recommended ✅)
1. **Enhanced Pipeline with Logging** - Use the full-featured pipeline:
   ```bash
   cp /Users/jeremy/crewAI/pipeline/server_with_logs.py ~/your-openwebui-pipelines/myndy_ai_pipeline.py
   ```

2. **Simple Pipeline** - For basic functionality:
   ```bash
   cp /Users/jeremy/crewAI/pipeline/openwebui_server.py ~/your-openwebui-pipelines/myndy_simple_pipeline.py
   ```

3. In OpenWebUI Admin Panel:
   - Go to **Admin Panel** → **Pipelines** 
   - Click **"Add Pipeline"**
   - Upload either `server_with_logs.py` (recommended) or `openwebui_server.py`
   - The pipeline will be automatically detected with proper OpenWebUI signature

   **To test pipeline class mode locally:**
   ```bash
   python server_with_logs.py --pipeline
   ```

### Option 2: Server-based Integration (Default)
1. **Main Pipeline Server**:
   ```bash
   cd /Users/jeremy/crewAI/pipeline
   python server_with_logs.py
   ```
   *Available at: http://localhost:9099*

2. **Beta Pipeline Server** (Enhanced Performance):
   ```bash
   cd /Users/jeremy/crewAI/pipeline
   python myndy_ai_beta.py --server
   ```
   *Available at: http://localhost:9098*

3. In OpenWebUI:
   - Go to **Admin Panel** → **Pipelines**
   - Add pipeline URL: `http://localhost:9099` (main) or `http://localhost:9098` (beta)
   - Both servers can run simultaneously for A/B testing

## 🎯 Available Models

Once integrated, you'll see these models in OpenWebUI:

**Main Pipeline (port 9099):**
- **🧠 Myndy AI v0.1** (auto-routing) - Automatically selects the best agent
- **🎯 Memory Librarian** - Contact management, entity tracking, conversation analysis
- **🎯 Research Specialist** - Text analysis, document processing, research
- **🎯 Personal Assistant** - Scheduling, weather, time management, productivity
- **🎯 Health Analyst** - Health data analysis, wellness insights
- **🎯 Finance Tracker** - Expense tracking, budget analysis

**Beta Pipeline (port 9098):**
- **🚀 Myndy AI Beta (Enhanced)** (auto_beta) - Enhanced intelligent routing with learning
- **⚡ Memory Librarian Pro** - Enhanced contact management with relationship mapping
- **⚡ Research Specialist Plus** - Advanced research with multi-source verification
- **⚡ Personal Assistant Pro** - Optimized personal productivity with predictive scheduling
- **⚡ Health Analyst Plus** - Enhanced health analytics with predictive insights
- **⚡ Finance Tracker Pro** - Smart financial tracking with budget optimization

## 📊 Enhanced Pipeline Features

### ✨ OpenWebUI-Compatible Structure
- **Proper Pipeline Class**: Follows OpenWebUI pipeline specification exactly
- **Valves Configuration**: User-configurable settings in OpenWebUI interface
- **Manifold Type**: Allows model selection within OpenWebUI
- **Lifecycle Methods**: Proper startup/shutdown handling

### 🔧 Configurable Valves
Access these settings through OpenWebUI's pipeline configuration:
- **Enhanced Logging**: Toggle detailed terminal output
- **Intelligent Routing**: Enable/disable smart agent selection
- **Tool Execution**: Control tool usage by agents
- **Debug Mode**: Additional troubleshooting information

### 📊 Terminal Logging Features
When running, you'll see detailed logs in your terminal:
- 🎯 **Pipeline calls** with routing decisions
- 🧠 **Intelligent agent selection** with reasoning
- 🤖 **Agent execution** progress
- ⚙️ **Tool usage** and results
- 💬 **Session tracking** and conversation history
- ✅ **Success indicators** and error handling
- 🔧 **Valve updates** when configuration changes

### 🚀 Beta Pipeline Features
The beta pipeline (`myndy_ai_beta.py`) includes enhanced capabilities:
- **🧠 Enhanced Routing**: Machine learning-like scoring with pattern weighting
- **📈 Learning Component**: Tracks successful routes and applies feedback
- **⚡ Performance Optimization**: Target response times (Memory < 3s, Assistant < 2s)
- **🎯 Priority Multipliers**: Boost for specific agent types based on query patterns
- **💬 Interactive Mode**: Direct chat interface when run without `--server`
- **🔄 A/B Testing**: Run alongside main pipeline for performance comparison

## 🔧 Troubleshooting

### ✅ Fixed: Server Auto-Shutdown Issue
**Issue:** Server automatically shutting down due to port conflicts
**Solution:** Enhanced port handling with automatic process cleanup:
- **Smart Port Management**: Automatically detects port conflicts (errno 48: address already in use)
- **Process Cleanup**: On first conflict, attempts to kill existing processes using the port
- **Fallback Ports**: If cleanup fails, automatically tries next available port (9099 → 9100 → 9101)
- **Clean Shutdown**: Uses SIGTERM for graceful process termination with 1-second wait
- **Clear Messaging**: Provides detailed feedback about what's happening

**How it works:**
1. **First attempt**: Try to start on preferred port (9099 for main, 9098 for beta)
2. **On conflict**: Automatically find and kill existing processes on that port
3. **Retry**: Attempt to start again on the same port after cleanup
4. **Fallback**: If still conflicts, try next available port
5. **Limit**: Maximum 3 attempts with clear error messages

**Manual cleanup (if needed):**
```bash
# Stop existing pipeline servers
pkill -f 'server_with_logs.py'
pkill -f 'myndy_ai_beta.py'

# Start fresh
python server_with_logs.py          # Main pipeline
python myndy_ai_beta.py --server    # Beta pipeline
```

### ✅ Fixed: Missing OpenWebUI Endpoints
**Issue:** OpenWebUI requesting endpoints that didn't exist
**Solution:** Added complete OpenWebUI API compatibility:
- `POST /openai/verify` - Primary OpenWebUI verification endpoint
- `POST /verify` - Alternative verification endpoint
- `GET /api/v1/pipelines/list` - Pipeline discovery endpoint for OpenWebUI
- All endpoints return proper OpenWebUI-compatible responses

### Pipeline Not Detected
- ✅ **Fixed**: Proper OpenWebUI Pipeline class structure implemented
- ✅ **Fixed**: Correct `pipe()` method signature matching OpenWebUI requirements
- ✅ **Fixed**: Verification endpoints added for connection testing

### Connection Issues
- **Check server status**: Ensure pipeline server is running on correct port
- **Test endpoints manually**:
  ```bash
  curl -X POST http://localhost:9099/openai/verify -H "Content-Type: application/json" -d '{}'
  ```
- **Check logs**: Server provides detailed logging for all requests

### Agent Not Responding
- Check terminal logs for error messages
- Ensure Ollama models are running (llama3.2, mixtral, phi3)
- Verify qdrant service is running

### Tools Not Working
- Check that `/Users/jeremy/myndy-ai` path is correct
- Verify tool repository exists and is accessible
- Review bridge configuration in logs

## 📝 Log Files

- **Terminal logs**: Real-time in console
- **Pipeline logs**: `/tmp/myndy_pipeline.log`
- **OpenWebUI logs**: `/tmp/myndy_openwebui_pipeline.log`

## 🎉 Ready to Use!

Your Myndy AI pipeline is now integrated with comprehensive terminal logging. Enjoy chatting with your personal AI assistant!