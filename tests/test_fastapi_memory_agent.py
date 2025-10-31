#!/usr/bin/env python3
"""
Unit Tests for FastAPI Memory Agent

Tests the FastAPI-based Memory Agent implementation following Phase 1
of the implementation plan.

File: tests/test_fastapi_memory_agent.py
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

from agents.fastapi_memory_agent import FastAPIMemoryAgent, create_fastapi_memory_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFastAPIMemoryAgent(unittest.TestCase):
    """Test FastAPI Memory Agent implementation"""
    
    def setUp(self):
        """Set up test environment"""
        logger.info("Setting up FastAPI Memory Agent tests")
        self.agent = None
        
    def test_agent_creation(self):
        """Test that FastAPI Memory Agent can be created with proper configuration"""
        
        agent = create_fastapi_memory_agent("http://localhost:8000")
        
        # Verify agent was created
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, FastAPIMemoryAgent)
        
        # Verify API configuration
        self.assertEqual(agent.api_base_url, "http://localhost:8000")
        
        # Verify tools were loaded
        self.assertIsNotNone(agent.tools)
        self.assertGreater(len(agent.tools), 0)
        
        # Verify agent was created
        self.assertIsNotNone(agent.agent)
        
        logger.info(f"✅ Agent created with {len(agent.tools)} tools")
        
    def test_http_tool_integration(self):
        """Test that agent uses HTTP tools correctly"""
        
        agent = create_fastapi_memory_agent()
        
        # Check for HTTP-based tools
        http_tool_count = 0
        tool_names = []
        
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown'))
            tool_names.append(tool_name)
            
            # Check if tool is HTTP-based
            if ('HTTP' in str(type(tool)) or 
                'http' in tool_name.lower() or
                hasattr(tool, '_run') or
                hasattr(tool, 'run')):
                http_tool_count += 1
        
        logger.info(f"Tool names: {tool_names}")
        logger.info(f"HTTP tools: {http_tool_count}/{len(agent.tools)}")
        
        # Verify we have HTTP tools
        self.assertGreater(http_tool_count, 0, "Agent should have HTTP-based tools")
        
        # Verify essential memory tools are present
        essential_tools = [
            'get_self_profile', 'update_self_profile',
            'search_memory', 'create_entity', 'add_fact',
            'search_conversation_memory', 'get_conversation_summary',
            'store_conversation_analysis'
        ]
        
        missing_tools = []
        for tool in essential_tools:
            if tool not in tool_names:
                missing_tools.append(tool)
        
        self.assertEqual(len(missing_tools), 0, 
                        f"Missing essential tools: {missing_tools}")
        
        logger.info("✅ HTTP tool integration verified")
        
    def test_agent_configuration(self):
        """Test that agent is configured correctly for memory operations"""
        
        agent = create_fastapi_memory_agent()
        
        # Verify agent role and goal
        self.assertEqual(agent.agent.role, "Memory Librarian")
        self.assertIn("HTTP API calls", agent.agent.goal)
        self.assertIn("service separation", agent.agent.goal)
        
        # Verify backstory mentions HTTP architecture
        self.assertIn("HTTP API calls", agent.agent.backstory)
        self.assertIn("FastAPI backend", agent.agent.backstory)
        self.assertIn("architectural compliance", agent.agent.backstory)
        
        # Verify agent settings
        self.assertTrue(agent.agent.verbose)
        self.assertFalse(agent.agent.allow_delegation)
        self.assertEqual(agent.agent.max_iter, 3)
        self.assertEqual(agent.agent.max_execution_time, 120)
        
        logger.info("✅ Agent configuration verified")
        
    @patch('agents.fastapi_memory_agent.search_conversation_memory')
    def test_search_memory_tool(self, mock_search):
        """Test the search memory tool functionality"""
        
        # Mock the search response
        mock_search.return_value = json.dumps({
            "results": [
                {
                    "conversation_id": "test-123",
                    "content": "Discussion about project planning",
                    "similarity_score": 0.85,
                    "timestamp": "2025-06-10T10:00:00Z"
                }
            ],
            "total": 1
        })
        
        agent = create_fastapi_memory_agent()
        
        # Find the search tool
        search_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'search_conversation_memory':
                search_tool = tool
                break
        
        self.assertIsNotNone(search_tool, "Search conversation memory tool not found")
        
        # Test tool execution
        result = search_tool("project planning", 5)
        result_data = json.loads(result)
        
        self.assertIn("results", result_data)
        self.assertEqual(len(result_data["results"]), 1)
        self.assertEqual(result_data["results"][0]["conversation_id"], "test-123")
        
        # Verify mock was called correctly
        mock_search.assert_called_once_with("project planning", "default", 5)
        
        logger.info("✅ Search memory tool verified")
        
    @patch('agents.fastapi_memory_agent.get_conversation_summary')
    def test_conversation_summary_tool(self, mock_summary):
        """Test the conversation summary tool functionality"""
        
        # Mock the summary response
        mock_summary.return_value = json.dumps({
            "conversation_id": "test-123",
            "summary": "Discussion about Q2 project planning and resource allocation",
            "entities": ["person:Alice", "project:Q2_Planning"],
            "insights": ["work_pattern", "planning_activity"],
            "timestamp": "2025-06-10T10:00:00Z"
        })
        
        agent = create_fastapi_memory_agent()
        
        # Find the summary tool
        summary_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'get_conversation_summary':
                summary_tool = tool
                break
        
        self.assertIsNotNone(summary_tool, "Conversation summary tool not found")
        
        # Test tool execution
        result = summary_tool("test-123")
        result_data = json.loads(result)
        
        self.assertEqual(result_data["conversation_id"], "test-123")
        self.assertIn("summary", result_data)
        self.assertIn("entities", result_data)
        self.assertIn("insights", result_data)
        
        # Verify mock was called correctly
        mock_summary.assert_called_once_with("test-123")
        
        logger.info("✅ Conversation summary tool verified")
        
    @patch('agents.fastapi_memory_agent.store_conversation_analysis')
    def test_store_analysis_tool(self, mock_store):
        """Test the store conversation analysis tool functionality"""
        
        # Mock the storage response
        mock_store.return_value = json.dumps({
            "conversation_id": "new-456",
            "stored": True,
            "entities_extracted": 3,
            "insights_generated": 2,
            "timestamp": "2025-06-10T10:30:00Z"
        })
        
        agent = create_fastapi_memory_agent()
        
        # Find the store tool
        store_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'store_conversation_analysis':
                store_tool = tool
                break
        
        self.assertIsNotNone(store_tool, "Store conversation analysis tool not found")
        
        # Test tool execution
        conversation_text = "We discussed the new marketing campaign with Sarah and decided to launch next month."
        result = store_tool(conversation_text, "test-456")
        result_data = json.loads(result)
        
        self.assertTrue(result_data["stored"])
        self.assertEqual(result_data["conversation_id"], "new-456")
        self.assertIn("entities_extracted", result_data)
        
        # Verify mock was called correctly
        mock_store.assert_called_once_with(conversation_text, "test-456", "default")
        
        logger.info("✅ Store conversation analysis tool verified")
        
    def test_error_handling(self):
        """Test that tools handle errors gracefully"""
        
        agent = create_fastapi_memory_agent()
        
        # Find the search tool
        search_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'search_conversation_memory':
                search_tool = tool
                break
        
        self.assertIsNotNone(search_tool)
        
        # Test with mock that raises exception
        with patch('agents.fastapi_memory_agent.search_conversation_memory', 
                  side_effect=Exception("API connection failed")):
            
            result = search_tool("test query", 5)
            result_data = json.loads(result)
            
            # Verify error is handled gracefully
            self.assertIn("error", result_data)
            self.assertEqual(result_data["error"], "API connection failed")
            self.assertIn("results", result_data)
            self.assertEqual(result_data["results"], [])
        
        logger.info("✅ Error handling verified")
        
    def test_architecture_compliance(self):
        """Test that agent follows service-oriented architecture"""
        
        agent = create_fastapi_memory_agent()
        
        # Verify agent mentions HTTP/API architecture
        self.assertIn("HTTP", agent.agent.goal.upper())
        self.assertIn("API", agent.agent.goal.upper()) 
        self.assertIn("backend", agent.agent.backstory.lower())
        
        # Verify no direct imports from myndy-ai memory system
        agent_module = sys.modules.get('agents.fastapi_memory_agent')
        if agent_module:
            module_dict = vars(agent_module)
            
            # Check that we don't import forbidden modules
            forbidden_imports = [
                'memory.models', 'qdrant.core', 'agents.tools'
            ]
            
            for forbidden in forbidden_imports:
                for name, obj in module_dict.items():
                    if hasattr(obj, '__module__') and obj.__module__:
                        self.assertNotIn(forbidden, obj.__module__,
                                        f"Found forbidden import: {forbidden} in {name}")
        
        logger.info("✅ Architecture compliance verified")

def run_fastapi_memory_agent_tests():
    """Run all FastAPI Memory Agent tests"""
    
    print("🧪 Testing FastAPI Memory Agent Implementation")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFastAPIMemoryAgent)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All FastAPI Memory Agent tests passed!")
        print("✅ HTTP tool integration verified")
        print("✅ Service-oriented architecture compliance confirmed")
        print("✅ Phase 1 implementation complete")
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_fastapi_memory_agent_tests()
    sys.exit(0 if success else 1)