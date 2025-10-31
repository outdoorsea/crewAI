#!/bin/bash

# FastAPI Test Assistant Demo Runner
# 
# This script runs the FastAPI Test Assistant demonstration, showing
# how the specialized testing agent validates all FastAPI-based tools.
#
# File: run_test_assistant_demo.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo -e "${PURPLE}🤖 FastAPI Test Assistant Demo${NC}"
echo -e "${PURPLE}======================================${NC}"
echo -e "${CYAN}Demonstrating specialized agent for FastAPI tool validation${NC}"
echo

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "$SCRIPT_DIR/test_fastapi_assistant_demo.py" ]]; then
    echo -e "${RED}❌ test_fastapi_assistant_demo.py not found${NC}"
    echo -e "${RED}   Please run this script from the crewAI directory${NC}"
    exit 1
fi

# Check if agent file exists
if [[ ! -f "$SCRIPT_DIR/agents/fastapi_test_assistant.py" ]]; then
    echo -e "${RED}❌ FastAPI Test Assistant agent not found${NC}"
    echo -e "${RED}   The agent file should be at agents/fastapi_test_assistant.py${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies check passed${NC}"

# Check if required Python packages are available
echo -e "${BLUE}🐍 Checking Python packages...${NC}"

# Check for required packages
REQUIRED_PACKAGES=(
    "crewai"
    "httpx" 
    "pydantic"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" &> /dev/null; then
        echo -e "${YELLOW}⚠️ Package '$package' not found, attempting to install...${NC}"
        pip3 install "$package" || {
            echo -e "${RED}❌ Failed to install $package${NC}"
            exit 1
        }
    else
        echo -e "${GREEN}✅ $package is available${NC}"
    fi
done

# Set up environment
echo -e "${BLUE}🔧 Setting up environment...${NC}"

# Set Python path to include both crewAI and myndy-ai
MYNDY_AI_DIR="$SCRIPT_DIR/../myndy-ai"
export PYTHONPATH="$SCRIPT_DIR:$MYNDY_AI_DIR:$PYTHONPATH"

# Set working directory
cd "$SCRIPT_DIR"

echo -e "${GREEN}✅ Environment setup complete${NC}"
echo

# Check if FastAPI server is running (optional)
echo -e "${BLUE}🌐 Checking FastAPI server status...${NC}"
if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ FastAPI server is running - live testing will be performed${NC}"
    SERVER_RUNNING=true
else
    echo -e "${YELLOW}⚠️ FastAPI server not detected - demo will run in offline mode${NC}"
    echo -e "${CYAN}💡 To enable live testing, start the server with:${NC}"
    echo -e "${CYAN}   cd ../myndy-ai && python start_api_server.py${NC}"
    SERVER_RUNNING=false
fi
echo

# Provide demo options
echo -e "${PURPLE}🎯 Demo Options:${NC}"
echo -e "${CYAN}1. Full Demo - Run comprehensive test assistant demonstration${NC}"
echo -e "${CYAN}2. Quick Demo - Just show agent creation and capabilities${NC}"
echo -e "${CYAN}3. Live Testing - Run actual tool tests (requires FastAPI server)${NC}"
echo

# Get user choice or default to full demo
read -p "$(echo -e ${YELLOW}Choose option [1-3] or press Enter for Full Demo: ${NC})" choice
choice=${choice:-1}

case $choice in
    1)
        echo -e "${CYAN}🚀 Running Full Demo...${NC}"
        DEMO_MODE="full"
        ;;
    2)
        echo -e "${CYAN}⚡ Running Quick Demo...${NC}"
        DEMO_MODE="quick"
        ;;
    3)
        if [[ "$SERVER_RUNNING" == "true" ]]; then
            echo -e "${CYAN}🔥 Running Live Testing...${NC}"
            DEMO_MODE="live"
        else
            echo -e "${RED}❌ FastAPI server is not running. Cannot perform live testing.${NC}"
            echo -e "${YELLOW}   Falling back to Full Demo mode...${NC}"
            DEMO_MODE="full"
        fi
        ;;
    *)
        echo -e "${YELLOW}⚠️ Invalid option. Running Full Demo...${NC}"
        DEMO_MODE="full"
        ;;
