"""
Myndy-AI HTTP Client for CrewAI Integration

This module provides HTTP client tools that communicate with the Myndy-AI FastAPI backend,
following the mandatory service-oriented architecture where CrewAI (frontend) communicates
with myndy-ai (backend) only via HTTP REST APIs.

File: tools/myndy_http_client.py
"""

import json
import logging
import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

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

logger = logging.getLogger("crewai.myndy_http_client")


class MyndyAPIClient:
    """HTTP client for Myndy-AI FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "development-key"):
        """
        Initialize Myndy API client
        
        Args:
            base_url: Base URL of the Myndy-AI FastAPI server
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = 30.0
        
        # Default headers for all requests
        self.headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "CrewAI-MyndyBridge/1.0"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to Myndy-AI API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/api/v1/memory/search")
            data: Request body data for POST/PUT requests
            params: Query parameters for GET requests
            
        Returns:
            Response data as dictionary
            
        Raises:
            Exception: If request fails or API returns error
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = client.get(url, headers=self.headers, params=params)
                elif method.upper() == "POST":
                    response = client.post(url, headers=self.headers, json=data)
                elif method.upper() == "PUT":
                    response = client.put(url, headers=self.headers, json=data)
                elif method.upper() == "DELETE":
                    response = client.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check if request was successful
                response.raise_for_status()
                
                # Parse JSON response
                response_data = response.json()
                
                # Check if API returned success
                if not response_data.get("success", False):
                    error_msg = response_data.get("message", "Unknown API error")
                    raise Exception(f"API Error: {error_msg}")
                
                return response_data
                
        except httpx.ConnectError:
            raise Exception(f"Failed to connect to Myndy-AI API at {self.base_url}. Is the FastAPI server running?")
        except httpx.TimeoutException:
            raise Exception(f"Request to Myndy-AI API timed out after {self.timeout}s")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Authentication failed. Check API key.")
            elif e.response.status_code == 503:
                raise Exception("Myndy-AI service temporarily unavailable")
            else:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("message", f"HTTP {e.response.status_code}")
                except:
                    error_msg = f"HTTP {e.response.status_code}"
                raise Exception(f"API request failed: {error_msg}")
        except Exception as e:
            logger.error(f"Request failed - method: {method}, endpoint: {endpoint}, error: {e}")
            raise


# Global API client instance
_api_client = None

def get_api_client() -> MyndyAPIClient:
    """Get or create the global API client instance"""
    global _api_client
    if _api_client is None:
        # TODO: Get these from environment variables
        base_url = "http://localhost:8000"
        api_key = "development-key-crewai-integration"
        _api_client = MyndyAPIClient(base_url=base_url, api_key=api_key)
    return _api_client


class GetSelfProfileHTTPTool(BaseTool):
    """HTTP client tool for getting user profile via Myndy-AI API"""
    name: str = "get_self_profile"
    description: str = "Get the user's profile information via HTTP API"
    
    def _run(self, **kwargs) -> str:
        """Get self profile via HTTP API"""
        try:
            logger.info("Getting self profile via HTTP API")
            client = get_api_client()
            
            # Call FastAPI endpoint
            response = client._make_request("GET", "/api/v1/profile/self")
            
            # Extract profile data from response
            profile_data = response.get("profile", {})
            
            result = {
                "success": True,
                "profile": profile_data,
                "message": response.get("message", "Profile retrieved successfully"),
                "retrieved_at": datetime.now().isoformat(),
                "note": "Profile retrieved via Myndy-AI FastAPI backend"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"HTTP get_self_profile failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "retrieved_at": datetime.now().isoformat(),
                "note": "Failed to retrieve profile via HTTP API"
            }, indent=2)


