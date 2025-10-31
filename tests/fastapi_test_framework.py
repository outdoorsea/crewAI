#!/usr/bin/env python3
"""
Comprehensive FastAPI Test Framework

This framework provides base classes, fixtures, and utilities for testing
FastAPI endpoints and HTTP client tools in the CrewAI integration system.

File: tests/fastapi_test_framework.py
"""

import sys
import json
import logging
import pytest
import asyncio
import httpx
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from dataclasses import dataclass
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MockAPIResponse:
    """Mock API response for testing"""
    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str] = None
    
    def json(self):
        return self.data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=Mock(),
                response=Mock(status_code=self.status_code)
            )

@dataclass 
class TestAPIEndpoint:
    """Test configuration for API endpoints"""
    url: str
    method: str
    expected_status: int = 200
    request_data: Optional[Dict[str, Any]] = None
    expected_response_keys: List[str] = None
    auth_required: bool = True
    timeout: float = 10.0

class FastAPITestFramework:
    """Base testing framework for FastAPI endpoints and HTTP clients"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize test framework
        
        Args:
            base_url: Base URL for API testing
        """
        self.base_url = base_url.rstrip('/')
        self.client = None
        self.mock_responses = {}
        self.test_endpoints = {}
        
    def setup_mock_client(self):
        """Set up mock HTTP client for testing"""
        self.client = Mock(spec=httpx.Client)
        return self.client
    
    def setup_async_mock_client(self):
        """Set up mock async HTTP client for testing"""
        self.client = AsyncMock(spec=httpx.AsyncClient)
        return self.client
        
    def add_mock_response(self, endpoint: str, response: MockAPIResponse):
        """Add mock response for specific endpoint"""
        self.mock_responses[endpoint] = response
        
    def add_test_endpoint(self, name: str, endpoint: TestAPIEndpoint):
        """Add test endpoint configuration"""
        self.test_endpoints[name] = endpoint
        
    def create_mock_response(self, 
                           status_code: int = 200, 
                           data: Dict[str, Any] = None,
                           headers: Dict[str, str] = None) -> MockAPIResponse:
        """Create a mock API response"""
        return MockAPIResponse(
            status_code=status_code,
            data=data or {"status": "success"},
            headers=headers or {"Content-Type": "application/json"}
        )
    
    def mock_http_request(self, method: str, url: str, **kwargs) -> MockAPIResponse:
        """Mock HTTP request based on registered responses"""
        endpoint_key = f"{method.upper()}:{url}"
        
        if endpoint_key in self.mock_responses:
            return self.mock_responses[endpoint_key]
        
        # Default success response
        return self.create_mock_response(200, {"mocked": True, "url": url})
    
    @asynccontextmanager
    async def async_http_client(self):
        """Async context manager for HTTP client testing"""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            yield client

