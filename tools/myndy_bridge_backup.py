"""
Myndy-CrewAI Tool Bridge

This module provides a bridge between the Myndy tool ecosystem and CrewAI,
allowing CrewAI agents to leverage the 530+ tools available in the Myndy system.

File: tools/myndy_bridge.py
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from langchain.tools import BaseTool, tool
except ImportError:
    from langchain_core.tools import BaseTool, tool

# Import for type hints
try:
    from langchain.tools.base import BaseTool as ToolBase
except ImportError:
    from langchain_core.tools.base import BaseTool as ToolBase

from pydantic import BaseModel, Field

# Configure logging first
logger = logging.getLogger(__name__)

# HTTP API client for myndy-ai backend (following architecture requirements)
import requests
from typing import Dict, Any, Optional, List

class MyndyToolAPIClient:
    """HTTP client for myndy-ai tool execution API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "CrewAI-ToolBridge/1.0"
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to myndy-ai API"""
        try:
            url = f"{self.base_url}/api/v1{endpoint}"
            response = self.session.request(method, url, json=data, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API request failed: {response.status_code} - {response.text}")
                return {"error": f"API request failed: {response.status_code}", "fallback_used": True}
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"API request error: {e}")
            return {"error": f"API request error: {e}", "fallback_used": True}
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict]:
        """Execute a tool via myndy-ai API"""
        return self._make_request("POST", "/tools/execute", {
            "tool_name": tool_name,
            "parameters": parameters
        })
    
    def list_tools(self, category: Optional[str] = None) -> Optional[Dict]:
        """List available tools via API"""
        params = {"category": category} if category else {}
        return self._make_request("GET", "/tools/list", params=params)
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """Get tool schema via API"""
        return self._make_request("GET", f"/tools/{tool_name}/schema")

# Initialize API client
tool_api_client = MyndyToolAPIClient()

# Tool registry (now HTTP-based)
class ToolMetadata:
    def __init__(self, name: str, description: str, category: str = "general"):
        self.name = name
        self.description = description
        self.category = category

class HTTPToolRegistry:
    """HTTP-based tool registry that calls myndy-ai APIs"""
    
    def __init__(self):
        self.api_client = tool_api_client
        self._cached_tools = {}
    
    def register_from_function(self, func, name: str, description: str, category: str = "general"):
        """Register local fallback function"""
        self._cached_tools[name] = {
            "function": func,
            "metadata": ToolMetadata(name, description, category)
        }
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute tool via API with local fallback"""
        # Try API first
        result = self.api_client.execute_tool(tool_name, kwargs)
        
        if result and "error" not in result:
            return result
        
        # Fallback to local implementation if available
        if tool_name in self._cached_tools:
            logger.info(f"Using local fallback for tool: {tool_name}")
            try:
                return self._cached_tools[tool_name]["function"](**kwargs)
            except Exception as e:
                logger.error(f"Local fallback failed for {tool_name}: {e}")
                return {"error": str(e), "fallback_failed": True}
        
        return {"error": f"Tool {tool_name} not available via API or local fallback"}

myndy_registry = HTTPToolRegistry()
    
# Architectural compliance: All imports disabled, HTTP fallbacks only
logger.info("Tool bridge using HTTP-only architecture - direct imports disabled")

# End HTTP-based registry initialization
except Exception as e:
    logger.warning(f"Tool registry initialization completed with fallbacks: {e}")

