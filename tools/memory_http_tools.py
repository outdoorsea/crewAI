#!/usr/bin/env python3
"""
Memory HTTP Client Tools

HTTP client tools for memory operations that communicate with the Myndy-AI FastAPI backend.
These tools follow the mandatory service-oriented architecture.

File: tools/memory_http_tools.py
"""

import json
import logging
import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

try:
    from langchain.tools import BaseTool, tool
except ImportError:
    from langchain_core.tools import BaseTool, tool

from pydantic import BaseModel, Field

logger = logging.getLogger("crewai.memory_http_tools")

class MemoryAPIClient:
    """HTTP client for Myndy-AI memory API endpoints"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        # Use environment configuration
        if base_url is None:
            try:
                from ..config.env_config import env_config
                base_url = env_config.myndy_api_base_url
            except ImportError:
                import os
                base_url = os.getenv("CREWAI_MYNDY_API_URL", "http://localhost:8081")
        
        if api_key is None:
            try:
                from ..config.env_config import env_config
                api_key = env_config.myndy_api_key
            except ImportError:
                import os
                api_key = os.getenv("MYNDY_API_KEY", "development-key")
        """
        Initialize Memory API client
        
        Args:
            base_url: Base URL of the Myndy-AI FastAPI server
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = 30.0
        
        # Default headers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "CrewAI-Memory-Agent/1.0"
        }
        
    def _get_user_headers(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Get headers with user context for API requests
        
        Args:
            user_context: User context dictionary from pipeline
            
        Returns:
            Headers dictionary with user information
        """
        headers = self.headers.copy()
        
        if user_context:
            headers["X-User-ID"] = user_context.get("id", "anonymous")
            headers["X-User-Name"] = user_context.get("name", "Unknown User")
            if user_context.get("email"):
                headers["X-User-Email"] = user_context["email"]
            headers["X-User-Role"] = user_context.get("role", "user")
            headers["X-User-Authenticated"] = str(user_context.get("is_authenticated", False))
            
        return headers
        
    async def search_memory(self, query: str, model_types: List[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Search memory using the FastAPI endpoint
        
        Args:
            query: Search query
            model_types: Optional list of model types to search
            limit: Maximum number of results
            
        Returns:
            Search results dictionary
        """
        try:
            url = urljoin(self.base_url, "/api/v1/memory/search")
            
            payload = {
                "query": query,
                "limit": limit
            }
            
            if model_types:
                payload["model_types"] = model_types
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Memory search request failed: {e}")
            return {"error": f"Request failed: {e}", "results": []}
        except httpx.HTTPStatusError as e:
            logger.error(f"Memory search HTTP error: {e}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}", "results": []}
        except Exception as e:
            logger.error(f"Memory search unexpected error: {e}")
            return {"error": f"Unexpected error: {e}", "results": []}
    
    async def create_person(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new person entity via FastAPI
        
        Args:
            person_data: Person data dictionary
            
        Returns:
            Creation result dictionary
        """
        try:
            url = urljoin(self.base_url, "/api/v1/memory/entities/person")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=person_data, headers=self.headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Person creation request failed: {e}")
            return {"error": f"Request failed: {e}", "created": False}
        except httpx.HTTPStatusError as e:
            logger.error(f"Person creation HTTP error: {e}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}", "created": False}
        except Exception as e:
            logger.error(f"Person creation unexpected error: {e}")
            return {"error": f"Unexpected error: {e}", "created": False}
    
    async def get_self_profile(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get user's self profile via FastAPI
        
        Args:
            user_context: User context dictionary from pipeline
        
        Returns:
            Profile data dictionary
        """
        try:
            url = urljoin(self.base_url, "/api/v1/profile/self")
            headers = self._get_user_headers(user_context)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Profile get request failed: {e}")
            return {"error": f"Request failed: {e}", "profile": None}
        except httpx.HTTPStatusError as e:
            logger.error(f"Profile get HTTP error: {e}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}", "profile": None}
        except Exception as e:
            logger.error(f"Profile get unexpected error: {e}")
            return {"error": f"Unexpected error: {e}", "profile": None}
    
    async def update_self_profile(self, profile_updates: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update user's self profile via FastAPI
        
        Args:
            profile_updates: Profile update dictionary
            user_context: User context dictionary from pipeline
            
        Returns:
            Update result dictionary
        """
        try:
            url = urljoin(self.base_url, "/api/v1/profile/self")
            headers = self._get_user_headers(user_context)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(url, json=profile_updates, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Profile update request failed: {e}")
            return {"error": f"Request failed: {e}", "updated": False}
        except httpx.HTTPStatusError as e:
            logger.error(f"Profile update HTTP error: {e}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}", "updated": False}
        except Exception as e:
            logger.error(f"Profile update unexpected error: {e}")
            return {"error": f"Unexpected error: {e}", "updated": False}

# Global client instance
_memory_client = MemoryAPIClient()

def _extract_user_context_from_task() -> Optional[Dict[str, Any]]:
    """
    Extract user context from the current CrewAI task execution environment
    
    This function attempts to get user context from the agent's task description
    or other available context sources.
    
    Returns:
        User context dictionary if available, None otherwise
    """
    try:
        import inspect
        
        # Try to get the current frame and look for user context in the call stack
        frame = inspect.currentframe()
        while frame:
            # Look for variables that might contain user context
            frame_locals = frame.f_locals
            
            # Check for user context in common variable names
            for var_name in ['user_info', 'user_context', '__user_context__', 'task_description']:
                if var_name in frame_locals:
                    value = frame_locals[var_name]
                    
                    # If it's a dict with user info, return it
                    if isinstance(value, dict) and 'id' in value:
                        return value
                    
                    # If it's a string containing user context, try to parse it
                    if isinstance(value, str) and 'User Context:' in value:
                        try:
                            # Extract user info from task description
                            lines = value.split('\n')
                            for line in lines:
                                if line.startswith('User Context:'):
                                    # Parse: "User Context: John Doe (ID: user_123, Role: admin)"
                                    import re
                                    match = re.search(r'User Context: (.+?) \(ID: (.+?), Role: (.+?)\)', line)
                                    if match:
                                        name, user_id, role = match.groups()
                                        return {
                                            'id': user_id,
                                            'name': name,
                                            'role': role,
                                            'is_authenticated': True
                                        }
                        except Exception:
                            pass
            
            frame = frame.f_back
        
        return None
    except Exception as e:
        logger.debug(f"Could not extract user context: {e}")
        return None

def get_memory_api_client() -> MemoryAPIClient:
    """Get the global memory API client instance"""
    return _memory_client

# HTTP Tool Implementations

@tool
def search_memory_via_api(query: str, model_types: str = "", limit: int = 10) -> str:
    """
    Search memory using HTTP API call to Myndy-AI backend
    
    Args:
        query: Search query string
        model_types: Comma-separated list of model types to search (optional)
        limit: Maximum number of results to return
        
    Returns:
        JSON string with search results
    """
    import asyncio
    
    # Extract user context from current execution environment
    user_context = _extract_user_context_from_task()
    if user_context:
        logger.info(f"Searching memory for user: {user_context.get('name', 'Unknown')} (ID: {user_context.get('id', 'unknown')})")
    
    # Update client headers with user context
    if user_context:
        _memory_client.headers = _memory_client._get_user_headers(user_context)
    
    # Parse model types
    types_list = [t.strip() for t in model_types.split(",") if t.strip()] if model_types else None
    
    # Run async search
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_memory_client.search_memory(query, types_list, limit))
        return json.dumps(result, indent=2)
    finally:
        loop.close()

@tool
def create_person_via_api(name: str, email: str = "", phone: str = "", organization: str = "") -> str:
    """
    Create a new person entity using HTTP API call to Myndy-AI backend
    
    Args:
        name: Full name of the person
        email: Email address (optional)
        phone: Phone number (optional) 
        organization: Organization/company (optional)
        
    Returns:
        JSON string with creation result
    """
    import asyncio
    import uuid
    
    # Extract user context from current execution environment
    user_context = _extract_user_context_from_task()
    if user_context:
        logger.info(f"Creating person for user: {user_context.get('name', 'Unknown')} (ID: {user_context.get('id', 'unknown')})")
    
    # Update client headers with user context
    if user_context:
        _memory_client.headers = _memory_client._get_user_headers(user_context)
    
    # Construct person data
    person_data = {
        "id": str(uuid.uuid4()),
        "name": {"full": name},
        "contact_methods": [],
        "employments": [],
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    # Add contact methods
    if email:
        person_data["contact_methods"].append({
            "type": "email",
            "value": email,
            "is_primary": True
        })
    
    if phone:
        person_data["contact_methods"].append({
            "type": "phone", 
            "value": phone,
            "is_primary": not email  # Primary if no email
        })
    
    # Add employment
    if organization:
        person_data["employments"].append({
            "name": organization,
            "is_current": True
        })
    
    # Run async creation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_memory_client.create_person(person_data))
        return json.dumps(result, indent=2)
    finally:
        loop.close()

@tool
def get_self_profile_via_api() -> str:
    """
    Get user's self profile using HTTP API call to Myndy-AI backend.
    Automatically extracts user context from the current task execution.
    
    Returns:
        JSON string with profile data
    """
    import asyncio
    
    # Extract user context from current execution
    user_context = _extract_user_context_from_task()
    
    if user_context:
        logger.info(f"Getting profile for user: {user_context.get('name')} (ID: {user_context.get('id')})")
    else:
        logger.warning("No user context found, using anonymous profile")
    
    # Run async profile get
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_memory_client.get_self_profile(user_context))
        return json.dumps(result, indent=2)
    finally:
        loop.close()

@tool
def update_self_profile_via_api(updates_json: str) -> str:
    """
    Update user's self profile using HTTP API call to Myndy-AI backend.
    Automatically extracts user context from the current task execution.
    
    Args:
        updates_json: JSON string with profile updates
        
    Returns:
        JSON string with update result
    """
    import asyncio
    
    try:
        # Parse updates
        updates = json.loads(updates_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {e}", "updated": False})
    
    # Extract user context from current execution
    user_context = _extract_user_context_from_task()
    
    if user_context:
        logger.info(f"Updating profile for user: {user_context.get('name')} (ID: {user_context.get('id')})")
    else:
        logger.warning("No user context found, updating anonymous profile")
    
    # Run async profile update
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_memory_client.update_self_profile(updates, user_context))
        return json.dumps(result, indent=2)
    finally:
        loop.close()

# Class-based tools for compatibility

class SearchMemoryHTTPTool(BaseTool):
    """HTTP tool for searching memory via FastAPI"""
    name: str = "search_memory_http"
    description: str = "Search memory using HTTP API call to Myndy-AI backend"
    
    def _run(self, query: str, model_types: str = "", limit: int = 10) -> str:
        """Execute memory search via HTTP API"""
        return search_memory_via_api(query, model_types, limit)

class CreatePersonHTTPTool(BaseTool):
    """HTTP tool for creating person entities via FastAPI"""
    name: str = "create_person_http"
    description: str = "Create new person entity using HTTP API call to Myndy-AI backend"
    
    def _run(self, name: str, email: str = "", phone: str = "", organization: str = "") -> str:
        """Execute person creation via HTTP API"""
        return create_person_via_api(name, email, phone, organization)

class GetSelfProfileHTTPTool(BaseTool):
    """HTTP tool for getting self profile via FastAPI with user context support"""
    name: str = "get_self_profile_http"
    description: str = "Get user's self profile using HTTP API call to Myndy-AI backend. Automatically extracts user context from the current task execution."
    
    def _run(self) -> str:
        """Execute profile retrieval via HTTP API with user context"""
        return get_self_profile_via_api()

class UpdateSelfProfileHTTPTool(BaseTool):
    """HTTP tool for updating self profile via FastAPI with user context support"""
    name: str = "update_self_profile_http"
    description: str = "Update user's self profile using HTTP API call to Myndy-AI backend. Automatically extracts user context from the current task execution."
    
    def _run(self, updates_json: str) -> str:
        """Execute profile update via HTTP API with user context"""
        return update_self_profile_via_api(updates_json)

def get_memory_http_tools() -> List[BaseTool]:
    """
    Get all memory HTTP tools for agent use
    
    Returns:
        List of memory HTTP tools
    """
    return [
        SearchMemoryHTTPTool(),
        CreatePersonHTTPTool(),
        GetSelfProfileHTTPTool(),
        UpdateSelfProfileHTTPTool()
    ]

def test_memory_http_tools():
    """Test memory HTTP tools functionality"""
    
    print("🧪 Testing Memory HTTP Tools")
    print("=" * 40)
    
    tools = get_memory_http_tools()
    print(f"✅ Created {len(tools)} memory HTTP tools")
    
    for tool in tools:
        print(f"📋 Tool: {tool.name} - {tool.description}")
    
    # Test client creation
    client = get_memory_api_client()
    print(f"🌐 API Client: {client.base_url}")
    
    print("✅ Memory HTTP tools ready for use")
    print("🔗 All tools use HTTP API calls to myndy-ai backend")
    
    return tools

if __name__ == "__main__":
    test_memory_http_tools()