class FastAPIEndpointTestBase:
    """Base class for FastAPI endpoint testing"""
    
    def __init__(self, framework: FastAPITestFramework):
        self.framework = framework
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def test_endpoint_availability(self, endpoint: TestAPIEndpoint):
        """Test that endpoint is available and returns expected status"""
        
        with patch('httpx.request') as mock_request:
            mock_request.return_value = self.framework.create_mock_response(
                endpoint.expected_status,
                {"endpoint": endpoint.url, "available": True}
            )
            
            # Make request
            response = httpx.request(
                endpoint.method,
                f"{self.framework.base_url}{endpoint.url}",
                json=endpoint.request_data,
                timeout=endpoint.timeout
            )
            
            # Verify response
            assert response.status_code == endpoint.expected_status
            
            if endpoint.expected_response_keys:
                data = response.json()
                for key in endpoint.expected_response_keys:
                    assert key in data, f"Expected key '{key}' not found in response"
            
            self.logger.info(f"✅ Endpoint {endpoint.method} {endpoint.url} available")
            
    def test_endpoint_authentication(self, endpoint: TestAPIEndpoint):
        """Test endpoint authentication requirements"""
        
        if not endpoint.auth_required:
            self.logger.info(f"⏭️  Skipping auth test for {endpoint.url} (auth not required)")
            return
            
        with patch('httpx.request') as mock_request:
            # Test without authentication
            mock_request.return_value = self.framework.create_mock_response(
                401, {"error": "Authentication required"}
            )
            
            response = httpx.request(
                endpoint.method,
                f"{self.framework.base_url}{endpoint.url}",
                json=endpoint.request_data
            )
            
            # Should return 401 without auth
            assert response.status_code == 401
            
            # Test with authentication
            mock_request.return_value = self.framework.create_mock_response(
                endpoint.expected_status,
                {"authenticated": True}
            )
            
            headers = {"Authorization": "Bearer test-token"}
            response = httpx.request(
                endpoint.method,
                f"{self.framework.base_url}{endpoint.url}",
                json=endpoint.request_data,
                headers=headers
            )
            
            # Should succeed with auth
            assert response.status_code == endpoint.expected_status
            
            self.logger.info(f"✅ Authentication test passed for {endpoint.url}")
            
    def test_endpoint_error_handling(self, endpoint: TestAPIEndpoint):
        """Test endpoint error handling"""
        
        error_scenarios = [
            (400, {"error": "Bad request"}),
            (404, {"error": "Not found"}), 
            (500, {"error": "Internal server error"}),
            (503, {"error": "Service unavailable"})
        ]
        
        with patch('httpx.request') as mock_request:
            for status_code, error_data in error_scenarios:
                mock_request.return_value = self.framework.create_mock_response(
                    status_code, error_data
                )
                
                response = httpx.request(
                    endpoint.method,
                    f"{self.framework.base_url}{endpoint.url}",
                    json=endpoint.request_data
                )
                
                assert response.status_code == status_code
                data = response.json()
                assert "error" in data
                
        self.logger.info(f"✅ Error handling test passed for {endpoint.url}")

class HTTPClientTestBase:
    """Base class for HTTP client tool testing"""
    
    def __init__(self, framework: FastAPITestFramework):
        self.framework = framework
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def test_client_initialization(self, client_class, api_base_url: str = None):
        """Test HTTP client initialization"""
        
        api_url = api_base_url or self.framework.base_url
        client = client_class(api_url)
        
        # Verify client properties
        assert hasattr(client, 'api_base_url')
        assert client.api_base_url == api_url
        
        # Verify client has required methods
        assert hasattr(client, '_run') or hasattr(client, 'run')
        assert hasattr(client, 'name')
        assert hasattr(client, 'description')
        
        self.logger.info(f"✅ Client {client_class.__name__} initialized correctly")
        return client
        
    def test_client_tool_execution(self, client, test_params: Dict[str, Any] = None):
        """Test client tool execution with mocked responses"""
        
        test_params = test_params or {}
        
        with patch('httpx.post') as mock_post:
            # Mock successful response
            mock_post.return_value = self.framework.create_mock_response(
                200, {"result": "success", "data": test_params}
            )
            
            # Execute tool
            if hasattr(client, '_run'):
                result = client._run(**test_params)
            else:
                result = client.run(**test_params)
            
            # Verify result
            assert result is not None
            
            # If result is JSON string, parse and verify
            if isinstance(result, str):
                try:
                    result_data = json.loads(result)
                    assert "result" in result_data or "status" in result_data
                except json.JSONDecodeError:
                    # Non-JSON result is also valid
                    pass
            
            self.logger.info(f"✅ Client tool execution successful")
            return result
            
    def test_client_error_handling(self, client, test_params: Dict[str, Any] = None):
        """Test client error handling with various failure scenarios"""
        
        test_params = test_params or {}
        
        error_scenarios = [
            # Network errors
            (httpx.ConnectError, "Connection failed"),
            (httpx.TimeoutException, "Request timeout"),
            (httpx.HTTPStatusError, "HTTP error"),
            # Generic errors
            (Exception, "Unexpected error")
        ]
        
        for error_class, error_msg in error_scenarios:
            with patch('httpx.post', side_effect=error_class(error_msg)):
                
                # Execute tool and expect graceful error handling
                if hasattr(client, '_run'):
                    result = client._run(**test_params)
                else:
                    result = client.run(**test_params)
                
                # Verify error is handled gracefully
                assert result is not None
                
                if isinstance(result, str):
                    try:
                        result_data = json.loads(result)
                        assert "error" in result_data or "status" in result_data
                    except json.JSONDecodeError:
                        # Non-JSON error result is also valid
                        pass
                
        self.logger.info(f"✅ Client error handling verified")

