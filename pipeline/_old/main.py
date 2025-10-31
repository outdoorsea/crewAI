"""
Main entry point for the CrewAI-Myndy Pipeline

This file serves as the entry point for the OpenWebUI pipeline system.
It imports and initializes the CrewAI-Myndy pipeline.

File: pipeline/main.py
"""

from crewai_myndy_pipeline import Pipeline

# Export the pipeline class for OpenWebUI to discover
__all__ = ["Pipeline"]