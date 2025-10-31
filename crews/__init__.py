"""
Crews Module for CrewAI-Myndy Integration

This module provides pre-configured crews that combine specialized agents
for comprehensive task execution and workflow management.

File: crews/__init__.py
"""

from .personal_productivity_crew import PersonalProductivityCrew, create_personal_productivity_crew

__all__ = [
    "PersonalProductivityCrew",
    "create_personal_productivity_crew"
]