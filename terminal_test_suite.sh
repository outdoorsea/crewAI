#!/bin/bash

echo "========================================"
echo "  MCP Server Terminal Test Suite"
echo "========================================"
echo ""

BASE_URL="http://localhost:9092"
FAILED=0
PASSED=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local params=$3

    echo -n "Testing: $name... "

    response=$(curl -s -X POST "$BASE_URL/mcp" \
        -H "Content-Type: application/json" \
        -d "{
            \"jsonrpc\": \"2.0\",
            \"id\": 1,
            \"method\": \"$method\",
            \"params\": $params
        }")

    if echo "$response" | jq -e '.result' > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Response: $response"
        ((FAILED++))
        return 1
    fi
}

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq not installed. Install with 'brew install jq' for better output.${NC}"
    echo ""
fi

# Health Check
echo "1. Health Check"
health_response=$(curl -s "$BASE_URL/health")
echo "$health_response" | jq 2>/dev/null || echo "$health_response"
echo ""

if echo "$health_response" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Server is healthy${NC}"
else
    echo -e "${RED}❌ Server health check failed${NC}"
    echo "Make sure the server is running: python3 start_mcp_server.py"
    exit 1
fi
echo ""

# Test Tools
echo "2. Testing Tools"
echo "----------------"
test_endpoint "List Tools" "tools/list" "{}"
test_endpoint "Get Current Time (UTC)" "tools/call" '{"name":"get_current_time","arguments":{"timezone":"UTC"}}'
test_endpoint "Get Current Time (LA)" "tools/call" '{"name":"get_current_time","arguments":{"timezone":"America/Los_Angeles"}}'
test_endpoint "Search Memory" "tools/call" '{"name":"search_memory","arguments":{"query":"test"}}'
test_endpoint "Get Self Profile" "tools/call" '{"name":"get_self_profile","arguments":{}}'
echo ""

# Test Resources
echo "3. Testing Resources"
echo "--------------------"
test_endpoint "List Resources" "resources/list" "{}"
test_endpoint "Read Profile" "resources/read" '{"uri":"myndy://profile/self"}'
test_endpoint "Read Memory Entities" "resources/read" '{"uri":"myndy://memory/entities"}'
test_endpoint "Read Goals" "resources/read" '{"uri":"myndy://profile/goals"}'
test_endpoint "Read Health Status" "resources/read" '{"uri":"myndy://health/status"}'
echo ""

# Test Prompts
echo "4. Testing Prompts"
echo "------------------"
test_endpoint "List Prompts" "prompts/list" "{}"
test_endpoint "Get Personal Assistant Prompt" "prompts/get" '{"name":"personal_assistant","arguments":{"task":"test"}}'
test_endpoint "Get Memory Search Prompt" "prompts/get" '{"name":"memory_search","arguments":{"query":"test","limit":"5"}}'
test_endpoint "Get Health Metrics Prompt" "prompts/get" '{"name":"health_metrics","arguments":{"metric_type":"sleep"}}'
echo ""

# Summary
echo "========================================"
echo "  Test Results"
echo "========================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
