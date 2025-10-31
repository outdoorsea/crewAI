#!/bin/bash

echo "MCP Server Response Time Benchmark"
echo "===================================="
echo ""

BASE_URL="http://localhost:9092"
ITERATIONS=10

# Check if server is running
health_check=$(curl -s "$BASE_URL/health")
if ! echo "$health_check" | grep -q "healthy"; then
    echo "❌ Server is not running. Start it with: python3 start_mcp_server.py"
    exit 1
fi

echo "Running $ITERATIONS iterations for each test..."
echo ""

# Function to benchmark an endpoint
benchmark() {
    local name=$1
    local curl_cmd=$2

    echo "Testing: $name"

    total=0
    min=999999
    max=0

    for i in $(seq 1 $ITERATIONS); do
        start=$(date +%s%N)
        eval "$curl_cmd" > /dev/null 2>&1
        end=$(date +%s%N)

        duration=$(( (end - start) / 1000000 ))
        total=$((total + duration))

        if [ $duration -lt $min ]; then
            min=$duration
        fi

        if [ $duration -gt $max ]; then
            max=$duration
        fi
    done

    average=$((total / ITERATIONS))

    echo "  Average: ${average}ms"
    echo "  Min: ${min}ms"
    echo "  Max: ${max}ms"
    echo ""
}

# Run benchmarks
benchmark "Health Check" \
    "curl -s $BASE_URL/health"

benchmark "List Tools" \
    "curl -s -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\",\"params\":{}}'"

benchmark "Execute Tool (get_current_time)" \
    "curl -s -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"get_current_time\",\"arguments\":{\"timezone\":\"UTC\"}}}'"

benchmark "List Resources" \
    "curl -s -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"resources/list\",\"params\":{}}'"

benchmark "Read Resource (profile/self)" \
    "curl -s -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"resources/read\",\"params\":{\"uri\":\"myndy://profile/self\"}}'"

benchmark "List Prompts" \
    "curl -s -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"prompts/list\",\"params\":{}}'"

benchmark "Get Prompt (personal_assistant)" \
    "curl -s -X POST $BASE_URL/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"prompts/get\",\"params\":{\"name\":\"personal_assistant\",\"arguments\":{\"task\":\"test\"}}}'"

echo "===================================="
echo "Benchmark Complete"
echo "===================================="
