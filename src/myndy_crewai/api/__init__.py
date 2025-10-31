"""
Myndy-Core API Module

This module provides API components for the myndy-crewai integration,
including valve management, routing, and OpenWebUI integration.

File: src/myndy_crewai/api/__init__.py
"""

from .valve_manager import EnhancedValveManager, create_valve_manager

try:
    from .agent_router import AgentRouter
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False

try:
    from .main import app
    from .server import create_production_app
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

__all__ = [
    "EnhancedValveManager",
    "create_valve_manager"
]

if ROUTER_AVAILABLE:
    __all__.append("AgentRouter")

if FASTAPI_AVAILABLE:
    __all__.extend(["app", "create_production_app"])

__version__ = "0.1.0"