esac

echo

# Run the demo based on selected mode
echo -e "${CYAN}🎬 Starting FastAPI Test Assistant Demo...${NC}"
echo -e "${CYAN}===========================================${NC}"

# Set environment variables to suppress warnings
export PYTHONWARNINGS="ignore::UserWarning,ignore::DeprecationWarning"

if [[ "$DEMO_MODE" == "quick" ]]; then
    # Quick demo - just test agent creation
    echo -e "${BLUE}🔧 Quick Demo: Testing agent creation...${NC}"
    python3 -W ignore -c "
from agents.fastapi_test_assistant import create_fastapi_test_assistant, get_fastapi_test_assistant_capabilities
print('🤖 Creating FastAPI Test Assistant...')
try:
    agent = create_fastapi_test_assistant(verbose=False)
    print(f'✅ Agent created successfully: {agent.role}')
    print(f'   Tools available: {len(agent.tools)}')
    print('\\n🔧 Available Tools:')
    for tool in agent.tools:
        print(f'   • {tool.name}')
    print('\\n⭐ Agent Capabilities:')
    for cap in get_fastapi_test_assistant_capabilities():
        print(f'   • {cap}')
    print('\\n🎉 Quick demo completed successfully!')
except Exception as e:
    print(f'❌ Quick demo failed: {e}')
    import traceback
    traceback.print_exc()
    "
else
    # Full or live demo - run the complete demonstration
    export DEMO_MODE
    python3 -W ignore test_fastapi_assistant_demo.py
fi

EXIT_CODE=$?

echo
echo -e "${PURPLE}===========================================${NC}"

if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}🎉 FastAPI Test Assistant Demo completed successfully!${NC}"
    echo
    echo -e "${PURPLE}📋 What was demonstrated:${NC}"
    echo -e "   ${GREEN}✅${NC} FastAPI Test Assistant agent creation"
    echo -e "   ${GREEN}✅${NC} Specialized testing tools for FastAPI validation"
    echo -e "   ${GREEN}✅${NC} Comprehensive test suite capabilities"
    echo -e "   ${GREEN}✅${NC} Individual tool testing functionality"
    echo -e "   ${GREEN}✅${NC} Service-oriented architecture validation"
    echo -e "   ${GREEN}✅${NC} Error handling and reporting mechanisms"
    echo
    echo -e "${PURPLE}🎯 Key Features of the Test Assistant:${NC}"
    echo -e "   • Systematic validation of all FastAPI memory tools"
    echo -e "   • Comprehensive test reporting with metrics"
    echo -e "   • Individual and suite-based testing modes"
    echo -e "   • Service boundary compliance checking"
    echo -e "   • Real-time HTTP communication testing"
    echo -e "   • Detailed error analysis and performance assessment"
    echo
    echo -e "${PURPLE}💡 Usage Recommendations:${NC}"
    echo -e "   1. Use for regular validation during development"
    echo -e "   2. Integrate into CI/CD pipelines for automated testing"
    echo -e "   3. Run before deploying FastAPI service updates"
    echo -e "   4. Extend with additional test cases as needed"
    echo
else
    echo -e "${RED}❌ Demo failed with exit code $EXIT_CODE${NC}"
    echo
    echo -e "${YELLOW}💡 Troubleshooting tips:${NC}"
    echo -e "   1. Check Python package dependencies (crewai, httpx, pydantic)"
    echo -e "   2. Verify Python path includes both crewAI and myndy-ai directories"
    echo -e "   3. For live testing, ensure FastAPI server is running"
    echo -e "   4. Check error messages above for specific issues"
    echo -e "   5. Try quick demo mode first to test basic functionality"
    echo
fi

echo -e "${PURPLE}✨ FastAPI Test Assistant is ready for validation tasks!${NC}"