"""
MCP Resources Provider

Exposes myndy-ai data via MCP protocol using URI-based resources.
Implements the myndy:// URI scheme for accessing memory, profiles, and documents.

File: myndy_crewai_mcp/resources_provider.py
"""

import logging
import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs

# Import HTTP client for myndy-ai backend
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.myndy_bridge import MyndyToolAPIClient

from .schemas import (
    ResourceDefinition,
    ResourceContent,
    ResourceTemplate,
    ResourceType,
)
from .config import MCPConfig

logger = logging.getLogger(__name__)


class ResourcesProvider:
    """
    MCP Resources Provider

    Provides access to myndy-ai data via URI-based resources.
    Implements myndy:// URI scheme for memory, profiles, and documents.
    """

    def __init__(self, config: MCPConfig):
        """Initialize resources provider"""
        self.config = config
        self.api_client = MyndyToolAPIClient(base_url=config.myndy_api_url)
        self.resources: Dict[str, ResourceDefinition] = {}
        self.templates: Dict[str, ResourceTemplate] = {}

        logger.info("Resources Provider Initializing")
        logger.info(f"   Myndy API: {config.myndy_api_url}")

    async def initialize(self):
        """Initialize and register available resources"""
        logger.info("Registering resources and templates")

        # Register static resources
        self._register_memory_resources()
        self._register_profile_resources()
        self._register_health_resources()
        self._register_finance_resources()
        self._register_document_resources()

        # Register templates for parameterized resources
        self._register_templates()

        logger.info(f"Registered {len(self.resources)} resources")
        logger.info(f"Registered {len(self.templates)} resource templates")

    def _register_memory_resources(self):
        """Register memory-related resources"""

        # All memory entities
        self.resources["myndy://memory/entities"] = ResourceDefinition(
            uri="myndy://memory/entities",
            name="Memory Entities",
            description="All memory entities (people, places, events, etc.)",
            mimeType=ResourceType.JSON
        )

        # Conversation history
        self.resources["myndy://memory/conversations"] = ResourceDefinition(
            uri="myndy://memory/conversations",
            name="Conversation History",
            description="Recent conversation history and context",
            mimeType=ResourceType.JSON
        )

        # Short-term memory
        self.resources["myndy://memory/short-term"] = ResourceDefinition(
            uri="myndy://memory/short-term",
            name="Short-Term Memory",
            description="Recent short-term memory entries",
            mimeType=ResourceType.JSON
        )

        # People
        self.resources["myndy://memory/people"] = ResourceDefinition(
            uri="myndy://memory/people",
            name="People",
            description="All people in memory",
            mimeType=ResourceType.JSON
        )

        # Places
        self.resources["myndy://memory/places"] = ResourceDefinition(
            uri="myndy://memory/places",
            name="Places",
            description="All places in memory",
            mimeType=ResourceType.JSON
        )

        # Events
        self.resources["myndy://memory/events"] = ResourceDefinition(
            uri="myndy://memory/events",
            name="Events",
            description="All events in memory",
            mimeType=ResourceType.JSON
        )

        logger.debug("Registered 6 memory resources")

    def _register_profile_resources(self):
        """Register profile-related resources"""

        # Self profile
        self.resources["myndy://profile/self"] = ResourceDefinition(
            uri="myndy://profile/self",
            name="Self Profile",
            description="User's self profile with preferences and settings",
            mimeType=ResourceType.JSON
        )

        # Goals
        self.resources["myndy://profile/goals"] = ResourceDefinition(
            uri="myndy://profile/goals",
            name="Goals",
            description="User's current goals and objectives",
            mimeType=ResourceType.JSON
        )

        # Preferences
        self.resources["myndy://profile/preferences"] = ResourceDefinition(
            uri="myndy://profile/preferences",
            name="Preferences",
            description="User preferences and settings",
            mimeType=ResourceType.JSON
        )

        logger.debug("Registered 3 profile resources")

    def _register_health_resources(self):
        """Register health-related resources"""

        # Health metrics
        self.resources["myndy://health/metrics"] = ResourceDefinition(
            uri="myndy://health/metrics",
            name="Health Metrics",
            description="Recent health metrics and data",
            mimeType=ResourceType.JSON
        )

        # Health status
        self.resources["myndy://health/status"] = ResourceDefinition(
            uri="myndy://health/status",
            name="Health Status",
            description="Current health status entries",
            mimeType=ResourceType.JSON
        )

        logger.debug("Registered 2 health resources")

    def _register_finance_resources(self):
        """Register finance-related resources"""

        # Transactions
        self.resources["myndy://finance/transactions"] = ResourceDefinition(
            uri="myndy://finance/transactions",
            name="Financial Transactions",
            description="Recent financial transactions",
            mimeType=ResourceType.JSON
        )

        # Budget summary
        self.resources["myndy://finance/budget"] = ResourceDefinition(
            uri="myndy://finance/budget",
            name="Budget Summary",
            description="Current budget and spending summary",
            mimeType=ResourceType.JSON
        )

        logger.debug("Registered 2 finance resources")

    def _register_document_resources(self):
        """Register document-related resources"""

        # Documents list
        self.resources["myndy://documents/list"] = ResourceDefinition(
            uri="myndy://documents/list",
            name="Documents List",
            description="List of available documents",
            mimeType=ResourceType.JSON
        )

        logger.debug("Registered 1 document resource")

    def _register_templates(self):
        """Register resource URI templates for parameterized access"""

        # Specific entity by ID
        self.templates["memory-entity"] = ResourceTemplate(
            uriTemplate="myndy://memory/entities/{entity_id}",
            name="Memory Entity",
            description="Specific memory entity by ID",
            mimeType=ResourceType.JSON
        )

        # Specific conversation by ID
        self.templates["conversation"] = ResourceTemplate(
            uriTemplate="myndy://memory/conversations/{conversation_id}",
            name="Conversation",
            description="Specific conversation by ID",
            mimeType=ResourceType.JSON
        )

        # Specific person by ID
        self.templates["person"] = ResourceTemplate(
            uriTemplate="myndy://memory/people/{person_id}",
            name="Person",
            description="Specific person by ID",
            mimeType=ResourceType.JSON
        )

        # Specific place by ID
        self.templates["place"] = ResourceTemplate(
            uriTemplate="myndy://memory/places/{place_id}",
            name="Place",
            description="Specific place by ID",
            mimeType=ResourceType.JSON
        )

        # Document by path
        self.templates["document"] = ResourceTemplate(
            uriTemplate="myndy://documents/{path}",
            name="Document",
            description="Specific document by path",
            mimeType=ResourceType.JSON
        )

        logger.debug("Registered 5 resource templates")

    async def read_resource(self, uri: str) -> ResourceContent:
        """Read a resource by URI"""
        logger.info(f"Reading resource: {uri}")

        try:
            # Parse the URI
            parsed = urlparse(uri)

            if parsed.scheme != "myndy":
                raise ValueError(f"Invalid URI scheme: {parsed.scheme} (expected 'myndy')")

            # For myndy:// URIs, urlparse treats the first part as netloc (hostname)
            # So myndy://memory/entities becomes:
            #   netloc = "memory"
            #   path = "/entities"
            # We need to combine them to get the full path
            if parsed.netloc:
                # Standard format: myndy://category/type[/id]
                category = parsed.netloc
                path_parts = [p for p in parsed.path.strip("/").split("/") if p]

                if not path_parts:
                    raise ValueError(f"Invalid URI format: {uri} (need at least category/type)")

                resource_type = path_parts[0]  # e.g., "entities", "self", "metrics"
                resource_id = path_parts[1] if len(path_parts) > 1 else None
            else:
                # Alternative format (if netloc is empty): myndy:category/type[/id]
                path_parts = [p for p in parsed.path.strip("/").split("/") if p]

                if len(path_parts) < 2:
                    raise ValueError(f"Invalid URI format: {uri} (need at least category/type)")

                category = path_parts[0]
                resource_type = path_parts[1]
                resource_id = path_parts[2] if len(path_parts) > 2 else None

            # Route to appropriate handler
            if category == "memory":
                content = await self._read_memory_resource(resource_type, resource_id)
            elif category == "profile":
                content = await self._read_profile_resource(resource_type, resource_id)
            elif category == "health":
                content = await self._read_health_resource(resource_type, resource_id)
            elif category == "finance":
                content = await self._read_finance_resource(resource_type, resource_id)
            elif category == "documents":
                content = await self._read_document_resource(resource_type, resource_id)
            else:
                raise ValueError(f"Unknown resource category: {category}")

            logger.info(f"Successfully read resource: {uri}")
            return ResourceContent(
                uri=uri,
                mimeType=ResourceType.JSON,
                text=json.dumps(content, indent=2)
            )

        except Exception as e:
            logger.error(f"Failed to read resource {uri}: {e}")
            return ResourceContent(
                uri=uri,
                mimeType=ResourceType.JSON,
                text=json.dumps({"error": str(e)}, indent=2)
            )

    async def _read_memory_resource(self, resource_type: str, resource_id: Optional[str] = None) -> Dict[str, Any]:
        """Read memory-related resource"""

        if resource_type == "entities":
            if resource_id:
                # Get specific entity
                result = await self.api_client.execute_tool_async(
                    "search_memory",
                    {"query": resource_id, "limit": 1}
                )
            else:
                # Get all entities
                result = await self.api_client.execute_tool_async(
                    "search_memory",
                    {"query": "*", "limit": 100}
                )
            return result or {"entities": [], "error": "No data"}

        elif resource_type == "conversations":
            # Get conversation history via short-term memory
            result = await self.api_client.execute_tool_async(
                "short_term_memory",
                {"action": "retrieve", "limit": 50}
            )
            return result or {"conversations": [], "error": "No data"}

        elif resource_type == "short-term":
            result = await self.api_client.execute_tool_async(
                "short_term_memory",
                {"action": "retrieve", "limit": 20}
            )
            return result or {"entries": [], "error": "No data"}

        elif resource_type == "people":
            result = await self.api_client.execute_tool_async(
                "manage_people",
                {"action": "list"}
            )
            return result or {"people": [], "error": "No data"}

        elif resource_type == "places":
            result = await self.api_client.execute_tool_async(
                "manage_places",
                {"action": "list"}
            )
            return result or {"places": [], "error": "No data"}

        elif resource_type == "events":
            result = await self.api_client.execute_tool_async(
                "manage_events",
                {"action": "list"}
            )
            return result or {"events": [], "error": "No data"}

        else:
            raise ValueError(f"Unknown memory resource type: {resource_type}")

    async def _read_profile_resource(self, resource_type: str, resource_id: Optional[str] = None) -> Dict[str, Any]:
        """Read profile-related resource"""

        if resource_type == "self":
            result = await self.api_client.execute_tool_async(
                "get_self_profile",
                {}
            )
            return result or {"profile": None, "error": "No profile"}

        elif resource_type == "goals":
            # Get profile and extract goals
            profile = await self.api_client.execute_tool_async(
                "get_self_profile",
                {}
            )
            if profile and "result" in profile:
                goals = profile.get("result", {}).get("output", {}).get("value", {}).get("profile", {}).get("dynamic_state", {}).get("current_goals", [])
                return {"goals": goals}
            return {"goals": [], "error": "No goals found"}

        elif resource_type == "preferences":
            # Get profile and extract preferences
            profile = await self.api_client.execute_tool_async(
                "get_self_profile",
                {}
            )
            if profile and "result" in profile:
                prefs = profile.get("result", {}).get("output", {}).get("value", {}).get("profile", {}).get("preferences", {})
                return {"preferences": prefs}
            return {"preferences": {}, "error": "No preferences found"}

        else:
            raise ValueError(f"Unknown profile resource type: {resource_type}")

    async def _read_health_resource(self, resource_type: str, resource_id: Optional[str] = None) -> Dict[str, Any]:
        """Read health-related resource"""

        if resource_type == "metrics":
            result = await self.api_client.execute_tool_async(
                "manage_status",
                {"action": "list", "limit": 20}
            )
            return result or {"metrics": [], "error": "No data"}

        elif resource_type == "status":
            result = await self.api_client.execute_tool_async(
                "manage_status",
                {"action": "list", "limit": 10}
            )
            return result or {"status": [], "error": "No data"}

        else:
            raise ValueError(f"Unknown health resource type: {resource_type}")

    async def _read_finance_resource(self, resource_type: str, resource_id: Optional[str] = None) -> Dict[str, Any]:
        """Read finance-related resource"""

        # Note: Finance tools may not be available yet
        # This is a placeholder implementation

        if resource_type == "transactions":
            return {
                "transactions": [],
                "message": "Finance tools not yet available in backend"
            }

        elif resource_type == "budget":
            return {
                "budget": {},
                "message": "Finance tools not yet available in backend"
            }

        else:
            raise ValueError(f"Unknown finance resource type: {resource_type}")

    async def _read_document_resource(self, resource_type: str, resource_id: Optional[str] = None) -> Dict[str, Any]:
        """Read document-related resource"""

        if resource_type == "list":
            return {
                "documents": [],
                "message": "Document listing not yet implemented"
            }

        elif resource_id:
            # Specific document by path
            return {
                "document": None,
                "path": resource_id,
                "message": "Document retrieval not yet implemented"
            }

        else:
            raise ValueError(f"Unknown document resource type: {resource_type}")

    def get_resource_definitions(self) -> List[ResourceDefinition]:
        """Get all registered resource definitions"""
        return list(self.resources.values())

    def get_resource_templates(self) -> List[ResourceTemplate]:
        """Get all registered resource templates"""
        return list(self.templates.values())

    def get_resource_count(self) -> int:
        """Get the number of registered resources"""
        return len(self.resources)

    def get_template_count(self) -> int:
        """Get the number of registered templates"""
        return len(self.templates)


# ============================================================================
# Utility Functions
# ============================================================================

async def create_resources_provider(config: MCPConfig) -> ResourcesProvider:
    """Create and initialize a resources provider"""
    provider = ResourcesProvider(config)
    await provider.initialize()
    return provider
