#!/bin/bash

# Interactive resource browser
BASE_URL="http://localhost:9092"

echo "MCP Resource Browser"
echo "===================="
echo ""
echo "Available Resources:"
echo "1. myndy://profile/self - User profile and preferences"
echo "2. myndy://profile/goals - User goals and objectives"
echo "3. myndy://profile/preferences - User preferences"
echo "4. myndy://memory/entities - All memory entities"
echo "5. myndy://memory/conversations - Conversation history"
echo "6. myndy://memory/short-term - Short-term memory"
echo "7. myndy://memory/people - People in memory"
echo "8. myndy://memory/places - Places in memory"
echo "9. myndy://memory/events - Events in memory"
echo "10. myndy://health/status - Health status"
echo "11. myndy://health/metrics - Health metrics"
echo "12. myndy://finance/transactions - Financial transactions"
echo "13. myndy://finance/budget - Budget summary"
echo "14. myndy://documents/list - Document listing"
echo ""
echo "Or enter a custom URI (e.g., myndy://memory/entities/123)"
echo ""

read -p "Enter resource number or URI: " choice

case $choice in
    1) URI="myndy://profile/self" ;;
    2) URI="myndy://profile/goals" ;;
    3) URI="myndy://profile/preferences" ;;
    4) URI="myndy://memory/entities" ;;
    5) URI="myndy://memory/conversations" ;;
    6) URI="myndy://memory/short-term" ;;
    7) URI="myndy://memory/people" ;;
    8) URI="myndy://memory/places" ;;
    9) URI="myndy://memory/events" ;;
    10) URI="myndy://health/status" ;;
    11) URI="myndy://health/metrics" ;;
    12) URI="myndy://finance/transactions" ;;
    13) URI="myndy://finance/budget" ;;
    14) URI="myndy://documents/list" ;;
    *) URI=$choice ;;
esac

echo ""
echo "Fetching: $URI"
echo "===================="

response=$(curl -s -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"resources/read\",
    \"params\": {
      \"uri\": \"$URI\"
    }
  }")

# Pretty print with jq if available
if command -v jq &> /dev/null; then
    echo "$response" | jq
else
    echo "$response"
fi
