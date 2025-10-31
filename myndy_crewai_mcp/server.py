"""
MCP Server Implementation with SSE (Server-Sent Events) Streaming

HTTP/SSE streaming MCP server that exposes CrewAI agents, tools, resources,
and prompts to LibreChat and other MCP-compatible clients.

File: myndy_crewai_mcp/server.py
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
import mcp.types as types

from .config import get_config, MCPConfig
from .schemas import (
    ServerInfo,
    ServerCapabilities,
    InitializeResult,
    ToolDefinition,
    ResourceDefinition,
    PromptDefinition,
    create_tool_result,
    create_error_result,
)

# Configure logging
logger = logging.getLogger(__name__)


class MyndyMCPServer:
    """
    MCP Server for CrewAI-Myndy Integration

    Exposes:
    - Tools: 85+ myndy tools for memory, calendar, health, finance, etc.
    - Resources: Memory entities, profiles, documents via myndy:// URIs
    - Prompts: Agent workflow templates for personal assistant, research, etc.
    """

    def __init__(self, config: Optional[MCPConfig] = None):
        """Initialize MCP server"""
        self.config = config or get_config()

        # Create MCP server instance
        self.server = Server(self.config.server_name)

        # Storage for registered components
        self.tools: Dict[str, ToolDefinition] = {}
        self.resources: Dict[str, ResourceDefinition] = {}
        self.prompts: Dict[str, PromptDefinition] = {}

        # Tool providers (will be injected)
        self.tools_provider = None
        self.resources_provider = None
        self.prompts_provider = None

        logger.info(f"Initializing {self.config.server_name} v{self.config.server_version}")

        # Register MCP handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP protocol handlers"""

        # List tools handler
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List available tools"""
            logger.debug(f"Listing {len(self.tools)} tools")

            if not self.config.enable_tools:
                logger.warning("Tools are disabled in configuration")
                return []

            # Convert internal tool definitions to MCP Tool format
            mcp_tools = []
            for tool_def in self.tools.values():
                mcp_tool = types.Tool(
                    name=tool_def.name,
                    description=tool_def.description,
                    inputSchema=tool_def.inputSchema
                )
                mcp_tools.append(mcp_tool)

            logger.info(f"Returning {len(mcp_tools)} tools")
            return mcp_tools

        # Call tool handler
        @self.server.call_tool()
        async def call_tool(
            name: str,
            arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Execute a tool"""
            logger.info(f"Executing tool: {name}")
            logger.debug(f"   Arguments: {arguments}")

            if not self.config.enable_tools:
                error_msg = "Tools are disabled in configuration"
                logger.error(f"Error: {error_msg}")
                return [types.TextContent(type="text", text=f"Error: {error_msg}")]

            try:
                # Check if tool exists
                if name not in self.tools:
                    error_msg = f"Tool not found: {name}"
                    logger.error(f"Error: {error_msg}")
                    return [types.TextContent(type="text", text=f"Error: {error_msg}")]

                # Execute tool via tools provider
                if self.tools_provider is None:
                    error_msg = "Tools provider not initialized"
                    logger.error(f"Error: {error_msg}")
                    return [types.TextContent(type="text", text=f"Error: {error_msg}")]

                result = await self.tools_provider.execute_tool(name, arguments)

                logger.info(f"Tool {name} executed successfully")
                return [types.TextContent(type="text", text=str(result))]

            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                logger.error(f"Error: {error_msg}", exc_info=True)
                return [types.TextContent(type="text", text=f"Error: {error_msg}")]

        # List resources handler
        @self.server.list_resources()
        async def list_resources() -> List[types.Resource]:
            """List available resources"""
            logger.debug(f"Listing {len(self.resources)} resources")

            if not self.config.enable_resources:
                logger.warning("Resources are disabled in configuration")
                return []

            # Convert internal resource definitions to MCP Resource format
            mcp_resources = []
            for resource_def in self.resources.values():
                mcp_resource = types.Resource(
                    uri=resource_def.uri,
                    name=resource_def.name,
                    description=resource_def.description,
                    mimeType=resource_def.mimeType
                )
                mcp_resources.append(mcp_resource)

            logger.info(f"Returning {len(mcp_resources)} resources")
            return mcp_resources

        # Read resource handler
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource by URI"""
            logger.info(f"Reading resource: {uri}")

            if not self.config.enable_resources:
                error_msg = "Resources are disabled in configuration"
                logger.error(f"Error: {error_msg}")
                raise ValueError(error_msg)

            try:
                # Check if resource exists
                if uri not in self.resources:
                    error_msg = f"Resource not found: {uri}"
                    logger.error(f"Error: {error_msg}")
                    raise ValueError(error_msg)

                # Read resource via resources provider
                if self.resources_provider is None:
                    error_msg = "Resources provider not initialized"
                    logger.error(f"Error: {error_msg}")
                    raise ValueError(error_msg)

                content = await self.resources_provider.read_resource(uri)

                logger.info(f"Resource {uri} read successfully")
                return content

            except Exception as e:
                error_msg = f"Resource read failed: {str(e)}"
                logger.error(f"Error: {error_msg}", exc_info=True)
                raise ValueError(error_msg)

        # List prompts handler
        @self.server.list_prompts()
        async def list_prompts() -> List[types.Prompt]:
            """List available prompts"""
            logger.debug(f"Listing {len(self.prompts)} prompts")

            if not self.config.enable_prompts:
                logger.warning("Prompts are disabled in configuration")
                return []

            # Convert internal prompt definitions to MCP Prompt format
            mcp_prompts = []
            for prompt_def in self.prompts.values():
                # Convert prompt arguments
                mcp_args = [
                    types.PromptArgument(
                        name=arg.name,
                        description=arg.description,
                        required=arg.required
                    )
                    for arg in prompt_def.arguments
                ]

                mcp_prompt = types.Prompt(
                    name=prompt_def.name,
                    description=prompt_def.description,
                    arguments=mcp_args
                )
                mcp_prompts.append(mcp_prompt)

            logger.info(f"Returning {len(mcp_prompts)} prompts")
            return mcp_prompts

        # Get prompt handler
        @self.server.get_prompt()
        async def get_prompt(
            name: str,
            arguments: Optional[Dict[str, str]] = None
        ) -> types.GetPromptResult:
            """Get a prompt with arguments"""
            logger.info(f"Getting prompt: {name}")
            logger.debug(f"   Arguments: {arguments}")

            if not self.config.enable_prompts:
                error_msg = "Prompts are disabled in configuration"
                logger.error(f"Error: {error_msg}")
                raise ValueError(error_msg)

            try:
                # Check if prompt exists
                if name not in self.prompts:
                    error_msg = f"Prompt not found: {name}"
                    logger.error(f"Error: {error_msg}")
                    raise ValueError(error_msg)

                # Get prompt via prompts provider
                if self.prompts_provider is None:
                    error_msg = "Prompts provider not initialized"
                    logger.error(f"Error: {error_msg}")
                    raise ValueError(error_msg)

                result = await self.prompts_provider.get_prompt(name, arguments or {})

                # Convert to MCP format
                mcp_messages = [
                    types.PromptMessage(
                        role=msg.role,
                        content=types.TextContent(type="text", text=msg.content)
                    )
                    for msg in result.messages
                ]

                logger.info(f"Prompt {name} retrieved successfully")
                return types.GetPromptResult(
                    description=result.description,
                    messages=mcp_messages
                )

            except Exception as e:
                error_msg = f"Prompt retrieval failed: {str(e)}"
                logger.error(f"Error: {error_msg}", exc_info=True)
                raise ValueError(error_msg)

    def register_tool(self, tool_def: ToolDefinition):
        """Register a tool"""
        self.tools[tool_def.name] = tool_def
        logger.debug(f"   Registered tool: {tool_def.name}")

    def register_resource(self, resource_def: ResourceDefinition):
        """Register a resource"""
        self.resources[resource_def.uri] = resource_def
        logger.debug(f"   Registered resource: {resource_def.uri}")

    def register_prompt(self, prompt_def: PromptDefinition):
        """Register a prompt"""
        self.prompts[prompt_def.name] = prompt_def
        logger.debug(f"   Registered prompt: {prompt_def.name}")

    def set_tools_provider(self, provider):
        """Set the tools provider"""
        self.tools_provider = provider
        logger.info(f"Tools provider registered")

    def set_resources_provider(self, provider):
        """Set the resources provider"""
        self.resources_provider = provider
        logger.info(f"Resources provider registered")

    def set_prompts_provider(self, provider):
        """Set the prompts provider"""
        self.prompts_provider = provider
        logger.info(f"Prompts provider registered")

    def get_capabilities(self) -> ServerCapabilities:
        """Get server capabilities"""
        capabilities = ServerCapabilities(
            tools={"listChanged": True} if self.config.enable_tools else None,
            resources={"subscribe": False, "listChanged": True} if self.config.enable_resources else None,
            prompts={"listChanged": True} if self.config.enable_prompts else None,
            logging={}
        )
        return capabilities

    def get_server_info(self) -> ServerInfo:
        """Get server information"""
        return ServerInfo(
            name=self.config.server_name,
            version=self.config.server_version,
            protocolVersion="2024-11-05",
            capabilities=self.get_capabilities()
        )

    async def run_sse(self):
        """Run MCP server with SSE transport"""
        logger.info(f"Starting MCP server with SSE transport")
        logger.info(f"   Host: {self.config.http_host}")
        logger.info(f"   Port: {self.config.http_port}")

        # Create Starlette app for SSE
        @asynccontextmanager
        async def lifespan(app):
            """App lifespan manager"""
            logger.info("MCP Server starting up...")
            yield
            logger.info("MCP Server shutting down...")

        async def handle_sse(request: Request) -> Response:
            """Handle SSE connections"""
            logger.info(f"New SSE connection from {request.client}")

            async with SseServerTransport("/messages") as transport:
                await self.server.run(
                    transport.read_stream,
                    transport.write_stream,
                    self.server.create_initialization_options()
                )

            return Response()

        async def health_check(request: Request) -> Response:
            """Health check endpoint"""
            return Response(
                content='{"status":"healthy","server":"myndy-crewai-mcp"}',
                media_type="application/json"
            )

        async def handle_json_rpc(request: Request) -> Response:
            """Handle JSON-RPC requests for testing"""
            try:
                body = await request.json()
                method = body.get("method", "")
                params = body.get("params", {})
                request_id = body.get("id", 1)

                result = None

                # Handle different MCP methods
                if method == "tools/list":
                    # Use tools registry directly
                    result = {"tools": [
                        {
                            "name": tool_def.name,
                            "description": tool_def.description,
                            "inputSchema": tool_def.inputSchema
                        } for tool_def in self.tools.values()
                    ]}

                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    # Execute tool via provider
                    if self.tools_provider:
                        tool_result = await self.tools_provider.execute_tool(tool_name, arguments)
                        result = {"content": [{"type": "text", "text": str(tool_result)}]}
                    else:
                        raise ValueError("Tools provider not initialized")

                elif method == "resources/list":
                    # Use resources registry directly
                    result = {"resources": [
                        {
                            "uri": res_def.uri,
                            "name": res_def.name,
                            "description": res_def.description,
                            "mimeType": res_def.mimeType
                        } for res_def in self.resources.values()
                    ]}

                elif method == "resources/read":
                    uri = params.get("uri")
                    # Read resource via provider
                    if self.resources_provider:
                        resource_content = await self.resources_provider.read_resource(uri)
                        result = {
                            "contents": [{
                                "uri": resource_content.uri,
                                "mimeType": resource_content.mimeType,
                                "text": resource_content.text
                            }]
                        }
                    else:
                        raise ValueError("Resources provider not initialized")

                elif method == "prompts/list":
                    # Use prompts registry directly
                    result = {"prompts": [
                        {
                            "name": p.name,
                            "description": p.description,
                            "arguments": [
                                {"name": a.name, "description": a.description, "required": a.required}
                                for a in (p.arguments or [])
                            ]
                        } for p in self.prompts.values()
                    ]}

                elif method == "prompts/get":
                    name = params.get("name")
                    arguments = params.get("arguments", {})
                    # Get prompt via provider
                    if self.prompts_provider:
                        prompt_result = await self.prompts_provider.get_prompt(name, arguments)
                        result = {
                            "description": prompt_result.description,
                            "messages": [
                                {
                                    "role": m.role,
                                    "content": m.content
                                } for m in prompt_result.messages
                            ]
                        }
                    else:
                        raise ValueError("Prompts provider not initialized")

                else:
                    return Response(
                        content=json.dumps({
                            "jsonrpc": "2.0",
                            "error": {"code": -32601, "message": f"Method not found: {method}"},
                            "id": request_id
                        }),
                        media_type="application/json",
                        status_code=404
                    )

                return Response(
                    content=json.dumps({
                        "jsonrpc": "2.0",
                        "result": result,
                        "id": request_id
                    }),
                    media_type="application/json"
                )

            except Exception as e:
                logger.error(f"JSON-RPC error: {e}")
                import traceback
                traceback.print_exc()
                return Response(
                    content=json.dumps({
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": str(e)},
                        "id": body.get("id", 1) if isinstance(body, dict) else 1
                    }),
                    media_type="application/json",
                    status_code=500
                )

        app = Starlette(
            debug=self.config.debug_mode,
            lifespan=lifespan,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Route("/health", endpoint=health_check),
                Route("/mcp", endpoint=handle_json_rpc, methods=["POST"]),
            ],
        )

        # Run with uvicorn
        import uvicorn
        config = uvicorn.Config(
            app,
            host=self.config.http_host,
            port=self.config.http_port,
            log_level=self.config.log_level.lower(),
        )
        server = uvicorn.Server(config)

        logger.info(f"MCP Server ready at http://{self.config.http_host}:{self.config.http_port}")
        logger.info(f"   SSE endpoint: /sse")
        logger.info(f"   Health check: /health")
        logger.info(f"   Tools: {len(self.tools)} registered")
        logger.info(f"   Resources: {len(self.resources)} registered")
        logger.info(f"   Prompts: {len(self.prompts)} registered")

        await server.serve()

    async def run(self):
        """Run MCP server with configured transport"""
        if self.config.transport_type == "sse":
            await self.run_sse()
        else:
            raise ValueError(f"Unsupported transport: {self.config.transport_type}")


# ============================================================================
# CLI Entry Point
# ============================================================================

async def main():
    """Main entry point for MCP server"""
    # Load configuration
    config = get_config()

    # Create server
    server = MyndyMCPServer(config)

    # TODO: Initialize and register providers
    # from .tools_provider import create_tools_provider
    # from .resources_provider import create_resources_provider
    # from .prompts_provider import create_prompts_provider
    #
    # tools_provider = await create_tools_provider(config)
    # server.set_tools_provider(tools_provider)
    #
    # resources_provider = await create_resources_provider(config)
    # server.set_resources_provider(resources_provider)
    #
    # prompts_provider = await create_prompts_provider(config)
    # server.set_prompts_provider(prompts_provider)

    logger.info("=" * 60)
    logger.info(f"{config.server_name} v{config.server_version}")
    logger.info("=" * 60)
    logger.info(f"   Transport: {config.transport_type.upper()}")
    logger.info(f"   Myndy API: {config.myndy_api_url}")
    logger.info(f"   Debug: {config.debug_mode}")
    logger.info("=" * 60)

    # Run server
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
