"""
Configuration Module for CrewAI-Myndy Integration

This module provides configuration management for the CrewAI integration,
including LLM configuration, environment settings, and agent parameters.

File: config/__init__.py
"""

from .llm_config import (
    LLMConfig,
    get_llm_config,
    get_agent_llm
)

__all__ = [
    "LLMConfig",
    "get_llm_config", 
    "get_agent_llm"
]