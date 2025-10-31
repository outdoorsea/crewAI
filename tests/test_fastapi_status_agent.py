#!/usr/bin/env python3
"""
Unit Tests for FastAPI Status Agent

Tests the FastAPI-based Status Agent implementation following Phase 2
of the implementation plan.

File: tests/test_fastapi_status_agent.py
"""

import sys
import json
import logging
import pytest
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.fastapi_status_agent import FastAPIStatusAgent, create_fastapi_status_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFastAPIStatusAgent(unittest.TestCase):
    """Test FastAPI Status Agent implementation"""
    
    def setUp(self):
        """Set up test environment"""
        logger.info("Setting up FastAPI Status Agent tests")
        
    def test_agent_creation(self):
        """Test that FastAPI Status Agent can be created with proper configuration"""
        
        agent = create_fastapi_status_agent("http://localhost:8000")
        
        # Verify agent was created
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, FastAPIStatusAgent)
        
        # Verify API configuration
        self.assertEqual(agent.api_base_url, "http://localhost:8000")
        
        # Verify tools were loaded
        self.assertIsNotNone(agent.tools)
        self.assertGreater(len(agent.tools), 0)
        
        # Verify agent was created
        self.assertIsNotNone(agent.agent)
        
        logger.info(f"✅ Agent created with {len(agent.tools)} tools")
        
    def test_status_tool_integration(self):
        """Test that agent uses HTTP status tools correctly"""
        
        agent = create_fastapi_status_agent()
        
        # Check for status-specific tools
        tool_names = []
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown'))
            tool_names.append(tool_name)
        
        logger.info(f"Status agent tool names: {tool_names}")
        
        # Verify essential status tools are present
        essential_status_tools = [
            'get_current_status', 'update_status',
            'analyze_current_status', 'track_mood_change', 'get_status_history'
        ]
        
        missing_tools = []
        for tool in essential_status_tools:
            if tool not in tool_names:
                missing_tools.append(tool)
        
        self.assertEqual(len(missing_tools), 0, 
                        f"Missing essential status tools: {missing_tools}")
        
        logger.info("✅ Status tool integration verified")
        
    def test_agent_configuration(self):
        """Test that agent is configured correctly for status operations"""
        
        agent = create_fastapi_status_agent()
        
        # Verify agent role and goal
        self.assertEqual(agent.agent.role, "Status Manager")
        self.assertIn("HTTP API calls", agent.agent.goal)
        self.assertIn("status information", agent.agent.goal)
        
        # Verify backstory mentions status management and HTTP architecture
        self.assertIn("Status Manager", agent.agent.backstory)
        self.assertIn("HTTP API calls", agent.agent.backstory)
        self.assertIn("mood patterns", agent.agent.backstory)
        
        # Verify agent settings
        self.assertTrue(agent.agent.verbose)
        self.assertFalse(agent.agent.allow_delegation)
        self.assertEqual(agent.agent.max_iter, 3)
        self.assertEqual(agent.agent.max_execution_time, 90)
        
        logger.info("✅ Status agent configuration verified")
        
    @patch('tools.myndy_http_client.GetCurrentStatusHTTPTool')
    def test_status_analysis_tool(self, mock_status_tool):
        """Test the status analysis tool functionality"""
        
        # Mock the status tool
        mock_instance = Mock()
        mock_status_tool.return_value = mock_instance
        mock_instance._run.return_value = json.dumps({
            "mood": "focused",
            "activity": "work",
            "energy_level": "high",
            "timestamp": "2025-06-10T10:00:00Z"
        })
        
        agent = create_fastapi_status_agent()
        
        # Find the analysis tool
        analysis_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'analyze_current_status':
                analysis_tool = tool
                break
        
        self.assertIsNotNone(analysis_tool, "Status analysis tool not found")
        
        # Test tool execution
        result = analysis_tool("work meeting preparation")
        result_data = json.loads(result)
        
        self.assertIn("current_status", result_data)
        self.assertIn("insights", result_data)
        self.assertIn("recommendations", result_data)
        self.assertEqual(result_data["context"], "work meeting preparation")
        
        logger.info("✅ Status analysis tool verified")
        
    @patch('tools.myndy_http_client.GetCurrentStatusHTTPTool')
    @patch('tools.myndy_http_client.UpdateStatusHTTPTool')
    def test_mood_tracking_tool(self, mock_update_tool, mock_get_tool):
        """Test the mood tracking tool functionality"""
        
        # Mock current status
        mock_get_instance = Mock()
        mock_get_tool.return_value = mock_get_instance
        mock_get_instance._run.return_value = json.dumps({
            "mood": "neutral",
            "activity": "work",
            "energy_level": "medium"
        })
        
        # Mock update status
        mock_update_instance = Mock()
        mock_update_tool.return_value = mock_update_instance
        mock_update_instance._run.return_value = json.dumps({
            "updated": True,
            "timestamp": "2025-06-10T11:00:00Z"
        })
        
        agent = create_fastapi_status_agent()
        
        # Find the mood tracking tool
        mood_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'track_mood_change':
                mood_tool = tool
                break
        
        self.assertIsNotNone(mood_tool, "Mood tracking tool not found")
        
        # Test tool execution
        result = mood_tool("excited", "Just finished a great presentation")
        result_data = json.loads(result)
        
        self.assertTrue(result_data["mood_updated"])
        self.assertEqual(result_data["new_mood"], "excited")
        self.assertEqual(result_data["notes"], "Just finished a great presentation")
        self.assertIn("previous_status", result_data)
        
        logger.info("✅ Mood tracking tool verified")
        
    def test_status_history_tool(self):
        """Test the status history tool functionality"""
        
        agent = create_fastapi_status_agent()
        
        # Find the history tool
        history_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'get_status_history':
                history_tool = tool
                break
        
        self.assertIsNotNone(history_tool, "Status history tool not found")
        
        # Test tool execution
        result = history_tool(14)  # 14 days
        result_data = json.loads(result)
        
        self.assertEqual(result_data["period_days"], 14)
        self.assertIn("historical_trends", result_data)
        self.assertIn("mood_patterns", result_data["historical_trends"])
        self.assertIn("activity_patterns", result_data["historical_trends"])
        self.assertIn("recommendations", result_data)
        
        logger.info("✅ Status history tool verified")
        
    def test_error_handling(self):
        """Test that status tools handle errors gracefully"""
        
        agent = create_fastapi_status_agent()
        
        # Find the analysis tool
        analysis_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'analyze_current_status':
                analysis_tool = tool
                break
        
        self.assertIsNotNone(analysis_tool)
        
        # Test with mock that raises exception
        with patch('tools.myndy_http_client.GetCurrentStatusHTTPTool') as mock_tool:
            mock_instance = Mock()
            mock_tool.return_value = mock_instance
            mock_instance._run.side_effect = Exception("API connection failed")
            
            result = analysis_tool("test context")
            result_data = json.loads(result)
            
            # Verify error is handled gracefully
            self.assertIn("error", result_data)
            self.assertIn("API connection failed", result_data["error"])
            self.assertIsNone(result_data["analysis"])
        
        logger.info("✅ Error handling verified")
        
    def test_status_agent_specialization(self):
        """Test that agent is specialized for status operations"""
        
        agent = create_fastapi_status_agent()
        
        # Verify agent focuses on status-related operations
        role_keywords = ["status", "mood", "activity", "well-being"]
        goal_contains_keywords = any(keyword in agent.agent.goal.lower() for keyword in role_keywords)
        self.assertTrue(goal_contains_keywords, "Agent goal should focus on status operations")
        
        backstory_contains_keywords = any(keyword in agent.agent.backstory.lower() for keyword in role_keywords)
        self.assertTrue(backstory_contains_keywords, "Agent backstory should emphasize status expertise")
        
        # Verify tools are status-focused
        status_tool_count = 0
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown')).lower()
            if any(keyword in tool_name for keyword in ['status', 'mood', 'track', 'analyze']):
                status_tool_count += 1
        
        self.assertGreaterEqual(status_tool_count, 3, "Should have multiple status-focused tools")
        
        logger.info("✅ Status agent specialization verified")
        
    def test_architecture_compliance(self):
        """Test that agent follows service-oriented architecture"""
        
        agent = create_fastapi_status_agent()
        
        # Verify agent mentions HTTP/API architecture
        self.assertIn("HTTP", agent.agent.goal.upper())
        self.assertIn("API", agent.agent.goal.upper())
        self.assertIn("backend", agent.agent.backstory.lower())
        
        # Verify tools use HTTP pattern
        http_based_tools = 0
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown'))
            tool_type = str(type(tool))
            
            if 'HTTP' in tool_type or hasattr(tool, '_run') or hasattr(tool, 'run'):
                http_based_tools += 1
        
        self.assertGreater(http_based_tools, 0, "Agent should have HTTP-based tools")
        
        logger.info("✅ Architecture compliance verified")

def run_fastapi_status_agent_tests():
    """Run all FastAPI Status Agent tests"""
    
    print("🧪 Testing FastAPI Status Agent Implementation")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFastAPIStatusAgent)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All FastAPI Status Agent tests passed!")
        print("✅ Status tool integration verified")
        print("✅ Service-oriented architecture compliance confirmed")
        print("✅ Phase 2 implementation complete")
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_fastapi_status_agent_tests()
    sys.exit(0 if success else 1)