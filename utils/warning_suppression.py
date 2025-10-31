"""
Warning Suppression Utilities

This module provides utilities to suppress known warnings from dependencies
that don't affect functionality but clutter the output during testing.

File: utils/warning_suppression.py
"""

import warnings
import sys
from functools import wraps


def suppress_warnings():
    """
    Suppress known warnings from CrewAI dependencies that don't affect functionality.
    
    This suppresses:
    - pkg_resources deprecation warnings from CrewAI telemetry
    - Pydantic V1/V2 mixing warnings from CrewAI
    - Other common dependency warnings
    """
    
    # Suppress pkg_resources deprecation warning
    warnings.filterwarnings(
        "ignore",
        message="pkg_resources is deprecated as an API.*",
        category=UserWarning,
        module="crewai.telemtry.telemetry"
    )
    
    # Suppress Pydantic V1/V2 mixing warning
    warnings.filterwarnings(
        "ignore", 
        message="Mixing V1 models and V2 models.*",
        category=UserWarning,
        module="pydantic._internal._generate_schema"
    )
    
    # Suppress general setuptools warnings
    warnings.filterwarnings(
        "ignore",
        message=".*setuptools.*",
        category=UserWarning
    )
    
    # Suppress LangChain deprecation warnings
    warnings.filterwarnings(
        "ignore",
        message=".*langchain.*deprecated.*",
        category=DeprecationWarning
    )


def suppress_warnings_decorator(func):
    """
    Decorator to suppress warnings for a specific function.
    
    Args:
        func: Function to wrap with warning suppression
        
    Returns:
        Wrapped function with warnings suppressed
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with warnings.catch_warnings():
            suppress_warnings()
            return func(*args, **kwargs)
    return wrapper


def clean_output_context():
    """
    Context manager for clean output without dependency warnings.
    
    Usage:
        with clean_output_context():
            # Your code here - warnings will be suppressed
            pass
    """
    return warnings.catch_warnings()


class CleanOutputContext:
    """
    Context manager class for suppressing warnings during execution.
    
    Usage:
        with CleanOutputContext():
            # Your code here
            pass
    """
    
    def __enter__(self):
        warnings.simplefilter("ignore", UserWarning)
        warnings.simplefilter("ignore", DeprecationWarning) 
        suppress_warnings()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        warnings.resetwarnings()


def setup_clean_environment():
    """
    Set up a clean environment by suppressing known dependency warnings.
    Call this at the start of your scripts for cleaner output.
    """
    suppress_warnings()
    
    # Additional environment setup
    import os
    
    # Suppress other verbose outputs
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    
    # Suppress urllib3 warnings
    try:
        import urllib3
        urllib3.disable_warnings()
    except ImportError:
        pass


if __name__ == "__main__":
    # Test the warning suppression
    print("Testing warning suppression...")
    
    setup_clean_environment()
    
    # This should not show warnings
    try:
        from crewai import Agent
        print("✅ CrewAI imported without warnings")
    except Exception as e:
        print(f"❌ Error importing CrewAI: {e}")
    
    print("Warning suppression test completed.")