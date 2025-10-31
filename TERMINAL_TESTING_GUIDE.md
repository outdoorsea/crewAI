# MCP Server Terminal Testing Guide

## Overview

This guide shows how to test the MCP server directly from the terminal using curl and other command-line tools. Perfect for debugging, CI/CD testing, or understanding how the MCP protocol works.

## Prerequisites

1. **MCP Server Running**:
   ```bash
   cd /Users/jeremy/myndy-core/myndy-crewai
   python3 start_mcp_server.py
   ```

2. **Myndy-AI Backend Running**:
   ```bash
   # In another terminal
   cd /Users/jeremy/myndy-core/myndy-ai
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Tools Available**: curl, jq (optional, for pretty JSON)

## Quick Health Check

```bash
# Simple health check
curl http://localhost:9092/health

# Expected response:
# {"status":"healthy","server":"myndy-crewai-mcp"}

# With pretty formatting
curl -s http://localhost:9092/health | jq
```

## MCP Protocol Testing

The MCP server uses JSON-RPC 2.0 over SSE. You can send requests using curl.

### 1. List Available Tools

```bash
# List all tools
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }' | jq

# Expected response includes 33 tools with schemas
```

**What You'll See**:
- Tool names, descriptions, categories
- Parameter schemas with types and requirements
- Result schemas

### 2. Execute a Tool

**Example 1: Get Current Time**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_current_time",
      "arguments": {
        "timezone": "America/Los_Angeles"
      }
    }
  }' | jq
```

**Example 2: Search Memory**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "search_memory",
      "arguments": {
        "query": "John"
      }
    }
  }' | jq
```

**Example 3: Get Self Profile**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "get_self_profile",
      "arguments": {}
    }
  }' | jq
```

**Example 4: Format Date**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "format_date",
      "arguments": {
        "date": "2025-10-07",
        "format": "%B %d, %Y"
      }
    }
  }' | jq
```

### 3. List Available Resources

```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "resources/list",
    "params": {}
  }' | jq

# Expected: 14 resources + 5 templates
```

### 4. Read a Resource

**Example 1: Get Self Profile**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "resources/read",
    "params": {
      "uri": "myndy://profile/self"
    }
  }' | jq
```

**Example 2: Get Memory Entities**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 8,
    "method": "resources/read",
    "params": {
      "uri": "myndy://memory/entities"
    }
  }' | jq
```

**Example 3: Get Goals**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 9,
    "method": "resources/read",
    "params": {
      "uri": "myndy://profile/goals"
    }
  }' | jq
```

**Example 4: Get Health Status**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 10,
    "method": "resources/read",
    "params": {
      "uri": "myndy://health/status"
    }
  }' | jq
```

### 5. List Available Prompts

```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 11,
    "method": "prompts/list",
    "params": {}
  }' | jq

# Expected: 16 prompts across 5 categories
```

### 6. Get a Prompt

**Example 1: Personal Assistant**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 12,
    "method": "prompts/get",
    "params": {
      "name": "personal_assistant",
      "arguments": {
        "task": "Check my schedule for today"
      }
    }
  }' | jq
```

**Example 2: Memory Search**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 13,
    "method": "prompts/get",
    "params": {
      "name": "memory_search",
      "arguments": {
        "query": "people I met last week",
        "limit": "5"
      }
    }
  }' | jq
```

**Example 3: Health Metrics**
```bash
curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 14,
    "method": "prompts/get",
    "params": {
      "name": "health_metrics",
      "arguments": {
        "metric_type": "sleep",
        "time_range": "week"
      }
    }
  }' | jq
```

## Automated Testing Scripts

### Complete Test Suite Script

Create `terminal_test_suite.sh`:

```bash
#!/bin/bash

echo "========================================"
echo "  MCP Server Terminal Test Suite"
echo "========================================"
echo ""

BASE_URL="http://localhost:9092"
FAILED=0
PASSED=0

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
        echo "✅ PASS"
        ((PASSED++))
        return 0
    else
        echo "❌ FAIL"
        echo "Response: $response"
        ((FAILED++))
        return 1
    fi
}

# Health Check
echo "1. Health Check"
curl -s "$BASE_URL/health" | jq
echo ""

