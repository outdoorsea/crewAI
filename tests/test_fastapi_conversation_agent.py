#!/usr/bin/env python3
"""
Unit Tests for FastAPI Conversation Agent

Tests the FastAPI-based Conversation Agent implementation following Phase 3
of the implementation plan.

File: tests/test_fastapi_conversation_agent.py
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

from agents.fastapi_conversation_agent import FastAPIConversationAgent, create_fastapi_conversation_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFastAPIConversationAgent(unittest.TestCase):
    """Test FastAPI Conversation Agent implementation"""
    
    def setUp(self):
        """Set up test environment"""
        logger.info("Setting up FastAPI Conversation Agent tests")
        
    def test_agent_creation(self):
        """Test that FastAPI Conversation Agent can be created with proper configuration"""
        
        agent = create_fastapi_conversation_agent("http://localhost:8000")
        
        # Verify agent was created
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, FastAPIConversationAgent)
        
        # Verify API configuration
        self.assertEqual(agent.api_base_url, "http://localhost:8000")
        
        # Verify tools were loaded
        self.assertIsNotNone(agent.tools)
        self.assertGreater(len(agent.tools), 0)
        
        # Verify agent was created
        self.assertIsNotNone(agent.agent)
        
        # Verify conversation analyzer
        self.assertIsNotNone(agent.conversation_analyzer)
        
        logger.info(f"✅ Agent created with {len(agent.tools)} tools")
        
    def test_conversation_tool_integration(self):
        """Test that agent uses conversation analysis tools correctly"""
        
        agent = create_fastapi_conversation_agent()
        
        # Check for conversation-specific tools
        tool_names = []
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown'))
            tool_names.append(tool_name)
        
        logger.info(f"Conversation agent tool names: {tool_names}")
        
        # Verify essential conversation analysis tools are present
        essential_conversation_tools = [
            'extract_conversation_entities', 'infer_conversation_intent',
            'store_conversation_analysis', 'search_conversations',
            'get_conversation_summary', 'analyze_conversation_sentiment',
            'extract_conversation_topics', 'analyze_conversation_relationships'
        ]
        
        missing_tools = []
        for tool in essential_conversation_tools:
            if tool not in tool_names:
                missing_tools.append(tool)
        
        self.assertEqual(len(missing_tools), 0, 
                        f"Missing essential conversation tools: {missing_tools}")
        
        logger.info("✅ Conversation tool integration verified")
        
    def test_agent_configuration(self):
        """Test that agent is configured correctly for conversation analysis"""
        
        agent = create_fastapi_conversation_agent()
        
        # Verify agent role and goal
        self.assertEqual(agent.agent.role, "Conversation Analyst")
        self.assertIn("conversation", agent.agent.goal.lower())
        self.assertIn("HTTP API calls", agent.agent.goal)
        
        # Verify backstory mentions conversation analysis and HTTP architecture
        self.assertIn("Conversation Analyst", agent.agent.backstory)
        self.assertIn("HTTP API calls", agent.agent.backstory)
        self.assertIn("conversation", agent.agent.backstory.lower())
        self.assertIn("insights", agent.agent.backstory.lower())
        
        # Verify agent settings for complex analysis
        self.assertTrue(agent.agent.verbose)
        self.assertFalse(agent.agent.allow_delegation)
        self.assertEqual(agent.agent.max_iter, 4)  # More iterations for analysis
        self.assertEqual(agent.agent.max_execution_time, 150)  # More time for thorough analysis
        
        logger.info("✅ Conversation agent configuration verified")
        
    def test_entity_extraction_tool(self):
        """Test the entity extraction tool functionality"""
        
        agent = create_fastapi_conversation_agent()
        
        # Find the entity extraction tool
        entity_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'extract_conversation_entities':
                entity_tool = tool
                break
        
        self.assertIsNotNone(entity_tool, "Entity extraction tool not found")
        
        # Test tool execution with sample conversation
        test_conversation = "I met with Sarah Johnson at Microsoft yesterday to discuss the project timeline. We decided to schedule a follow-up meeting next week in Seattle."
        
        result = entity_tool(test_conversation)
        result_data = json.loads(result)
        
        self.assertIn("entities", result_data)
        self.assertIn("entity_count", result_data)
        self.assertIn("entities_by_type", result_data)
        self.assertGreater(result_data["entity_count"], 0)
        
        logger.info("✅ Entity extraction tool verified")
        
    def test_intent_inference_tool(self):
        """Test the intent inference tool functionality"""
        
        agent = create_fastapi_conversation_agent()
        
        # Find the intent inference tool
        intent_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'infer_conversation_intent':
                intent_tool = tool
                break
        
        self.assertIsNotNone(intent_tool, "Intent inference tool not found")
        
        # Test tool execution with sample conversation
        test_conversation = "I need help with the quarterly report. Can you schedule a meeting with the team to discuss the deadline?"
        
        result = intent_tool(test_conversation, "work context")
        result_data = json.loads(result)
        
        self.assertIn("primary_intent", result_data)
        self.assertIn("intent_categories", result_data)
        self.assertIn("emotional_tone", result_data)
        self.assertIn("action_required", result_data)
        self.assertTrue(result_data["action_required"])  # Help-seeking should require action
        
        logger.info("✅ Intent inference tool verified")
        
    def test_sentiment_analysis_tool(self):
        """Test the sentiment analysis tool functionality"""
        
        agent = create_fastapi_conversation_agent()
        
        # Find the sentiment analysis tool
        sentiment_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'analyze_conversation_sentiment':
                sentiment_tool = tool
                break
        
        self.assertIsNotNone(sentiment_tool, "Sentiment analysis tool not found")
        
        # Test with positive conversation
        positive_conversation = "I'm so excited about the new project! This is going to be amazing and I can't wait to get started."
        
        result = sentiment_tool(positive_conversation)
        result_data = json.loads(result)
        
        self.assertIn("overall_sentiment", result_data)
        self.assertIn("sentiment_score", result_data)
        self.assertIn("emotional_indicators", result_data)
        self.assertEqual(result_data["overall_sentiment"], "positive")
        self.assertGreater(result_data["sentiment_score"], 0)
        
        logger.info("✅ Sentiment analysis tool verified")
        
    def test_topic_extraction_tool(self):
        """Test the topic extraction tool functionality"""
        
        agent = create_fastapi_conversation_agent()
        
        # Find the topic extraction tool
        topic_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'extract_conversation_topics':
                topic_tool = tool
                break
        
        self.assertIsNotNone(topic_tool, "Topic extraction tool not found")
        
        # Test with topic-rich conversation
        work_conversation = "We need to finish the software project by the deadline. The client meeting is scheduled for next week to demo the new app features."
        
        result = topic_tool(work_conversation)
        result_data = json.loads(result)
        
        self.assertIn("main_topics", result_data)
        self.assertIn("topic_categories", result_data)
        self.assertIn("keywords", result_data)
        
        # Should detect work-related topics
        topic_categories = [cat["category"] for cat in result_data["topic_categories"]]
        self.assertIn("work", topic_categories)
        
        logger.info("✅ Topic extraction tool verified")
        
    def test_relationship_analysis_tool(self):
        """Test the relationship analysis tool functionality"""
        
        agent = create_fastapi_conversation_agent()
        
        # Find the relationship analysis tool
        relationship_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'analyze_conversation_relationships':
                relationship_tool = tool
                break
        
        self.assertIsNotNone(relationship_tool, "Relationship analysis tool not found")
        
        # Test with relationship-rich conversation
        relationship_conversation = "I talked to my colleague John about the project. My boss Sarah wants us to meet with the client next week."
        
        result = relationship_tool(relationship_conversation)
        result_data = json.loads(result)
        
        self.assertIn("mentioned_people", result_data)
        self.assertIn("relationship_types", result_data)
        self.assertIn("interaction_patterns", result_data)
        
        # Should detect professional relationships
        relationship_types = [rel["type"] for rel in result_data["relationship_types"]]
        self.assertIn("professional", relationship_types)
        
        logger.info("✅ Relationship analysis tool verified")
        
    @patch('tools.conversation_memory_persistence.store_conversation_analysis')
    def test_conversation_storage_tool(self, mock_store):
        """Test the conversation storage tool functionality"""
        
        # Mock the storage response
        mock_store.return_value = json.dumps({
            "conversation_id": "test-456",
            "stored": True,
            "entities_extracted": 5,
            "insights_generated": 3,
            "timestamp": "2025-06-10T12:00:00Z"
        })
        
        agent = create_fastapi_conversation_agent()
        
        # Find the storage tool
        storage_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'store_conversation_analysis':
                storage_tool = tool
                break
        
        self.assertIsNotNone(storage_tool, "Conversation storage tool not found")
        
        # Test tool execution
        test_conversation = "Let's discuss the quarterly planning for next year."
        result = storage_tool(test_conversation, "planning-session-123")
        result_data = json.loads(result)
        
        self.assertTrue(result_data["stored"])
        self.assertEqual(result_data["conversation_id"], "test-456")
        
        # Verify mock was called correctly
        mock_store.assert_called_once_with(test_conversation, "planning-session-123", "default")
        
        logger.info("✅ Conversation storage tool verified")
        
    @patch('tools.conversation_memory_persistence.search_conversation_memory')
    def test_conversation_search_tool(self, mock_search):
        """Test the conversation search tool functionality"""
        
        # Mock the search response
        mock_search.return_value = json.dumps({
            "results": [
                {
                    "conversation_id": "conv-123",
                    "content": "Discussion about project timeline",
                    "similarity_score": 0.89,
                    "timestamp": "2025-06-10T10:00:00Z"
                }
            ],
            "total": 1
        })
        
        agent = create_fastapi_conversation_agent()
        
        # Find the search tool
        search_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'search_conversations':
                search_tool = tool
                break
        
        self.assertIsNotNone(search_tool, "Conversation search tool not found")
        
        # Test tool execution
        result = search_tool("project timeline", 5)
        result_data = json.loads(result)
        
        self.assertIn("results", result_data)
        self.assertEqual(len(result_data["results"]), 1)
        self.assertEqual(result_data["results"][0]["conversation_id"], "conv-123")
        
        # Verify mock was called correctly
        mock_search.assert_called_once_with("project timeline", "default", 5)
        
        logger.info("✅ Conversation search tool verified")
        
    def test_error_handling(self):
        """Test that conversation tools handle errors gracefully"""
        
        agent = create_fastapi_conversation_agent()
        
        # Find the entity extraction tool
        entity_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'extract_conversation_entities':
                entity_tool = tool
                break
        
        self.assertIsNotNone(entity_tool)
        
        # Test with mock that raises exception
        with patch.object(agent.conversation_analyzer, 'extract_entities', 
                         side_effect=Exception("Analysis service unavailable")):
            
            result = entity_tool("test conversation")
            result_data = json.loads(result)
            
            # Verify error is handled gracefully
            self.assertIn("error", result_data)
            self.assertIn("Analysis service unavailable", result_data["error"])
            self.assertEqual(result_data["entity_count"], 0)
        
        logger.info("✅ Error handling verified")
        
    def test_conversation_agent_specialization(self):
        """Test that agent is specialized for conversation analysis"""
        
        agent = create_fastapi_conversation_agent()
        
        # Verify agent focuses on conversation analysis
        conversation_keywords = ["conversation", "analysis", "intent", "sentiment", "entity", "topic"]
        goal_contains_keywords = any(keyword in agent.agent.goal.lower() for keyword in conversation_keywords)
        self.assertTrue(goal_contains_keywords, "Agent goal should focus on conversation analysis")
        
        backstory_contains_keywords = any(keyword in agent.agent.backstory.lower() for keyword in conversation_keywords)
        self.assertTrue(backstory_contains_keywords, "Agent backstory should emphasize conversation expertise")
        
        # Verify tools are conversation-focused
        conversation_tool_count = 0
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown')).lower()
            if any(keyword in tool_name for keyword in ['conversation', 'extract', 'infer', 'analyze', 'sentiment', 'topic']):
                conversation_tool_count += 1
        
        self.assertGreaterEqual(conversation_tool_count, 6, "Should have multiple conversation-focused tools")
        
        logger.info("✅ Conversation agent specialization verified")
        
    def test_architecture_compliance(self):
        """Test that agent follows service-oriented architecture"""
        
        agent = create_fastapi_conversation_agent()
        
        # Verify agent mentions HTTP/API architecture
        self.assertIn("HTTP", agent.agent.goal.upper())
        self.assertIn("API", agent.agent.goal.upper())
        self.assertIn("backend", agent.agent.backstory.lower())
        
        # Verify specialized configuration for complex analysis
        self.assertEqual(agent.agent.max_iter, 4, "Conversation agent should allow more iterations")
        self.assertEqual(agent.agent.max_execution_time, 150, "Conversation agent should allow more time")
        
        # Verify tools are function-based (HTTP pattern)
        function_based_tools = 0
        for tool in agent.tools:
            if hasattr(tool, '__call__') and hasattr(tool, 'name'):
                function_based_tools += 1
        
        self.assertGreater(function_based_tools, 0, "Agent should have function-based tools")
        
        logger.info("✅ Architecture compliance verified")

def run_fastapi_conversation_agent_tests():
    """Run all FastAPI Conversation Agent tests"""
    
    print("🧪 Testing FastAPI Conversation Agent Implementation")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFastAPIConversationAgent)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All FastAPI Conversation Agent tests passed!")
        print("✅ Conversation analysis tools verified")
        print("✅ Entity extraction, intent inference, sentiment analysis working")
        print("✅ Topic extraction and relationship analysis functional")
        print("✅ Service-oriented architecture compliance confirmed")
        print("✅ Phase 3 implementation complete")
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_fastapi_conversation_agent_tests()
    sys.exit(0 if success else 1)