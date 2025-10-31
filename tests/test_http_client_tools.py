"""
test_http_client_tools.py - Comprehensive tests for CrewAI HTTP client tools

This module provides comprehensive testing for all HTTP client tools used by CrewAI agents
to communicate with the Myndy-AI FastAPI backend, ensuring proper client-side functionality,
error handling, and API integration.

File: tests/test_http_client_tools.py
"""

import pytest
import json
import httpx
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from typing import Dict, Any, List

# Import the HTTP client tools to test
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from tools.memory_http_tools import MemoryAPIClient, search_memory, store_memory, get_entity, create_entity
from tools.weather_http_tools import WeatherAPIClient, get_current_weather, get_weather_forecast
from tools.time_http_tools import TimeAPIClient, get_current_time, get_timezone_info
from tools.shadow_agent_http_tools import ShadowAgentAPIClient, update_context, get_behavioral_insights


class TestMemoryHTTPClientTools:
    """Test suite for memory HTTP client tools"""
    
    def setup_method(self):
        """Setup method run before each test"""
        self.base_url = "http://localhost:8081"
        self.api_key = "test-api-key"
        self.client = MemoryAPIClient(base_url=self.base_url, api_key=self.api_key)
    
    @patch('httpx.post')
    def test_memory_search_success(self, mock_post):
        """Test successful memory search API call"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "results": [
                {
                    "id": "test-memory-1",
                    "title": "Test Memory",
                    "content": "Test memory content",
                    "score": 0.95
                }
            ],
            "total": 1,
            "query": "test query"
        }
        mock_post.return_value = mock_response
        
        # Test the search function
        result = search_memory("test query", limit=10)
        
        # Verify the API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0].endswith("/api/v1/memory/search")
        assert call_args[1]["json"]["query"] == "test query"
        assert call_args[1]["json"]["limit"] == 10
        
        # Verify the response
        assert "success" in result
        assert "results" in result
        assert result["total"] == 1
    
    @patch('httpx.post')
    def test_memory_search_api_error(self, mock_post):
        """Test memory search with API error"""
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_post.return_value = mock_response
        
        # Test error handling
        result = search_memory("test query")
        
        # Should return error response
        assert "error" in result
        assert result["success"] is False
    
    @patch('httpx.post')
    def test_memory_search_network_error(self, mock_post):
        """Test memory search with network error"""
        # Mock network error
        mock_post.side_effect = httpx.ConnectError("Connection failed")
        
        # Test network error handling
        result = search_memory("test query")
        
        # Should return error response with fallback
        assert "error" in result
        assert result["success"] is False
        assert "Connection failed" in str(result.get("error", ""))
    
    @patch('httpx.post')
    def test_store_memory_success(self, mock_post):
        """Test successful memory storage"""
        # Mock successful storage response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "success": True,
            "id": "new-memory-123",
            "message": "Memory stored successfully"
        }
        mock_post.return_value = mock_response
        
        # Test memory storage
        memory_data = {
            "title": "Test Memory",
            "content": "Test memory content",
            "type": "general"
        }
        result = store_memory(memory_data)
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0].endswith("/api/v1/memory/store")
        assert call_args[1]["json"]["title"] == "Test Memory"
        
        # Verify response
        assert result["success"] is True
        assert "id" in result
    
    @patch('httpx.get')
    def test_get_entity_success(self, mock_get):
        """Test successful entity retrieval"""
        # Mock successful entity response
        entity_id = "test-entity-123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": entity_id,
            "type": "person",
            "name": "Test Person",
            "metadata": {"email": "test@example.com"}
        }
        mock_get.return_value = mock_response
        
        # Test entity retrieval
        result = get_entity(entity_id)
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert entity_id in call_args[0][0]
        
        # Verify response
        assert result["id"] == entity_id
        assert result["type"] == "person"
    
    @patch('httpx.get')
    def test_get_entity_not_found(self, mock_get):
        """Test entity retrieval when entity not found"""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Entity not found"}
        mock_get.return_value = mock_response
        
        # Test entity retrieval
        result = get_entity("non-existent-id")
        
        # Should return error response
        assert "error" in result
        assert result.get("success") is False
    
    @patch('httpx.post')
    def test_create_entity_success(self, mock_post):
        """Test successful entity creation"""
        # Mock successful creation response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "success": True,
            "id": "new-entity-456",
            "type": "person",
            "name": "New Person"
        }
        mock_post.return_value = mock_response
        
        # Test entity creation
        entity_data = {
            "type": "person",
            "name": "New Person",
            "metadata": {"email": "new@example.com"}
        }
        result = create_entity(entity_data)
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0].endswith("/api/v1/memory/entities")
        assert call_args[1]["json"]["type"] == "person"
        
        # Verify response
        assert result["success"] is True
        assert "id" in result


class TestWeatherHTTPClientTools:
    """Test suite for weather HTTP client tools"""
    
    def setup_method(self):
        """Setup method run before each test"""
        self.base_url = "http://localhost:8081"
        self.api_key = "test-api-key"
        self.client = WeatherAPIClient(base_url=self.base_url, api_key=self.api_key)
    
    @patch('httpx.get')
    def test_get_current_weather_success(self, mock_get):
        """Test successful current weather retrieval"""
        # Mock successful weather response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "location": "New York, NY",
            "current": {
                "temperature": 22,
                "condition": "sunny",
                "humidity": 65,
                "wind_speed": 10
            },
            "timestamp": datetime.now().isoformat()
        }
        mock_get.return_value = mock_response
        
        # Test weather retrieval
        result = get_current_weather("New York")
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "weather" in call_args[0][0]
        
        # Verify response
        assert result["success"] is True
        assert result["location"] == "New York, NY"
        assert "current" in result
    
    @patch('httpx.get')
    def test_get_current_weather_invalid_location(self, mock_get):
        """Test weather retrieval with invalid location"""
        # Mock error response for invalid location
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "success": False,
            "error": "Invalid location specified"
        }
        mock_get.return_value = mock_response
        
        # Test with invalid location
        result = get_current_weather("InvalidLocation123")
        
        # Should return error response
        assert result["success"] is False
        assert "error" in result
    
    @patch('httpx.get')
    def test_get_weather_forecast_success(self, mock_get):
        """Test successful weather forecast retrieval"""
        # Mock successful forecast response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "location": "Los Angeles, CA",
            "forecast": [
                {
                    "date": "2025-08-16",
                    "high": 28,
                    "low": 18,
                    "condition": "partly cloudy"
                },
                {
                    "date": "2025-08-17", 
                    "high": 30,
                    "low": 20,
                    "condition": "sunny"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Test forecast retrieval
        result = get_weather_forecast("Los Angeles", days=2)
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "forecast" in call_args[0][0]
        
        # Verify response
        assert result["success"] is True
        assert len(result["forecast"]) == 2
    
    @patch('httpx.get')
    def test_weather_client_timeout_handling(self, mock_get):
        """Test weather client timeout handling"""
        # Mock timeout error
        mock_get.side_effect = httpx.TimeoutException("Request timeout")
        
        # Test timeout handling
        result = get_current_weather("New York")
        
        # Should handle timeout gracefully
        assert result["success"] is False
        assert "timeout" in str(result.get("error", "")).lower()


class TestTimeHTTPClientTools:
    """Test suite for time HTTP client tools"""
    
    def setup_method(self):
        """Setup method run before each test"""
        self.base_url = "http://localhost:8081"
        self.api_key = "test-api-key"
        self.client = TimeAPIClient(base_url=self.base_url, api_key=self.api_key)
    
    @patch('httpx.get')
    def test_get_current_time_success(self, mock_get):
        """Test successful current time retrieval"""
        # Mock successful time response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "current_time": "2025-08-15T14:30:00-04:00",
            "timezone": "America/New_York",
            "formatted": "Thursday, August 15, 2025 at 2:30 PM EDT"
        }
        mock_get.return_value = mock_response
        
        # Test time retrieval
        result = get_current_time("America/New_York")
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "time" in call_args[0][0]
        
        # Verify response
        assert result["success"] is True
        assert "current_time" in result
        assert result["timezone"] == "America/New_York"
    
    @patch('httpx.get')
    def test_get_current_time_invalid_timezone(self, mock_get):
        """Test time retrieval with invalid timezone"""
        # Mock error response for invalid timezone
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "success": False,
            "error": "Invalid timezone specified"
        }
        mock_get.return_value = mock_response
        
        # Test with invalid timezone
        result = get_current_time("Invalid/Timezone")
        
        # Should return error response
        assert result["success"] is False
        assert "error" in result
    
    @patch('httpx.get')
    def test_get_timezone_info_success(self, mock_get):
        """Test successful timezone info retrieval"""
        # Mock successful timezone info response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "timezone": "Europe/London",
            "offset": "+01:00",
            "dst_active": True,
            "abbreviation": "BST"
        }
        mock_get.return_value = mock_response
        
        # Test timezone info retrieval
        result = get_timezone_info("Europe/London")
        
        # Verify response
        assert result["success"] is True
        assert result["timezone"] == "Europe/London"
        assert "offset" in result
    
    def test_time_client_initialization(self):
        """Test time client initialization with different parameters"""
        # Test with custom base URL and API key
        custom_client = TimeAPIClient(
            base_url="http://custom:8080",
            api_key="custom-key"
        )
        
        assert custom_client.base_url == "http://custom:8080"
        assert custom_client.api_key == "custom-key"
    
    @patch('httpx.get')
    def test_time_client_authentication(self, mock_get):
        """Test that time client includes proper authentication"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response
        
        # Make request
        get_current_time("UTC")
        
        # Verify authentication headers were included
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]
        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == self.api_key