# Test Tools
echo "2. Testing Tools"
test_endpoint "List Tools" "tools/list" "{}"
test_endpoint "Get Current Time" "tools/call" '{"name":"get_current_time","arguments":{"timezone":"UTC"}}'
test_endpoint "Search Memory" "tools/call" '{"name":"search_memory","arguments":{"query":"test"}}'
echo ""

# Test Resources
echo "3. Testing Resources"
test_endpoint "List Resources" "resources/list" "{}"
test_endpoint "Read Profile" "resources/read" '{"uri":"myndy://profile/self"}'
test_endpoint "Read Memory Entities" "resources/read" '{"uri":"myndy://memory/entities"}'
echo ""

# Test Prompts
echo "4. Testing Prompts"
test_endpoint "List Prompts" "prompts/list" "{}"
test_endpoint "Get Personal Assistant Prompt" "prompts/get" '{"name":"personal_assistant","arguments":{"task":"test"}}'
echo ""

# Summary
echo "========================================"
echo "  Test Results"
echo "========================================"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
```

Make it executable and run:
```bash
chmod +x terminal_test_suite.sh
./terminal_test_suite.sh
```

### Quick Tool Test Script

Create `quick_tool_test.sh`:

```bash
#!/bin/bash

# Quick tool execution test
TOOL_NAME=${1:-"get_current_time"}
TIMEZONE=${2:-"UTC"}

echo "Testing tool: $TOOL_NAME with timezone: $TIMEZONE"

curl -X POST http://localhost:9092/mcp \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"$TOOL_NAME\",
      \"arguments\": {
        \"timezone\": \"$TIMEZONE\"
      }
    }
  }" | jq

# Usage:
# ./quick_tool_test.sh get_current_time America/New_York
# ./quick_tool_test.sh get_current_time Europe/London
```

### Resource Browser Script

Create `browse_resources.sh`:

```bash
#!/bin/bash

# Interactive resource browser
BASE_URL="http://localhost:9092"

echo "Available Resources:"
echo "===================="
echo "1. myndy://profile/self"
echo "2. myndy://profile/goals"
echo "3. myndy://memory/entities"
echo "4. myndy://memory/people"
echo "5. myndy://health/status"
echo "6. myndy://finance/transactions"
echo ""

read -p "Enter resource number (or custom URI): " choice

case $choice in
    1) URI="myndy://profile/self" ;;
    2) URI="myndy://profile/goals" ;;
    3) URI="myndy://memory/entities" ;;
    4) URI="myndy://memory/people" ;;
    5) URI="myndy://health/status" ;;
    6) URI="myndy://finance/transactions" ;;
    *) URI=$choice ;;
esac

echo ""
echo "Fetching: $URI"
echo "===================="

curl -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"resources/read\",
    \"params\": {
      \"uri\": \"$URI\"
    }
  }" | jq
```

## SSE Stream Testing

The MCP server uses SSE for real-time streaming. You can test SSE with curl:

```bash
# Connect to SSE endpoint
curl -N http://localhost:9092/sse

# Send a message (in another terminal)
# This requires the SSE connection to be established
```

For interactive SSE testing, use a tool like `websocat` or create a Python script:

```python
# sse_test.py
import asyncio
from httpx_sse import aconnect_sse
import httpx
import json

async def test_sse():
    async with httpx.AsyncClient() as client:
        async with aconnect_sse(client, "GET", "http://localhost:9092/sse") as event_source:
            # Send a request
            await client.post(
                "http://localhost:9092/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
            )

            # Receive events
            async for sse in event_source.aiter_sse():
                print(f"Event: {sse.event}")
                print(f"Data: {sse.data}")
                if sse.event == "message":
                    data = json.loads(sse.data)
                    if "result" in data:
                        print(f"Result: {json.dumps(data['result'], indent=2)}")
                        break

asyncio.run(test_sse())
```

## Performance Testing

### Load Test Script

Create `load_test.sh`:

```bash
#!/bin/bash

REQUESTS=${1:-100}
CONCURRENCY=${2:-10}

echo "Running load test: $REQUESTS requests with $CONCURRENCY concurrent connections"

# Create temporary file with request
cat > /tmp/mcp_request.json << 'EOF'
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_current_time",
    "arguments": {
      "timezone": "UTC"
    }
  }
}
EOF

# Run load test using ab (Apache Bench) if available
if command -v ab &> /dev/null; then
    ab -n $REQUESTS -c $CONCURRENCY -p /tmp/mcp_request.json -T application/json \
       http://localhost:9092/mcp
