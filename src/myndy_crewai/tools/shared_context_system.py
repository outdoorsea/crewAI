"""
Shared Context System for Agent Coordination

This system provides a shared memory and context space that allows multiple
agents to coordinate by sharing information, maintaining conversation context,
and building upon each other's work.

File: tools/shared_context_system.py
"""

import json
import logging
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of context that can be shared between agents."""
    CONVERSATION = "conversation"
    USER_PROFILE = "user_profile"
    TASK_CONTEXT = "task_context"
    AGENT_INSIGHTS = "agent_insights"
    COLLABORATION_STATE = "collaboration_state"
    DECISION_LOG = "decision_log"
    SHARED_MEMORY = "shared_memory"

class AccessLevel(Enum):
    """Access levels for context items."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    OWNER_ONLY = "owner_only"
    PUBLIC = "public"

@dataclass
class ContextItem:
    """Individual context item in the shared system."""
    id: str
    type: ContextType
    title: str
    content: Dict[str, Any]
    owner_agent: str
    access_level: AccessLevel
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    tags: List[str] = None
    related_tasks: List[str] = None
    related_agents: List[str] = None
    version: int = 1

@dataclass
class ContextSubscription:
    """Agent subscription to context updates."""
    agent_id: str
    context_types: List[ContextType]
    tags: List[str]
    created_at: datetime
    last_notification: Optional[datetime] = None

