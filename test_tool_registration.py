#!/usr/bin/env python3
"""
Test script for tool registration debugging

File: test_tool_registration.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from myndy_crewai_mcp.config import get_config
from myndy_crewai_mcp.tools_provider import ToolsProvider

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Test tool registration with detailed output"""
    print("=" * 70)
    print("  Tool Registration Test")
    print("=" * 70)
    print()

    # Get configuration
    config = get_config()
    print(f"Backend URL: {config.myndy_api_url}")
    print()

    # Create and initialize provider
    provider = ToolsProvider(config)
    await provider.initialize()

    print()
    print("=" * 70)
    print("  Registration Results")
    print("=" * 70)
    print()

    # Get statistics
    tool_count = provider.get_tool_count()
    categories = provider.get_tool_categories()

    print(f"Total tools registered: {tool_count}")
    print()

    print("Tools by category:")
    for category, tools in sorted(categories.items()):
        print(f"  {category}: {len(tools)} tools")
        for tool_name in sorted(tools):
            print(f"    - {tool_name}")

    print()
    print("=" * 70)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
