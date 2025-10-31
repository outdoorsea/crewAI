"""
MCP Server Main Entry Point

Starts the MCP server with SSE streaming transport for LibreChat integration.

File: myndy_crewai_mcp/main.py

Usage:
    python -m myndy_crewai_mcp.main
"""

import asyncio
import logging
from pathlib import Path

from .config import get_config
from .server import MyndyMCPServer
from .tools_provider import create_tools_provider
from .resources_provider import create_resources_provider
from .prompts_provider import create_prompts_provider

logger = logging.getLogger(__name__)


async def main():
    """Main entry point for MCP server"""
    print("=" * 70)
    print("  Myndy CrewAI MCP Server")
    print("  Model Context Protocol Server for LibreChat")
    print("=" * 70)

    # Load configuration
    config = get_config()

    # Create server
    logger.info("Creating MCP server...")
    server = MyndyMCPServer(config)

    # Initialize and register tools provider
    logger.info("Initializing tools provider...")
    tools_provider = await create_tools_provider(config)
    server.set_tools_provider(tools_provider)

    # Register tools with server
    logger.info("Registering tools with MCP server...")
    for tool_def in tools_provider.get_tool_definitions():
        server.register_tool(tool_def)

    logger.info(f"Registered {len(server.tools)} tools")

    # Initialize and register resources provider
    logger.info("Initializing resources provider...")
    resources_provider = await create_resources_provider(config)
    server.set_resources_provider(resources_provider)

    # Register resources with server
    logger.info("Registering resources with MCP server...")
    for resource_def in resources_provider.get_resource_definitions():
        server.register_resource(resource_def)

    logger.info(f"Registered {len(server.resources)} resources")

    # Initialize and register prompts provider
    logger.info("Initializing prompts provider...")
    prompts_provider = await create_prompts_provider(config)
    server.set_prompts_provider(prompts_provider)

    # Register prompts with server
    logger.info("Registering prompts with MCP server...")
    for prompt_def in prompts_provider.get_prompt_definitions():
        server.register_prompt(prompt_def)

    logger.info(f"Registered {len(server.prompts)} prompts")

    # Display server info
    print()
    print("Server Configuration:")
    print(f"  Name: {config.server_name}")
    print(f"  Version: {config.server_version}")
    print(f"  Transport: {config.transport_type.upper()}")
    print(f"  Host: {config.http_host}")
    print(f"  Port: {config.http_port}")
    print(f"  Myndy API: {config.myndy_api_url}")
    print()
    print("Capabilities:")
    print(f"  Tools: {len(server.tools)} registered")
    print(f"  Resources: {len(server.resources)} registered")
    print(f"  Prompts: {len(server.prompts)} registered")
    print()
    print("Endpoints:")
    print(f"  SSE: http://{config.http_host}:{config.http_port}/sse")
    print(f"  Health: http://{config.http_host}:{config.http_port}/health")
    print()
    print("=" * 70)
    print()

    # Run server
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\nServer stopped.")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