class SharedContextSystem:
    """System for managing shared context between agents."""
    
    def __init__(self):
        """Initialize the shared context system."""
        self.context_items: Dict[str, ContextItem] = {}
        self.subscriptions: Dict[str, ContextSubscription] = {}
        self.access_log: List[Dict[str, Any]] = []
        self.context_lock = threading.Lock()
        
        # Conversation state tracking
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        self.conversation_participants: Dict[str, Set[str]] = {}
        
        logger.info("Shared Context System initialized")
    
    def create_context_item(self, type: ContextType, title: str, content: Dict[str, Any],
                           owner_agent: str, access_level: AccessLevel = AccessLevel.READ_WRITE,
                           tags: List[str] = None, expires_in_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a new context item.
        
        Args:
            type: Type of context
            title: Title for the context item
            content: Content data
            owner_agent: Agent creating the context
            access_level: Access level for other agents
            tags: Optional tags for categorization
            expires_in_hours: Optional expiration time
            
        Returns:
            Creation result with context item ID
        """
        try:
            with self.context_lock:
                context_id = f"ctx_{uuid.uuid4()}"
                
                expires_at = None
                if expires_in_hours:
                    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
                
                context_item = ContextItem(
                    id=context_id,
                    type=type,
                    title=title,
                    content=content,
                    owner_agent=owner_agent,
                    access_level=access_level,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    expires_at=expires_at,
                    tags=tags or [],
                    related_tasks=[],
                    related_agents=[owner_agent]
                )
                
                self.context_items[context_id] = context_item
                
                # Log the creation
                self._log_access(context_id, owner_agent, "create", {"type": type.value, "title": title})
                
                # Notify subscribers
                self._notify_subscribers(context_item, "created")
                
                logger.info(f"Created context item {context_id} by {owner_agent}")
                
                return {
                    "success": True,
                    "context_id": context_id,
                    "type": type.value,
                    "title": title,
                    "access_level": access_level.value
                }
                
        except Exception as e:
            logger.error(f"Error creating context item: {e}")
            return {"success": False, "error": str(e)}
    
    def update_context_item(self, context_id: str, agent_id: str, 
                           updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing context item.
        
        Args:
            context_id: ID of context item to update
            agent_id: Agent making the update
            updates: Updates to apply
            
        Returns:
            Update result
        """
        try:
            with self.context_lock:
                if context_id not in self.context_items:
                    return {"success": False, "error": f"Context item {context_id} not found"}
                
                context_item = self.context_items[context_id]
                
                # Check access permissions
                if not self._can_modify(context_item, agent_id):
                    return {"success": False, "error": "Insufficient permissions to modify context"}
                
                # Apply updates
                if "content" in updates:
                    context_item.content.update(updates["content"])
                
                if "tags" in updates:
                    context_item.tags = updates["tags"]
                
                if "related_tasks" in updates:
                    context_item.related_tasks = updates["related_tasks"]
                
                if "title" in updates:
                    context_item.title = updates["title"]
                
                # Add agent to related agents if not already there
                if agent_id not in context_item.related_agents:
                    context_item.related_agents.append(agent_id)
                
                context_item.updated_at = datetime.utcnow()
                context_item.version += 1
                
                # Log the update
                self._log_access(context_id, agent_id, "update", updates)
                
                # Notify subscribers
                self._notify_subscribers(context_item, "updated")
                
                logger.info(f"Updated context item {context_id} by {agent_id}")
                
                return {
                    "success": True,
                    "context_id": context_id,
                    "version": context_item.version,
                    "updated_at": context_item.updated_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error updating context item: {e}")
            return {"success": False, "error": str(e)}
    
    def get_context_item(self, context_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Get a context item.
        
        Args:
            context_id: ID of context item
            agent_id: Agent requesting the context
            
        Returns:
            Context item data or error
        """
        try:
            if context_id not in self.context_items:
                return {"success": False, "error": f"Context item {context_id} not found"}
            
            context_item = self.context_items[context_id]
            
            # Check if expired
            if context_item.expires_at and datetime.utcnow() > context_item.expires_at:
                return {"success": False, "error": "Context item has expired"}
            
            # Check access permissions
            if not self._can_read(context_item, agent_id):
                return {"success": False, "error": "Insufficient permissions to read context"}
            
            # Log the access
            self._log_access(context_id, agent_id, "read", {})
            
            return {
                "success": True,
                "context_item": asdict(context_item)
            }
            
        except Exception as e:
            logger.error(f"Error getting context item: {e}")
            return {"success": False, "error": str(e)}
    
    def search_context(self, agent_id: str, query: str = None, 
                      context_types: List[ContextType] = None,
                      tags: List[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Search for context items.
        
        Args:
            agent_id: Agent performing the search
            query: Text query to search in titles and content
            context_types: Types of context to search
            tags: Tags to filter by
            limit: Maximum number of results
            
        Returns:
            Search results
        """
        try:
            matching_items = []
            
            for context_item in self.context_items.values():
                # Check if expired
                if context_item.expires_at and datetime.utcnow() > context_item.expires_at:
                    continue
                
                # Check access permissions
                if not self._can_read(context_item, agent_id):
                    continue
                
                # Filter by type
                if context_types and context_item.type not in context_types:
                    continue
                
                # Filter by tags
                if tags and not any(tag in context_item.tags for tag in tags):
                    continue
                
                # Text search
                if query:
                    query_lower = query.lower()
                    title_match = query_lower in context_item.title.lower()
                    content_match = query_lower in json.dumps(context_item.content).lower()
                    
                    if not (title_match or content_match):
                        continue
                
                matching_items.append(context_item)
            
            # Sort by relevance and recency
            matching_items.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Limit results
            matching_items = matching_items[:limit]
            
            return {
                "success": True,
                "results": [asdict(item) for item in matching_items],
                "result_count": len(matching_items)
            }
            
        except Exception as e:
            logger.error(f"Error searching context: {e}")
            return {"success": False, "error": str(e)}
    
    def subscribe_to_updates(self, agent_id: str, context_types: List[ContextType],
                           tags: List[str] = None) -> Dict[str, Any]:
        """
        Subscribe an agent to context updates.
        
        Args:
            agent_id: Agent subscribing
            context_types: Types of context to subscribe to
            tags: Optional tags to filter subscriptions
            
        Returns:
            Subscription result
        """
        try:
            subscription = ContextSubscription(
                agent_id=agent_id,
                context_types=context_types,
                tags=tags or [],
                created_at=datetime.utcnow()
            )
            
            self.subscriptions[agent_id] = subscription
            
            logger.info(f"Agent {agent_id} subscribed to {len(context_types)} context types")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "context_types": [ct.value for ct in context_types],
                "tags": tags or []
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {"success": False, "error": str(e)}
    
    def start_conversation_context(self, conversation_id: str, participants: List[str],
                                 topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start a new conversation context for multi-agent collaboration.
        
        Args:
            conversation_id: Unique conversation identifier
            participants: List of agent IDs participating
            topic: Conversation topic
            context: Initial context data
            
        Returns:
            Conversation creation result
        """
        try:
            with self.context_lock:
                conversation_context = {
                    "id": conversation_id,
                    "topic": topic,
                    "participants": participants,
                    "started_at": datetime.utcnow().isoformat(),
                    "last_activity": datetime.utcnow().isoformat(),
                    "context": context or {},
                    "messages": [],
                    "shared_artifacts": []
                }
                
                self.active_conversations[conversation_id] = conversation_context
                self.conversation_participants[conversation_id] = set(participants)
                
                # Create shared context item for the conversation
                context_result = self.create_context_item(
                    type=ContextType.CONVERSATION,
                    title=f"Conversation: {topic}",
                    content=conversation_context,
                    owner_agent=participants[0],
                    access_level=AccessLevel.READ_WRITE,
                    tags=["conversation", "active"]
                )
                
                logger.info(f"Started conversation {conversation_id} with {len(participants)} participants")
                
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "context_id": context_result.get("context_id"),
                    "participants": participants
                }
                
        except Exception as e:
            logger.error(f"Error starting conversation context: {e}")
            return {"success": False, "error": str(e)}
    
    def add_conversation_message(self, conversation_id: str, agent_id: str,
                               message: str, message_type: str = "message") -> Dict[str, Any]:
        """
        Add a message to a conversation context.
        
        Args:
            conversation_id: Conversation ID
            agent_id: Agent sending the message
            message: Message content
            message_type: Type of message (message, insight, decision, etc.)
            
        Returns:
            Message addition result
        """
        try:
            with self.context_lock:
                if conversation_id not in self.active_conversations:
                    return {"success": False, "error": f"Conversation {conversation_id} not found"}
                
                if agent_id not in self.conversation_participants[conversation_id]:
                    return {"success": False, "error": "Agent not a participant in this conversation"}
                
                conversation = self.active_conversations[conversation_id]
                
                message_entry = {
                    "id": f"msg_{uuid.uuid4()}",
                    "agent_id": agent_id,
                    "message": message,
                    "message_type": message_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                conversation["messages"].append(message_entry)
                conversation["last_activity"] = datetime.utcnow().isoformat()
                
                logger.info(f"Added message to conversation {conversation_id} from {agent_id}")
                
                return {
                    "success": True,
                    "message_id": message_entry["id"],
                    "conversation_id": conversation_id
                }
                
        except Exception as e:
            logger.error(f"Error adding conversation message: {e}")
            return {"success": False, "error": str(e)}
    
    def _can_read(self, context_item: ContextItem, agent_id: str) -> bool:
        """Check if agent can read the context item."""
        if context_item.access_level == AccessLevel.PUBLIC:
            return True
        if context_item.access_level == AccessLevel.OWNER_ONLY:
            return agent_id == context_item.owner_agent
        if context_item.access_level in [AccessLevel.READ_ONLY, AccessLevel.READ_WRITE]:
            return agent_id in context_item.related_agents or agent_id == context_item.owner_agent
        return False
    
    def _can_modify(self, context_item: ContextItem, agent_id: str) -> bool:
        """Check if agent can modify the context item."""
        if context_item.access_level == AccessLevel.OWNER_ONLY:
            return agent_id == context_item.owner_agent
        if context_item.access_level == AccessLevel.READ_WRITE:
            return agent_id in context_item.related_agents or agent_id == context_item.owner_agent
        return False
    
    def _log_access(self, context_id: str, agent_id: str, action: str, details: Dict[str, Any]):
        """Log context access for audit purposes."""
        log_entry = {
            "context_id": context_id,
            "agent_id": agent_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        self.access_log.append(log_entry)
        
        # Keep only last 1000 log entries
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-1000:]
    
    def _notify_subscribers(self, context_item: ContextItem, event_type: str):
        """Notify subscribed agents about context changes."""
        for subscription in self.subscriptions.values():
            if context_item.type in subscription.context_types:
                # Check tag match if subscription has tag filters
                if subscription.tags and not any(tag in context_item.tags for tag in subscription.tags):
                    continue
                
                # Skip if agent is the owner (they already know about the change)
                if subscription.agent_id == context_item.owner_agent:
                    continue
                
                logger.debug(f"Notifying {subscription.agent_id} about {event_type} context {context_item.id}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        try:
            active_contexts = sum(1 for item in self.context_items.values() 
                                if item.expires_at is None or item.expires_at > datetime.utcnow())
            
            return {
                "total_contexts": len(self.context_items),
                "active_contexts": active_contexts,
                "active_conversations": len(self.active_conversations),
                "total_subscriptions": len(self.subscriptions),
                "recent_access_count": len([log for log in self.access_log 
                                          if datetime.fromisoformat(log["timestamp"]) > datetime.utcnow() - timedelta(hours=1)])
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}


# Global instance
_shared_context = SharedContextSystem()

# Tool functions for registry
def create_shared_context(type: str, title: str, content: str, owner_agent: str,
                         access_level: str = "read_write", tags: str = None) -> str:
    """Create a new shared context item."""
    try:
        context_type = ContextType(type)
        access_enum = AccessLevel(access_level)
        content_data = json.loads(content) if content else {}
        tags_list = [tag.strip() for tag in tags.split(",")] if tags else None
        
        result = _shared_context.create_context_item(
            context_type, title, content_data, owner_agent, access_enum, tags_list
        )
        return json.dumps(result, indent=2)
    except (ValueError, json.JSONDecodeError) as e:
        return json.dumps({"success": False, "error": f"Invalid input: {e}"}, indent=2)

def update_shared_context(context_id: str, agent_id: str, updates: str) -> str:
    """Update an existing shared context item."""
    try:
        updates_data = json.loads(updates) if updates else {}
        result = _shared_context.update_context_item(context_id, agent_id, updates_data)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {e}"}, indent=2)

def get_shared_context(context_id: str, agent_id: str) -> str:
    """Get a shared context item."""
    result = _shared_context.get_context_item(context_id, agent_id)
    return json.dumps(result, indent=2)

def search_shared_context(agent_id: str, query: str = None, context_types: str = None,
                         tags: str = None, limit: int = 10) -> str:
    """Search for shared context items."""
    try:
        types_list = [ContextType(t.strip()) for t in context_types.split(",")] if context_types else None
        tags_list = [tag.strip() for tag in tags.split(",")] if tags else None
        
        result = _shared_context.search_context(agent_id, query, types_list, tags_list, limit)
        return json.dumps(result, indent=2)
    except ValueError as e:
        return json.dumps({"success": False, "error": f"Invalid context type: {e}"}, indent=2)

def start_agent_conversation(conversation_id: str, participants: str, topic: str,
                           initial_context: str = None) -> str:
    """Start a new conversation context for multi-agent collaboration."""
    try:
        participants_list = [p.strip() for p in participants.split(",")]
        context_data = json.loads(initial_context) if initial_context else None
        
        result = _shared_context.start_conversation_context(
            conversation_id, participants_list, topic, context_data
        )
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {e}"}, indent=2)

def add_conversation_message(conversation_id: str, agent_id: str, message: str,
                           message_type: str = "message") -> str:
    """Add a message to a conversation context."""
    result = _shared_context.add_conversation_message(conversation_id, agent_id, message, message_type)
    return json.dumps(result, indent=2)

def get_context_system_status() -> str:
    """Get overall shared context system status."""
    result = _shared_context.get_system_status()
    return json.dumps(result, indent=2)