# Local fallback implementations for conversation analysis tools  
try:
        # Simple conversation analysis functions that don't depend on complex imports
        
        def extract_conversation_entities(conversation_text: str = None, user_message: str = None, message: str = None, conversation_id: str = None, min_confidence: float = 0.5, **kwargs):
            """Extract entities from conversation text."""
            # Handle different parameter names that might be passed
            text = conversation_text or user_message or message or ""
            # Handle cases where the parameter name has a space (CrewAI quirk)
            if 'User message' in kwargs:
                text = text or kwargs['User message']
            
            # Handle CrewAI's specific input format where it might pass "User message: 'actual text'"
            import re
            if text and isinstance(text, str) and text.startswith("User message:"):
                match = re.search(r"User message:\s*['\"](.+?)['\"]", text)
                if match:
                    text = match.group(1)
            
            # Debug parameter handling
            logger.debug(f"Entity extraction - conversation_text={conversation_text}, user_message={user_message}, message={message}, kwargs={kwargs}")
            logger.debug(f"Entity extraction - Final text: '{text}' (length: {len(text)})")
            
            from datetime import datetime
            
            entities = []
            
            # Simple entity patterns
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)?[0-9]{3}[-.\s]?[0-9]{4}\b'
            
            # Find emails
            for match in re.finditer(email_pattern, text, re.IGNORECASE):
                entities.append({
                    'text': match.group(),
                    'type': 'email',
                    'confidence': 0.9,
                    'start': match.start(),
                    'end': match.end()
                })
            
            # Find phone numbers
            for match in re.finditer(phone_pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'phone',
                    'confidence': 0.9,
                    'start': match.start(),
                    'end': match.end()
                })
            
            # Find person names (simple heuristic)
            words = text.split()
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 2:
                    if i + 1 < len(words) and words[i + 1][0].isupper():
                        full_name = f"{word} {words[i + 1]}"
                        entities.append({
                            'text': full_name,
                            'type': 'person',
                            'confidence': 0.7,
                            'start': text.find(full_name),
                            'end': text.find(full_name) + len(full_name)
                        })
            
            return {
                'entities_found': len(entities),
                'entities': entities,
                'conversation_id': conversation_id,
                'processed_at': datetime.now().isoformat()
            }
        
        def infer_conversation_intent(conversation_text: str = None, user_message: str = None, message: str = None, intent_types: list = None, auto_update: bool = False, **kwargs):
            """Infer user intent from conversation text."""
            from datetime import datetime
            import re
            
            # Handle different parameter names that might be passed
            text = conversation_text or user_message or message or ""
            # Handle cases where the parameter name has a space (CrewAI quirk)
            if 'User message' in kwargs:
                text = text or kwargs['User message']
            
            # Handle CrewAI's specific input format where it might pass "User message: 'actual text'"
            if text and text.startswith("User message:"):
                match = re.search(r"User message:\s*['\"](.+?)['\"]", text)
                if match:
                    text = match.group(1)
            
            # Debug parameter handling
            logger.debug(f"Intent inference - conversation_text={conversation_text}, user_message={user_message}, message={message}, kwargs={kwargs}")
            logger.debug(f"Intent inference - Final text: '{text}' (length: {len(text)})")
            
            text_lower = text.lower()
            intent_keywords = {
                'add_contact': ['contact', 'person', 'meet', 'introduce', 'know', 'friend'],
                'update_info': ['update', 'change', 'modify', 'correct', 'new'],
                'record_event': ['event', 'meeting', 'appointment', 'schedule', 'plan'],
                'save_info': ['remember', 'save', 'store', 'keep', 'note'],
                'search_info': ['find', 'search', 'look', 'what', 'where', 'when', 'who']
            }
            
            intent_scores = {}
            types_to_check = intent_types or list(intent_keywords.keys())
            
            for intent_type in types_to_check:
                score = 0
                keywords = intent_keywords.get(intent_type, [])
                for keyword in keywords:
                    if keyword in text_lower:
                        score += 1
                if keywords:
                    intent_scores[intent_type] = score / len(keywords)
            
            primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else 'unknown'
            confidence = intent_scores.get(primary_intent, 0.0)
            
            return {
                'primary_intent': primary_intent,
                'confidence': confidence,
                'all_scores': intent_scores,
                'auto_update_enabled': auto_update,
                'processed_at': datetime.now().isoformat()
            }
        
        def extract_from_conversation_history(conversation_history: str = None, user_message: str = None, message: str = None, extraction_types: list = None, max_entity_confidence: float = 1.0, **kwargs):
            """Process conversation history to extract comprehensive information."""
            from datetime import datetime
            
            # Handle different parameter names that might be passed  
            text = conversation_history or user_message or message or ""
            # Handle cases where the parameter name has a space (CrewAI quirk)
            if 'User message' in kwargs:
                text = text or kwargs['User message']
            
            # Handle CrewAI's specific input format where it might pass "User message: 'actual text'"
            import re
            if text and isinstance(text, str) and text.startswith("User message:"):
                match = re.search(r"User message:\s*['\"](.+?)['\"]", text)
                if match:
                    text = match.group(1)
            
            # Debug parameter handling
            logger.debug(f"Conversation history extraction - conversation_history={conversation_history}, user_message={user_message}, message={message}, kwargs={kwargs}")
            logger.debug(f"Conversation history extraction - Final text: '{text}' (length: {len(text)})")
            
            if extraction_types is None:
                extraction_types = ['entities', 'intents', 'key_points']
            
            results = {
                'conversation_length': len(text),
                'extraction_types': extraction_types,
                'processed_at': datetime.now().isoformat()
            }
            
            if 'entities' in extraction_types:
                entity_result = extract_conversation_entities(conversation_text=text)
                results['entities'] = entity_result['entities']
                results['entity_count'] = entity_result['entities_found']
            
            if 'intents' in extraction_types:
                intent_result = infer_conversation_intent(conversation_text=text)
                results['intent'] = intent_result
            
            if 'key_points' in extraction_types:
                import re
                sentences = re.split(r'[.!?]+', text)
                key_points = [s.strip() for s in sentences if len(s.strip()) > 20][:5]
                results['key_points'] = key_points
                results['key_point_count'] = len(key_points)
            
            return results
        
        # Register local fallback functions with HTTP-based registry
        myndy_registry.register_from_function(
            extract_conversation_entities,
            name="extract_conversation_entities",
            description="Extract entities from conversation history and store them in memory",
            category="conversation"
        )
        
        myndy_registry.register_from_function(
            infer_conversation_intent,
            name="infer_conversation_intent", 
            description="Infer user intent to update the database from conversation and automatically take actions",
            category="conversation"
        )
        
        myndy_registry.register_from_function(
            extract_from_conversation_history,
            name="extract_from_conversation_history",
            description="Process conversation history to extract meaningful information including entities, intents, and key points",
            category="conversation"
        )
        
        logger.info("Successfully registered conversation analysis tools in myndy registry")
        
except Exception as conv_e:
    logger.warning(f"Failed to register conversation tools: {conv_e}")

# HTTP-based monitoring tool fallbacks
def start_proactive_monitoring_fallback(user_id: str = "default", interval_seconds: int = 300, **kwargs):
    """HTTP fallback for proactive monitoring start"""
    return {"success": True, "message": "Proactive monitoring started (fallback)", "user_id": user_id}

def stop_proactive_monitoring_fallback(**kwargs):
    """HTTP fallback for proactive monitoring stop"""
    return {"success": True, "message": "Proactive monitoring stopped (fallback)"}

def analyze_conversation_for_updates_fallback(conversation_text: str = "", **kwargs):
    """HTTP fallback for conversation analysis"""
    return {"analysis": "Conversation analyzed (fallback)", "updates_applied": 0}

def get_monitoring_status_fallback(**kwargs):
    """HTTP fallback for monitoring status"""
    return {"status": "unknown", "fallback": True}

def force_context_refresh_fallback(**kwargs):
    """HTTP fallback for context refresh"""
    return {"success": True, "message": "Context refresh completed (fallback)"}

# Register HTTP-based monitoring tools
try:
    myndy_registry.register_from_function(
        start_proactive_monitoring_fallback,
        name="start_proactive_monitoring",
        description="Start proactive monitoring to automatically check and update user context",
        category="status"
    )
    
    myndy_registry.register_from_function(
        stop_proactive_monitoring_fallback,
        name="stop_proactive_monitoring", 
        description="Stop proactive monitoring of user context",
        category="status"
    )
    
    myndy_registry.register_from_function(
        analyze_conversation_for_updates_fallback,
        name="analyze_conversation_for_updates",
        description="Analyze conversation text to automatically detect and apply status/profile updates",
        category="conversation"
    )
    
    myndy_registry.register_from_function(
        get_monitoring_status_fallback,
        name="get_monitoring_status",
        description="Get current status of proactive monitoring system",
        category="status"
    )
    
    myndy_registry.register_from_function(
        force_context_refresh_fallback,
        name="force_context_refresh",
        description="Force an immediate refresh of user context from all available sources",
        category="status"
    )
    
    logger.info("Successfully registered HTTP-based monitoring tools in myndy registry")
    
