"""
Myndy-CrewAI HTTP-Only Tool Bridge

This module provides a compliant bridge between the Myndy tool ecosystem and CrewAI,
using ONLY HTTP communication to the myndy-ai FastAPI backend. This follows the
mandatory service-oriented architecture requirements.

ARCHITECTURAL COMPLIANCE:
✅ HTTP-only communication with myndy-ai FastAPI endpoints
✅ No direct imports from myndy-ai modules  
✅ No shared database connections or file system access
✅ Proper error handling for service unavailability
✅ Authentication via API keys

File: tools/myndy_bridge_http_only.py
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

try:
    # Try LangChain's BaseTool first (which CrewAI uses)
    from langchain.tools import BaseTool
except ImportError:
    try:
        from langchain_core.tools import BaseTool
    except ImportError:
        # Fallback to CrewAI imports
        try:
            from crewai.tools.base_tool import BaseTool
        except ImportError:
            try:
                from crewai.tools import BaseTool
            except ImportError:
                from crewai import BaseTool

from pydantic import BaseModel, Field
from typing import Type

# Configure logging
logger = logging.getLogger("crewai.myndy_bridge_http")

# Configuration from environment variables
MYNDY_API_BASE_URL = os.getenv('MYNDY_API_BASE_URL', 'http://127.0.0.1:8000')
MYNDY_API_KEY = os.getenv('MYNDY_API_KEY', 'development-key-crewai-integration')


class MyndyHTTPTool(BaseTool):
    """Base class for all Myndy HTTP tools"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to myndy-ai FastAPI backend"""
        try:
            import httpx
            
            url = f"{MYNDY_API_BASE_URL.rstrip('/')}{endpoint}"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": MYNDY_API_KEY
            }
            
            with httpx.Client(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = client.get(url, headers=headers, params=data or {})
                elif method.upper() == "POST":
                    response = client.post(url, headers=headers, json=data or {})
                elif method.upper() == "PUT":
                    response = client.put(url, headers=headers, json=data or {})
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"HTTP API request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to communicate with myndy-ai FastAPI service",
                "note": f"Ensure myndy-ai server is running on {MYNDY_API_BASE_URL}"
            }


# Core Memory Operations
class SearchMemoryHTTPTool(MyndyHTTPTool):
    """Search memory via HTTP API"""
    name: str = "search_memory"
    description: str = "Search through memory using semantic search via HTTP API"
    
    def _run(self, query: str, limit: int = 10, **kwargs) -> str:
        data = {"query": query, "limit": limit}
        result = self._make_api_request("POST", "/api/v1/memory/search", data)
        return json.dumps(result, indent=2)


class CreatePersonHTTPTool(MyndyHTTPTool):
    """Create person entity via HTTP API"""
    name: str = "create_person"
    description: str = "Create a new person entity in memory via HTTP API"
    
    def _run(self, name: str, email: str = None, phone: str = None, **kwargs) -> str:
        data = {"name": name}
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone
        
        result = self._make_api_request("POST", "/api/v1/memory/people", data)
        return json.dumps(result, indent=2)


class AddFactHTTPTool(MyndyHTTPTool):
    """Add fact to memory via HTTP API"""
    name: str = "add_fact"
    description: str = "Add a fact to memory storage via HTTP API"
    
    def _run(self, content: str, category: str = "general", **kwargs) -> str:
        data = {"content": content, "category": category}
        result = self._make_api_request("POST", "/api/v1/memory/facts", data)
        return json.dumps(result, indent=2)


# Profile Management
class GetSelfProfileHTTPTool(MyndyHTTPTool):
    """Get user profile via HTTP API"""
    name: str = "get_self_profile"
    description: str = "Retrieve user profile information via HTTP API"
    
    def _run(self, **kwargs) -> str:
        result = self._make_api_request("GET", "/api/v1/profile/self")
        return json.dumps(result, indent=2)


