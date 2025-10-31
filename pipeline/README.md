# CrewAI-Myndy Pipeline for OpenWebUI

This pipeline provides intelligent agent routing and myndy tool execution for OpenWebUI. It analyzes conversations and automatically selects the appropriate agent to handle each request.

## 🎯 Features

### 🤖 Intelligent Agent Routing
- **Auto model**: Automatically selects the best agent based on conversation analysis
- **5 Specialized Agents**: Memory Librarian, Research Specialist, Personal Assistant, Health Analyst, Finance Tracker
- **Context Awareness**: Maintains conversation history for better routing decisions

### 🔧 Contact Management
- **Search Contacts**: Find people and their information
- **Update Information**: Natural language updates like "Update John works for Google"
- **Company Tracking**: Track where people work and their roles

### 🧠 Memory Integration
- **Knowledge Search**: Search your personal knowledge base
- **Entity Recognition**: Find people, places, and relationships
- **Conversation History**: Access past conversations and context

## 🚀 Installation

### Option 1: Docker (Recommended)

1. **Build the pipeline container:**
```bash
cd /Users/jeremy/crewAI/pipeline
docker build -t crewai-myndy-pipeline .
```

2. **Run the pipeline:**
```bash
docker run -d -p 9099:9099 \
  -v /Users/jeremy/myndy:/myndy:ro \
  crewai-myndy-pipeline
```

3. **Configure in OpenWebUI:**
   - Go to **Admin Settings > Pipelines**
   - Add pipeline URL: `http://localhost:9099`
   - The pipeline will appear as available models

### Option 2: Manual Setup

1. **Install dependencies:**
```bash
cd /Users/jeremy/crewAI/pipeline
pip install -r requirements.txt
```

2. **Start the pipeline server:**
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 9099
```

3. **Configure in OpenWebUI:**
   - Add pipeline URL: `http://localhost:9099`

## 🎮 Usage

### Available Models

| Model | Description | Best For |
|-------|-------------|----------|
| **🤖 Auto (Intelligent Routing)** | Automatically selects the best agent | Most conversations |
| **🎯 Memory Librarian** | Knowledge and contact management | "Do you know John?", "Update contact info" |
| **🎯 Research Specialist** | Information gathering and analysis | "Research AI trends", "Find information about..." |
| **🎯 Personal Assistant** | Productivity and scheduling | "Schedule meeting", "Manage tasks" |
| **🎯 Health Analyst** | Health and wellness tracking | "Analyze my fitness", "Track sleep patterns" |
| **🎯 Finance Tracker** | Financial analysis and budgeting | "Track expenses", "Budget analysis" |

### Example Conversations

#### Contact Management
```
User: "Do you know Bryan Roth?"
Memory Librarian: 📧 Contacts Found:
• 👤 Bryan Roth | 🏢 OpenAI | 💼 Engineer | 📧 bryan@openai.com

User: "Update Bryan Roth works for Anthropic"
Memory Librarian: ✅ Updated Bryan Roth's company to Anthropic
Contact updated successfully in memory.
```

#### Intelligent Routing
```
User: "Help me track my spending this month"
🤖 Finance Tracker (Auto-selected)
Routing: Selected Finance Tracker | Keywords: track, spending | Confidence: 0.75

💰 Financial analysis tools ready. I can track and analyze your expenses...
```

## ⚙️ Configuration

The pipeline includes configurable valves:

- **enable_intelligent_routing**: Enable/disable auto-routing (default: true)
- **enable_tool_execution**: Enable/disable tool execution (default: true)  
- **enable_contact_management**: Enable/disable contact features (default: true)
- **enable_memory_search**: Enable/disable memory search (default: true)
- **debug_mode**: Enable debug logging (default: false)
- **myndy_path**: Path to myndy installation (default: "/Users/jeremy/myndy")

## 🔧 Architecture

```
OpenWebUI Frontend
       ↓
Pipeline Interface (port 9099)
       ↓
Agent Router (analyzes message)
       ↓
Selected Agent (executes tools)
       ↓
Myndy Tools (search/update data)
       ↓
Response Generation
```

## 🎁 Benefits Over API Server

- **Native Integration**: Built specifically for OpenWebUI pipelines
- **Better UX**: Models appear naturally in the interface
- **Simpler Deployment**: Single pipeline deployment
- **Enhanced Features**: Access to OpenWebUI pipeline capabilities
- **Cleaner Architecture**: Purpose-built for this use case

## 🔍 Troubleshooting

### Pipeline not appearing in OpenWebUI
- Check pipeline server is running on port 9099
- Verify OpenWebUI can reach the pipeline URL
- Check OpenWebUI logs for connection errors

### Tool execution errors
- Ensure myndy is properly installed and accessible
- Check that Qdrant is running (if using vector search)
- Verify Python path includes both crewai and myndy directories

### Contact updates not working
- Ensure myndy database is writable
- Check that contact collections are properly initialized
- Verify natural language parsing is extracting names correctly

## 🚀 Ready to Use!

The CrewAI-Myndy pipeline brings intelligent agent routing and powerful contact management directly into your OpenWebUI interface. Simply select the "Auto" model and let the system choose the perfect agent for each conversation!