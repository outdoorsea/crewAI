"""
Myndy-Core Configuration Module

This module provides configuration management for LLMs, environment variables,
and system settings for the myndy-crewai integration.

File: src/myndy_crewai/config/__init__.py
"""

from .llm_config import (
    LLMConfig,
    get_llm_config,
    get_agent_llm
)

try:
    from .env_config import EnvConfig, load_environment_config
    ENV_CONFIG_AVAILABLE = True
except ImportError:
    ENV_CONFIG_AVAILABLE = False

__all__ = [
    "LLMConfig",
    "get_llm_config", 
    "get_agent_llm"
]

if ENV_CONFIG_AVAILABLE:
    __all__.extend([
        "EnvConfig",
        "load_environment_config"
    ])