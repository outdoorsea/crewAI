#!/usr/bin/env python3
"""
Test script for prompts functionality via MCP server

File: test_prompts.py
"""

import asyncio
import logging
import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from myndy_crewai_mcp.config import get_config
from myndy_crewai_mcp.prompts_provider import PromptsProvider

# Enable INFO level logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_prompt(provider: PromptsProvider, name: str, arguments: dict = None):
    """Test retrieving a single prompt"""
    print(f"\n{'=' * 70}")
    print(f"Testing prompt: {name}")
    if arguments:
        print(f"Arguments: {json.dumps(arguments, indent=2)}")
    print("=" * 70)

    try:
        result = await provider.get_prompt(name, arguments)
        print(f"\nDescription: {result.description}")
        print(f"\nMessages ({len(result.messages)}):")
        for i, msg in enumerate(result.messages, 1):
            print(f"\n  Message {i} ({msg.role}):")
            content_preview = msg.content[:200] if len(msg.content) > 200 else msg.content
            print(f"    {content_preview}")
            if len(msg.content) > 200:
                print(f"    ... (truncated, total {len(msg.content)} chars)")

        print(f"\n✅ Prompt {name} retrieved successfully")
        return True
    except Exception as e:
        print(f"\n❌ Prompt {name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Test prompts with various agent workflows"""
    print("=" * 70)
    print("  MCP Prompts Test")
    print("=" * 70)
    print()

    # Get configuration and initialize provider
    config = get_config()
    provider = PromptsProvider(config)
    await provider.initialize()

    print(f"\nInitialized with {provider.get_prompt_count()} prompts")
    print()

    # Display available prompts by category
    print("Available Prompts by Category:")
    categories = provider.get_prompts_by_category()
    for category, prompts in categories.items():
        print(f"\n  {category} ({len(prompts)} prompts):")
        for prompt_name in prompts:
            prompt_def = provider.get_prompt_by_name(prompt_name)
            if prompt_def:
                print(f"    - {prompt_name}: {prompt_def.description}")
    print()

    # Test results tracking
    tests = []

    # Test 1: Personal Assistant (basic)
    tests.append(
        await test_prompt(
            provider,
            "personal_assistant",
            {"task": "Check my schedule for today"}
        )
    )

    # Test 2: Schedule Management
    tests.append(
        await test_prompt(
            provider,
            "schedule_management",
            {"action": "view", "date": "tomorrow"}
        )
    )

    # Test 3: Memory Search
    tests.append(
        await test_prompt(
            provider,
            "memory_search",
            {"query": "people I met last week", "limit": "5"}
        )
    )

    # Test 4: Research Specialist
    tests.append(
        await test_prompt(
            provider,
            "research_specialist",
            {"topic": "artificial intelligence trends", "depth": "thorough"}
        )
    )

    # Test 5: Health Analyst
    tests.append(
        await test_prompt(
            provider,
            "health_metrics",
            {"metric_type": "sleep", "time_range": "week"}
        )
    )

    # Test 6: Finance Tracker
    tests.append(
        await test_prompt(
            provider,
            "expense_tracking",
            {"action": "analyze", "time_range": "month"}
        )
    )

    # Test 7: Conversation Analysis
    tests.append(
        await test_prompt(
            provider,
            "conversation_analysis",
            {"text": "I met John at the coffee shop yesterday. We discussed the new AI project."}
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
