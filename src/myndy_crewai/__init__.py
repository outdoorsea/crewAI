"""
Myndy-Core CrewAI Integration

Specialized agents with intelligent routing, memory integration, and 530+ tool access
via HTTP bridge to myndy-ai backend.

This package provides:
- 2 specialized agents: Personal Assistant and Shadow Agent
- Intelligent routing system with confidence scoring
- HTTP bridge to myndy-ai FastAPI backend
- OpenWebUI pipeline integration
- Enhanced valve management system
- Comprehensive logging and diagnostics

File: src/myndy_crewai/__init__.py
"""

__version__ = "0.1.0"
__author__ = "Jeremy"
__email__ = "jeremy@myndy.ai"

# Core imports from standard CrewAI (using existing src/crewai structure)
try:
    from crewai import Agent, Crew, Task, Process
except ImportError:
    # Fallback to relative import if needed
    try:
        from ..crewai import Agent, Crew, Task, Process
    except ImportError:
        # Provide placeholder if CrewAI not available
        Agent = Crew = Task = Process = None

# Our custom components (use lazy imports to avoid circular dependencies)
def get_pipeline():
    """Get Pipeline class (lazy import)"""
    from .pipeline import Pipeline
    return Pipeline

def get_tools():
    """Get tool components (lazy import)"""
    from .tools import MyndyBridge
    return {"MyndyBridge": MyndyBridge}

def get_agents():
    """Get agent factory functions (lazy import)"""
    from .agents import (
        create_personal_assistant,
        create_enhanced_shadow_agent,
    )
    return {
        "create_personal_assistant": create_personal_assistant,
        "create_enhanced_shadow_agent": create_enhanced_shadow_agent,
    }

def get_config():
    """Get configuration classes (lazy import)"""
    from .config import LLMConfig
    return {"LLMConfig": LLMConfig}

# Convenience functions for common imports
Pipeline = None  # Will be loaded on first access
MyndyBridge = None
LLMConfig = None
create_personal_assistant = None
create_enhanced_shadow_agent = None

__all__ = [
    # Core CrewAI classes
    "Agent",
    "Crew", 
    "Task",
    "Process",
    
    # Lazy loaders for our components
    "get_pipeline",
    "get_tools",
    "get_agents", 
    "get_config",
    
    # Convenience placeholders (will be None until loaded)
    "Pipeline",
    "MyndyBridge",
    "LLMConfig",
    "create_personal_assistant",
    "create_enhanced_shadow_agent"
]