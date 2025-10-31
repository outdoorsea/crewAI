"""
CrewAI Tools Module

This module provides the bridge between Myndy tools and CrewAI agents,
enabling seamless integration of the extensive Myndy tool ecosystem.

File: tools/__init__.py
"""

# Lazy imports to avoid circular dependency
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

__all__ = [
    "load_myndy_tools_for_agent",
    "load_all_myndy_tools",
    "get_tool_loader"
]