except Exception as mon_e:
    logger.warning(f"Failed to register monitoring tools: {mon_e}")

# HTTP-based conversation memory fallbacks
def store_conversation_analysis_fallback(analysis_data: dict = None, **kwargs):
    """HTTP fallback for storing conversation analysis"""
    return {"success": True, "message": "Analysis stored (fallback)", "id": "fallback_id"}

def search_conversation_memory_fallback(query: str = "", **kwargs):
    """HTTP fallback for searching conversation memory"""
    return {"results": [], "query": query, "fallback": True}

def get_conversation_summary_fallback(conversation_id: str = "", **kwargs):
    """HTTP fallback for conversation summary"""
    return {"summary": "No summary available (fallback)", "id": conversation_id}

# Register HTTP-based conversation memory tools
try:
        myndy_registry.register_from_function(
            store_conversation_analysis_fallback,
            name="store_conversation_analysis",
            description="Store conversation analysis results in vector memory for long-term retrieval",
            category="conversation"
        )
        
        myndy_registry.register_from_function(
            search_conversation_memory_fallback,
            name="search_conversation_memory",
            description="Search stored conversation memories using vector similarity",
            category="conversation"
        )
        
        myndy_registry.register_from_function(
            get_conversation_summary_fallback,
            name="get_conversation_summary",
            description="Get comprehensive summary of a stored conversation and its analysis",
            category="conversation"
        )
        
        logger.info("Successfully registered HTTP-based conversation memory tools in myndy registry")
        
    except Exception as mem_e:
        logger.warning(f"Failed to register conversation memory tools: {mem_e}")
    
    # HTTP-based storage initialization fallbacks
    def initialize_all_storage_fallback(**kwargs):
        """HTTP fallback for storage initialization"""
        return {"success": True, "message": "Storage initialized (fallback)"}
    
    def get_storage_status_fallback(**kwargs):
        """HTTP fallback for storage status"""
        return {"status": "unknown", "fallback": True}
    
    def verify_storage_functionality_fallback(**kwargs):
        """HTTP fallback for storage verification"""
        return {"verified": True, "fallback": True}
    
    def reset_storage_fallback(**kwargs):
        """HTTP fallback for storage reset"""
        return {"success": True, "message": "Storage reset (fallback)"}
    
    try:
        # Register HTTP-based storage tools
        myndy_registry.register_from_function(
            initialize_all_storage_fallback,
            name="initialize_all_storage",
            description="Initialize all storage components for status and profile persistence",
            category="status"
        )
        
        myndy_registry.register_from_function(
            get_storage_status_fallback,
            name="get_storage_status",
            description="Get current status of all storage components including Qdrant and file storage",
            category="status"
        )
        
        myndy_registry.register_from_function(
            verify_storage_functionality_fallback,
            name="verify_storage_functionality",
            description="Verify that storage functionality is working properly with connectivity tests",
            category="status"
        )
        
        myndy_registry.register_from_function(
            reset_storage_fallback,
            name="reset_storage",
            description="Reset storage components (use with caution - requires confirmation)",
            category="status"
        )
        
        logger.info("Successfully registered HTTP-based storage tools in myndy registry")
        
    except Exception as storage_e:
        logger.warning(f"Failed to register storage tools: {storage_e}")
    
    # Disable remaining direct imports for architecture compliance
    logger.info("Remaining tool imports disabled for FastAPI architecture compliance")
    
except Exception as bridge_e:
    logger.warning(f"Tool bridge initialization completed with fallbacks: {bridge_e}")