class TestShadowAgentHTTPClientTools:
    """Test suite for shadow agent HTTP client tools"""
    
    def setup_method(self):
        """Setup method run before each test"""
        self.base_url = "http://localhost:8081"
        self.api_key = "test-api-key"
        self.client = ShadowAgentAPIClient(base_url=self.base_url, api_key=self.api_key)
    
    @patch('httpx.post')
    def test_update_context_success(self, mock_post):
        """Test successful context update"""
        # Mock successful context update response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "context_id": "context-123",
            "message": "Context updated successfully"
        }
        mock_post.return_value = mock_response
        
        # Test context update
        context_data = {
            "user_activity": "working",
            "mood_indicators": ["focused", "productive"],
            "location": "office"
        }
        result = update_context(context_data)
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "context" in call_args[0][0]
        assert call_args[1]["json"]["user_activity"] == "working"
        
        # Verify response
        assert result["success"] is True
        assert "context_id" in result
    
    @patch('httpx.get')
    def test_get_behavioral_insights_success(self, mock_get):
        """Test successful behavioral insights retrieval"""
        # Mock successful insights response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "insights": {
                "productivity_score": 8.5,
                "mood_trend": "positive",
                "activity_patterns": {
                    "most_productive_time": "10:00-12:00",
                    "common_interruptions": ["email", "meetings"]
                },
                "recommendations": [
                    "Schedule focused work during peak hours",
                    "Consider email batch processing"
                ]
            },
            "analysis_period": "7_days"
        }
        mock_get.return_value = mock_response
        
        # Test insights retrieval
        result = get_behavioral_insights(period="7_days")
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "insights" in call_args[0][0] or "behavioral" in call_args[0][0]
        
        # Verify response
        assert result["success"] is True
        assert "insights" in result
        assert result["insights"]["productivity_score"] == 8.5
    
    @patch('httpx.post')
    def test_update_context_validation_error(self, mock_post):
        """Test context update with validation error"""
        # Mock validation error response
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "success": False,
            "error": "Validation failed",
            "details": "user_activity is required"
        }
        mock_post.return_value = mock_response
        
        # Test with invalid context data
        invalid_data = {}  # Missing required fields
        result = update_context(invalid_data)
        
        # Should return validation error
        assert result["success"] is False
        assert "error" in result


