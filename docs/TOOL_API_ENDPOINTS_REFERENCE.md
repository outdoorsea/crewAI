# Myndy-AI Tool API Endpoints Reference

## Overview

This document provides a quick reference for accessing Myndy-AI tools via the FastAPI service-oriented architecture. All tools are accessed through standardized HTTP endpoints with JSON request/response patterns.

## 🔄 Base API Configuration

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**Tool Execution Endpoint**: `POST /api/v1/tools/execute`  
**Authentication**: Include in request headers as needed  
**Content-Type**: `application/json`

## 📊 Tool Discovery Endpoints

### List All Available Tools
```http
GET /api/v1/tools/
```

**Query Parameters:**
- `category` (optional): Filter by tool category
- `tags` (optional): Filter by comma-separated tags
- `provider` (optional): Filter by tool provider
- `requires_auth` (optional): Filter by authentication requirement
- `requires_gpu` (optional): Filter by GPU requirement
- `is_streaming` (optional): Filter by streaming capability
- `limit` (default: 20): Maximum results (1-100)
- `offset` (default: 0): Pagination offset

### Get Tool Categories
```http
GET /api/v1/tools/categories
```

Returns all available tool categories with counts.

### Get Tool Schema
```http
GET /api/v1/tools/{tool_name}/schema
```

Returns detailed metadata, parameters, and examples for a specific tool.

### Search Tools
```http
POST /api/v1/tools/search
```

**Request Body:**
```json
{
  "query": "search text",
  "category": "memory",
  "tags": ["conversation", "analysis"],
  "limit": 10
}
```

### Get Tool Recommendations
```http
POST /api/v1/tools/recommend
```

**Request Body:**
```json
{
  "user_query": "I need to analyze my calendar for conflicts",
  "context": "scheduling",
  "max_recommendations": 5
}
```

## 🛠️ Tool Execution Patterns

### Standard Tool Execution
```http
POST /api/v1/tools/execute
```

**Request Body Pattern:**
```json
{
  "tool_name": "tool_name_here",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "user_id": "optional_user_id",
  "conversation_id": "optional_conversation_id",
  "timeout": 30
}
```

### Bulk Tool Execution
```http
POST /api/v1/tools/execute/bulk
```

**Request Body Pattern:**
```json
{
  "executions": [
    {
      "tool_name": "tool1",
      "parameters": {"param": "value"}
    },
    {
      "tool_name": "tool2", 
      "parameters": {"param": "value"}
    }
  ],
  "parallel": true,
  "stop_on_failure": false,
  "max_concurrent": 5
}
```

### Direct Tool Execution
```http
POST /api/v1/tools/{tool_name}/execute
```

**Request Body Pattern:**
```json
{
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

## 🕐 Time & Date Tools

### get_current_time
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "get_current_time",
  "parameters": {
    "timezone": "America/Los_Angeles"
  }
}
```

### calculate_time_difference
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "calculate_time_difference",
  "parameters": {
    "start_date": "2025-06-10",
    "end_date": "2025-06-15"
  }
}
```

### format_date
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "format_date",
  "parameters": {
    "date_string": "2025-06-10",
    "format_string": "MM/dd/yyyy"
  }
}
```

### unix_timestamp
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "unix_timestamp",
  "parameters": {
    "action": "to_date",
    "value": "1717977600",
    "format": "yyyy-MM-dd HH:mm:ss"
  }
}
```

## 🌤️ Weather Tools

### local_weather
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "local_weather",
  "parameters": {
    "location": "San Francisco, CA",
    "data_dir": "/path/to/weather/data"
  }
}
```

### weather_api
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "weather_api",
  "parameters": {
    "location": "San Francisco, CA",
    "units": "metric",
    "forecast": true,
    "days": 3
  }
}
```

### format_weather
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "format_weather",
  "parameters": {
    "weather_data": {...},
    "format": "detailed"
  }
}
```

## 🧠 Memory & Conversation Tools

### extract_conversation_entities
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "extract_conversation_entities",
  "parameters": {
    "conversation_text": "Meeting with John tomorrow at Starbucks on Main Street",
    "conversation_id": "conv_123",
    "min_confidence": 0.7
  }
}
```

### extract_from_conversation_history
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "extract_from_conversation_history",
  "parameters": {
    "conversation_history": "Full conversation history text...",
    "extraction_types": ["people", "places", "events"],
    "max_entity_confidence": 0.9
  }
}
```

