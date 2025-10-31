"""
Myndy-Core Pipeline Module

This module provides the core pipeline functionality for integrating CrewAI
with OpenWebUI and the myndy-ai backend.

Key Components:
- Pipeline: Main orchestration class for agent routing and execution
- Server: FastAPI server for OpenWebUI integration
- Valve Management: Configuration and settings management

File: src/myndy_crewai/pipeline/__init__.py
"""

from .crewai_myndy_pipeline import Pipeline
from .server import app as pipeline_app

try:
    from .openwebui_pipeline import OpenWebUIPipeline
    OPENWEBUI_AVAILABLE = True
except ImportError:
    OPENWEBUI_AVAILABLE = False

__all__ = [
    "Pipeline",
    "pipeline_app"
]

if OPENWEBUI_AVAILABLE:
    __all__.append("OpenWebUIPipeline")