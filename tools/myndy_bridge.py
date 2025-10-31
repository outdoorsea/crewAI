"""
Myndy-CrewAI Tool Bridge (Architecture Compliant)

HTTP-only tool bridge that follows FastAPI service-oriented architecture.
All direct imports removed in compliance with architectural requirements.

File: tools/myndy_bridge_fixed.py
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from langchain.tools import BaseTool, tool
except ImportError:
    from langchain_core.tools import BaseTool, tool

from pydantic import BaseModel, Field

# Import the new async HTTP client and caching system
from .async_http_client import AsyncHTTPClient, async_post, async_get, get_http_metrics, get_http_client
from .tool_cache import (
    get_tool_cache, ToolResultCache, cached_tool, async_cached_tool, 
    CacheManager, configure_tool_cache
)

# Configure logging
logger = logging.getLogger(__name__)

# HTTP API client for myndy-ai backend (architecture compliant + performance optimized)
class MyndyToolAPIClient:
    """Async HTTP client for myndy-ai tool execution API endpoints with connection pooling"""
    
    def __init__(self, base_url: str = None):
        # Use environment configuration for base URL
        if base_url is None:
            try:
                from ..config.env_config import env_config
                base_url = env_config.myndy_api_base_url
            except ImportError:
                import os
                base_url = os.getenv("CREWAI_MYNDY_API_URL", "http://localhost:8081")
        self.base_url = base_url
        self.http_client = AsyncHTTPClient(base_url)
        logger.info("🚀 Initialized optimized MyndyToolAPIClient with connection pooling")
    
    def _run_async(self, coro):
        """Helper to run async functions in sync context"""
        try:
            # Always use asyncio.run for better isolation
            return asyncio.run(coro)
        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e):
                # We're in an existing event loop, use thread executor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result(timeout=15)
            else:
                # Try getting existing loop
                try:
                    loop = asyncio.get_event_loop()
                    if not loop.is_running():
                        return loop.run_until_complete(coro)
                    else:
                        # Fallback to thread executor
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, coro)
                            return future.result(timeout=15)
                except:
                    # Last resort fallback
                    logger.warning("Could not run async operation, using fallback")
                    return {"error": "Async operation failed", "fallback_used": True}
    
    async def _make_request_async(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make async HTTP request to myndy-ai API"""
        try:
            if method.upper() == "POST":
                result = await self.http_client.post(endpoint, data or {})
            else:  # GET
                result = await self.http_client.get(endpoint, params)
            
            return result
            
        except Exception as e:
            logger.warning(f"Async API request error: {e}")
            return {"error": f"API request error: {e}", "fallback_used": True}
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict]:
        """Execute a tool via myndy-ai API (sync wrapper for async call)"""
        return self._run_async(
            self._make_request_async("POST", "/api/v1/tools/execute", {
                "tool_name": tool_name,
                "parameters": parameters
            })
        )
    
    async def execute_tool_async(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict]:
        """Execute a tool via myndy-ai API (pure async)"""
        return await self._make_request_async("POST", "/api/v1/tools/execute", {
            "tool_name": tool_name,
            "parameters": parameters
        })
    
    def list_tools(self, category: Optional[str] = None) -> Optional[Dict]:
        """List available tools via API (sync wrapper)"""
        params = {"category": category} if category else {}
        return self._run_async(
            self._make_request_async("GET", "/api/v1/tools/list", params=params)
        )
    
    async def list_tools_async(self, category: Optional[str] = None) -> Optional[Dict]:
        """List available tools via API (pure async)"""
        params = {"category": category} if category else {}
        return await self._make_request_async("GET", "/api/v1/tools/list", params=params)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get HTTP client performance metrics"""
        return get_http_metrics()
    
    async def health_check_async(self) -> Dict[str, Any]:
        """Check API health asynchronously"""
        return await self.http_client.health_check()

# Initialize API client
tool_api_client = MyndyToolAPIClient()

# HTTP-based tool registry (architecture compliant + performance optimized)
class HTTPToolRegistry:
    """HTTP-based tool registry that calls myndy-ai APIs with async support"""
    
    def __init__(self):
        self.api_client = tool_api_client
        self._local_fallbacks = {}
        self._execution_stats = {
            "api_calls": 0,
            "fallback_calls": 0,
            "errors": 0,
            "total_execution_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Initialize caching system
        self.cache = get_tool_cache()
        logger.info("🔧 Tool registry initialized with caching system")
    
    def register_from_function(self, func, name: str, description: str, category: str = "general"):
        """Register local fallback function"""
        self._local_fallbacks[name] = {
            "function": func,
            "description": description,
            "category": category
        }
        logger.debug(f"Registered local fallback for {name}")
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute tool via API with local fallback and caching (sync)"""
        import time
        start_time = time.time()
        
        try:
            # Check cache first
            cached_result = self.cache.get(tool_name, kwargs)
            if cached_result is not None:
                self._execution_stats["cache_hits"] += 1
                execution_time = time.time() - start_time
                self._execution_stats["total_execution_time"] += execution_time
                logger.debug(f"⚡ Cache hit for {tool_name} in {execution_time:.3f}s")
                return cached_result
            
            self._execution_stats["cache_misses"] += 1
            
            # Try API first
            self._execution_stats["api_calls"] += 1
            result = self.api_client.execute_tool(tool_name, kwargs)
            
            if result and "error" not in result:
                execution_time = time.time() - start_time
                self._execution_stats["total_execution_time"] += execution_time
                
                # Cache successful result
                self.cache.set(tool_name, kwargs, result)
                
                logger.debug(f"✅ Tool {tool_name} executed via API and cached in {execution_time:.3f}s")
                return result
            
            # Fallback to local implementation if available
            if tool_name in self._local_fallbacks:
                logger.info(f"🔄 Using local fallback for tool: {tool_name}")
                self._execution_stats["fallback_calls"] += 1
                try:
                    result = self._local_fallbacks[tool_name]["function"](**kwargs)
                    execution_time = time.time() - start_time
                    self._execution_stats["total_execution_time"] += execution_time
                    
                    # Cache fallback result too
                    self.cache.set(tool_name, kwargs, result)
                    
                    return result
                except Exception as e:
                    logger.error(f"❌ Local fallback failed for {tool_name}: {e}")
                    self._execution_stats["errors"] += 1
                    return {"error": str(e), "fallback_failed": True}
            
            self._execution_stats["errors"] += 1
            return {"error": f"Tool {tool_name} not available via API or local fallback"}
            
        except Exception as e:
            self._execution_stats["errors"] += 1
            logger.error(f"💥 Tool execution failed for {tool_name}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def execute_tool_async(self, tool_name: str, **kwargs) -> Any:
        """Execute tool via API with local fallback and caching (async)"""
        import time
        start_time = time.time()
        
        try:
            # Check cache first
            cached_result = self.cache.get(tool_name, kwargs)
            if cached_result is not None:
                self._execution_stats["cache_hits"] += 1
                execution_time = time.time() - start_time
                self._execution_stats["total_execution_time"] += execution_time
                logger.debug(f"⚡ Async cache hit for {tool_name} in {execution_time:.3f}s")
                return cached_result
            
            self._execution_stats["cache_misses"] += 1
            
            # Try API first
            self._execution_stats["api_calls"] += 1
            result = await self.api_client.execute_tool_async(tool_name, kwargs)
            
            if result and "error" not in result:
                execution_time = time.time() - start_time
                self._execution_stats["total_execution_time"] += execution_time
                
                # Cache successful result
                self.cache.set(tool_name, kwargs, result)
                
                logger.debug(f"✅ Tool {tool_name} executed via async API and cached in {execution_time:.3f}s")
                return result
            
            # Fallback to local implementation if available
            if tool_name in self._local_fallbacks:
                logger.info(f"🔄 Using local fallback for tool: {tool_name}")
                self._execution_stats["fallback_calls"] += 1
                try:
                    result = self._local_fallbacks[tool_name]["function"](**kwargs)
                    execution_time = time.time() - start_time
                    self._execution_stats["total_execution_time"] += execution_time
                    
                    # Cache fallback result too
                    self.cache.set(tool_name, kwargs, result)
                    
                    return result
                except Exception as e:
                    logger.error(f"❌ Local fallback failed for {tool_name}: {e}")
                    self._execution_stats["errors"] += 1
                    return {"error": str(e), "fallback_failed": True}
            
            self._execution_stats["errors"] += 1
            return {"error": f"Tool {tool_name} not available via API or local fallback"}
            
        except Exception as e:
            self._execution_stats["errors"] += 1
            logger.error(f"💥 Async tool execution failed for {tool_name}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get tool registry performance statistics with caching metrics"""
        total_calls = self._execution_stats["api_calls"] + self._execution_stats["fallback_calls"]
        total_requests = total_calls + self._execution_stats["cache_hits"]
        avg_time = (self._execution_stats["total_execution_time"] / total_calls) if total_calls > 0 else 0
        
        # Get cache statistics
        cache_stats = self.cache.get_stats()
        
        return {
            "execution_stats": {
                **self._execution_stats,
                "total_calls": total_calls,
                "total_requests": total_requests,
                "average_execution_time": round(avg_time, 3),
                "api_success_rate": round((self._execution_stats["api_calls"] / total_calls * 100) if total_calls > 0 else 0, 2),
                "error_rate": round((self._execution_stats["errors"] / total_calls * 100) if total_calls > 0 else 0, 2),
                "registered_fallbacks": len(self._local_fallbacks)
            },
            "cache_performance": {
                "cache_hit_rate": round((self._execution_stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0, 2),
                "cache_efficiency": round((self._execution_stats["cache_hits"] / (self._execution_stats["cache_hits"] + self._execution_stats["cache_misses"]) * 100) if (self._execution_stats["cache_hits"] + self._execution_stats["cache_misses"]) > 0 else 0, 2),
                "detailed_cache_stats": cache_stats
            }
        }

# Initialize HTTP-based registry
myndy_registry = HTTPToolRegistry()

# Local fallback implementations for essential tools
def extract_conversation_entities_fallback(conversation_text: str = "", **kwargs):
    """Local fallback for entity extraction"""
    import re
    from datetime import datetime
    
    # Handle different parameter formats
    if isinstance(conversation_text, dict):
        # If first parameter is a dict, extract text from it
        text = conversation_text.get("conversation_text", "") or conversation_text.get("text", "") or str(conversation_text)
    else:
        text = str(conversation_text) if conversation_text else ""
    
    # Fallback to kwargs if no text found
    if not text:
        text = kwargs.get("user_message", "") or kwargs.get("message", "") or kwargs.get("text", "")
    
    entities = []
    
    # Simple patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)?[0-9]{3}[-.\s]?[0-9]{4}\b'
    
    for match in re.finditer(email_pattern, text, re.IGNORECASE):
        entities.append({
            'text': match.group(),
            'type': 'email',
            'confidence': 0.9
        })
    
    for match in re.finditer(phone_pattern, text):
        entities.append({
            'text': match.group(),
            'type': 'phone',
            'confidence': 0.9
        })
    
    return {
        'entities_found': len(entities),
        'entities': entities,
        'processed_at': datetime.now().isoformat()
    }

def analyze_conversation_fallback(conversation_text: str = "", **kwargs):
    """Local fallback for conversation analysis"""
    from datetime import datetime
    
    # Handle different parameter formats
    if isinstance(conversation_text, dict):
        # If first parameter is a dict, extract text from it
        text = conversation_text.get("conversation_text", "") or conversation_text.get("text", "") or str(conversation_text)
    else:
        text = str(conversation_text) if conversation_text else ""
    
    # Fallback to kwargs if no text found
    if not text:
        text = kwargs.get("user_message", "") or kwargs.get("message", "") or kwargs.get("text", "")
    
    return {
        "analysis": f"Analyzed {len(text)} characters (fallback)",
        "intent": "unknown",
        "entities": [],
        "processed_at": datetime.now().isoformat()
    }

# Register essential fallback tools
myndy_registry.register_from_function(
    extract_conversation_entities_fallback,
    name="extract_conversation_entities",
    description="Extract entities from conversation history",
    category="conversation"
)

myndy_registry.register_from_function(
    analyze_conversation_fallback,
    name="analyze_conversation_for_updates",
    description="Analyze conversation for updates",
    category="conversation"
)

logger.info("HTTP-based tool bridge initialized with architecture compliance")

# Import SpaCy tools
try:
    from .spacy_entity_extraction import (
        extract_entities_with_spacy,
        extract_and_categorize_entities,
        extract_and_store_entities
    )
    SPACY_TOOLS_AVAILABLE = True
    logger.info("✅ SpaCy entity extraction tools loaded successfully")
except ImportError as e:
    SPACY_TOOLS_AVAILABLE = False
    logger.warning(f"⚠️ SpaCy tools not available: {e}")

# Tool creation functions for CrewAI integration
@tool
@cached_tool(ttl=60, use_cache=True)  # Cache time results for 1 minute
def get_current_time(timezone: str = "UTC") -> str:
    """Get current time in specified timezone.
    
    Use this tool when users ask:
    - "What time is it?"
    - "What's the current time?"
    - Time-related questions
    
    Parameters:
    - timezone: timezone name (e.g., "UTC", "US/Eastern", "Europe/London")
    
    Always use this tool for time queries instead of guessing."""
    try:
        # Try API first
        result = myndy_registry.execute_tool("get_current_time", timezone=timezone)
        if result and "error" not in result:
            return json.dumps(result, indent=2)
    except Exception as e:
        logger.debug(f"API call failed: {e}")
    
    # Fallback to local implementation
    from datetime import datetime
    import pytz
    
    try:
        if timezone.upper() == "UTC":
            current_time = datetime.utcnow()
            tz_name = "UTC"
        else:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            tz_name = timezone
    except:
        # Default to local time if timezone is invalid
        current_time = datetime.now()
        tz_name = "Local"
    
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return f"Current time in {tz_name}: {formatted_time}"

@tool
@cached_tool(ttl=300, use_cache=True)  # Cache entity extraction for 5 minutes
def extract_conversation_entities(conversation_text: str = "") -> str:
    """Extract entities (people, places, emails, phone numbers) from conversation text"""
    try:
        # Try API first
        result = myndy_registry.execute_tool("extract_conversation_entities", conversation_text=conversation_text)
        if result and "error" not in result:
            return json.dumps(result, indent=2)
    except Exception as e:
        logger.debug(f"API call failed: {e}")
    
    # Use local fallback
    result = extract_conversation_entities_fallback(conversation_text=conversation_text)
    return json.dumps(result, indent=2)

@tool
@cached_tool(ttl=300, use_cache=True)  # Cache conversation analysis for 5 minutes
def analyze_conversation_for_updates(conversation_text: str = "") -> str:
    """Analyze conversation text to identify important information that should be remembered"""
    try:
        # Try API first  
        result = myndy_registry.execute_tool("analyze_conversation_for_updates", conversation_text=conversation_text)
        if result and "error" not in result:
            return json.dumps(result, indent=2)
    except Exception as e:
        logger.debug(f"API call failed: {e}")
    
    # Use local fallback
    result = analyze_conversation_fallback(conversation_text=conversation_text)
    return json.dumps(result, indent=2)

@tool
@cached_tool(ttl=3600, use_cache=True)  # Cache exercise recommendations for 1 hour
def get_exercise_recommendations(condition: str = "general fitness") -> str:
    """Get exercise recommendations for specific health conditions or fitness goals.
    
    Use this tool when users ask about:
    - Exercise for specific conditions (back pain, stress, sleep)
    - Workout recommendations
    - Fitness advice
    - "What exercises should I do for [condition]?"
    
    Parameters:
    - condition: health condition or goal (e.g., "back pain", "stress relief", "sleep", "general fitness")
    
    ALWAYS use this tool for exercise-related questions instead of giving general advice."""
    
    exercise_db = {
        "back pain": [
            "Cat-Cow stretches (5-10 reps)",
            "Child's pose (hold 30 seconds)",
            "Knee-to-chest stretches (10 reps each leg)",
            "Pelvic tilts (10-15 reps)",
            "Bird dog exercise (10 reps each side)"
        ],
        "stress relief": [
            "Deep breathing exercises (5-10 minutes)",
            "Gentle yoga flow (20-30 minutes)",
            "Walking meditation (15-20 minutes)",
            "Progressive muscle relaxation",
            "Tai chi movements"
        ],
        "sleep": [
            "Light stretching before bed",
            "Avoid intense exercise 3-4 hours before sleep",
            "Morning sunlight exposure (10-15 minutes)",
            "Consistent sleep schedule",
            "Bedroom temperature 65-68°F (18-20°C)"
        ],
        "general fitness": [
            "30 minutes moderate cardio 5x/week",
            "Strength training 2-3x/week",
            "Flexibility/stretching daily",
            "10,000 steps per day target",
            "Mix of aerobic and resistance exercises"
        ]
    }
    
    condition_lower = condition.lower()
    for key in exercise_db:
        if key in condition_lower:
            recommendations = exercise_db[key]
            return f"Exercise recommendations for {condition}:\n\n" + "\n".join([f"• {rec}" for rec in recommendations])
    
    # Default to general fitness
    recommendations = exercise_db["general fitness"]
    return f"General exercise recommendations:\n\n" + "\n".join([f"• {rec}" for rec in recommendations])

@tool
@cached_tool(ttl=1800, use_cache=True)  # Cache BMI calculations for 30 minutes
def calculate_bmi(weight_kg: float, height_cm: float) -> str:
    """Calculate Body Mass Index (BMI) given weight in kg and height in cm.
    
    Use this tool when users:
    - Ask to calculate their BMI
    - Provide height and weight measurements
    - Want to know their BMI category
    - Ask "What's my BMI if I'm [height] and weigh [weight]?"
    
    Parameters:
    - weight_kg: weight in kilograms (convert lbs to kg if needed: lbs ÷ 2.205)
    - height_cm: height in centimeters (convert feet/inches: ft*30.48 + in*2.54)
    
    ALWAYS use this tool when users provide height and weight data."""
    try:
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
        
        return f"BMI: {bmi:.1f} - Category: {category}\n\nBMI Categories:\n• Underweight: <18.5\n• Normal: 18.5-24.9\n• Overweight: 25-29.9\n• Obese: ≥30"
    
    except Exception as e:
        return f"Error calculating BMI: {e}. Please provide weight in kg and height in cm."

# Agent tool mapping (simplified for architecture compliance)
AGENT_TOOL_MAPPING = {
    "personal_assistant": [
        get_current_time,
        extract_conversation_entities,
    ],
    "shadow_agent": [
        extract_conversation_entities,
        analyze_conversation_for_updates,
    ] + ([extract_entities_with_spacy, extract_and_categorize_entities] if SPACY_TOOLS_AVAILABLE else []),
    "memory_librarian": [
        extract_conversation_entities,
        analyze_conversation_for_updates,
    ] + ([extract_and_categorize_entities, extract_and_store_entities] if SPACY_TOOLS_AVAILABLE else []),
    "research_specialist": [
        analyze_conversation_for_updates,
        extract_conversation_entities,
    ] + ([extract_entities_with_spacy] if SPACY_TOOLS_AVAILABLE else []),
    "health_analyst": [
        get_current_time,
        get_exercise_recommendations,
        calculate_bmi,
    ],
    "finance_tracker": [
        get_current_time,
        analyze_conversation_for_updates,
    ]
}

def get_agent_tools(agent_role: str) -> List:
    """Get tools for specific agent role (HTTP-based)"""
    try:
        tools = AGENT_TOOL_MAPPING.get(agent_role, [])
        logger.info(f"Loaded {len(tools)} HTTP-based tools for agent role: {agent_role}")
        return tools
    except Exception as e:
        logger.error(f"Error loading tools for agent {agent_role}: {e}")
        return []

def get_tool_documentation() -> Dict[str, Any]:
    """Get documentation for all available tools"""
    tool_docs = {}
    
    for agent_role, tools in AGENT_TOOL_MAPPING.items():
        tool_docs[agent_role] = []
        for tool in tools:
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "parameters": getattr(tool, 'args_schema', {})
            }
            tool_docs[agent_role].append(tool_info)
    
    return {
        "total_agents": len(AGENT_TOOL_MAPPING),
        "tools_by_agent": tool_docs,
        "all_tools": {
            "get_current_time": {
                "description": "Get current time in any timezone",
                "usage": "Use for time-related questions",
                "example": "What time is it?"
            },
            "get_exercise_recommendations": {
                "description": "Get exercise recommendations for health conditions",
                "usage": "Use for exercise/fitness questions",
                "example": "What exercises for back pain?"
            },
            "calculate_bmi": {
                "description": "Calculate BMI from height and weight",
                "usage": "Use when users provide height/weight",
                "example": "BMI for 70kg, 175cm?"
            }
        }
    }

# Tool loader class for compatibility
class MyndyToolLoader:
    """HTTP-based tool loader for CrewAI integration"""
    
    def __init__(self):
        self.api_client = tool_api_client
        self._tool_schemas = {}
        self._load_tool_schemas()
    
    def _load_tool_schemas(self):
        """Load tool schemas from API"""
        try:
            result = self.api_client.list_tools()
            if result and "tools" in result:
                for tool_data in result["tools"]:
                    self._tool_schemas[tool_data["name"]] = tool_data
            logger.info(f"Loaded {len(self._tool_schemas)} tool schemas from API")
        except Exception as e:
            logger.warning(f"Could not load tool schemas from API: {e}")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about available tools"""
        return {
            "total_tools": len(self._tool_schemas),
            "registry_available": True,
            "categories": ["conversation", "status", "general"],
            "tools_by_category": {
                "conversation": {"count": 2},
                "status": {"count": 0},
                "general": {"count": 1}
            }
        }
    
    def create_crewai_tool(self, tool_name: str):
        """Create a CrewAI-compatible tool"""
        if tool_name in ["get_current_time", "extract_conversation_entities", "analyze_conversation_for_updates"]:
            return globals()[tool_name]
        return None
    
    def get_tools_for_agent(self, agent_role: str) -> List:
        """Get tools for agent role"""
        return get_agent_tools(agent_role)

# Tool bridge class for agent integration
class MyndyToolBridge:
    """HTTP-based tool bridge for CrewAI agent integration"""
    
    def __init__(self):
        self.tool_loader = MyndyToolLoader()
    
    def get_tools_for_agent(self, agent_role: str) -> List:
        """Get tools for specific agent role"""
        return self.tool_loader.get_tools_for_agent(agent_role)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return self.tool_loader.get_tool_info()

# Compatibility functions for API imports
def get_tool_loader():
    """Get the tool loader instance"""
    return MyndyToolLoader()

def load_myndy_tools_for_agent(agent_role: str):
    """Load tools for agent (compatibility function)"""
    return get_agent_tools(agent_role)

# Performance monitoring functions
def get_bridge_performance_metrics() -> Dict[str, Any]:
    """Get comprehensive performance metrics for the tool bridge"""
    http_metrics = get_http_metrics()
    registry_stats = myndy_registry.get_performance_stats()
    cache_health = CacheManager.get_cache_health()
    
    return {
        "system": {
            "architecture": "HTTP-only (FastAPI compliant)",
            "connection_pooling": "Enabled",
            "async_support": "Enabled",
            "caching_system": "Enabled",
            "optimizations": [
                "HTTP connection pooling",
                "Tool result caching with TTL/LRU",
                "Async request handling",
                "Performance metrics tracking"
            ]
        },
        "http_client": http_metrics,
        "tool_registry": registry_stats,
        "cache_system": cache_health,
        "overall_health": {
            "status": "healthy" if (
                http_metrics.get("success_rate", 0) > 80 and 
                cache_health.get("status") in ["healthy", "degraded"]
            ) else "degraded",
            "total_requests": http_metrics.get("total_requests", 0),
            "total_tool_executions": registry_stats.get("execution_stats", {}).get("total_calls", 0),
            "cache_hit_rate": registry_stats.get("cache_performance", {}).get("cache_hit_rate", 0),
            "average_response_time": http_metrics.get("average_response_time", 0),
            "connection_pool_utilization": "active",
            "performance_improvements": {
                "cached_requests": registry_stats.get("execution_stats", {}).get("cache_hits", 0),
                "time_saved_estimate": "Calculated based on cache hits and average execution time"
            }
        }
    }

async def health_check_bridge() -> Dict[str, Any]:
    """Perform comprehensive health check of the bridge"""
    try:
        # Check API connectivity
        health_result = await tool_api_client.health_check_async()
        
        # Get performance metrics
        metrics = get_bridge_performance_metrics()
        
        return {
            "status": "healthy",
            "api_connectivity": health_result.get("status", "unknown"),
            "performance_metrics": metrics,
            "optimizations_active": [
                "HTTP connection pooling",
                "Async request handling", 
                "Performance metrics tracking",
                "Graceful error handling",
                "Local fallback mechanisms"
            ]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "fallback_available": True
        }

def reset_performance_metrics():
    """Reset all performance metrics"""
    myndy_registry._execution_stats = {
        "api_calls": 0,
        "fallback_calls": 0,
        "errors": 0,
        "total_execution_time": 0.0,
        "cache_hits": 0,
        "cache_misses": 0
    }
    
    # Reset HTTP client metrics (if available)
    try:
        client = get_http_client()
        client.reset_metrics()
        logger.info("🔄 HTTP client metrics reset")
    except:
        logger.warning("Could not reset HTTP client metrics")
    
    # Reset cache metrics
    try:
        CacheManager.clear_all_cache()
        logger.info("🔄 Tool cache cleared")
    except:
        logger.warning("Could not clear tool cache")
    
    logger.info("🔄 All performance metrics reset")

if __name__ == "__main__":
    # Test the optimized tool loader
    loader = MyndyToolLoader()
    info = loader.get_tool_info()
    
    print("🚀 Optimized HTTP-based Myndy Tool Loader Test")
    print("=" * 50)
    print(f"Total tools loaded: {info['total_tools']}")
    print(f"Registry available: {info['registry_available']}")
    print("Architecture: HTTP-only (FastAPI compliant)")
    print("Optimizations: Connection pooling, async support, metrics tracking")
    
    # Show performance metrics
    print("\n📊 Performance Metrics:")
    metrics = get_bridge_performance_metrics()
    print(json.dumps(metrics, indent=2))