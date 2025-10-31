"""
Shadow Agent HTTP Tools

HTTP client tools specifically designed for the Shadow Agent to interact
with the myndy-ai FastAPI backend for memory and status operations.

File: tools/shadow_agent_tools.py
"""

import json
import logging
import httpx
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger("tools.shadow_agent_tools")

# Base HTTP client configuration
MYNDY_API_BASE = "http://localhost:8000"
TIMEOUT = 30.0

class ShadowAgentHTTPTool(BaseTool):
    """Base class for Shadow Agent HTTP tools"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = httpx.Client(timeout=TIMEOUT)
        self.base_url = MYNDY_API_BASE
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CrewAI-Shadow-Agent/1.0"
        }
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to myndy-ai API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"HTTP request failed: {e}")
            return {"error": f"Request failed: {str(e)}"}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": f"Unexpected error: {str(e)}"}


class SearchMemoryInput(BaseModel):
    query: str = Field(description="Search query for memory")
    limit: Optional[int] = Field(default=10, description="Maximum number of results")
    search_type: Optional[str] = Field(default="semantic", description="Type of search (semantic, keyword)")

class SearchMemoryTool(ShadowAgentHTTPTool):
    name: str = "search_memory"
    description: str = "Search through user's memory and stored information"
    args_schema = SearchMemoryInput
    
    def _run(self, query: str, limit: int = 10, search_type: str = "semantic") -> str:
        """Search memory via HTTP API"""
        data = {
            "query": query,
            "limit": limit,
            "search_type": search_type
        }
        result = self.make_request("POST", "/api/v1/memory/search", data)
        return json.dumps(result, indent=2)


class GetCurrentStatusInput(BaseModel):
    user_id: Optional[str] = Field(default="primary_user", description="User ID to get status for")
    include_history: Optional[bool] = Field(default=False, description="Include recent status history")

class GetCurrentStatusTool(ShadowAgentHTTPTool):
    name: str = "get_current_status"
    description: str = "Get the user's current status including mood, location, and activities"
    args_schema = GetCurrentStatusInput
    
    def _run(self, user_id: str = "primary_user", include_history: bool = False) -> str:
        """Get current status via HTTP API"""
        params = {"user_id": user_id, "include_history": include_history}
        result = self.make_request("GET", f"/api/v1/status/current?{self._build_query_string(params)}")
        return json.dumps(result, indent=2)
    
    def _build_query_string(self, params: Dict[str, Any]) -> str:
        """Build query string from parameters"""
        return "&".join(f"{k}={v}" for k, v in params.items() if v is not None)


class GetSelfProfileInput(BaseModel):
    user_id: Optional[str] = Field(default="primary_user", description="User ID to get profile for")
    include_preferences: Optional[bool] = Field(default=True, description="Include user preferences")
    include_goals: Optional[bool] = Field(default=True, description="Include user goals")

class GetSelfProfileTool(ShadowAgentHTTPTool):
    name: str = "get_self_profile"
    description: str = "Get the user's self profile including preferences, goals, and identity"
    args_schema = GetSelfProfileInput
    
    def _run(self, user_id: str = "primary_user", include_preferences: bool = True, include_goals: bool = True) -> str:
        """Get self profile via HTTP API"""
        params = {
            "user_id": user_id,
            "include_preferences": include_preferences,
            "include_goals": include_goals
        }
        result = self.make_request("GET", f"/api/v1/profile/self?{self._build_query_string(params)}")
        return json.dumps(result, indent=2)
    
    def _build_query_string(self, params: Dict[str, Any]) -> str:
        """Build query string from parameters"""
        return "&".join(f"{k}={v}" for k, v in params.items() if v is not None)


class GetStatusHistoryInput(BaseModel):
    user_id: Optional[str] = Field(default="primary_user", description="User ID to get status history for")
    days: Optional[int] = Field(default=7, description="Number of days of history to retrieve")
    limit: Optional[int] = Field(default=50, description="Maximum number of status entries")

class GetStatusHistoryTool(ShadowAgentHTTPTool):
    name: str = "get_status_history"
    description: str = "Get the user's status history over time"
    args_schema = GetStatusHistoryInput
    
    def _run(self, user_id: str = "primary_user", days: int = 7, limit: int = 50) -> str:
        """Get status history via HTTP API"""
        params = {"user_id": user_id, "days": days, "limit": limit}
        result = self.make_request("GET", f"/api/v1/status/history?{self._build_query_string(params)}")
        return json.dumps(result, indent=2)
    
    def _build_query_string(self, params: Dict[str, Any]) -> str:
        """Build query string from parameters"""
        return "&".join(f"{k}={v}" for k, v in params.items() if v is not None)


class ReflectOnMemoryInput(BaseModel):
    topic: str = Field(description="Topic or theme to reflect on")
    time_period: Optional[str] = Field(default="recent", description="Time period for reflection (recent, week, month, year)")
    generate_insights: Optional[bool] = Field(default=True, description="Whether to generate insights from reflection")

class ReflectOnMemoryTool(ShadowAgentHTTPTool):
    name: str = "reflect_on_memory"
    description: str = "Reflect on memories and generate insights about patterns and growth"
    args_schema = ReflectOnMemoryInput
    
    def _run(self, topic: str, time_period: str = "recent", generate_insights: bool = True) -> str:
        """Reflect on memory via HTTP API"""
        data = {
            "topic": topic,
            "time_period": time_period,
            "generate_insights": generate_insights
        }
        result = self.make_request("POST", "/api/v1/memory/reflect", data)
        return json.dumps(result, indent=2)


class AddFactInput(BaseModel):
    fact: str = Field(description="Fact to add to memory")
    category: Optional[str] = Field(default="general", description="Category for the fact")
    confidence: Optional[float] = Field(default=1.0, description="Confidence level (0.0-1.0)")
    source: Optional[str] = Field(default="shadow_agent", description="Source of the fact")

class AddFactTool(ShadowAgentHTTPTool):
    name: str = "add_fact"
    description: str = "Add a fact or piece of information to the user's knowledge base"
    args_schema = AddFactInput
    
    def _run(self, fact: str, category: str = "general", confidence: float = 1.0, source: str = "shadow_agent") -> str:
        """Add fact via HTTP API"""
        data = {
            "fact": fact,
            "category": category,
            "confidence": confidence,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }
        result = self.make_request("POST", "/api/v1/memory/facts", data)
        return json.dumps(result, indent=2)


class AddPreferenceInput(BaseModel):
    preference: str = Field(description="Preference to add")
    category: str = Field(description="Category of preference (tech, lifestyle, work, etc.)")
    strength: Optional[float] = Field(default=1.0, description="Preference strength (0.0-1.0)")
    reasoning: Optional[str] = Field(default="", description="Reasoning behind the preference")

class AddPreferenceTool(ShadowAgentHTTPTool):
    name: str = "add_preference"
    description: str = "Add a user preference to their profile"
    args_schema = AddPreferenceInput
    
    def _run(self, preference: str, category: str, strength: float = 1.0, reasoning: str = "") -> str:
        """Add preference via HTTP API"""
        data = {
            "preference": preference,
            "category": category,
            "strength": strength,
            "reasoning": reasoning,
            "observed_at": datetime.utcnow().isoformat()
        }
        result = self.make_request("POST", "/api/v1/profile/preferences", data)
        return json.dumps(result, indent=2)


class UpdateStatusInput(BaseModel):
    mood: Optional[str] = Field(default=None, description="Current mood")
    activity: Optional[str] = Field(default=None, description="Current activity")
    location: Optional[str] = Field(default=None, description="Current location")
    energy_level: Optional[int] = Field(default=None, description="Energy level (1-10)")
    notes: Optional[str] = Field(default="", description="Additional notes")

class UpdateStatusTool(ShadowAgentHTTPTool):
    name: str = "update_status"
    description: str = "Update the user's current status based on observations"
    args_schema = UpdateStatusInput
    
    def _run(self, mood: Optional[str] = None, activity: Optional[str] = None, 
             location: Optional[str] = None, energy_level: Optional[int] = None, 
             notes: str = "") -> str:
        """Update status via HTTP API"""
        data = {
            "mood": mood,
            "activity": activity,
            "location": location,
            "energy_level": energy_level,
            "notes": notes,
            "updated_by": "shadow_agent",
            "timestamp": datetime.utcnow().isoformat()
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        result = self.make_request("PUT", "/api/v1/status/current", data)
        return json.dumps(result, indent=2)


class CreateEntityInput(BaseModel):
    entity_type: str = Field(description="Type of entity (person, place, project, etc.)")
    name: str = Field(description="Name of the entity")
    description: Optional[str] = Field(default="", description="Description of the entity")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class CreateEntityTool(ShadowAgentHTTPTool):
    name: str = "create_entity"
    description: str = "Create a new entity in the user's memory system"
    args_schema = CreateEntityInput
    
    def _run(self, entity_type: str, name: str, description: str = "", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create entity via HTTP API"""
        data = {
            "entity_type": entity_type,
            "name": name,
            "description": description,
            "metadata": metadata or {},
            "created_by": "shadow_agent",
            "created_at": datetime.utcnow().isoformat()
        }
        result = self.make_request("POST", f"/api/v1/entities/{entity_type}", data)
        return json.dumps(result, indent=2)


# Factory function to get all shadow agent tools
def get_shadow_agent_tools() -> List[ShadowAgentHTTPTool]:
    """Get all HTTP tools for the Shadow Agent"""
    return [
        SearchMemoryTool(),
        GetCurrentStatusTool(),
        GetSelfProfileTool(),
        GetStatusHistoryTool(),
        ReflectOnMemoryTool(),
        AddFactTool(),
        AddPreferenceTool(),
        UpdateStatusTool(),
        CreateEntityTool()
    ]


# Registry for easy access
SHADOW_AGENT_TOOLS = {
    "search_memory": SearchMemoryTool,
    "get_current_status": GetCurrentStatusTool,
    "get_self_profile": GetSelfProfileTool,
    "get_status_history": GetStatusHistoryTool,
    "reflect_on_memory": ReflectOnMemoryTool,
    "add_fact": AddFactTool,
    "add_preference": AddPreferenceTool,
    "update_status": UpdateStatusTool,
    "create_entity": CreateEntityTool
}