class UpdateSelfProfileHTTPTool(BaseTool):
    """HTTP client tool for updating user profile via Myndy-AI API"""
    name: str = "update_self_profile"
    description: str = "Update the user's profile information via HTTP API"
    
    def _run(self, name="", age="", email="", location="", occupation="", interests="", bio="", **kwargs) -> str:
        """Update self profile via HTTP API"""
        try:
            logger.info("Updating self profile via HTTP API")
            client = get_api_client()
            
            # Build update request data
            profile_data = {}
            if name:
                profile_data["name"] = name
            if age:
                try:
                    profile_data["age"] = int(age) if isinstance(age, str) else age
                except (ValueError, TypeError):
                    pass
            if email:
                profile_data["email"] = email
            if location:
                profile_data["location"] = location
            if occupation:
                profile_data["occupation"] = occupation
            if interests:
                if isinstance(interests, str):
                    profile_data["interests"] = [i.strip() for i in interests.split(",")]
                else:
                    profile_data["interests"] = interests
            if bio:
                profile_data["personal_info"] = {"biography": bio}
            
            # Add any additional kwargs to personal_info
            personal_info = profile_data.get("personal_info", {})
            for key, value in kwargs.items():
                if value and key not in ["name", "age", "email", "location", "occupation", "interests", "bio"]:
                    personal_info[key] = value
            if personal_info:
                profile_data["personal_info"] = personal_info
            
            # Call FastAPI endpoint
            response = client._make_request("POST", "/api/v1/profile/self/update", data=profile_data)
            
            # Extract updated profile data
            updated_profile = response.get("profile", {})
            
            result = {
                "success": True,
                "message": response.get("message", "Profile updated successfully"),
                "profile_id": updated_profile.get("id"),
                "profile_name": updated_profile.get("name"),
                "updated_fields": list(profile_data.keys()),
                "updated_at": datetime.now().isoformat(),
                "note": "Profile updated via Myndy-AI FastAPI backend"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"HTTP update_self_profile failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "updated_at": datetime.now().isoformat(),
                "note": "Failed to update profile via HTTP API"
            }, indent=2)


class SearchMemoryHTTPTool(BaseTool):
    """HTTP client tool for searching memory via Myndy-AI API"""
    name: str = "search_memory"
    description: str = "Search the memory system for people, organizations, and facts via HTTP API"
    
    def _run(self, query="", limit=10, include_people=True, include_places=True, include_events=True, include_content=True, **kwargs) -> str:
        """Search memory via HTTP API"""
        try:
            logger.info(f"Searching memory via HTTP API: {query}")
            client = get_api_client()
            
            # Build search request data
            search_data = {
                "query": query,
                "limit": int(limit),
                "include_people": bool(include_people),
                "include_places": bool(include_places),
                "include_events": bool(include_events),
                "include_content": bool(include_content),
                "offset": kwargs.get("offset", 0)
            }
            
            # Call FastAPI endpoint
            response = client._make_request("POST", "/api/v1/memory/search", data=search_data)
            
            # Extract search results
            results = response.get("results", [])
            
            result = {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results,
                "total_count": response.get("total_count", len(results)),
                "search_time_ms": response.get("search_time_ms", 0),
                "searched_at": datetime.now().isoformat(),
                "note": "Search performed via Myndy-AI FastAPI backend"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"HTTP search_memory failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "query": query,
                "results_count": 0,
                "results": [],
                "searched_at": datetime.now().isoformat(),
                "note": "Failed to search memory via HTTP API"
            }, indent=2)


