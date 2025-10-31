"""
Test suite for CrewAI agents.

File: tests/test_agents.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestAgentCreation:
    """Test cases for agent creation functions."""
    
    @patch('agents.memory_librarian.load_myndy_tools_for_agent')
    @patch('agents.memory_librarian.get_agent_llm')
    def test_create_memory_librarian(self, mock_get_llm, mock_load_tools):
        """Test creating a Memory Librarian agent."""
        # Mock dependencies
        mock_load_tools.return_value = []
        mock_get_llm.return_value = Mock()
        
        from agents import create_memory_librarian
        
        agent = create_memory_librarian(verbose=False)
        
        assert agent.role == "Memory Librarian"
        assert "memory" in agent.goal.lower()
        assert "knowledge" in agent.goal.lower()
        mock_load_tools.assert_called_once_with("memory_librarian")
        mock_get_llm.assert_called_once_with("memory_librarian")
    
    @patch('agents.research_specialist.load_myndy_tools_for_agent')
    @patch('agents.research_specialist.get_agent_llm')
    def test_create_research_specialist(self, mock_get_llm, mock_load_tools):
        """Test creating a Research Specialist agent."""
        # Mock dependencies
        mock_load_tools.return_value = []
        mock_get_llm.return_value = Mock()
        
        from agents import create_research_specialist
        
        agent = create_research_specialist(verbose=False)
        
        assert agent.role == "Research Specialist"
        assert "research" in agent.goal.lower()
        assert "information" in agent.goal.lower()
        mock_load_tools.assert_called_once_with("research_specialist")
        mock_get_llm.assert_called_once_with("research_specialist")
    
    @patch('agents.personal_assistant.load_myndy_tools_for_agent')
    @patch('agents.personal_assistant.get_agent_llm')
    def test_create_personal_assistant(self, mock_get_llm, mock_load_tools):
        """Test creating a Personal Assistant agent."""
        # Mock dependencies
        mock_load_tools.return_value = []
        mock_get_llm.return_value = Mock()
        
        from agents import create_personal_assistant
        
        agent = create_personal_assistant(verbose=False)
        
        assert agent.role == "Personal Assistant"
        assert "calendar" in agent.goal.lower() or "email" in agent.goal.lower()
        mock_load_tools.assert_called_once_with("personal_assistant")
        mock_get_llm.assert_called_once_with("personal_assistant")
    
    @patch('agents.health_analyst.load_myndy_tools_for_agent')
    @patch('agents.health_analyst.get_agent_llm')
    def test_create_health_analyst(self, mock_get_llm, mock_load_tools):
        """Test creating a Health Analyst agent."""
        # Mock dependencies
        mock_load_tools.return_value = []
        mock_get_llm.return_value = Mock()
        
        from agents import create_health_analyst
        
        agent = create_health_analyst(verbose=False)
        
        assert agent.role == "Health Analyst"
        assert "health" in agent.goal.lower()
        mock_load_tools.assert_called_once_with("health_analyst")
        mock_get_llm.assert_called_once_with("health_analyst")
    
    @patch('agents.finance_tracker.load_myndy_tools_for_agent')
    @patch('agents.finance_tracker.get_agent_llm')
    def test_create_finance_tracker(self, mock_get_llm, mock_load_tools):
        """Test creating a Finance Tracker agent."""
        # Mock dependencies
        mock_load_tools.return_value = []
        mock_get_llm.return_value = Mock()
        
        from agents import create_finance_tracker
        
        agent = create_finance_tracker(verbose=False)
        
        assert agent.role == "Finance Tracker"
        assert "financial" in agent.goal.lower() or "finance" in agent.goal.lower()
        mock_load_tools.assert_called_once_with("finance_tracker")
        mock_get_llm.assert_called_once_with("finance_tracker")


class TestAgentCapabilities:
    """Test cases for agent capability functions."""
    
    def test_memory_librarian_capabilities(self):
        """Test Memory Librarian capabilities list."""
        from agents import get_memory_librarian_capabilities
        
        capabilities = get_memory_librarian_capabilities()
        
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert any("memory" in cap.lower() for cap in capabilities)
        assert any("entity" in cap.lower() for cap in capabilities)
    
    def test_research_specialist_capabilities(self):
        """Test Research Specialist capabilities list."""
        from agents import get_research_specialist_capabilities
        
        capabilities = get_research_specialist_capabilities()
        
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert any("research" in cap.lower() for cap in capabilities)
        assert any("search" in cap.lower() for cap in capabilities)
    
    def test_personal_assistant_capabilities(self):
        """Test Personal Assistant capabilities list."""
        from agents import get_personal_assistant_capabilities
        
        capabilities = get_personal_assistant_capabilities()
        
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert any("calendar" in cap.lower() for cap in capabilities)
        assert any("email" in cap.lower() for cap in capabilities)
    
    def test_health_analyst_capabilities(self):
        """Test Health Analyst capabilities list."""
        from agents import get_health_analyst_capabilities
        
        capabilities = get_health_analyst_capabilities()
        
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert any("health" in cap.lower() for cap in capabilities)
        assert any("fitness" in cap.lower() for cap in capabilities)
    
    def test_finance_tracker_capabilities(self):
        """Test Finance Tracker capabilities list."""
        from agents import get_finance_tracker_capabilities
        
        capabilities = get_finance_tracker_capabilities()
        
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert any("financial" in cap.lower() or "finance" in cap.lower() for cap in capabilities)
        assert any("expense" in cap.lower() for cap in capabilities)


class TestAgentConfiguration:
    """Test cases for agent configuration options."""
    
    @patch('agents.memory_librarian.load_myndy_tools_for_agent')
    @patch('agents.memory_librarian.get_agent_llm')
    def test_agent_verbose_setting(self, mock_get_llm, mock_load_tools):
        """Test agent verbose setting."""
        # Mock dependencies
        mock_load_tools.return_value = []
        mock_get_llm.return_value = Mock()
        
        from agents import create_memory_librarian
        
        # Test verbose=True
        agent_verbose = create_memory_librarian(verbose=True)
        assert agent_verbose.verbose == True
        
        # Test verbose=False
        agent_quiet = create_memory_librarian(verbose=False)
        assert agent_quiet.verbose == False
    
    @patch('agents.research_specialist.load_myndy_tools_for_agent')
    @patch('agents.research_specialist.get_agent_llm')
    def test_agent_delegation_setting(self, mock_get_llm, mock_load_tools):
        """Test agent delegation setting."""
        # Mock dependencies
        mock_load_tools.return_value = []
        mock_get_llm.return_value = Mock()
        
        from agents import create_research_specialist
        
        # Test allow_delegation=True
        agent_delegating = create_research_specialist(allow_delegation=True)
        assert agent_delegating.allow_delegation == True
        
        # Test allow_delegation=False
        agent_no_delegation = create_research_specialist(allow_delegation=False)
        assert agent_no_delegation.allow_delegation == False
    
    @patch('agents.personal_assistant.load_myndy_tools_for_agent')
    @patch('agents.personal_assistant.get_agent_llm')
    def test_agent_max_iter_setting(self, mock_get_llm, mock_load_tools):
        """Test agent max_iter setting."""
        # Mock dependencies
        mock_load_tools.return_value = []
        mock_get_llm.return_value = Mock()
        
        from agents import create_personal_assistant
        
        # Test custom max_iter
        agent = create_personal_assistant(max_iter=10)
        assert agent.max_iter == 10


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])