"""
FastAPI HTTP Client Tools for CrewAI Agents

Provides HTTP client tools to consume myndy-ai FastAPI endpoints, enabling agents
to access memory, profile, and conversation services through the service-oriented architecture.

File: tools/myndy_fastapi_client.py
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FastAPIConfig:
    """Configuration for FastAPI client"""
    def __init__(
        self, 
        base_url: str = "http://localhost:8000",
        api_version: str = "api/v1",
        api_key: str = "dev-api-key-12345",
        timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip('/')
        self.api_version = api_version
        self.api_key = api_key
        self.timeout = timeout
        self.full_base_url = f"{self.base_url}/{self.api_version}"


class FastAPIClient:
    """HTTP client for myndy-ai FastAPI services"""
    
    def __init__(self, config: FastAPIConfig = None):
        self.config = config or FastAPIConfig()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to FastAPI service"""
        url = f"{self.config.full_base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=self.headers, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.ConnectError:
            logger.error(f"Failed to connect to FastAPI service at {url}")
            raise Exception(f"Unable to connect to myndy-ai service. Is the FastAPI server running at {self.config.base_url}?")
        except httpx.TimeoutException:
            logger.error(f"Request timeout for {url}")
            raise Exception(f"Request timeout after {self.config.timeout}s")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error calling FastAPI: {e}")
            raise Exception(f"FastAPI request failed: {str(e)}")


# Memory Tools

def search_memory(
    query: str,
    limit: int = 10,
    include_people: bool = True,
    include_places: bool = True,
    include_events: bool = True,
    include_content: bool = True,
    config: Optional[FastAPIConfig] = None
) -> str:
    """
    Search through memory using semantic search
    
    Args:
        query: Text to search for in memory
        limit: Maximum number of results (1-100)
        include_people: Include people in search results
        include_places: Include places in search results  
        include_events: Include events in search results
        include_content: Include content memories in search results
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with search results
    """
    async def _search():
        client = FastAPIClient(config)
        
        request_data = {
            "query": query,
            "limit": min(max(limit, 1), 100),
            "include_people": include_people,
            "include_places": include_places,
            "include_events": include_events,
            "include_content": include_content
        }
        
        return await client._make_request("POST", "/memory/search", data=request_data)
    
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_search())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Memory search failed"
        }
        return json.dumps(error_result, indent=2)


def create_person(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    organization: Optional[str] = None,
    job_title: Optional[str] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None,
    social_profiles: Optional[Dict[str, str]] = None,
    config: Optional[FastAPIConfig] = None
) -> str:
    """
    Create a new person in memory
    
    Args:
        name: Person's full name (required)
        email: Person's email address
        phone: Person's phone number
        organization: Person's organization
        job_title: Person's job title
        notes: Additional notes about the person
        tags: List of tags for categorization
        social_profiles: Dictionary of social media profiles
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with created person data
    """
    async def _create():
        client = FastAPIClient(config)
        
        request_data = {
            "name": name
        }
        
        if email:
            request_data["email"] = email
        if phone:
            request_data["phone"] = phone
        if organization:
            request_data["organization"] = organization
        if job_title:
            request_data["job_title"] = job_title
        if notes:
            request_data["notes"] = notes
        if tags:
            request_data["tags"] = tags
        if social_profiles:
            request_data["social_profiles"] = social_profiles
        
        return await client._make_request("POST", "/memory/people", data=request_data)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_create())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Person creation failed"
        }
        return json.dumps(error_result, indent=2)


def add_memory_fact(
    content: str,
    source: Optional[str] = None,
    confidence: Optional[float] = None,
    tags: Optional[List[str]] = None,
    related_entities: Optional[List[str]] = None,
    config: Optional[FastAPIConfig] = None
) -> str:
    """
    Add a fact to memory
    
    Args:
        content: The fact content (required)
        source: Source of the information
        confidence: Confidence score 0-1
        tags: List of tags for categorization
        related_entities: List of related entity IDs
        config: Optional FastAPI configuration
        
    Returns:
        JSON string confirming fact was added
    """
    async def _add_fact():
        client = FastAPIClient(config)
        
        request_data = {
            "content": content
        }
        
        if source:
            request_data["source"] = source
        if confidence is not None:
            request_data["confidence"] = confidence
        if tags:
            request_data["tags"] = tags
        if related_entities:
            request_data["related_entities"] = related_entities
        
        return await client._make_request("POST", "/memory/facts", data=request_data)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_add_fact())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Fact addition failed"
        }
        return json.dumps(error_result, indent=2)


def get_memory_person(person_id: str, config: Optional[FastAPIConfig] = None) -> str:
    """
    Get a specific person by ID
    
    Args:
        person_id: The unique identifier for the person
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with person data
    """
    async def _get_person():
        client = FastAPIClient(config)
        return await client._make_request("GET", f"/memory/people/{person_id}")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_get_person())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Person retrieval failed"
        }
        return json.dumps(error_result, indent=2)