class CreateEntityHTTPTool(BaseTool):
    """HTTP client tool for creating entities via Myndy-AI API"""
    name: str = "create_entity"
    description: str = "Create a new person or organization entity via HTTP API"
    
    def _run(self, name="", entity_type="person", description="", organization="", job_title="", email="", phone="", **kwargs) -> str:
        """Create entity via HTTP API"""
        try:
            logger.info(f"Creating {entity_type} entity via HTTP API: {name}")
            client = get_api_client()
            
            if entity_type.lower() == "person":
                # Build person creation request
                person_data = {
                    "name": name,
                    "email": email or None,
                    "phone": phone or None,
                    "organization": organization or None,
                    "job_title": job_title or None,
                    "notes": description or None,
                    "tags": kwargs.get("tags", []),
                    "social_profiles": kwargs.get("social_profiles", {})
                }
                
                # Call FastAPI endpoint for person creation
                response = client._make_request("POST", "/api/v1/memory/people", data=person_data)
                
                # Extract person data
                person = response.get("person", {})
                
                result = {
                    "success": True,
                    "entity_type": "person",
                    "entity_id": person.get("id"),
                    "name": person.get("name", name),
                    "message": response.get("message", "Person created successfully"),
                    "created_at": datetime.now().isoformat(),
                    "note": "Person created via Myndy-AI FastAPI backend"
                }
                
            else:
                # For now, only person entities are supported via API
                # Other entity types would need additional endpoints
                result = {
                    "success": False,
                    "error": f"Entity type '{entity_type}' not yet supported via HTTP API",
                    "supported_types": ["person"],
                    "name": name,
                    "entity_type": entity_type
                }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"HTTP create_entity failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "name": name,
                "entity_type": entity_type,
                "created_at": datetime.now().isoformat(),
                "note": "Failed to create entity via HTTP API"
            }, indent=2)


class GetCurrentStatusHTTPTool(BaseTool):
    """HTTP client tool for getting current status via Myndy-AI API"""
    name: str = "get_current_status"
    description: str = "Get the current user status via HTTP API"
    
    def _run(self, **kwargs) -> str:
        """Get current status via HTTP API"""
        try:
            logger.info("Getting current status via HTTP API")
            client = get_api_client()
            
            # Call FastAPI endpoint
            response = client._make_request("GET", "/api/v1/status/current")
            
            # Extract status data
            status_data = response.get("status", {})
            
            result = {
                "success": True,
                "status": status_data,
                "message": response.get("message", "Status retrieved successfully"),
                "retrieved_at": datetime.now().isoformat(),
                "note": "Status retrieved via Myndy-AI FastAPI backend"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"HTTP get_current_status failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "retrieved_at": datetime.now().isoformat(),
                "note": "Failed to retrieve status via HTTP API"
            }, indent=2)


class UpdateStatusHTTPTool(BaseTool):
    """HTTP client tool for updating status via Myndy-AI API"""
    name: str = "update_status"
    description: str = "Update the user status via HTTP API"
    
    def _run(self, mood="", energy_level="", location="", activity="", availability="", notes="", **kwargs) -> str:
        """Update status via HTTP API"""
        try:
            logger.info("Updating status via HTTP API")
            client = get_api_client()
            
            # Build status update request data
            status_data = {}
            if mood:
                status_data["mood"] = mood
            if energy_level:
                status_data["energy_level"] = energy_level
            if location:
                status_data["location"] = location
            if activity:
                status_data["activity"] = activity
            if availability:
                status_data["availability"] = availability
            if notes:
                status_data["notes"] = notes
            
            # Add optional fields
            if "visible_to" in kwargs:
                status_data["visible_to"] = kwargs["visible_to"]
            if "expires_at" in kwargs:
                status_data["expires_at"] = kwargs["expires_at"]
            
            # Call FastAPI endpoint
            response = client._make_request("POST", "/api/v1/status/update", data=status_data)
            
            # Extract updated status data
            updated_status = response.get("status", {})
            
            result = {
                "success": True,
                "message": response.get("message", "Status updated successfully"),
                "status_id": updated_status.get("id"),
                "updated_fields": list(status_data.keys()),
                "current_mood": updated_status.get("mood"),
                "current_activity": updated_status.get("activity"),
                "updated_at": datetime.now().isoformat(),
                "note": "Status updated via Myndy-AI FastAPI backend"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"HTTP update_status failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "updated_at": datetime.now().isoformat(),
                "note": "Failed to update status via HTTP API"
            }, indent=2)