### infer_conversation_intent
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "infer_conversation_intent",
  "parameters": {
    "conversation_text": "Can you schedule a meeting with Sarah next Tuesday?",
    "intent_types": ["schedule", "create", "update"],
    "auto_update": false
  }
}
```

## 📅 Calendar Tools

### calendar_query
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "calendar_query",
  "parameters": {
    "action": "get_todays_events",
    "user_id": "user_123"
  }
}
```

```json
{
  "tool_name": "calendar_query",
  "parameters": {
    "action": "get_events_for_date",
    "date": "2025-06-15",
    "user_id": "user_123"
  }
}
```

```json
{
  "tool_name": "calendar_query",
  "parameters": {
    "action": "get_upcoming_events",
    "days": 7,
    "user_id": "user_123"
  }
}
```

```json
{
  "tool_name": "calendar_query",
  "parameters": {
    "action": "query",
    "query": "meetings with team leads this week",
    "user_id": "user_123"
  }
}
```

## 💰 Finance Tools

### finance_tool
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "finance_tool",
  "parameters": {
    "action": "create",
    "transaction_data": {
      "amount": 25.50,
      "description": "Coffee at Starbucks",
      "category": "food",
      "date": "2025-06-10"
    }
  }
}
```

```json
{
  "tool_name": "finance_tool",
  "parameters": {
    "action": "categorize",
    "transaction_id": "txn_123",
    "category": "entertainment"
  }
}
```

### get_recent_expenses
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "get_recent_expenses",
  "parameters": {
    "days": 30,
    "category": "food",
    "min_amount": "10.00",
    "limit": 20
  }
}
```

### search_transactions
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "search_transactions",
  "parameters": {
    "query": "coffee purchases last month",
    "vendor": "",
    "category": "food",
    "start_date": "2025-05-01",
    "end_date": "2025-05-31",
    "min_amount": "",
    "max_amount": "",
    "tags": "",
    "limit": 10
  }
}
```

### get_spending_summary
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "get_spending_summary",
  "parameters": {
    "start_date": "2025-06-01",
    "end_date": "2025-06-10",
    "group_by": "category"
  }
}
```

## 🏥 Health Tools

### health_query
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "health_query",
  "parameters": {
    "action": "get_summary",
    "user_id": "user_123"
  }
}
```

```json
{
  "tool_name": "health_query",
  "parameters": {
    "action": "query",
    "query": "How many steps did I walk yesterday?",
    "user_id": "user_123"
  }
}
```

### health_query_simple
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "health_query_simple",
  "parameters": {
    "query": "show my sleep data for last week",
    "user_id": "user_123"
  }
}
```

### health_summary_simple
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "health_summary_simple",
  "parameters": {
    "user_id": "user_123"
  }
}
```

## 📄 Document Processing Tools

### process_document
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "process_document",
  "parameters": {
    "file_path": "/path/to/document.pdf",
    "use_ocr": true,
    "extract_tables": true,
    "extract_forms": false,
    "extract_images": false,
    "return_metadata_only": false
  }
}
```

### summarize_document
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "summarize_document",
  "parameters": {
    "file_path": "/path/to/document.pdf",
    "max_length": 500,
    "include_key_points": true
  }
}
```

### search_document
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "search_document",
  "parameters": {
    "file_path": "/path/to/document.pdf",
    "query": "quarterly revenue",
    "limit": 5,
    "include_context": true
  }
}
```

### extract_document_text
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "extract_document_text",
  "parameters": {
    "file_path": "/path/to/document.pdf",
    "use_ocr": true,
    "structured": true
  }
}
```

### extract_document_tables
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "extract_document_tables",
  "parameters": {
    "file_path": "/path/to/document.pdf",
    "format": "JSON"
  }
}
```

### convert_document
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "convert_document",
  "parameters": {
    "file_path": "/path/to/input.pdf",
    "output_format": "markdown",
    "output_path": "/path/to/output.md"
  }
}
```

## 📈 Text Analysis Tools

### analyze_sentiment
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "analyze_sentiment",
  "parameters": {
    "text": "I love this new feature! It's amazing.",
    "provider": "local"
  }
}
```

