#!/bin/bash

# Quick tool execution test
TOOL_NAME=${1:-"get_current_time"}
BASE_URL="http://localhost:9092"

# Parse additional arguments as tool parameters
shift
ARGS_JSON="{}"

# If arguments provided, parse them
if [ $# -gt 0 ]; then
    ARGS_JSON="{"
    first=true
    while [ $# -gt 0 ]; do
        key="${1%%=*}"
        value="${1#*=}"

        if [ "$first" = true ]; then
            first=false
        else
            ARGS_JSON="$ARGS_JSON,"
        fi

        ARGS_JSON="$ARGS_JSON\"$key\":\"$value\""
        shift
    done
    ARGS_JSON="$ARGS_JSON}"
fi

echo "Testing tool: $TOOL_NAME"
echo "Arguments: $ARGS_JSON"
echo "========================================"

response=$(curl -s -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"$TOOL_NAME\",
      \"arguments\": $ARGS_JSON
    }
  }")

# Pretty print with jq if available
if command -v jq &> /dev/null; then
    echo "$response" | jq
else
    echo "$response"
fi

# Usage examples:
# ./quick_tool_test.sh get_current_time timezone=America/New_York
# ./quick_tool_test.sh get_current_time timezone=Europe/London
# ./quick_tool_test.sh search_memory query=John
# ./quick_tool_test.sh format_date date=2025-10-07 format="%B %d, %Y"
