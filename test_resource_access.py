#!/usr/bin/env python3
"""
Test script for resource access via MCP server

File: test_resource_access.py
"""

import asyncio
import logging
import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from myndy_crewai_mcp.config import get_config
from myndy_crewai_mcp.resources_provider import ResourcesProvider

# Enable INFO level logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_resource(provider: ResourcesProvider, uri: str):
    """Test reading a single resource"""
    print(f"\n{'=' * 70}")
    print(f"Testing resource: {uri}")
    print("=" * 70)

    try:
        content = await provider.read_resource(uri)
        print(f"\nURI: {content.uri}")
        print(f"MIME Type: {content.mimeType}")
        print(f"\nContent:")

        # Parse and pretty-print JSON content
        if content.text:
            try:
                data = json.loads(content.text)
                print(json.dumps(data, indent=2)[:500])  # Limit output
                if len(content.text) > 500:
                    print(f"\n... (truncated, total {len(content.text)} chars)")
            except json.JSONDecodeError:
                print(content.text[:500])
                if len(content.text) > 500:
                    print(f"\n... (truncated)")

        print(f"\n✅ Resource {uri} read successfully")
        return True
    except Exception as e:
        print(f"\n❌ Resource {uri} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Test resource access with various resources"""
    print("=" * 70)
    print("  MCP Resource Access Test")
    print("=" * 70)
    print()

    # Get configuration and initialize provider
    config = get_config()
    provider = ResourcesProvider(config)
    await provider.initialize()

    print(f"\nInitialized with {provider.get_resource_count()} resources")
    print(f"Initialized with {provider.get_template_count()} resource templates")
    print()

    # Display available resources
    print("Available Resources:")
    for resource in provider.get_resource_definitions():
        print(f"  - {resource.uri}: {resource.name}")
    print()

    print("Available Resource Templates:")
    for template in provider.get_resource_templates():
        print(f"  - {template.uriTemplate}: {template.name}")
    print()

    # Test results tracking
    tests = []

    # Test 1: Self profile
    tests.append(
        await test_resource(
            provider,
            "myndy://profile/self"
        )
    )

    # Test 2: Memory entities
    tests.append(
        await test_resource(
            provider,
            "myndy://memory/entities"
        )
    )

    # Test 3: Short-term memory
    tests.append(
        await test_resource(
            provider,
            "myndy://memory/short-term"
        )
    )

    # Test 4: Health status
    tests.append(
        await test_resource(
            provider,
            "myndy://health/status"
        )
    )

    # Test 5: Profile goals
    tests.append(
        await test_resource(
            provider,
            "myndy://profile/goals"
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
