"""
Populate Myndy Registry with Tools from Tool Repository

This script loads all tools from the tool repository JSON files and registers them
with the myndy registry so they can be executed by CrewAI agents.

File: populate_registry.py
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add myndy to path
MYNDY_PATH = Path("/Users/jeremy/myndy")
sys.path.insert(0, str(MYNDY_PATH))

# Import registry
import importlib.util
registry_path = MYNDY_PATH / "agents" / "tools" / "registry.py"
spec = importlib.util.spec_from_file_location("myndy_registry", registry_path)
registry_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry_module)

from agents.tools.registry import ToolMetadata, ToolParameterSchema, ParameterType

logger = logging.getLogger(__name__)

def convert_openai_to_registry_schema(openai_schema: Dict[str, Any]) -> Dict[str, ToolParameterSchema]:
    """Convert OpenAI function schema to registry parameter schemas."""
    params = {}
    
    if "function" in openai_schema:
        function_def = openai_schema["function"]
        parameters = function_def.get("parameters", {})
        properties = parameters.get("properties", {})
        required_fields = set(parameters.get("required", []))
        
        for param_name, param_def in properties.items():
            param_type = param_def.get("type", "string")
            
            # Convert OpenAI types to our ParameterType enum
            type_mapping = {
                "string": ParameterType.STRING,
                "integer": ParameterType.INTEGER,
                "number": ParameterType.FLOAT,
                "boolean": ParameterType.BOOLEAN,
                "array": ParameterType.ARRAY,
                "object": ParameterType.OBJECT
            }
            
            registry_type = type_mapping.get(param_type, ParameterType.STRING)
            
            params[param_name] = ToolParameterSchema(
                name=param_name,
                type=registry_type,
                description=param_def.get("description", f"Parameter {param_name}"),
                required=param_name in required_fields,
                default=param_def.get("default"),
                enum=param_def.get("enum")
            )
    
    return params

def create_tool_function(tool_name: str, tool_schema: Dict[str, Any]):
    """Create a placeholder function for the tool."""
    def tool_function(**kwargs):
        """Placeholder tool function that returns schema info."""
        return {
            "tool_name": tool_name,
            "executed": True,
            "parameters": kwargs,
            "note": "This is a placeholder function. Actual implementation needed.",
            "schema": tool_schema
        }
    
    # Set function name for better debugging
    tool_function.__name__ = tool_name
    tool_function.__doc__ = f"Tool function for {tool_name}"
    
    return tool_function

def categorize_tool(tool_name: str, description: str) -> str:
    """Determine the appropriate category for a tool based on its name and description."""
    name_lower = tool_name.lower()
    desc_lower = description.lower()
    
    # Category mapping based on tool names and descriptions
    if any(keyword in name_lower for keyword in ["analyze", "sentiment", "text", "language", "detect"]):
        return "analysis"
    elif any(keyword in name_lower for keyword in ["document", "extract", "convert", "process", "search_document"]):
        return "document"
    elif any(keyword in name_lower for keyword in ["conversation", "extract_conversation", "infer_conversation"]):
        return "conversation"
    elif any(keyword in name_lower for keyword in ["health", "wellness", "fitness"]):
        return "health"
    elif any(keyword in name_lower for keyword in ["finance", "expense", "transaction", "spending", "budget"]):
        return "finance"
    elif any(keyword in name_lower for keyword in ["calendar", "time", "date", "schedule"]):
        return "calendar"
    elif any(keyword in name_lower for keyword in ["weather", "forecast", "temperature"]):
        return "weather"
    elif any(keyword in name_lower for keyword in ["format", "calculate", "unix"]):
        return "utility"
    else:
        return "general"

def populate_registry():
    """Populate the myndy registry with tools from tool repository."""
    tool_repo_path = MYNDY_PATH / "tool_repository"
    registry = registry_module.registry
    
    if not tool_repo_path.exists():
        logger.error(f"Tool repository not found: {tool_repo_path}")
        return False
    
    loaded_count = 0
    error_count = 0
    
    # Load all JSON tool files
    for tool_file in tool_repo_path.glob("*.json"):
        try:
            with open(tool_file, 'r', encoding='utf-8') as f:
                tool_schema = json.load(f)
            
            # Extract tool information
            tool_name = tool_schema.get('name')
            if not tool_name and 'function' in tool_schema:
                tool_name = tool_schema['function'].get('name')
            
            if not tool_name:
                logger.warning(f"No tool name found in {tool_file}")
                error_count += 1
                continue
            
            # Extract description
            description = ""
            if 'function' in tool_schema:
                description = tool_schema['function'].get('description', '')
            else:
                description = tool_schema.get('description', '')
            
            if not description:
                description = f"Tool for {tool_name}"
            
            # Convert parameters
            parameter_schemas = convert_openai_to_registry_schema(tool_schema)
            
            # Determine category
            category = categorize_tool(tool_name, description)
            
            # Create tool function
            tool_function = create_tool_function(tool_name, tool_schema)
            
            # Create metadata
            metadata = ToolMetadata(
                name=tool_name,
                description=description,
                parameters=parameter_schemas,
                category=category,
                tags=[category],
                function=tool_function,
                source="tool_repository",
                version="1.0.0"
            )
            
            # Register the tool
            registry.register(metadata)
            loaded_count += 1
            logger.info(f"Registered tool: {tool_name} (category: {category})")
            
        except Exception as e:
            logger.error(f"Failed to load tool from {tool_file}: {e}")
            error_count += 1
    
    logger.info(f"Registry population complete: {loaded_count} tools loaded, {error_count} errors")
    
    # Print summary
    print(f"✅ Successfully loaded {loaded_count} tools into myndy registry")
    if error_count > 0:
        print(f"❌ {error_count} tools failed to load")
    
    # Show categories
    categories = registry.get_all_categories()
    print(f"📂 Tool categories: {', '.join(sorted(categories))}")
    
    # Show tools per category
    for category in sorted(categories):
        tools_in_category = registry.get_tools_by_category(category)
        print(f"  {category}: {len(tools_in_category)} tools")
    
    return loaded_count > 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = populate_registry()
    sys.exit(0 if success else 1)