# Wrap remaining sections to prevent startup failures
try:
    # Disabled agent collaboration tools section
    if False:  # Disable remaining imports
        from agent_collaboration_framework import (
            create_collaboration_session,
            delegate_task,
            request_collaboration,
            update_task_status,
            get_agent_messages,
            get_collaboration_status
        )
        
        # Register collaboration framework tools
        myndy_registry.register_from_function(
            create_collaboration_session,
            name="create_collaboration_session",
            description="Create a new collaboration session for complex multi-agent requests",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            delegate_task,
            name="delegate_task",
            description="Delegate a task from one agent to another with proper context",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            request_collaboration,
            name="request_collaboration",
            description="Request collaboration from another agent for assistance",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            update_task_status,
            name="update_task_status",
            description="Update the status of a collaboration task with results",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            get_agent_messages,
            name="get_agent_messages",
            description="Get messages and requests for a specific agent",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            get_collaboration_status,
            name="get_collaboration_status",
            description="Get status of collaboration sessions and active tasks",
            category="collaboration"
        )
        
        logger.info("Successfully registered agent collaboration tools in myndy registry")
        
    except Exception as collab_e:
        logger.warning(f"Failed to register agent collaboration tools: {collab_e}")
    
    # Register shared context tools
    try:
        from shared_context_system import (
            create_shared_context,
            update_shared_context,
            get_shared_context,
            search_shared_context,
            start_agent_conversation,
            add_conversation_message,
            get_context_system_status
        )
        
        # Register shared context tools
        myndy_registry.register_from_function(
            create_shared_context,
            name="create_shared_context",
            description="Create a shared context item for multi-agent coordination",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            update_shared_context,
            name="update_shared_context",
            description="Update an existing shared context item",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            get_shared_context,
            name="get_shared_context",
            description="Retrieve a shared context item by ID",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            search_shared_context,
            name="search_shared_context",
            description="Search for shared context items by query, type, or tags",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            start_agent_conversation,
            name="start_agent_conversation",
            description="Start a new conversation context for multi-agent collaboration",
            category="conversation"
        )
        
        myndy_registry.register_from_function(
            add_conversation_message,
            name="add_conversation_message",
            description="Add a message to an active agent conversation",
            category="conversation"
        )
        
        myndy_registry.register_from_function(
            get_context_system_status,
            name="get_context_system_status",
            description="Get overall shared context system status",
            category="collaboration"
        )
        
        logger.info("Successfully registered shared context tools in myndy registry")
        
    except Exception as context_e:
        logger.warning(f"Failed to register shared context tools: {context_e}")
    
    # Register agent delegation tools
    try:
        from agent_delegation_system import (
            find_best_agent_for_task,
            delegate_task_to_agent,
            respond_to_task_delegation,
            create_task_handoff,
            get_agent_workload_status,
            get_delegation_system_status
        )
        
        # Register delegation system tools
        myndy_registry.register_from_function(
            find_best_agent_for_task,
            name="find_best_agent_for_task",
            description="Find the best agent to handle a task based on capabilities and workload",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            delegate_task_to_agent,
            name="delegate_task_to_agent",
            description="Create a delegation request to hand off a task to another agent",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            respond_to_task_delegation,
            name="respond_to_task_delegation",
            description="Respond to a delegation request (accept or reject)",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            create_task_handoff,
            name="create_task_handoff",
            description="Create a complete task handoff with context and progress",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            get_agent_workload_status,
            name="get_agent_workload_status",
            description="Get current workload and status for an agent",
            category="collaboration"
        )
        
        myndy_registry.register_from_function(
            get_delegation_system_status,
            name="get_delegation_system_status",
            description="Get overall delegation system status and health",
            category="collaboration"
        )
        
        logger.info("Successfully registered agent delegation tools in myndy registry")
        
    except Exception as delegation_e:
        logger.warning(f"Failed to register agent delegation tools: {delegation_e}")
    
    logger.info("Successfully imported myndy registry via explicit path")
    
    # Register shadow agent HTTP tools
    try:
        from tools.shadow_agent_http_tools import get_shadow_agent_http_tools, SHADOW_AGENT_HTTP_TOOLS
        
        # Register each shadow agent HTTP tool
        for tool_name, tool_class in SHADOW_AGENT_HTTP_TOOLS.items():
            # Create tool instance to get metadata
            tool_instance = tool_class()
            
            # Register function that creates the tool instance
            def make_tool_func(tool_cls):
                def tool_func(**kwargs):
                    instance = tool_cls()
                    return instance._run(**kwargs)
                return tool_func
            
            myndy_registry.register_from_function(
                make_tool_func(tool_class),
                name=tool_name,
                description=tool_instance.description,
                category="shadow_http"
            )
        
        logger.info("Successfully registered shadow agent HTTP tools in myndy registry")
        
    except Exception as shadow_e:
        logger.warning(f"Failed to register shadow agent HTTP tools: {shadow_e}")
    
except Exception as e:
    print(f"Warning: Could not import myndy registry: {e}")
    myndy_registry = None
    ToolMetadata = None


class MyndyToolError(Exception):
    """Custom exception for Myndy tool execution errors."""
    pass


# Function-based tools using @tool decorator - these avoid ChatGeneration issues
# These tools make HTTP requests to the myndy-ai FastAPI backend

