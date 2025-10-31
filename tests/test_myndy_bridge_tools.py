"""
test_myndy_bridge_tools.py - Comprehensive tests for CrewAI Myndy bridge tools

Tests the bridge tools that connect CrewAI agents with the Myndy-AI backend system,
ensuring proper tool registration, execution, and error handling.

File: tests/test_myndy_bridge_tools.py
"""

import pytest
import json
import httpx
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

# Import the bridge tools to test
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from tools.myndy_bridge import (
        get_all_myndy_tools,
        execute_myndy_tool,
        search_tools_by_category,
        get_tool_metadata,
        MyndyToolBridge
    )
    from tools.myndy_fastapi_client import (
        get_tool_list,
        execute_tool,
        search_memory,
        get_current_status
    )
except ImportError as e:
    pytest.skip(f"Could not import bridge tools: {e}", allow_module_level=True)


class TestMyndyToolBridge:
    """Test suite for the Myndy tool bridge"""
    
    def setup_method(self):
        """Setup method run before each test"""
        self.bridge = MyndyToolBridge(
            base_url="http://localhost:8081",
            api_key="test-api-key"
        )
    
    @patch('httpx.get')
    def test_get_all_myndy_tools_success(self, mock_get):
        """Test successful retrieval of all Myndy tools"""
        # Mock successful tools list response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "tools": [
                {
                    "name": "memory_search",
                    "description": "Search through memory database",
                    "category": "memory",
                    "parameters": {
                        "query": {"type": "string", "required": True},
                        "limit": {"type": "integer", "default": 10}
                    }
                },
                {
                    "name": "get_current_time",
                    "description": "Get the current time",
                    "category": "utility",
                    "parameters": {
                        "timezone": {"type": "string", "default": "UTC"}
                    }
                }
            ],
            "total": 2,
            "categories": ["memory", "utility"]
        }
        mock_get.return_value = mock_response
        
        # Test tool retrieval
        result = get_all_myndy_tools()
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "tools/list" in call_args[0][0]
        
        # Verify response
        assert result["success"] is True
        assert len(result["tools"]) == 2
        assert result["total"] == 2
        assert "memory" in result["categories"]
    
    @patch('httpx.post')
    def test_execute_myndy_tool_success(self, mock_post):
        """Test successful Myndy tool execution"""
        # Mock successful execution response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "tool_name": "memory_search",
            "result": {
                "results": [
                    {"id": "mem1", "title": "Test Memory", "score": 0.95}
                ],
                "total": 1
            },
            "execution_time_ms": 156
        }
        mock_post.return_value = mock_response
        
        # Test tool execution
        result = execute_myndy_tool(
            "memory_search",
            {"query": "test", "limit": 10}
        )
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "tools/execute" in call_args[0][0]
        assert call_args[1]["json"]["tool_name"] == "memory_search"
        assert call_args[1]["json"]["parameters"]["query"] == "test"
        
        # Verify response
        assert result["success"] is True
        assert result["tool_name"] == "memory_search"
        assert "result" in result
    
    @patch('httpx.post')
    def test_execute_myndy_tool_validation_error(self, mock_post):
        """Test tool execution with parameter validation error"""
        # Mock validation error response
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "success": False,
            "error": "Validation failed",
            "details": [
                {
                    "field": "query",
                    "message": "This field is required"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Test with invalid parameters
        result = execute_myndy_tool("memory_search", {})  # Missing required query
        
        # Should return validation error
        assert result["success"] is False
        assert "error" in result
    
    @patch('httpx.get')
    def test_search_tools_by_category_success(self, mock_get):
        """Test successful tool search by category"""
        # Mock category-specific tools response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "category": "memory",
            "tools": [
                {
                    "name": "memory_search",
                    "description": "Search through memory database"
                },
                {
                    "name": "entity_create",
                    "description": "Create a new entity"
                }
            ],
            "tool_count": 2
        }
        mock_get.return_value = mock_response
        
        # Test category search
        result = search_tools_by_category("memory")
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "category/memory" in call_args[0][0]
        
        # Verify response
        assert result["success"] is True
        assert result["category"] == "memory"
        assert len(result["tools"]) == 2
    
    @patch('httpx.get')
    def test_get_tool_metadata_success(self, mock_get):
        """Test successful tool metadata retrieval"""
        # Mock tool metadata response
        tool_name = "memory_search"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": tool_name,
            "description": "Search through memory database using semantic search",
            "category": "memory",
            "version": "2.1",
            "parameters": {
                "query": {
                    "type": "string",
                    "required": True,
                    "description": "Search query text"
                },
                "limit": {
                    "type": "integer", 
                    "required": False,
                    "default": 10,
                    "description": "Maximum results to return"
                }
            },
            "examples": [
                {
                    "description": "Simple search",
                    "input": {"query": "meeting notes", "limit": 5},
                    "output": {"results": [...]}
                }
            ],
            "usage_stats": {
                "total_calls": 1247,
                "avg_execution_time_ms": 156,
                "success_rate": 98.2
            }
        }
        mock_get.return_value = mock_response
        
        # Test metadata retrieval
        result = get_tool_metadata(tool_name)
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert f"tools/{tool_name}" in call_args[0][0]
        
        # Verify response
        assert result["name"] == tool_name
        assert "parameters" in result
        assert "examples" in result
        assert "usage_stats" in result
    
    @patch('httpx.get')
    def test_bridge_network_error_handling(self, mock_get):
        """Test bridge handling of network errors"""
        # Mock network error
        mock_get.side_effect = httpx.ConnectError("Connection refused")
        
        # Test network error handling
        result = get_all_myndy_tools()
        
        # Should handle error gracefully
        assert result["success"] is False
        assert "error" in result
        assert "connection" in str(result["error"]).lower()
    
    def test_bridge_initialization(self):
        """Test bridge initialization with different configurations"""
        # Test with default configuration
        default_bridge = MyndyToolBridge()
        assert default_bridge.base_url is not None
        
        # Test with custom configuration
        custom_bridge = MyndyToolBridge(
            base_url="http://custom:9000",
            api_key="custom-key",
            timeout=30.0
        )
        assert custom_bridge.base_url == "http://custom:9000"
        assert custom_bridge.api_key == "custom-key"
        assert custom_bridge.timeout == 30.0


