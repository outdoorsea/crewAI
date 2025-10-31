"""
Myndy-Core Tools Integration

This module provides the HTTP bridge and tool integration system that connects
CrewAI agents to the myndy-ai FastAPI backend with 530+ specialized tools.

Key Components:
- MyndyBridge: Main HTTP client bridge to myndy-ai backend  
- Shadow Agent HTTP Tools: Specialized tools for behavioral analysis
- Tool registry and mapping system

File: src/myndy_crewai/tools/__init__.py
"""

# Core bridge components
from .myndy_bridge import MyndyBridge, get_available_tools

# Shadow agent specialized tools
try:
    from .shadow_agent_http_tools import (
        MemorySearchTool,
        GetCurrentStatusTool,
        AddFactTool,
        AddPreferenceTool,
        UpdateStatusTool,
        CreateEntityTool,
        GetStatusHistoryTool,
        ReflectOnMemoryTool,
        StoreConversationAnalysisTool,
        GetHealthMetricsTool,
        GetRecentActivityTool,
        GetSelfProfileTool
    )
    SHADOW_TOOLS_AVAILABLE = True
except ImportError:
    SHADOW_TOOLS_AVAILABLE = False

# Legacy tool loading functions (maintained for compatibility)
def load_myndy_tools_for_agent(agent_role: str):
    """Load myndy tools for a specific agent role."""
    from .myndy_bridge import load_myndy_tools_for_agent as _load_tools
    return _load_tools(agent_role)

def load_all_myndy_tools():
    """Load all available myndy tools.""" 
    from .myndy_bridge import load_all_myndy_tools as _load_all_tools
    return _load_all_tools()

def get_tool_loader():
    """Get the global tool loader instance."""
    from .myndy_bridge import get_tool_loader as _get_loader
    return _get_loader()

# Export list
__all__ = [
    # Core bridge
    "MyndyBridge",
    "get_available_tools",
    
    # Legacy functions
    "load_myndy_tools_for_agent",
    "load_all_myndy_tools", 
    "get_tool_loader"
]

# Add shadow tools to exports if available
if SHADOW_TOOLS_AVAILABLE:
    __all__.extend([
        "MemorySearchTool",
        "GetCurrentStatusTool",
        "AddFactTool", 
        "AddPreferenceTool",
        "UpdateStatusTool",
        "CreateEntityTool",
        "GetStatusHistoryTool",
        "ReflectOnMemoryTool",
        "StoreConversationAnalysisTool",
        "GetHealthMetricsTool",
        "GetRecentActivityTool",
        "GetSelfProfileTool"
    ])