"""
agent_manager.py - Production-ready agent manager with runtime mode switching

This module provides a production-ready agent management system that switches
behavior based on runtime mode (production vs testing).

File: agents/agent_manager.py
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from enum import Enum

# Import runtime configuration
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.runtime_config import runtime_config, should_fail_fast, should_use_fallback

logger = logging.getLogger(__name__)


class AgentCreationError(Exception):
    """Exception raised when agent creation fails"""
    pass


class AgentType(Enum):
    """Available agent types"""
    MEMORY = "memory"
    STATUS = "status" 
    CONVERSATION = "conversation"
    TIME = "time"
    WEATHER = "weather"
    TEST_ASSISTANT = "test_assistant"


class AgentManager:
    """Production-ready agent manager with mode-aware behavior"""
    
    def __init__(self):
        self.available_agents = {}
        self.mock_agents_cache = {}
        self._discover_agents()
    
    def _discover_agents(self) -> None:
        """Discover available agent creation functions"""
        agent_imports = {
            AgentType.MEMORY: ('agents.fastapi_memory_agent', 'create_fastapi_memory_agent'),
            AgentType.STATUS: ('agents.fastapi_status_agent', 'create_fastapi_status_agent'),
            AgentType.CONVERSATION: ('agents.fastapi_conversation_agent', 'create_fastapi_conversation_agent'),
            AgentType.TIME: ('agents.fastapi_time_agent', 'create_fastapi_time_agent'),
            AgentType.WEATHER: ('agents.fastapi_weather_agent', 'create_fastapi_weather_agent'),
            AgentType.TEST_ASSISTANT: ('agents.fastapi_test_assistant', 'create_fastapi_test_assistant'),
        }
        
        for agent_type, (module_name, function_name) in agent_imports.items():
            try:
                module = __import__(module_name, fromlist=[function_name])
                create_func = getattr(module, function_name)
                self.available_agents[agent_type] = create_func
                
                if runtime_config.get_config_value('verbose_dependency_logging', False):
                    logger.info(f"✅ {agent_type.value} agent available")
                
            except ImportError as e:
                if should_fail_fast('agent_creation_error'):
                    logger.error(f"❌ Failed to import {agent_type.value} agent: {e}")
                else:
                    logger.debug(f"⚠️  {agent_type.value} agent not available: {e}")
            except Exception as e:
                if should_fail_fast('agent_creation_error'):
                    logger.error(f"❌ Error importing {agent_type.value} agent: {e}")
                else:
                    logger.debug(f"⚠️  {agent_type.value} agent error: {e}")
    
    def create_agent(
        self, 
        agent_type: Union[AgentType, str], 
        fallback_to_mock: Optional[bool] = None,
        **kwargs
    ) -> Any:
        """
        Create an agent with mode-aware behavior
        
        Args:
            agent_type: Type of agent to create
            fallback_to_mock: Whether to use mock agent if real one fails (overrides mode default)
            **kwargs: Arguments passed to agent creation function
            
        Returns:
            Agent instance or mock agent
            
        Raises:
            AgentCreationError: In production mode when agent creation fails
        """
        # Convert string to enum if needed
        if isinstance(agent_type, str):
            try:
                agent_type = AgentType(agent_type.lower())
            except ValueError:
                raise AgentCreationError(f"Invalid agent type: {agent_type}")
        
        # Determine fallback behavior
        if fallback_to_mock is None:
            fallback_to_mock = should_use_fallback('agents')
        
        # Try to create real agent
        if agent_type in self.available_agents:
            try:
                agent = self.available_agents[agent_type](**kwargs)
                logger.debug(f"✅ Created {agent_type.value} agent")
                return agent
                
            except Exception as e:
                error_msg = f"Failed to create {agent_type.value} agent: {e}"
                
                if should_fail_fast('agent_creation_error'):
                    logger.error(error_msg)
                    raise AgentCreationError(error_msg)
                else:
                    logger.warning(error_msg)
                    # Fall through to fallback logic
        
        # Handle missing or failed agent
        if fallback_to_mock and should_use_fallback('agents'):
            return self._create_mock_agent(agent_type)
        else:
            error_msg = f"Agent {agent_type.value} not available and fallback disabled"
            if should_fail_fast('agent_creation_error'):
                logger.error(error_msg)
                raise AgentCreationError(error_msg)
            else:
                logger.warning(error_msg)
                return None
    
    def _create_mock_agent(self, agent_type: AgentType) -> Any:
        """Create a mock agent for testing"""
        # Check if mock agents are allowed
        if not should_use_fallback('agents'):
            raise AgentCreationError(f"Mock agents not allowed in production mode")
        
        # Use cached mock agent if available
        if agent_type in self.mock_agents_cache:
            return self.mock_agents_cache[agent_type]
        
        class MockAgent:
            def __init__(self, agent_type: AgentType):
                self.role = f"Mock {agent_type.value.title().replace('_', ' ')} Agent"
                self.goal = f"Mock {agent_type.value} agent for testing purposes"
                self.backstory = f"A mock agent created when {agent_type.value} agent is unavailable"
                self.tools = []
                self.memory = True
                self.llm = None
                self.verbose = False
                self.agent_type = agent_type
                
            def __str__(self):
                return f"MockAgent({self.agent_type.value})"
                
            def __repr__(self):
                return self.__str__()
        
        mock_agent = MockAgent(agent_type)
        self.mock_agents_cache[agent_type] = mock_agent
        
        if runtime_config.get_config_value('verbose_dependency_logging', False):
            logger.warning(f"Created mock {agent_type.value} agent (mode: {runtime_config.mode.value})")
        
        return mock_agent
    
    def get_available_agents(self) -> List[AgentType]:
        """Get list of available agent types"""
        return list(self.available_agents.keys())
    
    def is_agent_available(self, agent_type: Union[AgentType, str]) -> bool:
        """Check if agent type is available"""
        if isinstance(agent_type, str):
            try:
                agent_type = AgentType(agent_type.lower())
            except ValueError:
                return False
        return agent_type in self.available_agents
    
    def create_all_available_agents(self, **kwargs) -> Dict[AgentType, Any]:
        """Create all available agents"""
        agents = {}
        
        for agent_type in AgentType:
            try:
                agent = self.create_agent(agent_type, **kwargs)
                if agent is not None:
                    agents[agent_type] = agent
            except AgentCreationError as e:
                if should_fail_fast('agent_creation_error'):
                    raise
                else:
                    logger.warning(f"Failed to create {agent_type.value}: {e}")
        
        return agents
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        available_count = len(self.available_agents)
        total_count = len(AgentType)
        mock_count = len(self.mock_agents_cache)
        
        return {
            'runtime_mode': runtime_config.mode.value,
            'available_agents': [agent.value for agent in self.available_agents.keys()],
            'available_count': available_count,
            'total_agent_types': total_count,
            'mock_agents_cached': mock_count,
            'availability_rate': f"{available_count}/{total_count}",
            'fallback_enabled': should_use_fallback('agents'),
            'fail_fast_enabled': should_fail_fast('agent_creation_error'),
        }


# Global agent manager instance
agent_manager = AgentManager()


def create_agent(agent_type: Union[AgentType, str], **kwargs) -> Any:
    """Global function to create agents"""
    return agent_manager.create_agent(agent_type, **kwargs)


def get_available_agents() -> List[AgentType]:
    """Global function to get available agents"""
    return agent_manager.get_available_agents()


def is_agent_available(agent_type: Union[AgentType, str]) -> bool:
    """Global function to check agent availability"""
    return agent_manager.is_agent_available(agent_type)


def print_agent_status():
    """Print agent manager status"""
    status = agent_manager.get_status_summary()
    
    print("🤖 CREWAI AGENT MANAGER STATUS")
    print("=" * 50)
    print(f"Runtime Mode: {status['runtime_mode'].upper()}")
    print(f"Available Agents: {status['availability_rate']}")
    print(f"Fallback Enabled: {status['fallback_enabled']}")
    print(f"Fail Fast Enabled: {status['fail_fast_enabled']}")
    
    if status['available_agents']:
        print(f"\n✅ Available ({status['available_count']}):")
        for agent_type in status['available_agents']:
            print(f"   - {agent_type}")
    
    unavailable = set(agent.value for agent in AgentType) - set(status['available_agents'])
    if unavailable:
        print(f"\n❌ Unavailable ({len(unavailable)}):")
        for agent_type in unavailable:
            print(f"   - {agent_type}")
    
    if status['mock_agents_cached'] > 0:
        print(f"\n🎭 Mock Agents Cached: {status['mock_agents_cached']}")
    
    print("=" * 50)


if __name__ == "__main__":
    print_agent_status()