"""
MCP Tools Provider

Exposes myndy-ai tools via MCP protocol by wrapping the existing HTTP tool bridge.
Preserves async operations, connection pooling, and caching.

File: myndy_crewai_mcp/tools_provider.py
"""

import logging
import json
from typing import Any, Dict, List, Optional

# Import existing HTTP tool bridge
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.myndy_bridge import MyndyToolAPIClient, tool_api_client
from tools.async_http_client import AsyncHTTPClient

from .schemas import (
    ToolDefinition,
    ToolParameter,
    ToolParameterType,
    create_tool_result,
    create_error_result,
)
from .config import MCPConfig

logger = logging.getLogger(__name__)


class ToolsProvider:
    """
    MCP Tools Provider

    Wraps the existing HTTP tool bridge to expose myndy-ai tools via MCP protocol.
    Leverages existing async HTTP client, connection pooling, and caching.
    """

    def __init__(self, config: MCPConfig):
        """Initialize tools provider"""
        self.config = config
        # Create API client with correct base URL from config
        self.api_client = MyndyToolAPIClient(base_url=config.myndy_api_url)
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_categories: Dict[str, str] = {}  # Track category for each tool

        logger.info("Tools Provider Initializing")
        logger.info(f"   Myndy API: {config.myndy_api_url}")

    async def initialize(self):
        """Initialize and discover tools from myndy-ai backend"""
        logger.info("Discovering tools from myndy-ai backend")

        try:
            # Try to fetch tools from myndy-ai backend
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.config.myndy_api_url}/api/v1/tools/",
                    params={"limit": 100}
                )

                if response.status_code == 200:
                    result = response.json()
                    tools_list = result.get("tools", [])

                    if tools_list:
                        logger.info(f"Discovered {len(tools_list)} tools from backend")

                        # Register discovered tools with detailed tracking
                        registered_count = 0
                        failed_count = 0
                        skipped_count = 0

                        for tool_info in tools_list:
                            tool_name = tool_info.get("name", "unknown")

                            # Skip duplicates - keep first registration
                            if tool_name in self.tools:
                                skipped_count += 1
                                logger.debug(f"Skipping duplicate tool: {tool_name} ({tool_info.get('category', 'unknown')})")
                                continue

                            success = self._register_tool_from_backend(tool_info)
                            if success:
                                registered_count += 1
                            else:
                                failed_count += 1
                                logger.warning(f"Failed to register tool: {tool_name}")

                        logger.info(f"Registered {registered_count} tools successfully")
                        if skipped_count > 0:
                            logger.info(f"Skipped {skipped_count} duplicate tools")
                        if failed_count > 0:
                            logger.warning(f"Failed to register {failed_count} tools")

                        logger.info(f"Total tools in registry: {len(self.tools)}")
                        return
                    else:
                        logger.warning("No tools found in backend response")
                else:
                    logger.warning(f"Backend returned status {response.status_code}")

        except Exception as e:
            logger.warning(f"Could not connect to myndy-ai backend: {e}")

        # Fallback to test tools if backend unavailable
        logger.info("Registering fallback tools for testing")
        self._register_fallback_tools()
        logger.info(f"Registered {len(self.tools)} fallback tools")

    def _register_tool_from_backend(self, tool_info: Dict[str, Any]) -> bool:
        """Register a tool from backend discovery. Returns True if successful."""
        try:
            name = tool_info.get("name")
            if not name:
                logger.warning(f"Tool missing name field: {tool_info}")
                return False

            description = tool_info.get("description", "No description")
            category = tool_info.get("category", "general")
            parameters_dict = tool_info.get("parameters", {})

            logger.debug(f"Registering tool: {name} (category: {category}, params: {len(parameters_dict)})")

            # Convert backend parameter format to MCP format
            tool_parameters = []
            for param_name, param_info in parameters_dict.items():
                # param_info is now a dict with structured parameter data
                param_type = self._map_parameter_type(param_info.get("type", "string"))
                param_required = param_info.get("required", False)
                param_default = param_info.get("default")
                param_description = param_info.get("description", "")

                tool_parameters.append(
                    ToolParameter(
                        name=param_name,
                        type=param_type,
                        description=param_description,
                        required=param_required,
                        default=param_default
                    )
                )

            # Create tool definition with category in description
            full_description = f"[{category}] {description}"
            tool_def = ToolDefinition.from_parameters(
                name=name,
                description=full_description,
                parameters=tool_parameters
            )

            self.tools[name] = tool_def
            self.tool_categories[name] = category
            logger.debug(f"   Successfully registered: {name} ({category})")
            return True

        except Exception as e:
            logger.warning(f"Failed to register tool {tool_info.get('name', 'unknown')}: {e}", exc_info=True)
            return False

    def _map_parameter_type(self, backend_type: str) -> ToolParameterType:
        """Map backend parameter types to MCP types"""
        type_mapping = {
            "string": ToolParameterType.STRING,
            "str": ToolParameterType.STRING,
            "number": ToolParameterType.NUMBER,
            "float": ToolParameterType.NUMBER,
            "integer": ToolParameterType.INTEGER,
            "int": ToolParameterType.INTEGER,
            "boolean": ToolParameterType.BOOLEAN,
            "bool": ToolParameterType.BOOLEAN,
            "array": ToolParameterType.ARRAY,
            "list": ToolParameterType.ARRAY,
            "object": ToolParameterType.OBJECT,
            "dict": ToolParameterType.OBJECT,
        }
        return type_mapping.get(backend_type.lower(), ToolParameterType.STRING)

    def _register_fallback_tools(self):
        """Register fallback tools for testing when backend is unavailable"""
        logger.info("Registering fallback test tools")

        # Time tool
        self.tools["get_current_time"] = ToolDefinition.from_parameters(
            name="get_current_time",
            description="Get the current time in a specific timezone",
            parameters=[
                ToolParameter(
                    name="timezone",
                    type=ToolParameterType.STRING,
                    description="Timezone name (e.g., 'UTC', 'America/New_York')",
                    required=False,
                    default="UTC"
                )
            ]
        )

        # Echo tool for testing
        self.tools["echo"] = ToolDefinition.from_parameters(
            name="echo",
            description="Echo back the provided message (test tool)",
            parameters=[
                ToolParameter(
                    name="message",
                    type=ToolParameterType.STRING,
                    description="Message to echo back",
                    required=True
                )
            ]
        )

        # Memory search tool
        self.tools["search_memory"] = ToolDefinition.from_parameters(
            name="search_memory",
            description="Search through memory entities",
            parameters=[
                ToolParameter(
                    name="query",
                    type=ToolParameterType.STRING,
                    description="Search query",
                    required=True
                ),
                ToolParameter(
                    name="limit",
                    type=ToolParameterType.INTEGER,
                    description="Maximum number of results",
                    required=False,
                    default=10
                )
            ]
        )

        logger.info(f"   Registered {len(self.tools)} fallback tools")

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool via the HTTP bridge"""
        logger.info(f"Executing tool: {name}")
        logger.debug(f"   Arguments: {arguments}")

        try:
            # Check if tool exists
            if name not in self.tools:
                error_msg = f"Tool not found: {name}"
                logger.error(f"Error: {error_msg}")
                return json.dumps({"error": error_msg})

            # Execute via HTTP tool bridge
            result = await self.api_client.execute_tool_async(
                tool_name=name,
                parameters=arguments
            )

            if result is None:
                error_msg = "Tool execution returned None"
                logger.error(f"Error: {error_msg}")
                return json.dumps({"error": error_msg})

            # Check for errors in result
            if isinstance(result, dict) and "error" in result:
                logger.warning(f"Tool execution error: {result['error']}")
                return json.dumps(result, indent=2)

            logger.info(f"Tool {name} executed successfully")

            # Format result as JSON
            if isinstance(result, str):
                return result
            else:
                return json.dumps(result, indent=2)

        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(f"Error: {error_msg}", exc_info=True)
            return json.dumps({"error": error_msg})

    def get_tool_definitions(self) -> List[ToolDefinition]:
        """Get all registered tool definitions"""
        return list(self.tools.values())

    def get_tool_by_name(self, name: str) -> Optional[ToolDefinition]:
        """Get a specific tool definition by name"""
        return self.tools.get(name)

    def get_tool_count(self) -> int:
        """Get the number of registered tools"""
        return len(self.tools)

    def get_tool_categories(self) -> Dict[str, List[str]]:
        """Get tools organized by category"""
        categories: Dict[str, List[str]] = {}

        for tool_name in self.tools.keys():
            # Use tracked category or default to general
            category = self.tool_categories.get(tool_name, "general")

            if category not in categories:
                categories[category] = []
            categories[category].append(tool_name)

        return categories

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get HTTP client performance metrics"""
        try:
            metrics = self.api_client.get_performance_metrics()
            return metrics
        except Exception as e:
            logger.warning(f"Could not get performance metrics: {e}")
            return {}


# ============================================================================
# Utility Functions
# ============================================================================

async def create_tools_provider(config: MCPConfig) -> ToolsProvider:
    """Create and initialize a tools provider"""
    provider = ToolsProvider(config)
    await provider.initialize()
    return provider