class TestHTTPClientToolsIntegration:
    """Integration tests for HTTP client tools"""
    
    @pytest.mark.integration
    def test_client_tool_coordination(self):
        """Test coordination between different client tools"""
        # This would test how different HTTP clients work together
        # For now, we'll test that they can be instantiated together
        
        memory_client = MemoryAPIClient()
        weather_client = WeatherAPIClient()
        time_client = TimeAPIClient()
        shadow_client = ShadowAgentAPIClient()
        
        # Verify all clients are properly initialized
        assert memory_client is not None
        assert weather_client is not None
        assert time_client is not None
        assert shadow_client is not None
    
    @patch('httpx.post')
    @patch('httpx.get')
    def test_multi_client_workflow(self, mock_get, mock_post):
        """Test a workflow using multiple HTTP clients"""
        # Mock responses for different clients
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"success": True, "data": "test"}
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True, "id": "test-123"}
        
        # Simulate a workflow: get time, check weather, store memory
        time_result = get_current_time("UTC")
        weather_result = get_current_weather("New York")
        memory_result = store_memory({"title": "Test", "content": "Test workflow"})
        
        # Verify all operations succeeded
        assert time_result["success"] is True
        assert weather_result["success"] is True
        assert memory_result["success"] is True


class TestHTTPClientToolsErrorHandling:
    """Test error handling across all HTTP client tools"""
    
    @pytest.mark.parametrize("tool_function,args", [
        (search_memory, ("test query",)),
        (get_current_weather, ("New York",)),
        (get_current_time, ("UTC",)),
        (update_context, ({"activity": "test"},))
    ])
    @patch('httpx.post')
    @patch('httpx.get')
    def test_network_error_handling(self, mock_get, mock_post, tool_function, args):
        """Test network error handling across all tools"""
        # Mock network errors
        mock_get.side_effect = httpx.ConnectError("Connection failed")
        mock_post.side_effect = httpx.ConnectError("Connection failed")
        
        # Test error handling
        result = tool_function(*args)
        
        # All tools should handle network errors gracefully
        assert "error" in result or result.get("success") is False
    
    @pytest.mark.parametrize("status_code,expected_error", [
        (400, "Bad Request"),
        (401, "Unauthorized"), 
        (404, "Not Found"),
        (422, "Validation Error"),
        (500, "Internal Server Error")
    ])
    @patch('httpx.get')
    def test_http_error_code_handling(self, mock_get, status_code, expected_error):
        """Test HTTP error code handling"""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"error": expected_error}
        mock_get.return_value = mock_response
        
        # Test with a sample function
        result = get_current_time("UTC")
        
        # Should handle HTTP errors appropriately
        assert result.get("success") is False or "error" in result


