"""
Agents Module for CrewAI-Myndy Integration

This module provides specialized agents that leverage the Myndy tool ecosystem
for comprehensive personal productivity and analysis.

File: agents/__init__.py
"""

from .memory_librarian import create_memory_librarian, get_memory_librarian_capabilities
from .research_specialist import create_research_specialist, get_research_specialist_capabilities
from .personal_assistant import create_personal_assistant, get_personal_assistant_capabilities
from .health_analyst import create_health_analyst, get_health_analyst_capabilities
from .finance_tracker import create_finance_tracker, get_finance_tracker_capabilities
from .fastapi_memory_librarian import create_fastapi_memory_librarian, get_fastapi_memory_librarian_capabilities
from .fastapi_test_assistant import create_fastapi_test_assistant, get_fastapi_test_assistant_capabilities

__all__ = [
    "create_memory_librarian",
    "get_memory_librarian_capabilities",
    "create_research_specialist", 
    "get_research_specialist_capabilities",
    "create_personal_assistant",
    "get_personal_assistant_capabilities",
    "create_health_analyst",
    "get_health_analyst_capabilities",
    "create_finance_tracker",
    "get_finance_tracker_capabilities",
    "create_fastapi_memory_librarian",
    "get_fastapi_memory_librarian_capabilities",
    "create_fastapi_test_assistant",
    "get_fastapi_test_assistant_capabilities"
]