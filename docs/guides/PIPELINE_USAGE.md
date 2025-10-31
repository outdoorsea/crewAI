# 🚀 Myndy AI Pipeline Usage Guide

This guide covers all the ways to run and use the Myndy AI pipelines with CrewAI.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Pipeline Options](#pipeline-options)
- [Running in OpenWebUI](#running-in-openwebui)
- [Running in Terminal](#running-in-terminal)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

---

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- OpenWebUI (optional, for web interface)
- Docker (optional, for containerized deployment)

### Install Dependencies
```bash
cd /Users/jeremy/crewAI/pipeline
pip install -r requirements.txt
```

**Required packages:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `sentence-transformers` - Text embeddings
- `qdrant-client` - Vector database client
- `langchain` - LLM framework
- `crewai` - Multi-agent framework

### Verify Myndy Installation
Ensure Myndy is installed at:
```bash
ls /Users/jeremy/myndy
```

---

## 🔧 Pipeline Options

### **Pipeline 1: Main Myndy AI Pipeline** (Recommended)
- **File**: `crewai_myndy_pipeline.py`
- **Features**: Full intelligent routing, 5 specialized agents
- **Best for**: Production use, complex conversations

### **Pipeline 2: Alternative Pipeline**
- **File**: `crewai_myndy_pipeline_proper.py` 
- **Features**: Streamlined version, basic routing
- **Best for**: Simple use cases, testing

---

## 🌐 Running in OpenWebUI

### Option 1: FastAPI Server (Recommended)
```bash
cd /Users/jeremy/crewAI/pipeline
python -m uvicorn server:app --host 0.0.0.0 --port 9099
```

### Option 2: Direct Integration
```bash
cd /Users/jeremy/crewAI/pipeline
python -m uvicorn main:app --host 0.0.0.0 --port 9099
```

### Option 3: Python Server Script
```bash
cd /Users/jeremy/crewAI/pipeline
python server.py
```

### Configure in OpenWebUI
1. Open **Admin Settings > Pipelines**
2. Add pipeline URL: `http://localhost:9099`
3. Available models will appear:
   - 🧠 **Myndy AI v0.1** (Auto-routing)
   - 🎯 **Memory Librarian**
   - 🎯 **Research Specialist**
   - 🎯 **Personal Assistant**
   - 🎯 **Health Analyst**
   - 🎯 **Finance Tracker**

---

## 💻 Running in Terminal

### Option 1: Interactive Python Shell

Create a terminal interface script:

```bash
# Create the terminal runner
cat > /Users/jeremy/crewAI/pipeline/terminal_runner.py << 'EOF'
#!/usr/bin/env python3
"""
Terminal interface for Myndy AI Pipeline
Run conversations directly from the command line
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, "/Users/jeremy/myndy")

from crewai_myndy_pipeline import Pipeline

class TerminalMyndyAI:
    def __init__(self):
        """Initialize the terminal interface"""
        self.pipeline = Pipeline()
        self.session_messages = []
        print("🧠 Myndy AI Terminal Interface")
        print("=" * 50)
        print("Available models:")
        models = self.pipeline.get_models()
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model['name']}")
        print()
    
    def select_model(self):
        """Let user select a model"""
        models = self.pipeline.get_models()
        while True:
            try:
                choice = input("Select model (1-6, or 'auto' for intelligent routing): ").strip().lower()
                
                if choice == 'auto' or choice == '1':
                    return 'auto'
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(models):
                        return models[idx]['id']
                
                print("❌ Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)
    
    def run_conversation(self):
        """Run an interactive conversation"""
        model_id = self.select_model()
        model_name = next((m['name'] for m in self.pipeline.get_models() if m['id'] == model_id), model_id)
        
        print(f"\n🎯 Using: {model_name}")
        print("💬 Start chatting! (Type 'quit' to exit, 'clear' to clear history, 'switch' to change model)")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    self.session_messages = []
                    print("🗑️  Conversation history cleared!")
                    continue
                elif user_input.lower() == 'switch':
                    model_id = self.select_model()
                    model_name = next((m['name'] for m in self.pipeline.get_models() if m['id'] == model_id), model_id)
                    print(f"🎯 Switched to: {model_name}")
                    continue
                elif not user_input:
                    continue
                
                # Add user message to history
                self.session_messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Process with pipeline
                print("🤔 Thinking...")
                
                try:
                    response = self.pipeline.pipe(
                        user_message=user_input,
                        model_id=model_id,
                        messages=self.session_messages,
                        body={}
                    )
                    
                    # Add response to history
                    self.session_messages.append({
                        "role": "assistant", 
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    print(f"🤖 Myndy: {response}")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

def main():
    """Main function"""
    try:
        terminal_ai = TerminalMyndyAI()
        terminal_ai.run_conversation()
    except Exception as e:
        print(f"❌ Failed to start Myndy AI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Make it executable
chmod +x /Users/jeremy/crewAI/pipeline/terminal_runner.py
```

**Run the terminal interface:**
```bash
cd /Users/jeremy/crewAI/pipeline
python terminal_runner.py
```

### Option 2: Single Command Execution

Create a script for one-off commands:

```bash
# Create single command runner
cat > /Users/jeremy/crewAI/pipeline/single_command.py << 'EOF'
#!/usr/bin/env python3
"""
Single command runner for Myndy AI
Usage: python single_command.py "Your message here" [model_id]
"""

import sys
import json
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, "/Users/jeremy/myndy")

from crewai_myndy_pipeline import Pipeline

def run_single_command(message, model_id="auto"):
    """Run a single command"""
    try:
        pipeline = Pipeline()
        
        # Create mock message history
        messages = [{"role": "user", "content": message}]
        
        # Process the message
        response = pipeline.pipe(
            user_message=message,
            model_id=model_id,
            messages=messages,
            body={}
        )
        
        return response
    except Exception as e:
        return f"Error: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python single_command.py \"Your message here\" [model_id]")
        print("Example: python single_command.py \"What's the weather like?\"")
        print("Example: python single_command.py \"Search for John Doe\" memory_librarian")
        sys.exit(1)
    
    message = sys.argv[1]
    model_id = sys.argv[2] if len(sys.argv) > 2 else "auto"
    
    print(f"🧠 Myndy AI Processing: {message}")
    print(f"🎯 Using model: {model_id}")
    print("-" * 50)
    
    response = run_single_command(message, model_id)
    print(f"🤖 Response: {response}")

if __name__ == "__main__":
    main()
EOF

chmod +x /Users/jeremy/crewAI/pipeline/single_command.py
```

**Usage examples:**
```bash
cd /Users/jeremy/crewAI/pipeline

# Auto-select agent
python single_command.py "What's the weather in San Francisco?"

# Use specific agent
python single_command.py "Search for John Doe" memory_librarian

# Financial query
python single_command.py "Track my expenses" finance_tracker
```

### Option 3: Batch Processing

Create a script for processing multiple commands:

```bash
# Create batch processor
cat > /Users/jeremy/crewAI/pipeline/batch_processor.py << 'EOF'
#!/usr/bin/env python3
"""
Batch processor for Myndy AI
Processes commands from a file or stdin
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, "/Users/jeremy/myndy")

from crewai_myndy_pipeline import Pipeline

def process_batch(commands_file=None, output_file=None):
    """Process batch commands"""
    pipeline = Pipeline()
    results = []
    
    # Read commands
    if commands_file:
        with open(commands_file, 'r') as f:
            commands = f.readlines()
    else:
        print("Enter commands (one per line, empty line to finish):")
        commands = []
        while True:
            cmd = input("Command: ").strip()
            if not cmd:
                break
            commands.append(cmd)
    
    # Process each command
    for i, command in enumerate(commands, 1):
        command = command.strip()
        if not command or command.startswith('#'):
            continue
            
        print(f"\n[{i}] Processing: {command}")
        
        try:
            messages = [{"role": "user", "content": command}]
            response = pipeline.pipe(
                user_message=command,
                model_id="auto",
                messages=messages,
                body={}
            )
            
            result = {
                "command": command,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            print(f"✅ Response: {response}")
            
        except Exception as e:
            result = {
                "command": command,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
            
            print(f"❌ Error: {e}")
        
        results.append(result)
    
    # Save results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch process commands with Myndy AI")
    parser.add_argument("-i", "--input", help="Input file with commands")
    parser.add_argument("-o", "--output", help="Output file for results")
    
    args = parser.parse_args()
    
    try:
        results = process_batch(args.input, args.output)
        print(f"\n🎉 Processed {len(results)} commands")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x /Users/jeremy/crewAI/pipeline/batch_processor.py
```

**Usage examples:**
```bash
cd /Users/jeremy/crewAI/pipeline

# Interactive mode
python batch_processor.py

# From file
echo -e "What's the weather?\nSearch for John\nTrack expenses" > commands.txt
python batch_processor.py -i commands.txt -o results.json
```

---

## 🐳 Docker Deployment

### Build and Run
```bash
cd /Users/jeremy/crewAI/pipeline

# Build the container
docker build -t crewai-myndy-pipeline .

# Run with port mapping
docker run -d -p 9099:9099 \
  -v /Users/jeremy/myndy:/myndy:ro \
  --name myndy-pipeline \
  crewai-myndy-pipeline

# View logs
docker logs myndy-pipeline

# Stop the container
docker stop myndy-pipeline
```

### Docker Compose (Optional)
```yaml
# docker-compose.yml
version: '3.8'
services:
  myndy-pipeline:
    build: .
    ports:
      - "9099:9099"
    volumes:
      - /Users/jeremy/myndy:/myndy:ro
    environment:
      - MYNDY_PATH=/myndy
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## ⚙️ Configuration

### Environment Variables
```bash
export MYNDY_PATH="/Users/jeremy/myndy"
export PIPELINE_PORT="9099"
export DEBUG_MODE="false"
```

### Pipeline Valves (OpenWebUI)
Configure in the OpenWebUI interface:

- **enable_intelligent_routing**: `true` (Auto-select best agent)
- **enable_tool_execution**: `true` (Allow tool usage)
- **enable_contact_management**: `true` (Contact search/update)
- **enable_memory_search**: `true` (Knowledge base search)
- **debug_mode**: `false` (Enable debug logging)
- **myndy_path**: `"/Users/jeremy/myndy"` (Path to Myndy installation)

---

## 🛠️ Troubleshooting

### Pipeline Won't Start
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify dependencies
pip list | grep -E "(fastapi|uvicorn|crewai)"

# Test basic import
python -c "from crewai_myndy_pipeline import Pipeline; print('✅ Import successful')"
```

### OpenWebUI Connection Issues
```bash
# Test pipeline endpoint
curl http://localhost:9099/v1/models

# Check if port is in use
lsof -i :9099

# Try different port
python -m uvicorn server:app --host 0.0.0.0 --port 9100
```

### Tool Execution Errors
```bash
# Verify Myndy installation
ls -la /Users/jeremy/myndy

# Check permissions
ls -la /Users/jeremy/myndy/agents/tools/

# Test direct tool import
python -c "import sys; sys.path.append('/Users/jeremy/myndy'); print('✅ Myndy path accessible')"
```

---

## 💡 Examples

### Example 1: Contact Management (Terminal)
```bash
python terminal_runner.py
# Select model: 2 (Memory Librarian)
# "Do you know John Doe?"
# "Update John works at Google"
```

### Example 2: Weather Query (Single Command)
```bash
python single_command.py "What's the weather in San Francisco?" personal_assistant
```

### Example 3: Financial Analysis (OpenWebUI)
1. Start pipeline: `python -m uvicorn server:app --port 9099`
2. Add to OpenWebUI: `http://localhost:9099`
3. Select "🎯 Finance Tracker"
4. Ask: "Track my spending this month"

### Example 4: Research Query (Batch)
```bash
cat > research_queries.txt << EOF
Research the latest AI trends
Analyze sentiment in tech news
Summarize recent developments in LLMs
EOF

python batch_processor.py -i research_queries.txt -o research_results.json
```

---

## 🎯 Quick Start Commands

### For OpenWebUI (Recommended)
```bash
cd /Users/jeremy/crewAI/pipeline
pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 9099
```

### For Terminal Use
```bash
cd /Users/jeremy/crewAI/pipeline
python terminal_runner.py
```

### For Single Commands
```bash
cd /Users/jeremy/crewAI/pipeline
python single_command.py "Your question here"
```

---

## 📚 Additional Resources

- **Pipeline Configuration**: See `crewai_myndy_pipeline.py` for detailed settings
- **Agent Capabilities**: Check individual agent files in `/agents/`
- **Tool Documentation**: Review `/tools/myndy_bridge.py` for available tools
- **Troubleshooting**: Check log files in `/pipeline/` directory

---

**🎉 You're ready to use Myndy AI! Choose your preferred method and start conversing with your intelligent assistant.**