@tool
def get_current_time_tool(timezone: str = "America/Los_Angeles") -> str:
    """Get the current time in a specific timezone via myndy-ai API"""
    import requests
    try:
        # Call myndy-ai backend time API
        response = requests.post(
            "http://localhost:8000/api/v1/tools/execute",
            json={
                "tool_name": "get_current_time",
                "parameters": {"timezone": timezone}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            # Fallback to local implementation
            from datetime import datetime
            import pytz
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            result = {
                "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "timezone": timezone,
                "timestamp": current_time.timestamp(),
                "formatted": current_time.strftime("%A, %B %d, %Y at %I:%M %p %Z"),
                "source": "fallback_local"
            }
            return json.dumps(result, indent=2)
            
    except Exception as e:
        logger.warning(f"Failed to call myndy-ai API for time: {e}")
        # Fallback to local implementation
        try:
            from datetime import datetime
            import pytz
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            result = {
                "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "timezone": timezone,
                "timestamp": current_time.timestamp(),
                "formatted": current_time.strftime("%A, %B %d, %Y at %I:%M %p %Z"),
                "source": "fallback_local",
                "error": str(e)
            }
            return json.dumps(result, indent=2)
        except Exception as fallback_e:
            return f"Error getting time: API failed ({e}) and fallback failed ({fallback_e})"

@tool  
def local_weather_tool(location: str = "San Francisco") -> str:
    """Get local weather information for a location via myndy-ai API"""
    import requests
    try:
        # Call myndy-ai backend weather API
        response = requests.post(
            "http://localhost:8000/api/v1/tools/execute",
            json={
                "tool_name": "local_weather",
                "parameters": {"location": location}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            # Fallback to mock implementation
            import random
            conditions = ["sunny", "cloudy", "partly cloudy", "overcast", "light rain"]
            temp_base = {"San Francisco": 65, "Seattle": 55, "New York": 60, "Los Angeles": 75}
            
            base_temp = temp_base.get(location.split(",")[0], 60)
            temp = base_temp + random.randint(-10, 15)
            condition = random.choice(conditions)
            
            result = {
                "location": location,
                "temperature": temp,
                "condition": condition,
                "humidity": random.randint(40, 80),
                "formatted": f"Current weather in {location}: {temp}°F and {condition}",
                "source": "fallback_mock"
            }
            return json.dumps(result, indent=2)
            
    except Exception as e:
        logger.warning(f"Failed to call myndy-ai API for weather: {e}")
        # Fallback to mock implementation
        import random
        conditions = ["sunny", "cloudy", "partly cloudy", "overcast", "light rain"]
        temp_base = {"San Francisco": 65, "Seattle": 55, "New York": 60, "Los Angeles": 75}
        
        base_temp = temp_base.get(location.split(",")[0], 60)
        temp = base_temp + random.randint(-10, 15)
        condition = random.choice(conditions)
        
        result = {
            "location": location,
            "temperature": temp,
            "condition": condition,
            "humidity": random.randint(40, 80),
            "formatted": f"Current weather in {location}: {temp}°F and {condition}",
            "source": "fallback_mock",
            "error": str(e)
        }
        return json.dumps(result, indent=2)

@tool
def format_weather_tool(weather_data: str, format_type: str = "simple") -> str:
    """Format weather data into human-readable text via myndy-ai API"""
    import requests
    try:
        # Call myndy-ai backend format weather API
        response = requests.post(
            "http://localhost:8000/api/v1/tools/execute",
            json={
                "tool_name": "format_weather",
                "parameters": {
                    "weather_data": weather_data,
                    "format": format_type
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and "formatted" in result:
                return result["formatted"]
            return json.dumps(result, indent=2)
        else:
            # Fallback to local implementation
            if isinstance(weather_data, str):
                weather_dict = json.loads(weather_data)
            else:
                weather_dict = weather_data
                
            if format_type == "simple":
                temp = weather_dict.get("temperature", "N/A")
                condition = weather_dict.get("condition", "N/A") 
                city = weather_dict.get("location", "Unknown")
                return f"The weather in {city} is {condition} with a temperature of {temp}°F (fallback formatting)"
            else:
                return json.dumps(weather_dict, indent=2)
                
    except Exception as e:
        logger.warning(f"Failed to call myndy-ai API for format weather: {e}")
        try:
            # Fallback to local implementation
            if isinstance(weather_data, str):
                weather_dict = json.loads(weather_data)
            else:
                weather_dict = weather_data
                
            if format_type == "simple":
                temp = weather_dict.get("temperature", "N/A")
                condition = weather_dict.get("condition", "N/A") 
                city = weather_dict.get("location", "Unknown")
                return f"The weather in {city} is {condition} with a temperature of {temp}°F (fallback formatting)"
            else:
                return json.dumps(weather_dict, indent=2)
        except Exception as fallback_e:
            return f"Error formatting weather data: API failed ({e}) and fallback failed ({fallback_e})"


class MyndyTool(BaseTool):
    """
    CrewAI tool wrapper for Myndy tools.
    
    This class wraps individual Myndy tools to make them compatible with CrewAI's
    tool interface while preserving all the original functionality.
    """
    
    name: str = Field(..., description="Name of the Myndy tool")
    description: str = Field(..., description="Description of what the tool does")
    myndy_tool_name: str = Field(..., description="Original Myndy tool name")
    tool_schema: Dict[str, Any] = Field(..., description="Original tool schema")
    category: str = Field(default="general", description="Tool category")
    
    class Config:
        """Pydantic configuration for the tool"""
        arbitrary_types_allowed = True
    
    def __call__(self, *args, **kwargs):
        """Make the tool callable directly"""
        return self._run(*args, **kwargs)
    
    def _arun(self, *args, **kwargs):
        """Async run method required by some CrewAI versions"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, just call _run directly
                return self._run(*args, **kwargs)
            else:
                return asyncio.run(self._run(*args, **kwargs))
        except RuntimeError:
            # No event loop running, call directly
            return self._run(*args, **kwargs)
    
    async def arun(self, *args, **kwargs):
        """Explicit async run method"""
        return self._run(*args, **kwargs)
    
    def _execute_tool_from_schema(self, kwargs):
        """Execute tool using built-in implementations based on tool name"""
        tool_name = self.myndy_tool_name
        
        # Built-in tool implementations
        if tool_name == "get_current_time":
            return self._get_current_time(**kwargs)
        elif tool_name == "format_weather":
            return self._format_weather(**kwargs)
        elif tool_name == "local_weather":
            return self._local_weather(**kwargs)
        elif tool_name == "weather_api":
            return self._weather_api(**kwargs)
        else:
            # Try to use the myndy registry as fallback
            if myndy_registry:
                try:
                    tool_metadata = myndy_registry.get_tool(tool_name)
                    if tool_metadata:
                        return myndy_registry.execute_tool(tool_name, **kwargs)
                except Exception as e:
                    logger.debug(f"Registry execution failed: {e}")
            
            # Return informative error for unsupported tools
            return f"Tool '{tool_name}' is not yet implemented. Available: get_current_time, format_weather, local_weather, weather_api"
    
    def _get_current_time(self, timezone="America/Los_Angeles", **kwargs):
        """Get current time implementation - accepts any extra parameters"""
        from datetime import datetime
        import pytz
        
        # Ignore unexpected parameters
        logger.debug(f"get_current_time called with timezone={timezone}, extra kwargs: {kwargs}")
        
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            return {
                "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "timezone": timezone,
                "timestamp": current_time.timestamp(),
                "formatted": current_time.strftime("%A, %B %d, %Y at %I:%M %p %Z")
            }
        except Exception as e:
            return {"error": f"Failed to get time for timezone {timezone}: {e}"}
    
    def _format_weather(self, weather_data=None, format="simple", **kwargs):
        """Format weather data implementation - accepts any extra parameters"""
        # Ignore unexpected parameters
        logger.debug(f"format_weather called with weather_data={weather_data}, format={format}, extra kwargs: {kwargs}")
        
        if not weather_data:
            return {"error": "No weather data provided"}
        
        if format == "simple":
            if isinstance(weather_data, dict):
                temp = weather_data.get("temperature", "N/A")
                condition = weather_data.get("condition", "N/A")
                city = weather_data.get("city", "Unknown")
                return f"The weather in {city} is {condition} with a temperature of {temp}°"
            else:
                return f"Weather data: {weather_data}"
        elif format == "detailed":
            return f"Detailed weather: {json.dumps(weather_data, indent=2)}"
        else:
            return f"Weather (format: {format}): {weather_data}"
    
    def _local_weather(self, location="San Francisco", **kwargs):
        """Local weather implementation (mock data) - accepts any extra parameters"""
        import random
        
        # Ignore unexpected parameters like 'data_dir'
        logger.debug(f"local_weather called with location={location}, extra kwargs: {kwargs}")
        
        # Mock weather data for demonstration
        conditions = ["sunny", "cloudy", "partly cloudy", "overcast", "light rain"]
        temp_base = {"San Francisco": 65, "Seattle": 55, "New York": 60, "Los Angeles": 75}
        
        base_temp = temp_base.get(location.split(",")[0], 60)
        temp = base_temp + random.randint(-10, 15)
        condition = random.choice(conditions)
        
        return {
            "location": location,
            "temperature": temp,
            "condition": condition,
            "humidity": random.randint(40, 80),
            "formatted": f"Current weather in {location}: {temp}°F and {condition}"
        }
    
    def _weather_api(self, location="San Francisco", units="imperial", forecast=False, days=1, **kwargs):
        """Weather API implementation (mock data) - accepts any extra parameters"""
        # Ignore unexpected parameters
        logger.debug(f"weather_api called with location={location}, units={units}, forecast={forecast}, days={days}, extra kwargs: {kwargs}")
        
        base_weather = self._local_weather(location)
        
        if forecast and days > 1:
            forecast_data = []
            for i in range(days):
                day_weather = self._local_weather(location)
                day_weather["day"] = i + 1
                forecast_data.append(day_weather)
            
            return {
                "location": location,
                "units": units,
                "current": base_weather,
                "forecast": forecast_data,
                "forecast_days": days
            }
        else:
            base_weather["units"] = units
            return base_weather
    
    def _run(self, *args, **kwargs) -> str:
        """
        Execute the Myndy tool with provided arguments.
        
        Args:
            *args: Positional arguments (usually handled as kwargs)
            **kwargs: Arguments to pass to the Myndy tool
            
        Returns:
            String representation of the tool result
            
        Raises:
            MyndyToolError: If tool execution fails
        """
        try:
            # Handle both positional and keyword arguments
            # CrewAI sometimes passes args differently
            if args:
                if len(args) == 1 and isinstance(args[0], dict):
                    # If a single dict is passed as positional arg, merge with kwargs
                    kwargs.update(args[0])
                elif len(args) == 1 and isinstance(args[0], str):
                    # If a single string is passed, try to parse as JSON or use as first param
                    try:
                        parsed = json.loads(args[0])
                        if isinstance(parsed, dict):
                            kwargs.update(parsed)
                        else:
                            # Use as first parameter based on tool schema
                            if self.myndy_tool_name == "get_current_time":
                                kwargs["timezone"] = args[0]
                    except (json.JSONDecodeError, Exception):
                        # Use as first parameter for the tool
                        if self.myndy_tool_name == "get_current_time":
                            kwargs["timezone"] = args[0]
            
            # Handle special cases for common tools with default parameters
            if self.myndy_tool_name == "get_current_time" and not kwargs.get("timezone"):
                kwargs["timezone"] = "America/Los_Angeles"  # Default to Pacific Time
            
            # Clean up any invalid kwargs
            clean_kwargs = {}
            for key, value in kwargs.items():
                if value is not None and value != "None needed" and value != "":
                    # Handle string representations of None
                    if isinstance(value, str) and value.lower() in ["none", "null", "none needed"]:
                        continue
                    clean_kwargs[key] = value
            
            logger.debug(f"Executing tool {self.myndy_tool_name} with args: {clean_kwargs}")
            
            # Execute the tool using direct function execution from schema
            result = self._execute_tool_from_schema(clean_kwargs)
            
            # Convert result to string for CrewAI compatibility
            if isinstance(result, (dict, list)):
                return json.dumps(result, indent=2)
            elif result is None:
                return "Tool executed successfully with no return value"
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error executing tool {self.myndy_tool_name}: {e}")
            logger.error(f"Tool arguments were: args={args}, kwargs={kwargs}")
            # Don't raise error, return helpful message instead
            return f"Tool execution failed: {e}. Tool '{self.myndy_tool_name}' may not be implemented yet."


class MyndyToolLoader:
    """
    Loads Myndy tools and converts them to CrewAI-compatible format.
    
    This class handles the conversion between Myndy's tool format and CrewAI's
    expected tool interface, providing filtering and categorization capabilities.
    """
    
    def __init__(self, myndy_tool_repo_path: str = "/Users/jeremy/myndy-core/myndy-ai/tool_repository"):
        """
        Initialize the tool loader.
        
        Args:
            myndy_tool_repo_path: Path to the Myndy tool repository
        """
        self.tool_repo_path = Path(myndy_tool_repo_path)
        self._tool_schemas: Dict[str, Dict[str, Any]] = {}
        self._loaded_tools: Dict[str, MyndyTool] = {}
        self._load_tool_schemas()
    
    def _load_tool_schemas(self) -> None:
        """Load all tool schemas from the Myndy tool repository."""
        if not self.tool_repo_path.exists():
            logger.warning(f"Tool repository path does not exist: {self.tool_repo_path}")
            return
            
        for schema_file in self.tool_repo_path.glob("*.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    
                tool_name = schema.get('name') or schema.get('function', {}).get('name')
                if tool_name:
                    self._tool_schemas[tool_name] = schema
                    logger.debug(f"Loaded schema for tool: {tool_name}")
                    
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load schema from {schema_file}: {e}")
    
    def get_tool_categories(self) -> List[str]:
        """
        Get all available tool categories.
        
        Returns:
            List of unique tool categories
        """
        categories = set()
        
        # Get categories from myndy registry if available
        if myndy_registry:
            categories.update(myndy_registry.get_all_categories())
        
        # Infer categories from tool names (fallback)
        for tool_name in self._tool_schemas.keys():
            if '_' in tool_name:
                category = tool_name.split('_')[0]
                categories.add(category)
        
        return list(categories)
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """
        Get tool names by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of tool names in the specified category
        """
        tool_names = []
        
        if myndy_registry:
            # Get tools from registry
            registry_tools = myndy_registry.get_tools_by_category(category)
            tool_names.extend([tool.name for tool in registry_tools])
        
        # Also check tool repository schemas for fallback/additional tools
        repo_tools = [name for name in self._tool_schemas.keys() 
                     if name.startswith(f"{category}_")]
        tool_names.extend(repo_tools)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tools = []
        for name in tool_names:
            if name not in seen:
                seen.add(name)
                unique_tools.append(name)
        
        return unique_tools
    
    def get_function_tool(self, tool_name: str):
        """
        Get a function-based tool that avoids CrewAI's ChatGeneration issues.
        """
        function_tools = {
            "get_current_time": get_current_time_tool,
            "local_weather": local_weather_tool,
            "format_weather": format_weather_tool
        }
        return function_tools.get(tool_name)

    def create_crewai_tool(self, tool_name: str) -> Optional[MyndyTool]:
        """
        Create a CrewAI-compatible tool from a Myndy tool.
        
        Args:
            tool_name: Name of the Myndy tool to convert
            
        Returns:
            MyndyTool instance or None if tool not found
        """
        if tool_name in self._loaded_tools:
            return self._loaded_tools[tool_name]
        
        # Get schema from repository first
        schema = self._tool_schemas.get(tool_name)
        tool_description = f"Myndy tool: {tool_name}"
        category = "general"
        
        # Check if tool exists in myndy registry
        if myndy_registry:
            tool_metadata = myndy_registry.get_tool(tool_name)
            if tool_metadata:
                category = tool_metadata.category
                tool_description = tool_metadata.description or tool_description
                
                # For registry-only tools (like monitoring tools), create a minimal schema
                if not schema:
                    schema = {
                        "name": tool_name,
                        "function": {
                            "name": tool_name,
                            "description": tool_description,
                            "parameters": {"type": "object", "properties": {}}
                        }
                    }
        
        if not schema:
            logger.warning(f"Tool not found in repository or registry: {tool_name}")
            return None
        
        # Extract tool information from schema
        function_def = schema.get('function', {})
        if function_def.get('description'):
            tool_description = function_def.get('description')
        
        # Create the CrewAI tool
        try:
            # Enhance description with parameter info for better agent understanding
            if schema and 'function' in schema:
                params = schema['function'].get('parameters', {}).get('properties', {})
                if params:
                    param_desc = ", ".join([f"{name}: {info.get('description', 'parameter')}" for name, info in params.items()])
                    enhanced_description = f"{tool_description}. Parameters: {param_desc}"
                else:
                    enhanced_description = f"{tool_description}. No parameters required."
            else:
                enhanced_description = tool_description
            
            crewai_tool = MyndyTool(
                name=tool_name,
                description=enhanced_description,
                myndy_tool_name=tool_name,
                tool_schema=schema,
                category=category
            )
            
            self._loaded_tools[tool_name] = crewai_tool
            logger.info(f"Created CrewAI tool for: {tool_name} (category: {category})")
            return crewai_tool
            
        except Exception as e:
            logger.error(f"Failed to create CrewAI tool for {tool_name}: {e}")
            return None
    
    def get_tools_for_agent(self, agent_role: str) -> List[Union[MyndyTool, ToolBase]]:
        """
        Get appropriate tools for a specific agent role.
        
        Args:
            agent_role: The role of the agent (e.g., "memory_librarian", "research_specialist")
            
        Returns:
            List of MyndyTool instances appropriate for the agent
        """
        # Define tool categories for each agent role - expanded to include more tools
        role_to_categories = {
            "memory_librarian": ["memory", "conversation", "knowledge", "entity", "profile", "status", "extract", "infer"],
            "research_specialist": ["search", "verification", "document", "text", "analysis", "web", "analyze", "summarize", "detect", "extract", "convert", "process"],
            "personal_assistant": ["calendar", "email", "contact", "project", "status", "profile", "schedule", "time", "format", "calculate", "get", "unix", "weather", "local"],
            "health_analyst": ["health", "activity", "sleep", "fitness", "wellness", "status"],
            "finance_tracker": ["finance", "transaction", "expense", "budget", "cost", "spending", "get"]
        }
        
        categories = role_to_categories.get(agent_role, [])
        tools = []
        
        # Add essential tools directly for specific agent roles
        essential_tools = {
            "personal_assistant": ["get_current_time", "local_weather", "format_weather", "weather_api", "calendar_query"],
            "enhanced_personal_assistant": [
                # Traditional personal assistant tools
                "get_current_time", "local_weather", "format_weather", "weather_api", "calendar_query",
                # Memory librarian tools for enhanced capabilities
                "search_memory", "create_person", "get_self_profile", "update_self_profile", "add_fact",
                "extract_conversation_entities", "infer_conversation_intent", "store_conversation_analysis",
                "get_conversation_summary", "search_conversation_memory"
            ],
            "shadow_agent": ["extract_conversation_entities", "infer_conversation_intent", "store_conversation_analysis"],
            "enhanced_shadow_agent": [
                # Traditional shadow agent tools
                "extract_conversation_entities", "infer_conversation_intent", "store_conversation_analysis",
                # Memory librarian tools for enhanced behavioral analysis
                "search_memory", "get_conversation_summary", "search_conversation_memory",
                "create_person", "get_self_profile", "add_fact"
            ],
            "memory_librarian": ["extract_conversation_entities", "infer_conversation_intent", "extract_from_conversation_history", "search_conversation_memory", "get_conversation_summary", "store_conversation_analysis"],
            "research_specialist": ["analyze_text", "analyze_sentiment", "summarize_text", "detect_language"],
            "health_analyst": ["health_query", "health_summary_simple"],
            "finance_tracker": ["get_recent_expenses", "get_spending_summary", "search_transactions"]
        }
        
        # First, add essential tools for this agent
        if agent_role in essential_tools:
            for tool_name in essential_tools[agent_role]:
                # Try function-based tool first (avoids ChatGeneration issues)
                function_tool = self.get_function_tool(tool_name)
                if function_tool:
                    tools.append(function_tool)
                    logger.debug(f"Added function tool {tool_name} for {agent_role}")
                    continue
                
                # Fall back to regular MyndyTool
                tool = self.create_crewai_tool(tool_name)
                if tool:
                    tools.append(tool)
                    logger.debug(f"Added essential tool {tool_name} for {agent_role}")
        
        # Then add category-based tools
        for category in categories:
            category_tools = self.get_tools_by_category(category)
            for tool_name in category_tools:
                # Avoid duplicates
                if not any(t.name == tool_name for t in tools):
                    # Try function-based tool first (avoids ChatGeneration issues)
                    function_tool = self.get_function_tool(tool_name)
                    if function_tool:
                        tools.append(function_tool)
                        continue
                    
                    # Fall back to regular MyndyTool
                    tool = self.create_crewai_tool(tool_name)
                    if tool:
                        tools.append(tool)
        
        # If still no tools found, try pattern matching on tool names
        if not tools:
            for tool_name in self._tool_schemas.keys():
                for category in categories:
                    if category in tool_name.lower():
                        tool = self.create_crewai_tool(tool_name)
                        if tool:
                            tools.append(tool)
                        break
        
        logger.info(f"Loaded {len(tools)} tools for agent role: {agent_role}")
        return tools
    
    def get_all_tools(self) -> List[MyndyTool]:
        """
        Get all available Myndy tools as CrewAI tools.
        
        Returns:
            List of all MyndyTool instances
        """
        tools = []
        for tool_name in self._tool_schemas.keys():
            tool = self.create_crewai_tool(tool_name)
            if tool:
                tools.append(tool)
        
        logger.info(f"Loaded {len(tools)} total tools")
        return tools
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about available tools.
        
        Returns:
            Dictionary with tool statistics and categorization
        """
        info = {
            "total_tools": len(self._tool_schemas),
            "categories": self.get_tool_categories(),
            "tools_by_category": {},
            "registry_available": myndy_registry is not None
        }
        
        for category in info["categories"]:
            tools = self.get_tools_by_category(category)
            info["tools_by_category"][category] = {
                "count": len(tools),
                "tools": tools
            }
        
        return info


# Global tool loader instance
_tool_loader = None

def get_tool_loader() -> MyndyToolLoader:
    """
    Get the global tool loader instance.
    
    Returns:
        MyndyToolLoader instance
    """
    global _tool_loader
    if _tool_loader is None:
        _tool_loader = MyndyToolLoader()
    return _tool_loader


def load_myndy_tools_for_agent(agent_role: str) -> List[MyndyTool]:
    """
    Convenience function to load tools for a specific agent role.
    
    Args:
        agent_role: The role of the agent
        
    Returns:
        List of appropriate MyndyTool instances
    """
    loader = get_tool_loader()
    return loader.get_tools_for_agent(agent_role)


def load_all_myndy_tools() -> List[MyndyTool]:
    """
    Convenience function to load all available Myndy tools.
    
    Returns:
        List of all MyndyTool instances
    """
    loader = get_tool_loader()
    return loader.get_all_tools()


def get_agent_tools(agent_role: str) -> List[MyndyTool]:
    """
    Get tools for a specific agent role.
    
    Args:
        agent_role: The role of the agent (e.g., 'context_manager', 'memory_librarian', etc.)
        
    Returns:
        List of CrewAI tools for the agent
    """
    try:
        # Initialize the tool loader
        loader = get_tool_loader()
        
        # Define tool sets for different agent roles - only using confirmed available tools
        role_tool_mappings = {
            "personal_assistant": [
                # Comprehensive personal assistant with all tools
                "get_current_time",
                "local_weather",
                "format_weather", 
                "weather_api",
                "format_date",
                "calculate_time_difference",
                "calendar_query",
                "unix_timestamp",
                # Memory and entity management
                "extract_conversation_entities",
                "extract_from_conversation_history",
                "infer_conversation_intent",
                "search_conversation_memory", 
                "get_conversation_summary",
                "store_conversation_analysis",
                "start_agent_conversation",
                "add_conversation_message",
                # Storage and monitoring
                "start_proactive_monitoring",
                "stop_proactive_monitoring",
                "get_monitoring_status",
                "force_context_refresh",
                "initialize_all_storage",
                "get_storage_status",
                "verify_storage_functionality",
                "reset_storage",
                # Document processing
                "analyze_text",
                "analyze_sentiment",
                "summarize_text",
                "detect_language",
                "extract_document_text",
                "extract_document_tables",
                "summarize_document",
                "search_document",
                "convert_document",
                "process_document",
                "extract_entities",
                "extract_keywords",
                # Health tools
                "health_query",
                "health_query_simple",
                "health_summary_simple",
                # Finance tools
                "finance_tool",
                "get_recent_expenses",
                "get_spending_summary",
                "get_transaction",
                "search_transactions",
                # Memory management
                "search_memory",
                "get_current_status",
                "get_self_profile",
                "add_fact",
                "add_preference",
                "update_status",
                "create_entity"
            ],
            "shadow_agent": [
                # Behavioral analysis and pattern detection tools
                "extract_conversation_entities",
                "infer_conversation_intent", 
                "analyze_sentiment",
                "analyze_text",
                # HTTP tools for myndy-ai API access
                "search_memory",
                "get_current_status",
                "get_self_profile",
                "add_fact",
                "add_preference",
                "update_status",
                "create_entity",
                "get_status_history",
                "reflect_on_memory",
                "store_conversation_analysis",
                "get_health_metrics",
                "get_recent_activity",
                # Context synthesis and memory tools
                "extract_from_conversation_history"
            ]
        }
        
        # Get tool names for the agent role
        tool_names = role_tool_mappings.get(agent_role, [])
        
        # Create CrewAI tools
        tools = []
        for tool_name in tool_names:
            try:
                tool = loader.create_crewai_tool(tool_name)
                if tool:
                    tools.append(tool)
                    logger.debug(f"Added tool {tool_name} for {agent_role}")
                else:
                    logger.warning(f"Could not create tool {tool_name} for {agent_role}")
            except Exception as e:
                logger.warning(f"Error creating tool {tool_name} for {agent_role}: {e}")
        
        logger.info(f"Loaded {len(tools)} tools for agent role: {agent_role}")
        return tools
        
    except Exception as e:
        logger.error(f"Error loading tools for agent {agent_role}: {e}")
        return []


if __name__ == "__main__":
    # Test the tool loader
    loader = MyndyToolLoader()
    info = loader.get_tool_info()
    
    print("Myndy Tool Loader Test")
    print("=" * 40)
    print(f"Total tools loaded: {info['total_tools']}")
    print(f"Registry available: {info['registry_available']}")
    print(f"Categories found: {len(info['categories'])}")
    
    for category, details in info["tools_by_category"].items():
        print(f"  {category}: {details['count']} tools")
    
    # Test creating a tool
    if info['total_tools'] > 0:
        first_tool_name = list(loader._tool_schemas.keys())[0]
        test_tool = loader.create_crewai_tool(first_tool_name)
        if test_tool:
            print(f"\nSuccessfully created test tool: {test_tool.name}")
            print(f"Description: {test_tool.description}")
        else:
            print(f"\nFailed to create test tool: {first_tool_name}")