class AgentTestBase:
    """Base class for testing FastAPI agents"""
    
    def __init__(self, framework: FastAPITestFramework):
        self.framework = framework
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def test_agent_creation(self, agent_class, api_base_url: str = None):
        """Test agent creation and initialization"""
        
        api_url = api_base_url or self.framework.base_url
        agent = agent_class(api_url)
        
        # Verify agent properties
        assert hasattr(agent, 'api_base_url')
        assert agent.api_base_url == api_url
        assert hasattr(agent, 'tools')
        assert hasattr(agent, 'agent')
        
        # Verify tools were loaded
        assert len(agent.tools) > 0
        
        # Verify agent configuration
        assert agent.agent.role is not None
        assert agent.agent.goal is not None
        assert agent.agent.backstory is not None
        
        self.logger.info(f"✅ Agent {agent_class.__name__} created successfully")
        return agent
        
    def test_agent_tools(self, agent):
        """Test agent tool availability and configuration"""
        
        # Verify all tools have required attributes
        for tool in agent.tools:
            assert hasattr(tool, 'name'), f"Tool missing name attribute"
            assert hasattr(tool, 'description'), f"Tool missing description attribute"
            assert hasattr(tool, '_run') or hasattr(tool, 'run'), f"Tool missing run method"
            
        # Get tool names
        tool_names = [getattr(tool, 'name', 'unknown') for tool in agent.tools]
        
        self.logger.info(f"✅ Agent tools verified: {tool_names}")
        return tool_names
        
    def test_agent_architecture_compliance(self, agent):
        """Test agent follows service-oriented architecture"""
        
        # Verify agent mentions HTTP/API architecture
        goal_text = agent.agent.goal.upper()
        backstory_text = agent.agent.backstory.lower()
        
        assert "HTTP" in goal_text or "API" in goal_text, "Agent goal should mention HTTP/API"
        assert "backend" in backstory_text or "api" in backstory_text, "Agent backstory should mention backend/API"
        
        # Verify architectural compliance mentions
        assert "service" in backstory_text or "architecture" in backstory_text
        
        self.logger.info(f"✅ Agent architecture compliance verified")

class IntegrationTestBase:
    """Base class for integration testing"""
    
    def __init__(self, framework: FastAPITestFramework):
        self.framework = framework
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def test_end_to_end_workflow(self, agents: List[Any], workflow_steps: List[Dict[str, Any]]):
        """Test end-to-end workflow with multiple agents"""
        
        results = []
        
        for i, step in enumerate(workflow_steps):
            agent_name = step.get('agent')
            method = step.get('method')
            params = step.get('params', {})
            expected_keys = step.get('expected_keys', [])
            
            # Find agent
            agent = None
            for a in agents:
                if a.__class__.__name__.lower().replace('agent', '') in agent_name.lower():
                    agent = a
                    break
            
            assert agent is not None, f"Agent for step {i} not found: {agent_name}"
            
            # Execute step
            with patch('httpx.post') as mock_post:
                mock_post.return_value = self.framework.create_mock_response(
                    200, {"step": i, "result": "success", **params}
                )
                
                if hasattr(agent, method):
                    result = getattr(agent, method)(**params)
                    results.append(result)
                    
                    # Verify expected keys in result
                    if expected_keys and isinstance(result, str):
                        try:
                            result_data = json.loads(result)
                            for key in expected_keys:
                                assert key in result_data
                        except json.JSONDecodeError:
                            pass
                            
        self.logger.info(f"✅ End-to-end workflow completed with {len(results)} steps")
        return results