class TestMyndyFastAPIClient:
    """Test suite for the Myndy FastAPI client"""
    
    @patch('httpx.get')
    def test_get_tool_list_success(self, mock_get):
        """Test successful tool list retrieval via FastAPI client"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tools": [
                {"name": "tool1", "category": "cat1"},
                {"name": "tool2", "category": "cat2"}
            ],
            "total": 2
        }
        mock_get.return_value = mock_response
        
        # Test function
        result = get_tool_list()
        
        # Verify result
        assert "tools" in result
        assert result["total"] == 2
    
    @patch('httpx.post')
    def test_execute_tool_success(self, mock_post):
        """Test successful tool execution via FastAPI client"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "tool_name": "test_tool",
            "result": {"output": "test result"}
        }
        mock_post.return_value = mock_response
        
        # Test function
        result = execute_tool("test_tool", {"param": "value"})
        
        # Verify result
        assert result["success"] is True
        assert result["tool_name"] == "test_tool"
    
    @patch('httpx.post')
    def test_search_memory_client_success(self, mock_post):
        """Test memory search via FastAPI client"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "1", "title": "Test", "score": 0.9}
            ],
            "total": 1,
            "query": "test"
        }
        mock_post.return_value = mock_response
        
        # Test function
        result = search_memory("test")
        
        # Verify result
        assert "results" in result
        assert result["total"] == 1
        assert result["query"] == "test"
    
    @patch('httpx.get')
    def test_get_current_status_success(self, mock_get):
        """Test current status retrieval via FastAPI client"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "mood": "happy",
            "energy_level": 8,
            "timestamp": datetime.now().isoformat()
        }
        mock_get.return_value = mock_response
        
        # Test function
        result = get_current_status()
        
        # Verify result
        assert result["mood"] == "happy"
        assert result["energy_level"] == 8
        assert "timestamp" in result


class TestBridgeToolsIntegration:
    """Integration tests for bridge tools"""
    
    @pytest.mark.integration
    @patch('httpx.get')
    @patch('httpx.post')
    def test_tool_discovery_and_execution_workflow(self, mock_post, mock_get):
        """Test complete workflow: discover tools, get metadata, execute"""
        
        # 1. Mock tool list response
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "success": True,
            "tools": [
                {"name": "memory_search", "category": "memory"}
            ],
            "total": 1
        }
        
        # 2. Mock tool metadata response  
        mock_metadata_response = Mock()
        mock_metadata_response.status_code = 200
        mock_metadata_response.json.return_value = {
            "name": "memory_search",
            "parameters": {
                "query": {"type": "string", "required": True}
            }
        }
        
        # 3. Mock tool execution response
        mock_execution_response = Mock()
        mock_execution_response.status_code = 200
        mock_execution_response.json.return_value = {
            "success": True,
            "tool_name": "memory_search",
            "result": {"results": [], "total": 0}
        }
        
        # Configure mock responses based on URL
        def mock_get_side_effect(url, **kwargs):
            if "tools/list" in url:
                return mock_get_response
            elif "tools/memory_search" in url:
                return mock_metadata_response
            else:
                return mock_get_response
        
        mock_get.side_effect = mock_get_side_effect
        mock_post.return_value = mock_execution_response
        
        # Execute workflow
        # 1. Get available tools
        tools = get_all_myndy_tools()
        assert tools["success"] is True
        assert len(tools["tools"]) == 1
        
        # 2. Get tool metadata
        tool_name = tools["tools"][0]["name"]
        metadata = get_tool_metadata(tool_name)
        assert metadata["name"] == tool_name
        
        # 3. Execute tool
        result = execute_myndy_tool(tool_name, {"query": "test"})
        assert result["success"] is True
        assert result["tool_name"] == tool_name
    
    @pytest.mark.integration
    def test_bridge_error_propagation(self):
        """Test that errors are properly propagated through the bridge"""
        
        with patch('httpx.get') as mock_get:
            # Mock 404 error
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Tool not found"}
            mock_get.return_value = mock_response
            
            # Test error handling
            result = get_tool_metadata("non_existent_tool")
            
            # Error should be propagated
            assert result.get("success") is False or "error" in result