else
    # Fallback to simple sequential test
    start=$(date +%s)
    for i in $(seq 1 $REQUESTS); do
        curl -s -X POST http://localhost:9092/mcp \
            -H "Content-Type: application/json" \
            -d @/tmp/mcp_request.json > /dev/null
    done
    end=$(date +%s)
    duration=$((end - start))
    echo "Completed $REQUESTS requests in ${duration}s"
    echo "Average: $((REQUESTS / duration)) requests/second"
fi

rm /tmp/mcp_request.json
```

### Response Time Benchmark

Create `benchmark.sh`:

```bash
#!/bin/bash

echo "MCP Server Response Time Benchmark"
echo "===================================="

# Test different operations
declare -A tests=(
    ["Health Check"]="curl -s http://localhost:9092/health"
    ["List Tools"]='curl -s -X POST http://localhost:9092/mcp -H "Content-Type: application/json" -d '"'"'{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'"'"''
    ["Execute Tool"]='curl -s -X POST http://localhost:9092/mcp -H "Content-Type: application/json" -d '"'"'{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_current_time","arguments":{"timezone":"UTC"}}}'"'"''
    ["Read Resource"]='curl -s -X POST http://localhost:9092/mcp -H "Content-Type: application/json" -d '"'"'{"jsonrpc":"2.0","id":1,"method":"resources/read","params":{"uri":"myndy://profile/self"}}'"'"''
)

for test_name in "${!tests[@]}"; do
    echo ""
    echo "Testing: $test_name"

    # Run test 10 times and get average
    total=0
    for i in {1..10}; do
        start=$(date +%s%N)
        eval ${tests[$test_name]} > /dev/null
        end=$(date +%s%N)
        duration=$(( (end - start) / 1000000 ))
        total=$((total + duration))
    done

    average=$((total / 10))
    echo "Average response time: ${average}ms"
done
```

## Debugging Tips

### Enable Verbose Logging

```bash
# Set environment variables before starting server
export MCP_DEBUG="true"
export MCP_LOG_LEVEL="DEBUG"
export MCP_VERBOSE="true"

python3 start_mcp_server.py
```

### Watch Server Logs

```bash
# In another terminal
tail -f /tmp/mcp_server.log
```

### Test Backend Connectivity

```bash
# Check myndy-ai backend is running
curl http://localhost:8000/health

# List tools from backend
curl http://localhost:8000/api/v1/tools/ | jq

# Execute tool directly on backend
curl -X POST http://localhost:8000/api/v1/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_current_time",
    "parameters": {"timezone": "UTC"}
  }' | jq
```

### Check Port Availability

```bash
# Check if MCP server port is in use
lsof -i :9092

# Check if backend port is in use
lsof -i :8000
```

## Common Issues and Solutions

### Issue 1: Connection Refused

```bash
# Check if server is running
curl http://localhost:9092/health

# If not running, start it
python3 start_mcp_server.py
```

### Issue 2: Tool Execution Fails

```bash
# Test backend directly
curl -X POST http://localhost:8000/api/v1/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_current_time",
    "parameters": {"timezone": "UTC"}
  }'

# Check if backend is running
curl http://localhost:8000/health
```

### Issue 3: Empty or Error Responses

```bash
# Check server logs
tail -100 /tmp/mcp_server.log

# Enable debug mode
export MCP_DEBUG="true"
python3 start_mcp_server.py
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/mcp-test.yml
name: MCP Server Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Start MCP Server
        run: |
          python3 start_mcp_server.py &
          sleep 5

      - name: Run terminal tests
        run: |
          chmod +x terminal_test_suite.sh
          ./terminal_test_suite.sh

      - name: Check test results
        run: |
          if [ $? -eq 0 ]; then
            echo "✅ All tests passed"
          else
            echo "❌ Tests failed"
            exit 1
          fi
```

## Summary

Terminal testing provides:
- **Quick validation** during development
- **CI/CD integration** for automated testing
- **Debugging capabilities** with verbose output
- **Performance benchmarking** for optimization
- **Protocol understanding** by seeing raw requests/responses

All test scripts can be found in the project root and are ready to use immediately after starting the MCP server.

---

**Last Updated**: October 7, 2025
**MCP Server Version**: 0.1.0
**Tested With**: curl, jq, bash