class UpdateSelfProfileHTTPTool(MyndyHTTPTool):
    """Update user profile via HTTP API"""
    name: str = "update_self_profile"
    description: str = "Update user profile information via HTTP API"
    
    def _run(self, name: str = None, age: int = None, email: str = None, 
             location: str = None, occupation: str = None, interests: str = None, 
             bio: str = None, **kwargs) -> str:
        data = {}
        if name:
            data["name"] = name
        if age:
            data["age"] = age
        if email:
            data["email"] = email
        if location:
            data["location"] = location
        if occupation:
            data["occupation"] = occupation
        if interests:
            data["interests"] = interests.split(",") if isinstance(interests, str) else interests
        if bio:
            data["bio"] = bio
            
        result = self._make_api_request("POST", "/api/v1/profile/self/update", data)
        return json.dumps(result, indent=2)


# Status Management
class GetCurrentStatusHTTPTool(MyndyHTTPTool):
    """Get current status via HTTP API"""
    name: str = "get_current_status"
    description: str = "Get current user status via HTTP API"
    
    def _run(self, **kwargs) -> str:
        result = self._make_api_request("GET", "/api/v1/status/current")
        return json.dumps(result, indent=2)


class UpdateStatusHTTPTool(MyndyHTTPTool):
    """Update user status via HTTP API"""
    name: str = "update_status"
    description: str = "Update user status via HTTP API"
    
    def _run(self, status: str, mood: str = None, energy_level: int = None, **kwargs) -> str:
        data = {"status": status}
        if mood:
            data["mood"] = mood
        if energy_level is not None:
            data["energy_level"] = energy_level
            
        result = self._make_api_request("POST", "/api/v1/status/update", data)
        return json.dumps(result, indent=2)


# Conversation Analysis
class ExtractConversationEntitiesHTTPTool(MyndyHTTPTool):
    """Extract entities from conversation via HTTP API"""
    name: str = "extract_conversation_entities"
    description: str = "Extract entities from conversation text via HTTP API"
    
    def _run(self, conversation_text: str, **kwargs) -> str:
        data = {"conversation_text": conversation_text}
        result = self._make_api_request("POST", "/api/v1/conversation/extract-entities", data)
        return json.dumps(result, indent=2)


class InferConversationIntentHTTPTool(MyndyHTTPTool):
    """Infer conversation intent via HTTP API"""
    name: str = "infer_conversation_intent"
    description: str = "Infer intent from conversation text via HTTP API"
    
    def _run(self, conversation_text: str, **kwargs) -> str:
        data = {"conversation_text": conversation_text}
        result = self._make_api_request("POST", "/api/v1/conversation/infer-intent", data)
        return json.dumps(result, indent=2)


class CreatePlaceHTTPTool(MyndyHTTPTool):
    """Create a new place via HTTP API"""
    name: str = "create_place"
    description: str = "Create a new place in memory with name, description, type, and optional address/coordinates"
    
    def _run(self, place_info: str, **kwargs) -> str:
        """
        Create a place from descriptive text.
        
        Args:
            place_info: Descriptive text about the place (e.g., "Starbucks on Main Street, coffee shop with WiFi")
        """
        try:
            # Parse the place information from text
            # Simple parsing - in practice, this could be more sophisticated
            parts = [part.strip() for part in place_info.split(',')]
            
            data = {
                "name": parts[0] if parts else place_info,
                "place_type": "location"
            }
            
            # Try to extract description, type, and other info from remaining parts
            if len(parts) > 1:
                for part in parts[1:]:
                    part_lower = part.lower()
                    if any(word in part_lower for word in ['coffee', 'cafe', 'restaurant', 'shop', 'store']):
                        data["place_type"] = "cafe" if 'coffee' in part_lower or 'cafe' in part_lower else "business"
                    elif any(word in part_lower for word in ['office', 'building', 'workplace']):
                        data["place_type"] = "office"
                    elif any(word in part_lower for word in ['park', 'garden', 'outdoor']):
                        data["place_type"] = "park"
                    elif any(word in part_lower for word in ['home', 'house', 'apartment']):
                        data["place_type"] = "home"
                    elif any(word in part_lower for word in ['gym', 'fitness', 'workout']):
                        data["place_type"] = "gym"
                    
                    # Use remaining parts as description
                    if part != parts[0] and not data.get("description"):
                        data["description"] = part
            
            result = self._make_api_request("POST", "/api/v1/memory/places", data)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)