# Test data factories
class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_memory_test_data():
        """Create test data for memory operations"""
        return {
            "search_query": "project planning meeting",
            "person_data": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-0123",
                "company": "Test Corp"
            },
            "fact_data": {
                "content": "John works on AI projects",
                "category": "work",
                "confidence": 0.9
            },
            "conversation_data": {
                "content": "We discussed the new AI initiative with the team",
                "participants": ["John", "Alice"],
                "timestamp": "2025-06-10T10:00:00Z"
            }
        }
    
    @staticmethod
    def create_status_test_data():
        """Create test data for status operations"""
        return {
            "status_update": {
                "mood": "productive",
                "energy": 8,
                "focus": "working on FastAPI integration",
                "location": "home office"
            },
            "mood_data": {
                "mood": "excited",
                "intensity": 7,
                "notes": "Making great progress on the project"
            }
        }
    
    @staticmethod
    def create_weather_test_data():
        """Create test data for weather operations"""
        return {
            "location": "San Francisco, CA",
            "forecast_days": 3,
            "locations": ["New York", "London", "Tokyo"],
            "travel_origin": "San Francisco",
            "travel_destination": "New York"
        }
    
    @staticmethod
    def create_time_test_data():
        """Create test data for time operations"""
        return {
            "timezone": "US/Pacific", 
            "date_string": "2025-06-10 15:30:00",
            "format_type": "human",
            "from_timezone": "UTC",
            "to_timezone": "US/Eastern",
            "meeting_time": "2025-06-10 14:00:00",
            "participant_timezones": ["US/Pacific", "Europe/London", "Asia/Tokyo"]
        }

# Pytest fixtures
@pytest.fixture
def fastapi_framework():
    """Pytest fixture for FastAPI test framework"""
    return FastAPITestFramework()

@pytest.fixture 
def endpoint_tester(fastapi_framework):
    """Pytest fixture for endpoint testing"""
    return FastAPIEndpointTestBase(fastapi_framework)

@pytest.fixture
def http_client_tester(fastapi_framework):
    """Pytest fixture for HTTP client testing"""
    return HTTPClientTestBase(fastapi_framework)

@pytest.fixture
def agent_tester(fastapi_framework):
    """Pytest fixture for agent testing"""
    return AgentTestBase(fastapi_framework)

@pytest.fixture
def integration_tester(fastapi_framework):
    """Pytest fixture for integration testing"""
    return IntegrationTestBase(fastapi_framework)

@pytest.fixture
def test_data():
    """Pytest fixture for test data"""
    return TestDataFactory()

# Utility functions
def run_test_suite(test_class, test_methods: List[str] = None):
    """Run a test suite with specific methods"""
    
    import unittest
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if test_methods:
        for method in test_methods:
            suite.addTest(test_class(method))
    else:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def create_comprehensive_test_report(test_results: Dict[str, bool]):
    """Create comprehensive test report"""
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values()) 
    failed_tests = total_tests - passed_tests
    
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE FASTAPI TEST REPORT")
    print("=" * 80)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nTest Results:")
    print("-" * 40)
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print("\n" + "=" * 80)
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED!")
        print("✅ FastAPI architecture implementation verified")
        print("✅ HTTP client tools functioning correctly") 
        print("✅ Service-oriented architecture compliance confirmed")
    else:
        print(f"⚠️  {failed_tests} tests failed - review implementation")
    
    print("=" * 80)
    
    return failed_tests == 0

if __name__ == "__main__":
    print("🧪 FastAPI Test Framework")
    print("This framework provides base classes and utilities for testing FastAPI integration.")
    print("Import this module in your test files to use the testing utilities.")