class TestBridgeToolsPerformance:
    """Performance tests for bridge tools"""
    
    @pytest.mark.performance
    @patch('httpx.get')
    def test_tool_list_retrieval_performance(self, mock_get):
        """Test performance of tool list retrieval"""
        import time
        
        # Mock large tool list
        large_tool_list = [
            {
                "name": f"tool_{i}",
                "category": f"category_{i % 10}",
                "description": f"Test tool {i}"
            }
            for i in range(100)  # 100 tools
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "tools": large_tool_list,
            "total": len(large_tool_list)
        }
        mock_get.return_value = mock_response
        
        # Time the operation
        start_time = time.time()
        result = get_all_myndy_tools()
        end_time = time.time()
        
        # Should handle large tool lists efficiently
        assert (end_time - start_time) < 0.5  # Less than 500ms
        assert result["success"] is True
        assert len(result["tools"]) == 100
    
    @pytest.mark.performance
    @patch('httpx.post')
    def test_concurrent_tool_execution_performance(self, mock_post):
        """Test performance of concurrent tool executions"""
        import concurrent.futures
        import time
        
        # Mock execution response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "tool_name": "test_tool",
            "result": {"output": "success"}
        }
        mock_post.return_value = mock_response
        
        def execute_test_tool(i):
            return execute_myndy_tool("test_tool", {"param": f"value_{i}"})
        
        # Execute multiple tools concurrently
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(execute_test_tool, i)
                for i in range(20)
            ]
            results = [
                future.result()
                for future in concurrent.futures.as_completed(futures)
            ]
        end_time = time.time()
        
        # All executions should succeed
        assert len(results) == 20
        assert all(result["success"] for result in results)
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 2.0  # Less than 2 seconds


class TestBridgeToolsErrorHandling:
    """Test error handling in bridge tools"""
    
    @pytest.mark.parametrize("error_type,mock_side_effect", [
        ("connection_error", httpx.ConnectError("Connection failed")),
        ("timeout_error", httpx.TimeoutException("Request timeout")),
        ("http_error", httpx.HTTPStatusError("Bad request", request=Mock(), response=Mock()))
    ])
    @patch('httpx.get')
    def test_network_error_handling(self, mock_get, error_type, mock_side_effect):
        """Test handling of various network errors"""
        # Mock the specific error
        mock_get.side_effect = mock_side_effect
        
        # Test error handling
        result = get_all_myndy_tools()
        
        # Should handle error gracefully
        assert result.get("success") is False
        assert "error" in result
    
    @pytest.mark.parametrize("status_code,error_message", [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (404, "Not Found"), 
        (422, "Validation Error"),
        (500, "Internal Server Error"),
        (503, "Service Unavailable")
    ])
    @patch('httpx.post')
    def test_http_status_code_handling(self, mock_post, status_code, error_message):
        """Test handling of different HTTP status codes"""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {
            "error": error_message,
            "status_code": status_code
        }
        mock_post.return_value = mock_response
        
        # Test error handling
        result = execute_myndy_tool("test_tool", {})
        
        # Should handle HTTP errors appropriately
        assert result.get("success") is False
        assert "error" in result
    
    def test_malformed_response_handling(self):
        """Test handling of malformed API responses"""
        
        with patch('httpx.get') as mock_get:
            # Mock response with invalid JSON
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_get.return_value = mock_response
            
            # Test malformed response handling
            result = get_all_myndy_tools()
            
            # Should handle JSON decode errors
            assert result.get("success") is False
            assert "error" in result


# Test utilities and fixtures
@pytest.fixture
def sample_tool_list():
    """Sample tool list for testing"""
    return {
        "success": True,
        "tools": [
            {
                "name": "memory_search",
                "description": "Search memory database",
                "category": "memory",
                "parameters": {"query": {"type": "string", "required": True}}
            },
            {
                "name": "get_current_time",
                "description": "Get current time",
                "category": "utility", 
                "parameters": {"timezone": {"type": "string", "default": "UTC"}}
            }
        ],
        "total": 2,
        "categories": ["memory", "utility"]
    }

@pytest.fixture
def sample_tool_execution_result():
    """Sample tool execution result for testing"""
    return {
        "success": True,
        "tool_name": "memory_search",
        "result": {
            "results": [
                {"id": "mem1", "title": "Test Memory", "score": 0.95}
            ],
            "total": 1,
            "query": "test"
        },
        "execution_time_ms": 156
    }

if __name__ == "__main__":
    pytest.main([__file__, "-v"])