class TestHTTPClientToolsPerformance:
    """Performance tests for HTTP client tools"""
    
    @pytest.mark.performance
    @patch('httpx.get')
    def test_client_response_time(self, mock_get):
        """Test HTTP client response times"""
        import time
        
        # Mock quick response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_get.return_value = mock_response
        
        # Time the operation
        start_time = time.time()
        result = get_current_time("UTC")
        end_time = time.time()
        
        # Response should be quick (mocked, so very fast)
        assert (end_time - start_time) < 0.1  # Less than 100ms
        assert result["success"] is True
    
    @pytest.mark.performance
    @patch('httpx.post')
    def test_concurrent_client_operations(self, mock_post):
        """Test concurrent HTTP client operations"""
        import concurrent.futures
        import time
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "id": "test"}
        mock_post.return_value = mock_response
        
        def store_test_memory(index):
            return store_memory({"title": f"Test {index}", "content": f"Content {index}"})
        
        # Run concurrent operations
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(store_test_memory, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        # All operations should succeed
        assert len(results) == 10
        assert all(result["success"] for result in results)
        
        # Concurrent operations should be faster than sequential
        assert (end_time - start_time) < 1.0  # Should complete within 1 second


class TestHTTPClientToolsConfiguration:
    """Test configuration and setup of HTTP client tools"""
    
    def test_client_default_configuration(self):
        """Test default configuration values"""
        # Test memory client defaults
        memory_client = MemoryAPIClient()
        assert memory_client.base_url is not None
        assert memory_client.api_key is not None
        
        # Test weather client defaults
        weather_client = WeatherAPIClient()
        assert weather_client.base_url is not None
        
        # Test time client defaults
        time_client = TimeAPIClient()
        assert time_client.base_url is not None
    
    def test_client_custom_configuration(self):
        """Test custom configuration values"""
        custom_base_url = "http://custom-api:8080"
        custom_api_key = "custom-test-key"
        
        # Test with custom configuration
        memory_client = MemoryAPIClient(
            base_url=custom_base_url,
            api_key=custom_api_key
        )
        
        assert memory_client.base_url == custom_base_url
        assert memory_client.api_key == custom_api_key
    
    @patch.dict('os.environ', {
        'CREWAI_MYNDY_API_URL': 'http://env-api:8080',
        'MYNDY_API_KEY': 'env-api-key'
    })
    def test_client_environment_configuration(self):
        """Test configuration from environment variables"""
        # Create client without explicit config (should use env vars)
        client = MemoryAPIClient()
        
        # Should use environment configuration
        assert client.base_url == "http://env-api:8080"
        assert client.api_key == "env-api-key"


# Additional test utilities and fixtures
@pytest.fixture
def mock_successful_response():
    """Fixture providing a mock successful HTTP response"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "success": True,
        "data": "test_data",
        "timestamp": datetime.now().isoformat()
    }
    return response

@pytest.fixture  
def mock_error_response():
    """Fixture providing a mock error HTTP response"""
    response = Mock()
    response.status_code = 500
    response.json.return_value = {
        "success": False,
        "error": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }
    return response

# Test data generators
def generate_test_memory_data(count: int = 5) -> List[Dict[str, Any]]:
    """Generate test memory data"""
    return [
        {
            "title": f"Test Memory {i}",
            "content": f"Test content for memory {i}",
            "type": "general",
            "metadata": {"source": "test", "index": i}
        }
        for i in range(count)
    ]

def generate_test_weather_data() -> Dict[str, Any]:
    """Generate test weather data"""
    return {
        "success": True,
        "location": "Test City",
        "current": {
            "temperature": 22,
            "condition": "sunny",
            "humidity": 65,
            "wind_speed": 10
        },
        "forecast": [
            {
                "date": "2025-08-16",
                "high": 25,
                "low": 15,
                "condition": "partly cloudy"
            }
        ]
    }

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])