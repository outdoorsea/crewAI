"""
Test Suite for CrewAI-Myndy Integration

This module contains comprehensive tests for the CrewAI integration with
the Myndy ecosystem, including tool bridge, agents, and memory integration.

File: tests/__init__.py
"""

import sys
from pathlib import Path

# Add project root to path for all tests
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))