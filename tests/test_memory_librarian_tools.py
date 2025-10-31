#!/usr/bin/env python3
"""
Test Memory Librarian Agent Tool Integration

This test verifies that the Memory Librarian agent has access to all required tools
and that the tool mapping fix resolves the 67% functionality issue.

File: tests/test_memory_librarian_tools.py
"""

import sys
import json
import logging
import pytest
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add crewAI to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMemoryLibrarianTools(unittest.TestCase):
    """Test Memory Librarian agent tool integration"""
    
    def setUp(self):
        """Set up test environment"""
        logger.info("Setting up Memory Librarian tool tests")
        
    def test_tool_mapping_fix(self):
        """Test that Memory Librarian agent has access to conversation memory tools"""
        from tools.myndy_bridge import MyndyToolBridge
        
        # Initialize the bridge
        bridge = MyndyToolBridge()
        
        # Get tools for Memory Librarian agent
        memory_librarian_tools = bridge.get_tools_for_agent("memory_librarian")
        
        # Extract tool names
        tool_names = []
        for tool in memory_librarian_tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            elif hasattr(tool, '__name__'):
                tool_names.append(tool.__name__)
        
        logger.info(f"Memory Librarian has {len(tool_names)} tools: {tool_names}")
        
        # Verify essential conversation memory tools are present
        essential_conversation_tools = [
            "search_conversation_memory",
            "get_conversation_summary", 
            "store_conversation_analysis"
        ]
        
        missing_tools = []
        for tool in essential_conversation_tools:
            if tool not in tool_names:
                missing_tools.append(tool)
        
        # Assert no tools are missing
        self.assertEqual(len(missing_tools), 0, 
                        f"Missing essential conversation tools: {missing_tools}")
        
        # Verify original tools are still present
        original_tools = [
            "extract_conversation_entities",
            "infer_conversation_intent", 
            "extract_from_conversation_history"
        ]
        
        missing_original = []
        for tool in original_tools:
            if tool not in tool_names:
                missing_original.append(tool)
        
        self.assertEqual(len(missing_original), 0,
                        f"Missing original tools: {missing_original}")
        
        logger.info("✅ Tool mapping fix verified - all essential tools present")
        
    def test_memory_librarian_completeness(self):
        """Test that Memory Librarian has comprehensive tool coverage"""
        from tools.myndy_bridge import MyndyToolBridge
        
        bridge = MyndyToolBridge()
        tools = bridge.get_tools_for_agent("memory_librarian")
        
        # Count tools by category
        tool_counts = {
            "conversation": 0,
            "memory": 0, 
            "entity": 0,
            "profile": 0,
            "knowledge": 0
        }
        
        for tool in tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown'))
            
            if 'conversation' in tool_name:
                tool_counts["conversation"] += 1
            elif 'memory' in tool_name or 'search' in tool_name:
                tool_counts["memory"] += 1
            elif 'entity' in tool_name or 'extract' in tool_name:
                tool_counts["entity"] += 1
            elif 'profile' in tool_name:
                tool_counts["profile"] += 1
            elif 'knowledge' in tool_name:
                tool_counts["knowledge"] += 1
        
        logger.info(f"Tool distribution: {tool_counts}")
        
        # Verify minimum tool counts per category
        self.assertGreaterEqual(tool_counts["conversation"], 3, 
                               "Should have at least 3 conversation tools")
        self.assertGreaterEqual(tool_counts["memory"], 2,
                               "Should have at least 2 memory tools")
        self.assertGreaterEqual(tool_counts["entity"], 2,
                               "Should have at least 2 entity tools")
        
        total_tools = sum(tool_counts.values())
        logger.info(f"✅ Memory Librarian has {total_tools} categorized tools")
        
    @patch('tools.conversation_memory_persistence.ConversationMemoryPersistence')
    def test_conversation_memory_tool_execution(self, mock_persistence):
        """Test that conversation memory tools can be executed"""
        
        # Mock the persistence layer
        mock_instance = Mock()
        mock_persistence.return_value = mock_instance
        
        # Test search_conversation_memory
        mock_instance.search_conversation_memory.return_value = {
            "results": [
                {
                    "conversation_id": "test-123",
                    "content": "Test conversation content",
                    "similarity_score": 0.85,
                    "timestamp": "2025-06-10T10:00:00Z"
                }
            ],
            "total": 1
        }
        
        from tools.conversation_memory_persistence import search_conversation_memory
        
        result = search_conversation_memory("test query", "test_user", 5)
        result_data = json.loads(result)
        
        self.assertIn("results", result_data)
        self.assertEqual(len(result_data["results"]), 1)
        self.assertEqual(result_data["results"][0]["conversation_id"], "test-123")
        
        # Test get_conversation_summary
        mock_instance.get_conversation_summary.return_value = {
            "conversation_id": "test-123",
            "summary": "Test conversation summary",
            "entities": ["person:John", "place:Office"],
            "insights": ["work_pattern"],
            "timestamp": "2025-06-10T10:00:00Z"
        }
        
        from tools.conversation_memory_persistence import get_conversation_summary
        
        summary_result = get_conversation_summary("test-123")
        summary_data = json.loads(summary_result)
        
        self.assertEqual(summary_data["conversation_id"], "test-123")
        self.assertIn("summary", summary_data)
        self.assertIn("entities", summary_data)
        
        logger.info("✅ Conversation memory tools execute successfully")
        
    def test_functionality_percentage_improvement(self):
        """Test that the tool mapping fix improves functionality from 33% to 100%"""
        from tools.myndy_bridge import MyndyToolBridge
        
        bridge = MyndyToolBridge()
        
        # Get all tools for Memory Librarian
        all_tools = bridge.get_tools_for_agent("memory_librarian")
        
        # Count essential tools vs total tools
        essential_tools = [
            "extract_conversation_entities", "infer_conversation_intent", 
            "extract_from_conversation_history", "search_conversation_memory",
            "get_conversation_summary", "store_conversation_analysis"
        ]
        
        tool_names = [getattr(tool, 'name', getattr(tool, '__name__', '')) for tool in all_tools]
        present_essential = sum(1 for tool in essential_tools if tool in tool_names)
        
        # Calculate functionality percentage
        functionality_percentage = (present_essential / len(essential_tools)) * 100
        
        logger.info(f"Essential tools present: {present_essential}/{len(essential_tools)}")
        logger.info(f"Functionality percentage: {functionality_percentage:.1f}%")
        
        # Verify we have 100% of essential tools
        self.assertEqual(functionality_percentage, 100.0,
                        f"Expected 100% functionality, got {functionality_percentage:.1f}%")
        
        logger.info("✅ Memory Librarian functionality improved to 100%")

def run_memory_librarian_tests():
    """Run all Memory Librarian tool tests"""
    
    print("🧪 Testing Memory Librarian Agent Tool Integration")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMemoryLibrarianTools)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All Memory Librarian tool tests passed!")
        print("✅ Tool mapping fix verified successfully")
        print("✅ Memory Librarian functionality: 100%")
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_memory_librarian_tests()
    sys.exit(0 if success else 1)