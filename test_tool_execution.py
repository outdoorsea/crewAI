#!/usr/bin/env python3
"""
Test script for tool execution via MCP server

File: test_tool_execution.py
"""

import asyncio
import logging
import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from myndy_crewai_mcp.config import get_config
from myndy_crewai_mcp.tools_provider import ToolsProvider

# Enable INFO level logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_tool(provider: ToolsProvider, tool_name: str, arguments: dict):
    """Test executing a single tool"""
    print(f"\n{'=' * 70}")
    print(f"Testing tool: {tool_name}")
    print(f"Arguments: {json.dumps(arguments, indent=2)}")
    print("=" * 70)

    try:
        result = await provider.execute_tool(tool_name, arguments)
        print(f"\nResult:")
        print(result)
        print(f"\n✅ Tool {tool_name} executed successfully")
        return True
    except Exception as e:
        print(f"\n❌ Tool {tool_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Test tool execution with various tools"""
    print("=" * 70)
    print("  MCP Tool Execution Test")
    print("=" * 70)
    print()

    # Get configuration and initialize provider
    config = get_config()
    provider = ToolsProvider(config)
    await provider.initialize()

    print(f"\nInitialized with {provider.get_tool_count()} tools")
    print()

    # Test results tracking
    tests = []

    # Test 1: Get current time
    tests.append(
        await test_tool(
            provider,
            "get_current_time",
            {"timezone": "America/New_York"}
        )
    )

    # Test 2: Search memory (may return empty results)
    tests.append(
        await test_tool(
            provider,
            "search_memory",
            {"query": "test", "limit": 5}
        )
    )

    # Test 3: Get self profile
    tests.append(
        await test_tool(
            provider,
            "get_self_profile",
            {}
        )
    )

    # Test 4: Format date
    tests.append(
        await test_tool(
            provider,
            "format_date",
            {
                "timestamp": "2025-10-07T09:00:00",
                "format": "%B %d, %Y at %I:%M %p"
            }
        )
    )

    # Summary
    print("\n" + "=" * 70)
    print("  Test Summary")
    print("=" * 70)
    passed = sum(tests)
    total = len(tests)
    print(f"\nPassed: {passed}/{total} tests")

    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
