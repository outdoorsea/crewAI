# 🚀 Quick Start Guide - Myndy AI Pipelines

## 🎯 Fastest Way to Get Started

### 1. Install Dependencies
```bash
cd /Users/jeremy/crewAI/pipeline
pip install -r requirements.txt
```

### 2. Choose Your Interface

#### 🌐 **OpenWebUI (Web Interface)**
```bash
# Start the pipeline server
python -m uvicorn server:app --host 0.0.0.0 --port 9099

# Then add http://localhost:9099 to OpenWebUI pipelines
```

#### 💻 **Terminal (Command Line)**
```bash
# Interactive conversation
python terminal_runner.py

# Single command
python single_command.py "What's the weather?"

# Batch processing
python batch_processor.py -i commands.txt -o results.json
```

## 📋 Available Models

1. **🧠 Myndy AI v0.1** - Auto-routing (chooses best agent)
2. **🎯 Memory Librarian** - Contact management, knowledge search
3. **🎯 Research Specialist** - Information gathering, analysis
4. **🎯 Personal Assistant** - Scheduling, productivity, weather
5. **🎯 Health Analyst** - Health data analysis, wellness
6. **🎯 Finance Tracker** - Expense tracking, budget analysis

## 💡 Example Commands

```bash
# Weather query (auto-routed to Personal Assistant)
python single_command.py "What's the weather in San Francisco?"

# Contact search (auto-routed to Memory Librarian)
python single_command.py "Do you know John Doe?"

# Financial analysis (auto-routed to Finance Tracker)
python single_command.py "Track my spending this month"

# Force specific agent
python single_command.py "Research AI trends" research_specialist
```

## 🛠️ Troubleshooting

### Quick Diagnostics
```bash
# Test basic import
python -c "from crewai_myndy_pipeline import Pipeline; print('✅ Pipeline OK')"

# Check if server is running
curl http://localhost:9099/v1/models

# View available ports
lsof -i :9099
```

### Common Issues
- **Import errors**: Ensure `/Users/jeremy/myndy` exists and is accessible
- **Port conflicts**: Use `--port 9100` for different port
- **Permission errors**: Check file permissions with `ls -la`

## 📚 Full Documentation

For complete details, see: [PIPELINE_USAGE.md](./PIPELINE_USAGE.md)

---

**🎉 Ready to chat with Myndy AI!**