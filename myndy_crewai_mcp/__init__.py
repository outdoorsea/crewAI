"""
MCP (Model Context Protocol) Server for CrewAI-Myndy Integration

This package implements the MCP server that exposes CrewAI agents,
tools, resources, and prompts to LibreChat and other MCP-compatible clients.

File: myndy_mcp/__init__.py
"""

__version__ = "0.1.0"

# Lazy imports to avoid circular dependencies and encoding issues
def get_server():
    from .server import MyndyMCPServer
    return MyndyMCPServer

def get_config_class():
    from .config import MCPConfig
    return MCPConfig

__all__ = ["get_server", "get_config_class", "__version__"]
