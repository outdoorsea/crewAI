"""
Register Conversation-Driven Update Tools with Myndy Registry

This script registers the conversation analyzer and auto updater tools
so they can be used by CrewAI agents for automatic status/profile updates.

File: register_conversation_tools.py
"""

import sys
import logging
from pathlib import Path

# Add paths
CREWAI_PATH = Path("/Users/jeremy/crewAI")
MYNDY_PATH = Path("/Users/jeremy/myndy")
sys.path.insert(0, str(CREWAI_PATH))
sys.path.insert(0, str(MYNDY_PATH))

# Import registry
import importlib.util
registry_path = MYNDY_PATH / "agents" / "tools" / "registry.py"
spec = importlib.util.spec_from_file_location("myndy_registry", registry_path)
registry_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry_module)

# Import conversation tools
sys.path.insert(0, str(CREWAI_PATH / "tools"))
from conversation_analyzer import analyze_message_for_updates
from auto_updater import (
    process_conversation_message, 
    get_conversation_update_summary,
    test_conversation_updates
)

logger = logging.getLogger(__name__)

def register_conversation_tools():
    """Register all conversation-driven update tools with the myndy registry."""
    registry = registry_module.registry
    
    # Conversation analysis tools
    conversation_tools = [
        (analyze_message_for_updates, "Analyze conversation message for status and profile updates", "conversation"),
        (process_conversation_message, "Process conversation message and automatically apply updates", "conversation"),
        (get_conversation_update_summary, "Get summary of conversation-driven updates for a user", "conversation"),
        (test_conversation_updates, "Test conversation update system with sample messages", "conversation"),
    ]
    
    registered_count = 0
    for tool_func, description, category in conversation_tools:
        try:
            registry.register_from_function(
                func=tool_func,
                description=description,
                category=category,
                tags=[category, "analysis", "automation", "updates"],
                source="conversation_tools",
                version="1.0.0"
            )
            registered_count += 1
            logger.info(f"Registered {tool_func.__name__} in category {category}")
        except Exception as e:
            logger.error(f"Failed to register {tool_func.__name__}: {e}")
    
    print(f"✅ Successfully registered {registered_count} conversation tools")
    
    # Show updated registry stats
    all_tools_in_registry = registry.get_all_tools()
    categories = registry.get_all_categories()
    print(f"📂 Total tools in registry: {len(all_tools_in_registry)}")
    print(f"📁 Categories: {', '.join(sorted(categories))}")
    
    # Show conversation tools specifically
    conversation_tools_in_registry = registry.get_tools_by_category("conversation")
    print(f"💬 Conversation tools: {len(conversation_tools_in_registry)}")
    for tool in conversation_tools_in_registry:
        print(f"  - {tool.name}: {tool.description}")
    
    return registered_count > 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = register_conversation_tools()
    sys.exit(0 if success else 1)