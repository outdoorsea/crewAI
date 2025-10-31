"""
dependency_manager.py - Dependency checking and management for CrewAI tests

This module provides dependency checking and graceful fallback mechanisms
for testing when dependencies are not available.

File: tests/dependency_manager.py
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Import runtime configuration
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.runtime_config import runtime_config, should_fail_fast, should_use_fallback

logger = logging.getLogger(__name__)

class DependencyManager:
    """Manages dependencies for CrewAI testing framework"""
    
    def __init__(self):
        self.dependencies = {}
        self.setup_paths()
        self.check_dependencies()
    
    def setup_paths(self) -> None:
        """Setup paths for myndy-ai imports"""
        # Get the correct path to myndy-ai
        crewai_path = Path(__file__).parent.parent  # /crewAI/
        myndy_path = crewai_path.parent / "myndy-ai"  # /myndy-ai/
        
        if myndy_path.exists():
            myndy_path_str = str(myndy_path)
            if myndy_path_str not in sys.path:
                sys.path.insert(0, myndy_path_str)
            logger.info(f"Added myndy-ai path: {myndy_path}")
        else:
            logger.warning(f"Myndy-AI path not found: {myndy_path}")
    
    def check_dependencies(self) -> None:
        """Check availability of all dependencies"""
        dependencies_to_check = [
            ('qdrant_client', 'from qdrant_client import QdrantClient'),
            ('qdrant_local', 'from qdrant.core.client import qdrant_client'),
            ('crewai', 'from crewai import Agent, Task, Crew'),
            ('httpx', 'import httpx'),
            ('pytest', 'import pytest'),
            ('memory_tools', 'from tools.conversation_memory_persistence import ConversationMemoryPersistence'),
            ('fastapi_agents', 'from agents.fastapi_memory_agent import create_fastapi_memory_agent'),
            ('status_agent', 'from agents.fastapi_status_agent import create_fastapi_status_agent'),
        ]
        
        for dep_name, import_stmt in dependencies_to_check:
            try:
                exec(import_stmt)
                self.dependencies[dep_name] = True
                if runtime_config.get_config_value('verbose_dependency_logging', False):
                    logger.info(f"✅ {dep_name}: Available")
                else:
                    logger.debug(f"✅ {dep_name}: Available")
            except ImportError as e:
                self.dependencies[dep_name] = False
                
                # In production mode, log missing dependencies as errors
                if should_fail_fast('missing_dependencies'):
                    logger.error(f"❌ {dep_name}: {e}")
                else:
                    logger.debug(f"❌ {dep_name}: {e}")
            except Exception as e:
                self.dependencies[dep_name] = False
                
                if should_fail_fast('missing_dependencies'):
                    logger.error(f"⚠️  {dep_name}: {e}")
                else:
                    logger.debug(f"⚠️  {dep_name}: {e}")
    
    def is_available(self, dependency: str) -> bool:
        """Check if a dependency is available"""
        return self.dependencies.get(dependency, False)
    
    def require_dependencies(self, *deps: str) -> bool:
        """Check if all required dependencies are available"""
        available = all(self.is_available(dep) for dep in deps)
        
        # In production mode, fail if required dependencies are missing
        if not available and should_fail_fast('missing_dependencies'):
            missing = [dep for dep in deps if not self.is_available(dep)]
            error_msg = f"Required dependencies missing: {', '.join(missing)}"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        return available
    
    def get_available_dependencies(self) -> List[str]:
        """Get list of available dependencies"""
        return [dep for dep, available in self.dependencies.items() if available]
    
    def get_missing_dependencies(self) -> List[str]:
        """Get list of missing dependencies"""
        return [dep for dep, available in self.dependencies.items() if not available]
    
    def get_dependency_summary(self) -> Dict[str, Any]:
        """Get comprehensive dependency summary"""
        available = self.get_available_dependencies()
        missing = self.get_missing_dependencies()
        
        return {
            "total": len(self.dependencies),
            "available": len(available),
            "missing": len(missing),
            "available_deps": available,
            "missing_deps": missing,
            "summary": f"{len(available)}/{len(self.dependencies)} dependencies available"
        }
    
    def create_mock_agent(self, agent_type: str = "test"):
        """Create a mock agent when real agents are unavailable"""
        # In production mode, don't allow mock agents
        if not should_use_fallback('agents'):
            error_msg = f"Mock agent not allowed in production mode: {agent_type}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        class MockAgent:
            def __init__(self, agent_type: str):
                self.role = f"Mock {agent_type.title()} Agent"
                self.goal = f"Mock {agent_type} agent for testing"
                self.backstory = f"A mock agent created for testing when {agent_type} agent is unavailable"
                self.tools = []
                self.memory = True
                self.llm = None
                self.verbose = False
        
        if runtime_config.get_config_value('verbose_dependency_logging', False):
            logger.warning(f"Created mock agent for {agent_type} (runtime mode: {runtime_config.mode.value})")
        
        return MockAgent(agent_type)
    
    def create_fallback_agents(self) -> Dict[str, Any]:
        """Create fallback agents when real agents are unavailable"""
        fallback_agents = {}
        
        agent_types = ['memory', 'status', 'conversation', 'time', 'weather', 'test_assistant']
        
        for agent_type in agent_types:
            fallback_agents[agent_type] = self.create_mock_agent(agent_type)
        
        return fallback_agents


# Global dependency manager instance
dependency_manager = DependencyManager()


def skip_if_missing_deps(*deps: str):
    """Decorator to skip tests if dependencies are missing"""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            if not dependency_manager.require_dependencies(*deps):
                missing = [dep for dep in deps if not dependency_manager.is_available(dep)]
                import pytest
                pytest.skip(f"Missing dependencies: {', '.join(missing)}")
            return test_func(*args, **kwargs)
        return wrapper
    return decorator


def get_dependency_manager() -> DependencyManager:
    """Get the global dependency manager instance"""
    return dependency_manager


def print_dependency_status():
    """Print current dependency status"""
    summary = dependency_manager.get_dependency_summary()
    
    print("🔍 DEPENDENCY STATUS REPORT")
    print("=" * 40)
    print(f"📊 {summary['summary']}")
    
    if summary['available_deps']:
        print(f"\n✅ Available ({len(summary['available_deps'])}):")
        for dep in summary['available_deps']:
            print(f"   - {dep}")
    
    if summary['missing_deps']:
        print(f"\n❌ Missing ({len(summary['missing_deps'])}):")
        for dep in summary['missing_deps']:
            print(f"   - {dep}")
    
    print("\n" + "=" * 40)


if __name__ == "__main__":
    print_dependency_status()