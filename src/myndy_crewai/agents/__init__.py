"""
Myndy-Core Specialized Agents

This module provides the core specialized agents for the myndy-core system:
- Personal Assistant: Comprehensive task handling with 19 tools
- Enhanced Shadow Agent: Behavioral analysis and memory integration

Simplified architecture with 2 main agents for focused functionality.

File: src/myndy_crewai/agents/__init__.py
"""

from .personal_assistant import create_personal_assistant, get_personal_assistant_capabilities
from .enhanced_shadow_agent import create_enhanced_shadow_agent
from .context_manager import create_context_manager

# Legacy imports for backward compatibility (marked for deprecation)
from .memory_librarian import create_memory_librarian, get_memory_librarian_capabilities
from .research_specialist import create_research_specialist, get_research_specialist_capabilities
from .health_analyst import create_health_analyst, get_health_analyst_capabilities
from .finance_tracker import create_finance_tracker, get_finance_tracker_capabilities
from .fastapi_memory_librarian import create_fastapi_memory_librarian, get_fastapi_memory_librarian_capabilities
from .fastapi_test_assistant import create_fastapi_test_assistant, get_fastapi_test_assistant_capabilities

# Primary exports (current architecture)
__all__ = [
    # Main agents (current)
    "create_personal_assistant",
    "get_personal_assistant_capabilities", 
    "create_enhanced_shadow_agent",
    "create_context_manager",
    
    # Legacy agents (deprecated but maintained for compatibility)
    "create_memory_librarian",
    "get_memory_librarian_capabilities",
    "create_research_specialist", 
    "get_research_specialist_capabilities",
    "create_health_analyst",
    "get_health_analyst_capabilities",
    "create_finance_tracker",
    "get_finance_tracker_capabilities",
    "create_fastapi_memory_librarian",
    "get_fastapi_memory_librarian_capabilities",
    "create_fastapi_test_assistant",
    "get_fastapi_test_assistant_capabilities"
]