class AddFactHTTPTool(BaseTool):
    """HTTP client tool for adding facts via Myndy-AI API"""
    name: str = "add_fact"
    description: str = "Add a fact to memory storage via HTTP API"
    
    def _run(self, content="", source="conversation", confidence=1.0, tags=None, related_entities=None, **kwargs) -> str:
        """Add fact via HTTP API"""
        try:
            logger.info(f"Adding fact via HTTP API: {content[:50]}...")
            client = get_api_client()
            
            # Build fact request data
            fact_data = {
                "content": content,
                "source": source,
                "confidence": float(confidence),
                "tags": tags or [],
                "related_entities": related_entities or [],
                "metadata": kwargs.get("metadata", {})
            }
            
            # Call FastAPI endpoint
            response = client._make_request("POST", "/api/v1/memory/facts", data=fact_data)
            
            # Extract result data
            fact_id = response.get("data", {}).get("fact_id")
            
            result = {
                "success": True,
                "message": response.get("message", "Fact added successfully"),
                "fact_id": fact_id,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "source": source,
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "note": "Fact stored via Myndy-AI FastAPI backend"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"HTTP add_fact failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "content": content[:100] + "..." if len(content) > 100 else content,
                "created_at": datetime.now().isoformat(),
                "note": "Failed to add fact via HTTP API"
            }, indent=2)


# Tool registry for HTTP client tools
HTTP_CLIENT_TOOLS = {
    "get_self_profile": GetSelfProfileHTTPTool,
    "update_self_profile": UpdateSelfProfileHTTPTool,
    "search_memory": SearchMemoryHTTPTool,
    "create_entity": CreateEntityHTTPTool,
    "get_current_status": GetCurrentStatusHTTPTool,
    "update_status": UpdateStatusHTTPTool,
    "add_fact": AddFactHTTPTool
}


def create_http_client_tool(tool_name: str) -> Optional[BaseTool]:
    """
    Create HTTP client tool instance
    
    Args:
        tool_name: Name of the tool to create
        
    Returns:
        BaseTool instance or None if not found
    """
    tool_class = HTTP_CLIENT_TOOLS.get(tool_name)
    if tool_class:
        return tool_class()
    return None


def get_all_http_client_tools() -> List[BaseTool]:
    """Get all available HTTP client tools"""
    return [tool_class() for tool_class in HTTP_CLIENT_TOOLS.values()]


def get_http_client_tools_for_agent(agent_role: str) -> List[BaseTool]:
    """
    Get HTTP client tools appropriate for specific agent role
    
    Args:
        agent_role: The role of the agent
        
    Returns:
        List of appropriate HTTP client tools
    """
    role_tool_mappings = {
        "memory_librarian": [
            "search_memory", "create_entity", "add_fact", 
            "get_current_status", "update_status", "get_self_profile"
        ],
        "personal_assistant": [
            "get_current_status", "update_status", "get_self_profile", 
            "update_self_profile", "search_memory"
        ],
        "research_specialist": [
            "search_memory", "add_fact", "create_entity"
        ],
        "health_analyst": [
            "get_current_status", "update_status", "add_fact"
        ],
        "finance_tracker": [
            "add_fact", "search_memory", "get_current_status"
        ],
        "shadow_agent": [
            "search_memory", "add_fact", "create_entity", "get_current_status", 
            "update_status", "get_self_profile", "update_self_profile"
        ]
    }
    
    tool_names = role_tool_mappings.get(agent_role, [])
    tools = []
    
    for tool_name in tool_names:
        tool = create_http_client_tool(tool_name)
        if tool:
            tools.append(tool)
    
    logger.info(f"Created {len(tools)} HTTP client tools for agent role: {agent_role}")
    return tools


if __name__ == "__main__":
    # Test the HTTP client tools
    print("Testing Myndy-AI HTTP Client Tools")
    print("=" * 40)
    
    # Test API client connection
    try:
        client = get_api_client()
        print(f"API Client configured for: {client.base_url}")
    except Exception as e:
        print(f"Failed to create API client: {e}")
    
    # List available tools
    tools = get_all_http_client_tools()
    print(f"\nAvailable HTTP client tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test a simple tool (if API is available)
    try:
        test_tool = create_http_client_tool("get_current_status")
        if test_tool:
            print(f"\nTesting {test_tool.name}...")
            result = test_tool._run()
            print("Test result:", result[:200] + "..." if len(result) > 200 else result)
    except Exception as e:
        print(f"Test failed (API may not be running): {e}")