class SearchPlacesHTTPTool(MyndyHTTPTool):
    """Search for places via HTTP API"""
    name: str = "search_places"
    description: str = "Search for places by name, type, or description"
    
    def _run(self, query: str, **kwargs) -> str:
        """
        Search for places.
        
        Args:
            query: Search query for places (e.g., "coffee shops", "parks near downtown")
        """
        try:
            # Use the memory search endpoint with places enabled
            data = {
                "query": query,
                "limit": 10,
                "include_people": False,
                "include_places": True,
                "include_events": False,
                "include_content": False
            }
            result = self._make_api_request("POST", "/api/v1/memory/search", data)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)


# Tool Categories for Agent Assignment
HTTP_TOOL_CATEGORIES = {
    "memory_operations": [
        SearchMemoryHTTPTool,
        CreatePersonHTTPTool,
        AddFactHTTPTool,
    ],
    "profile_management": [
        GetSelfProfileHTTPTool,
        UpdateSelfProfileHTTPTool,
    ],
    "status_management": [
        GetCurrentStatusHTTPTool,
        UpdateStatusHTTPTool,
    ],
    "conversation_analysis": [
        ExtractConversationEntitiesHTTPTool,
        InferConversationIntentHTTPTool,
    ]
}

# Agent Role Tool Mappings (HTTP-Only)
AGENT_TOOL_MAPPINGS_HTTP = {
    "Memory Librarian": [
        SearchMemoryHTTPTool(),
        CreatePersonHTTPTool(),
        AddFactHTTPTool(),
        ExtractConversationEntitiesHTTPTool(),
    ],
    "Personal Assistant": [
        GetSelfProfileHTTPTool(),
        UpdateSelfProfileHTTPTool(),
        GetCurrentStatusHTTPTool(),
        UpdateStatusHTTPTool(),
    ],
    "Research Specialist": [
        SearchMemoryHTTPTool(),
        ExtractConversationEntitiesHTTPTool(),
        InferConversationIntentHTTPTool(),
    ],
    "Health Analyst": [
        GetSelfProfileHTTPTool(),
        GetCurrentStatusHTTPTool(),
        SearchMemoryHTTPTool(),
    ],
    "Finance Tracker": [
        SearchMemoryHTTPTool(),
        AddFactHTTPTool(),
        GetSelfProfileHTTPTool(),
    ]
}


def get_tools_for_agent(agent_name: str) -> List[MyndyHTTPTool]:
    """Get HTTP tools for a specific agent"""
    return AGENT_TOOL_MAPPINGS_HTTP.get(agent_name, [])


def get_all_http_tools() -> List[MyndyHTTPTool]:
    """Get all available HTTP tools"""
    all_tools = []
    for category_tools in HTTP_TOOL_CATEGORIES.values():
        all_tools.extend([tool() for tool in category_tools])
    return all_tools


def test_api_connectivity() -> Dict[str, Any]:
    """Test connectivity to myndy-ai FastAPI service"""
    try:
        import httpx
        
        url = f"{MYNDY_API_BASE_URL}/health"
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return {
                "success": True,
                "message": "Successfully connected to myndy-ai FastAPI service",
                "url": url,
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to connect to myndy-ai FastAPI service",
            "url": f"{MYNDY_API_BASE_URL}/health",
            "note": "Ensure myndy-ai FastAPI server is running"
        }


# Export main interface
__all__ = [
    "MyndyHTTPTool",
    "SearchMemoryHTTPTool",
    "CreatePersonHTTPTool", 
    "AddFactHTTPTool",
    "GetSelfProfileHTTPTool",
    "UpdateSelfProfileHTTPTool",
    "GetCurrentStatusHTTPTool",
    "UpdateStatusHTTPTool",
    "ExtractConversationEntitiesHTTPTool",
    "InferConversationIntentHTTPTool",
    "get_tools_for_agent",
    "get_all_http_tools",
    "test_api_connectivity",
    "AGENT_TOOL_MAPPINGS_HTTP"
]