### analyze_text
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "analyze_text",
  "parameters": {
    "text": "Your text to analyze here...",
    "analysis_types": ["sentiment", "entities", "keywords"],
    "provider": "local"
  }
}
```

### detect_language
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "detect_language",
  "parameters": {
    "text": "Bonjour, comment allez-vous?",
    "provider": "local"
  }
}
```

### extract_entities
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "extract_entities",
  "parameters": {
    "text": "John Smith visited New York City last Tuesday.",
    "provider": "local"
  }
}
```

### extract_keywords
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "extract_keywords",
  "parameters": {
    "text": "Your text for keyword extraction...",
    "provider": "local",
    "max_keywords": 10
  }
}
```

### summarize_text
```http
POST /api/v1/tools/execute
```
```json
{
  "tool_name": "summarize_text",
  "parameters": {
    "text": "Long text to summarize...",
    "provider": "local",
    "max_length": 200,
    "format": "bullet_points"
  }
}
```

## 🔧 HTTP Client Pattern for CrewAI Tools

### Python Implementation Template
```python
import requests
import json
from typing import Dict, Any, Optional

def execute_myndy_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    timeout: int = 30
) -> str:
    """Execute a Myndy-AI tool via HTTP API"""
    try:
        url = "http://localhost:8000/api/v1/tools/execute"
        payload = {
            "tool_name": tool_name,
            "parameters": parameters
        }
        
        if user_id:
            payload["user_id"] = user_id
        if conversation_id:
            payload["conversation_id"] = conversation_id
        if timeout != 30:
            payload["timeout"] = timeout
            
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout
        )
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"
    except Exception as e:
        return f"Tool execution failed: {str(e)}"
```

### CrewAI Tool Decorator Pattern
```python
from crewai_tools import tool

@tool
def myndy_time_tool(timezone: str = "UTC") -> str:
    """Get current time in specified timezone using Myndy-AI"""
    return execute_myndy_tool(
        tool_name="get_current_time",
        parameters={"timezone": timezone}
    )

@tool
def myndy_weather_tool(location: str, units: str = "metric") -> str:
    """Get weather information using Myndy-AI"""
    return execute_myndy_tool(
        tool_name="weather_api",
        parameters={
            "location": location,
            "units": units,
            "forecast": True
        }
    )

@tool
def myndy_calendar_tool(action: str, **kwargs) -> str:
    """Query calendar using Myndy-AI"""
    parameters = {"action": action}
    parameters.update(kwargs)
    return execute_myndy_tool(
        tool_name="calendar_query",
        parameters=parameters
    )
```

## 📊 Response Format Standards

### Standard Success Response
```json
{
  "success": true,
  "message": "Tool executed successfully",
  "result": {
    "success": true,
    "output": "Tool output data",
    "execution_time_ms": 150,
    "metadata": {
      "tool_name": "get_current_time",
      "parameters_used": {"timezone": "UTC"},
      "timestamp": "2025-06-10T12:00:00Z"
    }
  }
}
```

### Standard Error Response
```json
{
  "success": false,
  "message": "Tool execution failed",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": "Invalid timezone parameter",
    "suggestions": ["Use IANA timezone format", "Try 'UTC' or 'America/Los_Angeles'"]
  }
}
```

## 🔍 Health Check & Monitoring

### System Health
```http
GET /api/v1/tools/health
```

Returns overall tool system health and statistics.

### Tool-Specific Health
```http
GET /api/v1/tools/{tool_name}/health
```

Returns health status for a specific tool.

---

**API Documentation**: This reference covers the most commonly used tools and endpoints. For complete API documentation, see the FastAPI interactive docs at `http://localhost:8000/docs` when the server is running.

**Authentication**: Some tools may require authentication. Include credentials in the `credentials` field of tool execution requests as needed.

**Rate Limiting**: API endpoints may have rate limiting. Implement appropriate retry logic in production code.

**Last Updated**: 2025-06-10  
**API Version**: v1  
**Tool Count**: 530+ available tools