#!/bin/bash

# FastAPI Memory Agent Integration Test Runner
# 
# This script runs the comprehensive integration test for the FastAPI-based
# Memory Agent, demonstrating the complete service-oriented architecture.
#
# File: run_fastapi_integration_test.sh

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

echo -e "${PURPLE}🚀 FastAPI Memory Agent Integration Test${NC}"
echo -e "${PURPLE}=====================================================${NC}"
echo

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "$SCRIPT_DIR/test_fastapi_memory_agent.py" ]]; then
    echo -e "${RED}❌ test_fastapi_memory_agent.py not found${NC}"
    echo -e "${RED}   Please run this script from the crewAI directory${NC}"
    exit 1
fi

# Check if myndy-ai directory exists
MYNDY_AI_DIR="$SCRIPT_DIR/../myndy-ai"
if [[ ! -d "$MYNDY_AI_DIR" ]]; then
    echo -e "${RED}❌ myndy-ai directory not found at $MYNDY_AI_DIR${NC}"
    echo -e "${RED}   The FastAPI server needs to be available${NC}"
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
    "requests"
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

# Set Python path
export PYTHONPATH="$SCRIPT_DIR:$MYNDY_AI_DIR:$PYTHONPATH"

# Set working directory
cd "$SCRIPT_DIR"

echo -e "${GREEN}✅ Environment setup complete${NC}"
echo

# Set environment variables to suppress warnings
export PYTHONWARNINGS="ignore::UserWarning,ignore::DeprecationWarning"

# Run the integration test
echo -e "${CYAN}🧪 Running FastAPI Memory Agent Integration Test...${NC}"
echo -e "${CYAN}=================================================${NC}"

# Make the test script executable
chmod +x test_fastapi_memory_agent.py

# Run the test
if python3 -W ignore test_fastapi_memory_agent.py; then
    echo
    echo -e "${GREEN}🎉 Integration test completed successfully!${NC}"
    echo
    echo -e "${PURPLE}📋 What was tested:${NC}"
    echo -e "   ${GREEN}✅${NC} FastAPI server startup and health checks"
    echo -e "   ${GREEN}✅${NC} HTTP client tools communication"
    echo -e "   ${GREEN}✅${NC} Service-oriented architecture boundaries"
    echo -e "   ${GREEN}✅${NC} FastAPI-based Memory Agent creation"
    echo -e "   ${GREEN}✅${NC} Agent tool execution through HTTP services"
    echo -e "   ${GREEN}✅${NC} Error handling and graceful degradation"
    echo
    echo -e "${PURPLE}🎯 Next Steps:${NC}"
    echo -e "   1. Implement remaining FastAPI-based agents (Status Agent, Conversation Agent)"
    echo -e "   2. Create comprehensive unit tests for all endpoints"
    echo -e "   3. Add authentication and security features"
    echo -e "   4. Implement performance monitoring and metrics"
    echo -e "   5. Deploy to production environment"
    echo
else
    EXIT_CODE=$?
    echo
    echo -e "${RED}❌ Integration test failed with exit code $EXIT_CODE${NC}"
    echo
    echo -e "${YELLOW}💡 Troubleshooting tips:${NC}"
    echo -e "   1. Check if myndy-ai dependencies are installed"
    echo -e "   2. Verify Qdrant service is available (if used)"
    echo -e "   3. Check Python path and import configurations"
    echo -e "   4. Review error messages above for specific issues"
    echo -e "   5. Try running components individually to isolate issues"
    echo
    exit $EXIT_CODE
fi

echo -e "${PURPLE}✨ FastAPI Service-Oriented Architecture is ready!${NC}"