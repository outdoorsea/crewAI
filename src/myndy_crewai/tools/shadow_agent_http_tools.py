"""
Shadow Agent HTTP Tools - Comprehensive myndy-ai FastAPI Client Tools

Provides HTTP client tools for the Enhanced Shadow Agent to access all myndy-ai
FastAPI endpoints for searching, adding, updating, and deleting data.

File: tools/shadow_agent_http_tools.py
"""

import json
import logging
import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from langchain.tools import BaseTool

logger = logging.getLogger(__name__)


class ShadowAgentHTTPConfig:
    """Configuration for Shadow Agent HTTP tools"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "development-shadow-agent-key"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "User-Agent": "Enhanced-Shadow-Agent/2.0"
        }
        self.timeout = 30.0


# Global config instance
_http_config = ShadowAgentHTTPConfig()


def get_http_client() -> httpx.Client:
    """Get configured HTTP client"""
    return httpx.Client(
        timeout=_http_config.timeout,
        headers=_http_config.headers
    )


# ============================================================================
# Memory Search and Query Tools
# ============================================================================

class MemorySearchTool(BaseTool):
    """Search through memory using semantic search"""
    
    name: str = "search_memory"
    description: str = "Search for information in memory using semantic search. Supports searching people, places, events, tasks, and general content."
    
    def _run(self, query: str, limit: int = 10, include_people: bool = True, 
             include_places: bool = True, include_groups: bool = True, **kwargs) -> str:
        """Search memory with semantic search"""
        try:
            with get_http_client() as client:
                search_data = {
                    "query": query,
                    "limit": limit,
                    "include_people": include_people,
                    "include_places": include_places,
                    "include_groups": include_groups
                }
                
                response = client.post(
                    f"{_http_config.base_url}/api/v1/memory/search",
                    json=search_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    return json.dumps({
                        "success": True,
                        "total_results": len(results),
                        "results": results[:limit],
                        "query": query
                    }, indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Search failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Search error: {str(e)}"
            }, indent=2)


class GetCurrentStatusTool(BaseTool):
    """Get current user status"""
    
    name: str = "get_current_status"
    description: str = "Get the current user status including mood, activity, location, and availability"
    
    def _run(self, **kwargs) -> str:
        """Get current status"""
        try:
            with get_http_client() as client:
                response = client.get(f"{_http_config.base_url}/api/v1/status/current")
                
                if response.status_code == 200:
                    return json.dumps(response.json(), indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Status retrieval failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Status error: {str(e)}"
            }, indent=2)


class GetSelfProfileTool(BaseTool):
    """Get user self profile"""
    
    name: str = "get_self_profile"
    description: str = "Get the user's self profile including personal information, preferences, and traits"
    
    def _run(self, **kwargs) -> str:
        """Get self profile"""
        try:
            with get_http_client() as client:
                response = client.get(f"{_http_config.base_url}/api/v1/profile/self")
                
                if response.status_code == 200:
                    return json.dumps(response.json(), indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Profile retrieval failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Profile error: {str(e)}"
            }, indent=2)


# ============================================================================
# Memory CRUD Operations
# ============================================================================

class AddFactTool(BaseTool):
    """Add a fact to memory"""
    
    name: str = "add_fact"
    description: str = "Add a fact or piece of information to memory with optional categorization and tags"
    
    def _run(self, content: str, category: str = "observation", confidence: float = 0.8, 
             source: str = "shadow_agent", tags: List[str] = None, **kwargs) -> str:
        """Add fact to memory"""
        try:
            with get_http_client() as client:
                fact_data = {
                    "content": content,
                    "category": category,
                    "confidence": confidence,
                    "source": source,
                    "tags": tags or []
                }
                
                response = client.post(
                    f"{_http_config.base_url}/api/v1/memory/facts",
                    json=fact_data
                )
                
                if response.status_code == 200:
                    return json.dumps({
                        "success": True,
                        "message": "Fact added successfully",
                        "data": response.json()
                    }, indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Fact creation failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Add fact error: {str(e)}"
            }, indent=2)


class AddPreferenceTool(BaseTool):
    """Add a user preference"""
    
    name: str = "add_preference"
    description: str = "Add or update a user preference based on observed behavior"
    
    def _run(self, preference_data: Dict[str, Any], **kwargs) -> str:
        """Add preference"""
        try:
            with get_http_client() as client:
                response = client.post(
                    f"{_http_config.base_url}/api/v1/profile/preferences",
                    json=preference_data
                )
                
                if response.status_code == 200:
                    return json.dumps({
                        "success": True,
                        "message": "Preference added successfully",
                        "data": response.json()
                    }, indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Preference creation failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Add preference error: {str(e)}"
            }, indent=2)


class UpdateStatusTool(BaseTool):
    """Update user status"""
    
    name: str = "update_status"
    description: str = "Update the user's current status including mood, activity, location, and availability"
    
    def _run(self, mood: str = None, activity: str = None, location: str = None, 
             availability: str = None, notes: str = None, **kwargs) -> str:
        """Update status"""
        try:
            status_data = {}
            if mood: status_data["mood"] = mood
            if activity: status_data["activity"] = activity
            if location: status_data["location"] = location
            if availability: status_data["availability"] = availability
            if notes: status_data["notes"] = notes
            
            with get_http_client() as client:
                response = client.post(
                    f"{_http_config.base_url}/api/v1/status/update",
                    json=status_data
                )
                
                if response.status_code == 200:
                    return json.dumps({
                        "success": True,
                        "message": "Status updated successfully",
                        "data": response.json()
                    }, indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Status update failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Status update error: {str(e)}"
            }, indent=2)


class CreateEntityTool(BaseTool):
    """Create a new entity (person, place, group, etc.)"""
    
    name: str = "create_entity"
    description: str = "Create a new entity like a person, place, group, task, or event"
    
    def _run(self, entity_type: str, entity_data: Dict[str, Any], **kwargs) -> str:
        """Create entity"""
        try:
            with get_http_client() as client:
                # Map entity types to endpoints
                endpoint_map = {
                    "person": "/api/v1/memory/people",
                    "place": "/api/v1/memory/places", 
                    "group": "/api/v1/memory/groups",
                    "task": "/api/v1/memory/tasks",
                    "event": "/api/v1/memory/events",
                    "journal": "/api/v1/memory/journal",
                    "health_metric": "/api/v1/memory/health-metrics"
                }
                
                if entity_type not in endpoint_map:
                    return json.dumps({
                        "success": False,
                        "error": f"Unknown entity type: {entity_type}",
                        "supported_types": list(endpoint_map.keys())
                    }, indent=2)
                
                response = client.post(
                    f"{_http_config.base_url}{endpoint_map[entity_type]}",
                    json=entity_data
                )
                
                if response.status_code == 200:
                    return json.dumps({
                        "success": True,
                        "message": f"{entity_type.capitalize()} created successfully",
                        "data": response.json()
                    }, indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"{entity_type.capitalize()} creation failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Create entity error: {str(e)}"
            }, indent=2)


# ============================================================================
# Advanced Query Tools
# ============================================================================

class GetStatusHistoryTool(BaseTool):
    """Get status history"""
    
    name: str = "get_status_history"
    description: str = "Get user status history for a specified time period"
    
    def _run(self, days: int = 7, limit: int = 50, **kwargs) -> str:
        """Get status history"""
        try:
            with get_http_client() as client:
                params = {"days": days, "limit": limit}
                response = client.get(
                    f"{_http_config.base_url}/api/v1/status/history",
                    params=params
                )
                
                if response.status_code == 200:
                    return json.dumps(response.json(), indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Status history retrieval failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Status history error: {str(e)}"
            }, indent=2)


class ReflectOnMemoryTool(BaseTool):
    """Reflect on memory patterns and insights"""
    
    name: str = "reflect_on_memory"
    description: str = "Process reflections and generate insights from memory patterns"
    
    def _run(self, reflection_content: str, reflection_type: str = "behavioral_pattern", **kwargs) -> str:
        """Process reflection"""
        try:
            with get_http_client() as client:
                reflection_data = {
                    "content": reflection_content,
                    "type": reflection_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "shadow_agent_reflection"
                }
                
                response = client.post(
                    f"{_http_config.base_url}/api/v1/memory/reflect",
                    json=reflection_data
                )
                
                if response.status_code == 200:
                    return json.dumps({
                        "success": True,
                        "message": "Reflection processed successfully",
                        "data": response.json()
                    }, indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Reflection processing failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Reflection error: {str(e)}"
            }, indent=2)


# ============================================================================
# Conversation Analysis Tools
# ============================================================================

class StoreConversationAnalysisTool(BaseTool):
    """Store conversation analysis results"""
    
    name: str = "store_conversation_analysis"
    description: str = "Store detailed conversation analysis results for future reference and pattern detection"
    
    def _run(self, analysis_data: Dict[str, Any], conversation_id: str = None, **kwargs) -> str:
        """Store conversation analysis"""
        try:
            with get_http_client() as client:
                store_data = {
                    "conversation_id": conversation_id or f"conv_{datetime.utcnow().isoformat()}",
                    "analysis_data": analysis_data,
                    "timestamp": datetime.utcnow().isoformat(),
                    "analyzer": "enhanced_shadow_agent"
                }
                
                response = client.post(
                    f"{_http_config.base_url}/api/v1/conversation/store-analysis",
                    json=store_data
                )
                
                if response.status_code == 200:
                    return json.dumps({
                        "success": True,
                        "message": "Conversation analysis stored successfully",
                        "data": response.json()
                    }, indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Analysis storage failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Store analysis error: {str(e)}"
            }, indent=2)


# ============================================================================
# Health and Finance Data Tools
# ============================================================================

class GetHealthMetricsTool(BaseTool):
    """Get health metrics data"""
    
    name: str = "get_health_metrics"
    description: str = "Retrieve health metrics and wellness data"
    
    def _run(self, metric_type: str = None, days: int = 7, **kwargs) -> str:
        """Get health metrics"""
        try:
            with get_http_client() as client:
                if metric_type:
                    response = client.get(
                        f"{_http_config.base_url}/api/v1/health/metric/{metric_type}/stats"
                    )
                else:
                    response = client.get(
                        f"{_http_config.base_url}/api/v1/memory/health-metrics"
                    )
                
                if response.status_code == 200:
                    return json.dumps(response.json(), indent=2)
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Health metrics retrieval failed: {response.status_code}",
                        "message": response.text
                    }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Health metrics error: {str(e)}"
            }, indent=2)


class GetRecentActivityTool(BaseTool):
    """Get recent user activity across all data types"""
    
    name: str = "get_recent_activity"
    description: str = "Get recent user activity including tasks, events, journal entries, and other interactions"
    
    def _run(self, activity_type: str = "all", limit: int = 20, **kwargs) -> str:
        """Get recent activity"""
        try:
            with get_http_client() as client:
                activities = {}
                
                if activity_type in ["all", "tasks"]:
                    task_response = client.get(f"{_http_config.base_url}/api/v1/tasks/upcoming")
                    if task_response.status_code == 200:
                        activities["tasks"] = task_response.json()
                
                if activity_type in ["all", "events"]:
                    event_response = client.get(f"{_http_config.base_url}/api/v1/calendar/upcoming")
                    if event_response.status_code == 200:
                        activities["events"] = event_response.json()
                
                if activity_type in ["all", "journal"]:
                    journal_response = client.get(f"{_http_config.base_url}/api/v1/journal/recent")
                    if journal_response.status_code == 200:
                        activities["journal"] = journal_response.json()
                
                return json.dumps({
                    "success": True,
                    "activity_type": activity_type,
                    "activities": activities,
                    "timestamp": datetime.utcnow().isoformat()
                }, indent=2)
                    
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Recent activity error: {str(e)}"
            }, indent=2)


# ============================================================================
# Tool Registration
# ============================================================================

SHADOW_AGENT_HTTP_TOOLS = {
    "search_memory": MemorySearchTool,
    "get_current_status": GetCurrentStatusTool,
    "get_self_profile": GetSelfProfileTool,
    "add_fact": AddFactTool,
    "add_preference": AddPreferenceTool,
    "update_status": UpdateStatusTool,
    "create_entity": CreateEntityTool,
    "get_status_history": GetStatusHistoryTool,
    "reflect_on_memory": ReflectOnMemoryTool,
    "store_conversation_analysis": StoreConversationAnalysisTool,
    "get_health_metrics": GetHealthMetricsTool,
    "get_recent_activity": GetRecentActivityTool
}


def get_shadow_agent_http_tools() -> List[BaseTool]:
    """Get all HTTP tools for the Shadow Agent"""
    return [tool_class() for tool_class in SHADOW_AGENT_HTTP_TOOLS.values()]


def configure_shadow_agent_http(base_url: str = "http://localhost:8000", api_key: str = "development-shadow-agent-key"):
    """Configure HTTP settings for Shadow Agent tools"""
    global _http_config
    _http_config = ShadowAgentHTTPConfig(base_url, api_key)
    logger.info(f"Shadow Agent HTTP tools configured for {base_url}")


# ============================================================================
# Enhanced Shadow Agent Integration
# ============================================================================

def update_enhanced_shadow_agent_tools():
    """Update the enhanced shadow agent with HTTP tools"""
    try:
        # Import and update the myndy_bridge tool mappings
        import sys
        from pathlib import Path
        
        # Add the tools to myndy_bridge role mappings
        bridge_path = Path(__file__).parent / "myndy_bridge.py"
        
        # Add HTTP tools to shadow_agent role in role_tool_mappings
        http_tool_names = list(SHADOW_AGENT_HTTP_TOOLS.keys())
        
        logger.info(f"Shadow Agent HTTP tools available: {http_tool_names}")
        return http_tool_names
        
    except Exception as e:
        logger.warning(f"Could not update enhanced shadow agent tools: {e}")
        return []


if __name__ == "__main__":
    # Test the Shadow Agent HTTP tools
    configure_shadow_agent_http()
    
    # Test search
    search_tool = MemorySearchTool()
    result = search_tool._run("behavioral patterns", limit=5)
    print("Search Test Result:")
    print(result)
    
    # Test status
    status_tool = GetCurrentStatusTool()
    result = status_tool._run()
    print("\nStatus Test Result:")
    print(result)
    
    # Test profile
    profile_tool = GetSelfProfileTool()
    result = profile_tool._run()
    print("\nProfile Test Result:")
    print(result)
    
    print(f"\nAvailable Shadow Agent HTTP Tools: {list(SHADOW_AGENT_HTTP_TOOLS.keys())}")