"""
Memory Integration Module for CrewAI-Myndy Integration

This module provides memory integration capabilities between CrewAI agents
and the comprehensive Myndy memory system.

File: memory/__init__.py
"""

# Memory integration imports - temporarily commented out due to path issues
# These can be re-enabled when needed for advanced memory integration features
try:
    from .myndy_memory_integration import (
        CrewAIMyndyBridge,
        MyndyAwareAgent,
        get_memory_bridge
    )
    __all__ = [
        "CrewAIMyndyBridge",
        "MyndyAwareAgent", 
        "get_memory_bridge"
    ]
except ImportError as e:
    # Memory integration not available, but basic functionality still works
    __all__ = []