def list_memory_people(
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = None,
    config: Optional[FastAPIConfig] = None
) -> str:
    """
    List people with optional search and pagination
    
    Args:
        limit: Maximum number of results (1-100)
        offset: Number of results to skip for pagination
        search: Optional search term to filter people
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with list of people
    """
    async def _list_people():
        client = FastAPIClient(config)
        
        params = {
            "limit": min(max(limit, 1), 100),
            "offset": max(offset, 0)
        }
        
        if search:
            params["search"] = search
        
        return await client._make_request("GET", "/memory/people", params=params)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_list_people())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "People listing failed"
        }
        return json.dumps(error_result, indent=2)


# Profile Tools

def get_user_profile(config: Optional[FastAPIConfig] = None) -> str:
    """
    Get the user's profile information
    
    Args:
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with user profile data
    """
    async def _get_profile():
        client = FastAPIClient(config)
        return await client._make_request("GET", "/profile/self")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_get_profile())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Profile retrieval failed"
        }
        return json.dumps(error_result, indent=2)


def update_user_profile(
    name: Optional[str] = None,
    email: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None,
    goals: Optional[List[str]] = None,
    interests: Optional[List[str]] = None,
    personal_info: Optional[Dict[str, Any]] = None,
    privacy_settings: Optional[Dict[str, Any]] = None,
    config: Optional[FastAPIConfig] = None
) -> str:
    """
    Update the user's profile information
    
    Args:
        name: User's full name
        email: User's email address
        preferences: User preferences dictionary
        goals: List of user's goals
        interests: List of user's interests
        personal_info: Additional personal information
        privacy_settings: Privacy preferences
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with updated profile data
    """
    async def _update_profile():
        client = FastAPIClient(config)
        
        request_data = {}
        
        if name:
            request_data["name"] = name
        if email:
            request_data["email"] = email
        if preferences:
            request_data["preferences"] = preferences
        if goals:
            request_data["goals"] = goals
        if interests:
            request_data["interests"] = interests
        if personal_info:
            request_data["personal_info"] = personal_info
        if privacy_settings:
            request_data["privacy_settings"] = privacy_settings
        
        return await client._make_request("POST", "/profile/self/update", data=request_data)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_update_profile())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Profile update failed"
        }
        return json.dumps(error_result, indent=2)


# Status Tools

def get_current_status(config: Optional[FastAPIConfig] = None) -> str:
    """
    Get the current user status
    
    Args:
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with current status information
    """
    async def _get_status():
        client = FastAPIClient(config)
        return await client._make_request("GET", "/status/current")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_get_status())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Status retrieval failed"
        }
        return json.dumps(error_result, indent=2)


def update_user_status(
    mood: Optional[str] = None,
    energy_level: Optional[str] = None,
    location: Optional[str] = None,
    activity: Optional[str] = None,
    availability: Optional[str] = None,
    notes: Optional[str] = None,
    config: Optional[FastAPIConfig] = None
) -> str:
    """
    Update the user status
    
    Args:
        mood: Current mood
        energy_level: Current energy level
        location: Current location
        activity: Current activity
        availability: Current availability
        notes: Additional status notes
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with updated status information
    """
    async def _update_status():
        client = FastAPIClient(config)
        
        request_data = {}
        
        if mood:
            request_data["mood"] = mood
        if energy_level:
            request_data["energy_level"] = energy_level
        if location:
            request_data["location"] = location
        if activity:
            request_data["activity"] = activity
        if availability:
            request_data["availability"] = availability
        if notes:
            request_data["notes"] = notes
        
        return await client._make_request("POST", "/status/update", data=request_data)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_update_status())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Status update failed"
        }
        return json.dumps(error_result, indent=2)


# Training and Help Tools

def get_memory_tools_help(config: Optional[FastAPIConfig] = None) -> str:
    """
    Get help information for memory tools to train agents
    
    Args:
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with comprehensive tool usage guidance
    """
    async def _get_help():
        client = FastAPIClient(config)
        return await client._make_request("GET", "/memory/tools/help")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_get_help())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Help retrieval failed"
        }
        return json.dumps(error_result, indent=2)


def get_memory_tools_examples(config: Optional[FastAPIConfig] = None) -> str:
    """
    Get example requests and responses for memory tools
    
    Args:
        config: Optional FastAPI configuration
        
    Returns:
        JSON string with detailed examples for agent training
    """
    async def _get_examples():
        client = FastAPIClient(config)
        return await client._make_request("GET", "/memory/tools/examples")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_get_examples())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Examples retrieval failed"
        }
        return json.dumps(error_result, indent=2)


# Export all tools for easy importing
__all__ = [
    "FastAPIConfig",
    "FastAPIClient", 
    "search_memory",
    "create_person",
    "add_memory_fact", 
    "get_memory_person",
    "list_memory_people",
    "get_user_profile",
    "update_user_profile",
    "get_current_status",
    "update_user_status",
    "get_memory_tools_help",
    "get_memory_tools_examples"
]