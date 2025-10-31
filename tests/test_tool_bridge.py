"""
Test suite for the Myndy-CrewAI tool bridge.

File: tests/test_tool_bridge.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.myndy_bridge import MyndyToolLoader, MyndyTool, MyndyToolError


class TestMemexToolLoader:
    """Test cases for the MyndyToolLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock tool repository path for testing
        self.test_repo_path = "/tmp/test_tool_repo"
        self.loader = MyndyToolLoader(self.test_repo_path)
    
    def test_loader_initialization(self):
        """Test that the loader initializes correctly."""
        assert self.loader.tool_repo_path == Path(self.test_repo_path)
        assert isinstance(self.loader._tool_schemas, dict)
        assert isinstance(self.loader._loaded_tools, dict)
    
    def test_get_tool_categories(self):
        """Test retrieving tool categories."""
        categories = self.loader.get_tool_categories()
        assert isinstance(categories, list)
    
    def test_get_tools_by_category(self):
        """Test filtering tools by category."""
        tools = self.loader.get_tools_by_category("memory")
        assert isinstance(tools, list)
    
    def test_get_tools_for_agent(self):
        """Test getting tools for specific agent roles."""
        # Test each agent role
        roles = [
            "memory_librarian",
            "research_specialist", 
            "personal_assistant",
            "health_analyst",
            "finance_tracker"
        ]
        
        for role in roles:
            tools = self.loader.get_tools_for_agent(role)
            assert isinstance(tools, list)
    
    def test_get_tool_info(self):
        """Test getting tool information summary."""
        info = self.loader.get_tool_info()
        
        assert "total_tools" in info
        assert "categories" in info
        assert "tools_by_category" in info
        assert "registry_available" in info
        assert isinstance(info["total_tools"], int)
        assert isinstance(info["categories"], list)


class TestMemexTool:
    """Test cases for the MyndyTool class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_schema = {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Test input"
                        }
                    },
                    "required": ["input"]
                }
            },
            "name": "test_tool"
        }
    
    def test_tool_creation(self):
        """Test creating a MyndyTool instance."""
        tool = MyndyTool(
            name="test_tool",
            description="A test tool",
            memex_tool_name="test_tool",
            tool_schema=self.test_schema,
            category="test"
        )
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.memex_tool_name == "test_tool"
        assert tool.category == "test"
    
    @patch('tools.myndy_bridge.myndy_registry')
    def test_tool_execution_success(self, mock_registry):
        """Test successful tool execution."""
        # Mock the registry behavior
        mock_tool_metadata = Mock()
        mock_registry.get_tool.return_value = mock_tool_metadata
        mock_registry.execute_tool.return_value = {"result": "success"}
        
        tool = MyndyTool(
            name="test_tool",
            description="A test tool",
            memex_tool_name="test_tool",
            tool_schema=self.test_schema,
            category="test"
        )
        
        result = tool._run(input="test")
        assert "success" in result
    
    @patch('tools.myndy_bridge.myndy_registry')
    def test_tool_execution_failure(self, mock_registry):
        """Test tool execution failure handling."""
        # Mock registry to return None (tool not found)
        mock_registry.get_tool.return_value = None
        
        tool = MyndyTool(
            name="test_tool",
            description="A test tool",
            memex_tool_name="test_tool",
            tool_schema=self.test_schema,
            category="test"
        )
        
        with pytest.raises(MyndyToolError):
            tool._run(input="test")


class TestToolBridgeIntegration:
    """Integration tests for the complete tool bridge."""
    
    def test_load_memex_tools_for_agent(self):
        """Test the convenience function for loading agent tools."""
        from tools import load_myndy_tools_for_agent
        
        tools = load_myndy_tools_for_agent("memory_librarian")
        assert isinstance(tools, list)
    
    def test_load_all_memex_tools(self):
        """Test loading all available tools."""
        from tools import load_all_myndy_tools
        
        tools = load_all_myndy_tools()
        assert isinstance(tools, list)
    
    def test_get_tool_loader(self):
        """Test the global tool loader function."""
        from tools import get_tool_loader
        
        loader = get_tool_loader()
        assert isinstance(loader, MyndyToolLoader)
        
        # Test that it returns the same instance
        loader2 = get_tool_loader()
        assert loader is loader2


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])