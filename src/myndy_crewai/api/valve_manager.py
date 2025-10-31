"""
Enhanced Pipeline Valve Manager for OpenWebUI Integration

This module provides efficient management of OpenWebUI pipeline valves with
dynamic configuration, validation, and runtime updates.

File: api/valve_manager.py
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from datetime import datetime
from enum import Enum

logger = logging.getLogger("crewai.valve_manager")


class ValveType(Enum):
    """Types of valves supported"""
    BOOLEAN = "boolean"
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    SELECT = "select"
    MULTISELECT = "multiselect"
    PATH = "path"
    URL = "url"


@dataclass
class ValveSpec:
    """Specification for a pipeline valve"""
    name: str
    valve_type: ValveType
    default_value: Any
    title: str
    description: str
    required: bool = False
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    options: Optional[List[str]] = None
    pattern: Optional[str] = None
    validator: Optional[Callable] = None
    depends_on: Optional[str] = None
    category: str = "General"
    advanced: bool = False
    restart_required: bool = False
    
    def to_openwebui_spec(self) -> Dict[str, Any]:
        """Convert to OpenWebUI valve specification format"""
        spec = {
            "type": self.valve_type.value,
            "default": self.default_value,
            "title": self.title,
            "description": self.description
        }
        
        if self.min_value is not None:
            spec["minimum"] = self.min_value
        if self.max_value is not None:
            spec["maximum"] = self.max_value
        if self.options:
            spec["enum"] = self.options
        if self.pattern:
            spec["pattern"] = self.pattern
        if self.required:
            spec["required"] = True
        if self.advanced:
            spec["advanced"] = True
        
        return spec


@dataclass
class ValveCategory:
    """Category grouping for valves"""
    name: str
    title: str
    description: str
    icon: Optional[str] = None
    order: int = 0


class EnhancedValveManager:
    """Enhanced valve manager with dynamic configuration and validation"""
    
    def __init__(self, pipeline_id: str, config_path: Optional[Path] = None):
        """
        Initialize the enhanced valve manager
        
        Args:
            pipeline_id: Unique identifier for the pipeline
            config_path: Optional path to store valve configurations
        """
        self.pipeline_id = pipeline_id
        self.config_path = config_path or Path(f"./{pipeline_id}_valves.json")
        self.valves: Dict[str, ValveSpec] = {}
        self.categories: Dict[str, ValveCategory] = {}
        self.current_values: Dict[str, Any] = {}
        self.change_listeners: List[Callable] = []
        
        # Register default categories
        self._register_default_categories()
        
        # Register default valves
        self._register_default_valves()
        
        # Load saved configuration
        self.load_configuration()
        
        logger.info(f"🔧 Enhanced Valve Manager initialized for pipeline: {pipeline_id}")
    
    def _register_default_categories(self):
        """Register default valve categories"""
        categories = [
            ValveCategory("core", "Core Features", "Essential pipeline functionality", "⚙️", 1),
            ValveCategory("agents", "Agent Configuration", "Agent behavior and routing", "🤖", 2),
            ValveCategory("tools", "Tool Execution", "Tool and integration settings", "🛠️", 3),
            ValveCategory("memory", "Memory & Storage", "Memory and data management", "🧠", 4),
            ValveCategory("performance", "Performance", "Performance and optimization", "⚡", 5),
            ValveCategory("debug", "Debug & Logging", "Debugging and logging options", "🐛", 6),
            ValveCategory("advanced", "Advanced", "Advanced configuration options", "🔬", 7)
        ]
        
        for category in categories:
            self.categories[category.name] = category
    
    def _register_default_valves(self):
        """Register default pipeline valves"""
        valves = [
            # Core Features
            ValveSpec(
                name="enable_intelligent_routing",
                valve_type=ValveType.BOOLEAN,
                default_value=True,
                title="Enable Intelligent Routing",
                description="Use AI to automatically select the best agent for each request",
                category="core"
            ),
            
            ValveSpec(
                name="enable_shadow_agent",
                valve_type=ValveType.BOOLEAN,
                default_value=True,
                title="Enable Shadow Agent",
                description="Enable behavioral analysis and learning",
                category="core"
            ),
            
            # Agent Configuration
            ValveSpec(
                name="default_agent",
                valve_type=ValveType.SELECT,
                default_value="auto",
                title="Default Agent",
                description="Default agent when routing is disabled or fails",
                options=["auto", "personal_assistant", "memory_librarian", "research_specialist", "health_analyst", "finance_tracker"],
                category="agents"
            ),
            
            ValveSpec(
                name="routing_confidence_threshold",
                valve_type=ValveType.FLOAT,
                default_value=0.7,
                title="Routing Confidence Threshold",
                description="Minimum confidence required for automatic agent selection",
                min_value=0.0,
                max_value=1.0,
                category="agents",
                advanced=True
            ),
            
            ValveSpec(
                name="max_agent_iterations",
                valve_type=ValveType.INTEGER,
                default_value=25,
                title="Max Agent Iterations",
                description="Maximum iterations per agent execution",
                min_value=1,
                max_value=100,
                category="agents",
                advanced=True
            ),
            
            # Tool Execution
            ValveSpec(
                name="enable_tool_execution",
                valve_type=ValveType.BOOLEAN,
                default_value=True,
                title="Enable Tool Execution",
                description="Allow agents to execute tools and integrations",
                category="tools"
            ),
            
            ValveSpec(
                name="enable_contact_management",
                valve_type=ValveType.BOOLEAN,
                default_value=True,
                title="Enable Contact Management",
                description="Enable automatic contact and entity management",
                category="tools"
            ),
            
            ValveSpec(
                name="tool_timeout",
                valve_type=ValveType.INTEGER,
                default_value=30,
                title="Tool Execution Timeout",
                description="Maximum time (seconds) for tool execution",
                min_value=5,
                max_value=300,
                category="tools",
                advanced=True
            ),
            
            # Memory & Storage
            ValveSpec(
                name="enable_memory_search",
                valve_type=ValveType.BOOLEAN,
                default_value=True,
                title="Enable Memory Search",
                description="Enable searching across memory and knowledge collections",
                category="memory"
            ),
            
            ValveSpec(
                name="memory_persistence",
                valve_type=ValveType.SELECT,
                default_value="automatic",
                title="Memory Persistence",
                description="How to handle conversation memory",
                options=["automatic", "manual", "disabled"],
                category="memory"
            ),
            
            ValveSpec(
                name="myndy_api_url",
                valve_type=ValveType.URL,
                default_value="http://localhost:8000",
                title="Myndy API URL",
                description="Base URL for myndy-ai FastAPI server",
                category="memory",
                restart_required=True
            ),
            
            # Performance
            ValveSpec(
                name="enable_caching",
                valve_type=ValveType.BOOLEAN,
                default_value=True,
                title="Enable Response Caching",
                description="Cache responses for similar requests",
                category="performance"
            ),
            
            ValveSpec(
                name="max_concurrent_agents",
                valve_type=ValveType.INTEGER,
                default_value=3,
                title="Max Concurrent Agents",
                description="Maximum number of agents that can run simultaneously",
                min_value=1,
                max_value=10,
                category="performance",
                advanced=True
            ),
            
            # Debug & Logging
            ValveSpec(
                name="debug_mode",
                valve_type=ValveType.BOOLEAN,
                default_value=False,
                title="Debug Mode",
                description="Enable detailed logging and debugging information",
                category="debug"
            ),
            
            ValveSpec(
                name="log_level",
                valve_type=ValveType.SELECT,
                default_value="INFO",
                title="Log Level",
                description="Logging verbosity level",
                options=["DEBUG", "INFO", "WARNING", "ERROR"],
                category="debug",
                advanced=True
            ),
            
            ValveSpec(
                name="log_agent_decisions",
                valve_type=ValveType.BOOLEAN,
                default_value=False,
                title="Log Agent Decisions",
                description="Log detailed agent routing and decision information",
                category="debug",
                advanced=True
            ),
            
            ValveSpec(
                name="expose_logs_ui",
                valve_type=ValveType.BOOLEAN,
                default_value=True,
                title="Expose Logs in UI",
                description="Make agent execution logs available in OpenWebUI frontend",
                category="debug"
            ),
            
            ValveSpec(
                name="log_retention_hours",
                valve_type=ValveType.INTEGER,
                default_value=24,
                title="Log Retention (Hours)",
                description="How long to keep logs in memory/file for UI display",
                min_value=1,
                max_value=168,
                category="debug",
                advanced=True
            ),
            
            # Advanced
            ValveSpec(
                name="myndy_path",
                valve_type=ValveType.PATH,
                default_value="/Users/jeremy/myndy-ai",
                title="Myndy Installation Path",
                description="Path to the myndy-ai installation directory",
                category="advanced",
                restart_required=True
            ),
            
            ValveSpec(
                name="custom_model_config",
                valve_type=ValveType.STRING,
                default_value="",
                title="Custom Model Configuration",
                description="JSON configuration for custom models (advanced users only)",
                category="advanced",
                advanced=True
            )
        ]
        
        for valve in valves:
            self.register_valve(valve)
    
    def register_valve(self, valve: ValveSpec):
        """Register a new valve"""
        self.valves[valve.name] = valve
        if valve.name not in self.current_values:
            self.current_values[valve.name] = valve.default_value
        logger.debug(f"Registered valve: {valve.name}")
    
    def register_category(self, category: ValveCategory):
        """Register a new valve category"""
        self.categories[category.name] = category
        logger.debug(f"Registered category: {category.name}")
    
    def get_openwebui_spec(self) -> Dict[str, Any]:
        """Get OpenWebUI-compatible valve specification"""
        spec = {
            "type": "object",
            "properties": {},
            "categories": {}
        }
        
        # Add categories
        for cat_name, category in self.categories.items():
            spec["categories"][cat_name] = {
                "title": category.title,
                "description": category.description,
                "icon": category.icon,
                "order": category.order
            }
        
        # Add valve properties
        for valve_name, valve in self.valves.items():
            valve_spec = valve.to_openwebui_spec()
            valve_spec["category"] = valve.category
            spec["properties"][valve_name] = valve_spec
        
        return spec
    
    def get_current_values(self) -> Dict[str, Any]:
        """Get current valve values"""
        return self.current_values.copy()
    
    def update_values(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update valve values with validation"""
        validation_results = {}
        updated_values = {}
        restart_required = False
        
        for name, value in updates.items():
            if name not in self.valves:
                validation_results[name] = {"error": "Unknown valve"}
                continue
            
            valve = self.valves[name]
            
            # Validate the value
            validation_result = self._validate_value(valve, value)
            if validation_result["valid"]:
                old_value = self.current_values.get(name)
                self.current_values[name] = value
                updated_values[name] = value
                
                # Check if restart is required
                if valve.restart_required and old_value != value:
                    restart_required = True
                
                validation_results[name] = {"success": True}
                logger.info(f"🔧 Updated valve {name}: {old_value} → {value}")
            else:
                validation_results[name] = {"error": validation_result["error"]}
        
        # Save configuration if any values were updated
        if updated_values:
            self.save_configuration()
            
            # Notify listeners
            for listener in self.change_listeners:
                try:
                    listener(updated_values)
                except Exception as e:
                    logger.warning(f"Valve change listener error: {e}")
        
        result = {
            "updated": updated_values,
            "validation": validation_results,
            "restart_required": restart_required,
            "current_values": self.get_current_values()
        }
        
        return result
    
    def _validate_value(self, valve: ValveSpec, value: Any) -> Dict[str, Any]:
        """Validate a valve value"""
        try:
            # Type validation
            if valve.valve_type == ValveType.BOOLEAN:
                if not isinstance(value, bool):
                    return {"valid": False, "error": "Must be a boolean value"}
            
            elif valve.valve_type == ValveType.STRING:
                if not isinstance(value, str):
                    return {"valid": False, "error": "Must be a string value"}
                if valve.pattern and not re.match(valve.pattern, value):
                    return {"valid": False, "error": f"Must match pattern: {valve.pattern}"}
            
            elif valve.valve_type == ValveType.INTEGER:
                if not isinstance(value, int):
                    return {"valid": False, "error": "Must be an integer value"}
                if valve.min_value is not None and value < valve.min_value:
                    return {"valid": False, "error": f"Must be >= {valve.min_value}"}
                if valve.max_value is not None and value > valve.max_value:
                    return {"valid": False, "error": f"Must be <= {valve.max_value}"}
            
            elif valve.valve_type == ValveType.FLOAT:
                if not isinstance(value, (int, float)):
                    return {"valid": False, "error": "Must be a numeric value"}
                if valve.min_value is not None and value < valve.min_value:
                    return {"valid": False, "error": f"Must be >= {valve.min_value}"}
                if valve.max_value is not None and value > valve.max_value:
                    return {"valid": False, "error": f"Must be <= {valve.max_value}"}
            
            elif valve.valve_type == ValveType.SELECT:
                if valve.options and value not in valve.options:
                    return {"valid": False, "error": f"Must be one of: {', '.join(valve.options)}"}
            
            elif valve.valve_type == ValveType.PATH:
                if not isinstance(value, str):
                    return {"valid": False, "error": "Must be a string path"}
                # Optional: Check if path exists
                # if not Path(value).exists():
                #     return {"valid": False, "error": "Path does not exist"}
            
            elif valve.valve_type == ValveType.URL:
                if not isinstance(value, str):
                    return {"valid": False, "error": "Must be a string URL"}
                if not value.startswith(('http://', 'https://')):
                    return {"valid": False, "error": "Must be a valid URL (http:// or https://)"}
            
            # Custom validator
            if valve.validator:
                custom_result = valve.validator(value)
                if not custom_result.get("valid", True):
                    return custom_result
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def get_value(self, name: str, default: Any = None) -> Any:
        """Get a valve value with optional default"""
        return self.current_values.get(name, default)
    
    def is_enabled(self, name: str) -> bool:
        """Check if a boolean valve is enabled"""
        return bool(self.get_value(name, False))
    
    def add_change_listener(self, listener: Callable):
        """Add a listener for valve changes"""
        self.change_listeners.append(listener)
    
    def remove_change_listener(self, listener: Callable):
        """Remove a valve change listener"""
        if listener in self.change_listeners:
            self.change_listeners.remove(listener)
    
    def save_configuration(self):
        """Save current valve configuration to file"""
        try:
            config = {
                "pipeline_id": self.pipeline_id,
                "timestamp": datetime.utcnow().isoformat(),
                "values": self.current_values
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.debug(f"Valve configuration saved to {self.config_path}")
        except Exception as e:
            logger.warning(f"Failed to save valve configuration: {e}")
    
    def load_configuration(self):
        """Load valve configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                # Load saved values
                saved_values = config.get("values", {})
                for name, value in saved_values.items():
                    if name in self.valves:
                        self.current_values[name] = value
                
                logger.info(f"Valve configuration loaded from {self.config_path}")
            else:
                logger.info("No existing valve configuration found, using defaults")
        except Exception as e:
            logger.warning(f"Failed to load valve configuration: {e}")
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export complete configuration including specs and values"""
        return {
            "pipeline_id": self.pipeline_id,
            "timestamp": datetime.utcnow().isoformat(),
            "categories": {name: {
                "title": cat.title,
                "description": cat.description,
                "icon": cat.icon,
                "order": cat.order
            } for name, cat in self.categories.items()},
            "valves": {name: {
                "spec": valve.to_openwebui_spec(),
                "category": valve.category,
                "advanced": valve.advanced,
                "restart_required": valve.restart_required
            } for name, valve in self.valves.items()},
            "current_values": self.current_values
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the valve manager state"""
        enabled_features = [name for name, valve in self.valves.items() 
                          if valve.valve_type == ValveType.BOOLEAN and self.is_enabled(name)]
        
        return {
            "pipeline_id": self.pipeline_id,
            "total_valves": len(self.valves),
            "categories": len(self.categories),
            "enabled_features": enabled_features,
            "advanced_mode": self.is_enabled("debug_mode"),
            "configuration_file": str(self.config_path)
        }


# Factory function for easy integration
def create_valve_manager(pipeline_id: str, config_path: Optional[Path] = None) -> EnhancedValveManager:
    """Create an enhanced valve manager instance"""
    return EnhancedValveManager(pipeline_id, config_path)


if __name__ == "__main__":
    # Test the valve manager
    manager = create_valve_manager("test_pipeline")
    
    # Display summary
    summary = manager.get_summary()
    print("🔧 Valve Manager Summary:")
    print(json.dumps(summary, indent=2))
    
    # Test valve updates
    updates = {
        "enable_intelligent_routing": False,
        "debug_mode": True,
        "max_agent_iterations": 50
    }
    
    result = manager.update_values(updates)
    print("\n📊 Update Results:")
    print(json.dumps(result, indent=2))
    
    # Display OpenWebUI spec
    spec = manager.get_openwebui_spec()
    print("\n🌐 OpenWebUI Specification:")
    print(json.dumps(spec, indent=2))