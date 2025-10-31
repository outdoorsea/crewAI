"""
Myndy Memory System Integration

This module provides integration between CrewAI agents and the comprehensive
Myndy memory system, enabling persistent context and knowledge sharing.

File: memory/myndy_memory_integration.py
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import sys

# Add parent directory to path for config imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.env_config import env_config

# Setup Myndy-AI path from environment
myndy_available = env_config.setup_myndy_path()

# HTTP API client for myndy-ai backend
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MyndyAPIClient:
    """HTTP client for myndy-ai API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "CrewAI-Integration/1.0"
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to myndy-ai API"""
        try:
            url = f"{self.base_url}/api/v1{endpoint}"
            response = self.session.request(method, url, json=data, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"API request error: {e}")
            return None
    
    def create_person(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create a person record via API"""
        return self._make_request("POST", "/memory/people", data)
    
    def get_person(self, person_id: str) -> Optional[Dict]:
        """Get person by ID via API"""
        return self._make_request("GET", f"/memory/people/{person_id}")
    
    def create_place(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create a place record via API"""
        return self._make_request("POST", "/memory/places", data)
    
    def create_event(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create an event record via API"""
        return self._make_request("POST", "/memory/events", data)
    
    def create_task(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create a task record via API"""
        return self._make_request("POST", "/memory/tasks", data)
    
    def search_memory(self, query: str, collection: str = "all") -> Optional[Dict]:
        """Search memory via API"""
        return self._make_request("POST", "/memory/search", {
            "query": query,
            "collection": collection
        })

# Initialize API client
api_client = MyndyAPIClient()

# Legacy compatibility - these are now HTTP-based
Person = None
Place = None 
Event = None
Task = None
Project = None
memory_manager = api_client

logger = logging.getLogger(__name__)


class CrewAIMyndyBridge:
    """
    Bridge between CrewAI agents and Myndy memory system.
    
    This class provides methods for CrewAI agents to interact with the
    comprehensive Myndy memory system, enabling persistent context,
    entity management, and conversation history.
    """
    
    def __init__(self, user_id: str = "default_user"):
        """
        Initialize the memory bridge.
        
        Args:
            user_id: User identifier for memory isolation
        """
        self.user_id = user_id
        self.logger = logging.getLogger(f"{__name__}.{user_id}")
        
        # Initialize myndy memory components if available
        self.memory_store = None
        self.entity_manager = None
        self.conversation_manager = None
        
        if MemoryStore:
            try:
                self.memory_store = MemoryStore()
                self.entity_manager = EntityManager(self.memory_store)
                self.conversation_manager = ConversationManager(self.memory_store)
                self.logger.info("Myndy memory components initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize myndy memory components: {e}")
    
    def is_available(self) -> bool:
        """
        Check if the myndy memory system is available.
        
        Returns:
            True if memory system is available, False otherwise
        """
        return all([
            self.memory_store is not None,
            self.entity_manager is not None,
            self.conversation_manager is not None
        ])
    
    def store_agent_interaction(
        self,
        agent_role: str,
        task_description: str,
        result: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store an agent interaction in the memory system.
        
        Args:
            agent_role: Role of the agent that performed the task
            task_description: Description of the task performed
            result: Result or output from the agent
            metadata: Optional metadata about the interaction
            
        Returns:
            Interaction ID or empty string if storage failed
        """
        if not self.is_available():
            self.logger.warning("Memory system not available for storing interaction")
            return ""
        
        try:
            # Create conversation entry for the interaction
            conversation_data = {
                "user_id": self.user_id,
                "agent_role": agent_role,
                "task": task_description,
                "response": result,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Store in conversation manager
            conversation_id = self.conversation_manager.store_conversation(
                user_input=task_description,
                agent_response=result,
                context=conversation_data
            )
            
            self.logger.info(f"Stored agent interaction: {agent_role} - {conversation_id}")
            return str(conversation_id)
            
        except Exception as e:
            self.logger.error(f"Failed to store agent interaction: {e}")
            return ""
    
    def retrieve_conversation_context(
        self,
        agent_role: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation context for an agent.
        
        Args:
            agent_role: Specific agent role to filter by
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of conversation entries
        """
        if not self.is_available():
            self.logger.warning("Memory system not available for retrieving context")
            return []
        
        try:
            # Retrieve recent conversations
            conversations = self.conversation_manager.get_recent_conversations(
                user_id=self.user_id,
                limit=limit
            )
            
            # Filter by agent role if specified
            if agent_role:
                conversations = [
                    conv for conv in conversations
                    if conv.get("metadata", {}).get("agent_role") == agent_role
                ]
            
            self.logger.info(f"Retrieved {len(conversations)} conversation entries")
            return conversations
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve conversation context: {e}")
            return []
    
    def search_memory(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search the memory system for relevant information.
        
        Args:
            query: Search query
            entity_types: Optional list of entity types to filter by
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        if not self.is_available():
            self.logger.warning("Memory system not available for search")
            return []
        
        try:
            # Use entity manager to search
            results = self.entity_manager.search_entities(
                query=query,
                entity_types=entity_types,
                limit=limit
            )
            
            self.logger.info(f"Memory search returned {len(results)} results for: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Memory search failed: {e}")
            return []
    
    def get_entity_relationships(
        self,
        entity_id: str,
        relationship_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get relationships for a specific entity.
        
        Args:
            entity_id: ID of the entity
            relationship_types: Optional list of relationship types to filter by
            
        Returns:
            List of entity relationships
        """
        if not self.is_available():
            self.logger.warning("Memory system not available for relationships")
            return []
        
        try:
            relationships = self.entity_manager.get_entity_relationships(
                entity_id=entity_id,
                relationship_types=relationship_types
            )
            
            self.logger.info(f"Retrieved {len(relationships)} relationships for entity: {entity_id}")
            return relationships
            
        except Exception as e:
            self.logger.error(f"Failed to get entity relationships: {e}")
            return []
    
    def store_task_result(
        self,
        task_name: str,
        result: str,
        agent_role: str,
        status: str = "completed",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a task result in the memory system.
        
        Args:
            task_name: Name of the task
            result: Task result or output
            agent_role: Role of the agent that completed the task
            status: Task status (completed, failed, etc.)
            metadata: Optional metadata about the task
            
        Returns:
            Task ID or empty string if storage failed
        """
        if not self.is_available():
            self.logger.warning("Memory system not available for storing task")
            return ""
        
        try:
            # Create task entity
            task_data = {
                "name": task_name,
                "description": result,
                "status": status,
                "agent_role": agent_role,
                "user_id": self.user_id,
                "completed_at": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Store as task entity
            task_id = self.entity_manager.create_entity("task", task_data)
            
            self.logger.info(f"Stored task result: {task_name} - {task_id}")
            return str(task_id)
            
        except Exception as e:
            self.logger.error(f"Failed to store task result: {e}")
            return ""
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get user profile information from memory.
        
        Returns:
            User profile data
        """
        if not self.is_available():
            self.logger.warning("Memory system not available for user profile")
            return {}
        
        try:
            # Search for user profile entities
            profile_results = self.entity_manager.search_entities(
                query=f"user_id:{self.user_id}",
                entity_types=["profile", "user"],
                limit=1
            )
            
            if profile_results:
                return profile_results[0]
            else:
                return {"user_id": self.user_id, "profile": "default"}
                
        except Exception as e:
            self.logger.error(f"Failed to get user profile: {e}")
            return {}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            Dictionary with memory statistics
        """
        if not self.is_available():
            return {"available": False, "error": "Memory system not available"}
        
        try:
            stats = {
                "available": True,
                "user_id": self.user_id,
                "entities_count": len(self.entity_manager.get_all_entities()),
                "conversations_count": len(
                    self.conversation_manager.get_recent_conversations(
                        user_id=self.user_id,
                        limit=1000
                    )
                ),
                "last_interaction": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {"available": False, "error": str(e)}


# Global memory bridge instance
_memory_bridge = None

def get_memory_bridge(user_id: str = "default_user") -> CrewAIMyndyBridge:
    """
    Get the global memory bridge instance.
    
    Args:
        user_id: User identifier for memory isolation
        
    Returns:
        CrewAIMyndyBridge instance
    """
    global _memory_bridge
    if _memory_bridge is None or _memory_bridge.user_id != user_id:
        _memory_bridge = CrewAIMyndyBridge(user_id)
    return _memory_bridge


class MyndyAwareAgent:
    """
    Mixin class to add memory capabilities to CrewAI agents.
    
    This class provides methods that can be used by agents to interact
    with the Myndy memory system for persistent context and knowledge.
    """
    
    def __init__(self, agent_role: str, user_id: str = "default_user"):
        """
        Initialize memory-aware capabilities.
        
        Args:
            agent_role: Role of the agent
            user_id: User identifier for memory isolation
        """
        self.agent_role = agent_role
        self.user_id = user_id
        self.memory_bridge = get_memory_bridge(user_id)
    
    def remember_interaction(
        self,
        task: str,
        result: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Remember an interaction in the memory system.
        
        Args:
            task: Task description
            result: Task result
            metadata: Optional metadata
            
        Returns:
            Interaction ID
        """
        return self.memory_bridge.store_agent_interaction(
            agent_role=self.agent_role,
            task_description=task,
            result=result,
            metadata=metadata
        )
    
    def recall_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recall recent interaction context.
        
        Args:
            limit: Maximum number of interactions to recall
            
        Returns:
            List of recent interactions
        """
        return self.memory_bridge.retrieve_conversation_context(
            agent_role=self.agent_role,
            limit=limit
        )
    
    def search_knowledge(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        return self.memory_bridge.search_memory(query=query, limit=limit)


if __name__ == "__main__":
    # Test memory integration
    print("Myndy Memory Integration Test")
    print("=" * 40)
    
    bridge = CrewAIMyndyBridge("test_user")
    
    print(f"Memory system available: {bridge.is_available()}")
    
    if bridge.is_available():
        # Test storing an interaction
        interaction_id = bridge.store_agent_interaction(
            agent_role="test_agent",
            task_description="Test task",
            result="Test result",
            metadata={"test": True}
        )
        print(f"Stored interaction: {interaction_id}")
        
        # Test retrieving context
        context = bridge.retrieve_conversation_context(limit=5)
        print(f"Retrieved {len(context)} context entries")
        
        # Test memory stats
        stats = bridge.get_memory_stats()
        print(f"Memory stats: {stats}")
    else:
        print("Memory system not available for testing")