"""
Test suite for Myndy memory integration.

File: tests/test_memory_integration.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from memory.myndy_memory_integration import CrewAIMyndyBridge, MyndyAwareAgent


class TestCrewAIMemoryBridge:
    """Test cases for the CrewAI Memory Bridge."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.user_id = "test_user"
        self.bridge = CrewAIMyndyBridge(self.user_id)
    
    def test_bridge_initialization(self):
        """Test that the bridge initializes correctly."""
        assert self.bridge.user_id == self.user_id
        assert hasattr(self.bridge, 'memory_store')
        assert hasattr(self.bridge, 'entity_manager')
        assert hasattr(self.bridge, 'conversation_manager')
    
    def test_is_available(self):
        """Test availability check."""
        available = self.bridge.is_available()
        assert isinstance(available, bool)
    
    @patch.object(CrewAIMyndyBridge, 'is_available', return_value=False)
    def test_store_interaction_unavailable(self, mock_available):
        """Test storing interaction when memory system is unavailable."""
        result = self.bridge.store_agent_interaction(
            agent_role="test_agent",
            task_description="test task",
            result="test result"
        )
        assert result == ""
    
    @patch.object(CrewAIMyndyBridge, 'is_available', return_value=False)
    def test_retrieve_context_unavailable(self, mock_available):
        """Test retrieving context when memory system is unavailable."""
        result = self.bridge.retrieve_conversation_context()
        assert result == []
    
    @patch.object(CrewAIMyndyBridge, 'is_available', return_value=False)
    def test_search_memory_unavailable(self, mock_available):
        """Test searching memory when system is unavailable."""
        result = self.bridge.search_memory("test query")
        assert result == []
    
    def test_get_memory_stats_unavailable(self):
        """Test getting memory stats when system is unavailable."""
        with patch.object(self.bridge, 'is_available', return_value=False):
            stats = self.bridge.get_memory_stats()
            assert stats["available"] == False
            assert "error" in stats
    
    @patch.object(CrewAIMyndyBridge, 'is_available', return_value=True)
    def test_get_memory_stats_available(self, mock_available):
        """Test getting memory stats when system is available."""
        # Mock the required methods
        with patch.object(self.bridge.entity_manager, 'get_all_entities', return_value=[]):
            with patch.object(self.bridge.conversation_manager, 'get_recent_conversations', return_value=[]):
                stats = self.bridge.get_memory_stats()
                assert stats["available"] == True
                assert stats["user_id"] == self.user_id
                assert "entities_count" in stats
                assert "conversations_count" in stats


class TestMemoryAwareAgent:
    """Test cases for the MyndyAwareAgent mixin."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent_role = "test_agent"
        self.user_id = "test_user"
        self.memory_agent = MyndyAwareAgent(self.agent_role, self.user_id)
    
    def test_memory_agent_initialization(self):
        """Test that the memory-aware agent initializes correctly."""
        assert self.memory_agent.agent_role == self.agent_role
        assert self.memory_agent.user_id == self.user_id
        assert hasattr(self.memory_agent, 'memory_bridge')
        assert isinstance(self.memory_agent.memory_bridge, CrewAIMyndyBridge)
    
    def test_remember_interaction(self):
        """Test remembering an interaction."""
        with patch.object(self.memory_agent.memory_bridge, 'store_agent_interaction') as mock_store:
            mock_store.return_value = "test_id"
            
            result = self.memory_agent.remember_interaction(
                task="test task",
                result="test result"
            )
            
            mock_store.assert_called_once_with(
                agent_role=self.agent_role,
                task_description="test task",
                result="test result",
                metadata=None
            )
            assert result == "test_id"
    
    def test_recall_context(self):
        """Test recalling interaction context."""
        with patch.object(self.memory_agent.memory_bridge, 'retrieve_conversation_context') as mock_retrieve:
            mock_retrieve.return_value = [{"test": "context"}]
            
            result = self.memory_agent.recall_context(limit=5)
            
            mock_retrieve.assert_called_once_with(
                agent_role=self.agent_role,
                limit=5
            )
            assert result == [{"test": "context"}]
    
    def test_search_knowledge(self):
        """Test searching the knowledge base."""
        with patch.object(self.memory_agent.memory_bridge, 'search_memory') as mock_search:
            mock_search.return_value = [{"test": "result"}]
            
            result = self.memory_agent.search_knowledge(
                query="test query",
                limit=10
            )
            
            mock_search.assert_called_once_with(
                query="test query",
                limit=10
            )
            assert result == [{"test": "result"}]


class TestMemoryBridgeIntegration:
    """Integration tests for memory bridge functionality."""
    
    def test_get_memory_bridge_singleton(self):
        """Test that get_memory_bridge returns singleton instances."""
        from memory import get_memory_bridge
        
        bridge1 = get_memory_bridge("user1")
        bridge2 = get_memory_bridge("user1")
        bridge3 = get_memory_bridge("user2")
        
        # Same user should get same instance
        assert bridge1 is bridge2
        
        # Different user should get different instance
        assert bridge1 is not bridge3
        assert bridge1.user_id != bridge3.user_id
    
    def test_memory_bridge_user_isolation(self):
        """Test that memory bridges properly isolate users."""
        from memory import get_memory_bridge
        
        bridge1 = get_memory_bridge("user1")
        bridge2 = get_memory_bridge("user2")
        
        assert bridge1.user_id == "user1"
        assert bridge2.user_id == "user2"
        assert bridge1 is not bridge2


class TestMemoryIntegrationErrorHandling:
    """Test error handling in memory integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.bridge = CrewAIMyndyBridge("test_user")
    
    @patch.object(CrewAIMyndyBridge, 'is_available', return_value=True)
    def test_store_interaction_error(self, mock_available):
        """Test handling errors during interaction storage."""
        with patch.object(self.bridge.conversation_manager, 'store_conversation', side_effect=Exception("Test error")):
            result = self.bridge.store_agent_interaction(
                agent_role="test_agent",
                task_description="test task", 
                result="test result"
            )
            assert result == ""
    
    @patch.object(CrewAIMyndyBridge, 'is_available', return_value=True)
    def test_search_memory_error(self, mock_available):
        """Test handling errors during memory search."""
        with patch.object(self.bridge.entity_manager, 'search_entities', side_effect=Exception("Test error")):
            result = self.bridge.search_memory("test query")
            assert result == []
    
    @patch.object(CrewAIMyndyBridge, 'is_available', return_value=True)
    def test_get_memory_stats_error(self, mock_available):
        """Test handling errors when getting memory stats."""
        with patch.object(self.bridge.entity_manager, 'get_all_entities', side_effect=Exception("Test error")):
            stats = self.bridge.get_memory_stats()
            assert stats["available"] == False
            assert "error" in stats


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])