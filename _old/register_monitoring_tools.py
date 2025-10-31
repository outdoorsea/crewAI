"""
Register Status and Profile Monitoring Tools with Myndy Registry

This script registers the status and profile monitoring tools so they can be used by CrewAI agents.

File: register_monitoring_tools.py
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

# Import monitoring tools
sys.path.insert(0, str(CREWAI_PATH / "tools"))
from status_monitoring_tool import (
    get_current_status, update_user_status, update_mood_status,
    add_user_attribute, get_status_summary
)
from profile_monitoring_tool import (
    get_user_profile, update_user_basic_info, add_user_preference,
    add_user_goal, add_important_person, update_user_values, get_profile_summary
)

logger = logging.getLogger(__name__)

def register_monitoring_tools():
    """Register all monitoring tools with the myndy registry."""
    registry = registry_module.registry
    
    # Status monitoring tools
    status_tools = [
        (get_current_status, "Get user's current status including mood, activity, and health", "status"),
        (update_user_status, "Update user's status with mood, activity, and stress information", "status"),
        (update_mood_status, "Update user's mood and stress level", "status"),
        (add_user_attribute, "Add status attributes like 'hungry', 'tired', 'busy'", "status"),
        (get_status_summary, "Get summary of user's current status for agent context", "status"),
    ]
    
    # Profile monitoring tools
    profile_tools = [
        (get_user_profile, "Get complete user profile including preferences and goals", "profile"),
        (update_user_basic_info, "Update basic user information like name and biography", "profile"),
        (add_user_preference, "Add user preference in a specific category", "profile"),
        (add_user_goal, "Add user goal with title, description, and category", "profile"),
        (add_important_person, "Add important person to user's profile", "profile"),
        (update_user_values, "Update user's core values", "profile"),
        (get_profile_summary, "Get summary of user's profile for agent context", "profile"),
    ]
    
    all_tools = status_tools + profile_tools
    
    registered_count = 0
    for tool_func, description, category in all_tools:
        try:
            registry.register_from_function(
                func=tool_func,
                description=description,
                category=category,
                tags=[category, "monitoring", "user"],
                source="monitoring_tools",
                version="1.0.0"
            )
            registered_count += 1
            logger.info(f"Registered {tool_func.__name__} in category {category}")
        except Exception as e:
            logger.error(f"Failed to register {tool_func.__name__}: {e}")
    
    print(f"✅ Successfully registered {registered_count} monitoring tools")
    print(f"📊 Status tools: {len(status_tools)}")
    print(f"👤 Profile tools: {len(profile_tools)}")
    
    # Show updated registry stats
    all_tools_in_registry = registry.get_all_tools()
    categories = registry.get_all_categories()
    print(f"📂 Total tools in registry: {len(all_tools_in_registry)}")
    print(f"📁 Categories: {', '.join(sorted(categories))}")
    
    return registered_count > 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = register_monitoring_tools()
    sys.exit(0 if success else 1)