"""
CrewAI-Myndy OpenAPI Server

FastAPI-based OpenAPI server for the CrewAI-Myndy integration,
providing RESTful access to multi-agent workflows and tools.

Compatible with Open WebUI and other front-end interfaces.

File: api/__init__.py
"""

from .main import app
from .models import *
from .server import create_production_app

__version__ = "1.0.0"
__all__ = ["app", "create_production_app"]