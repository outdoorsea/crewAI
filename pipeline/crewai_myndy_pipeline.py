"""
title: Myndy AI v0.1 - Personal Intelligence Pipeline
author: Jeremy
version: 0.1.0
license: MIT
description: Myndy AI - Your personal intelligent assistant with conversation-driven learning. Features 5 specialized agents, automatic status/profile updates, and comprehensive tool integration.
requirements: crewai, fastapi, uvicorn, pydantic
"""

import os
import sys
import logging
import uuid
import re
import warnings
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Generator, Iterator
from pathlib import Path

# Suppress specific warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", message=".*Mixing V1 models and V2 models.*")
warnings.filterwarnings("ignore", category=UserWarning, module="crewai.telemtry.telemetry")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")

# Configure enhanced terminal logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Terminal output
        logging.FileHandler('/tmp/myndy_pipeline.log')  # Also log to file
    ]
)

# Create logger
logger = logging.getLogger("crewai.pipeline")

# Add project paths
PIPELINE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path("/Users/jeremy/myndy-ai")))

from pydantic import BaseModel

# Import Enhanced Shadow Agent
try:
    from agents.enhanced_shadow_agent import create_enhanced_shadow_agent
    SHADOW_AGENT_AVAILABLE = True
    logger.info("✅ Enhanced Shadow Agent imported successfully")
except ImportError as e:
    SHADOW_AGENT_AVAILABLE = False
    logger.warning(f"⚠️ Enhanced Shadow Agent not available: {e}")

# Import Performance Monitor Agent
try:
    from agents.performance_monitor_agent import create_performance_monitor_agent
    PERFORMANCE_AGENT_AVAILABLE = True
    logger.info("✅ Performance Monitor Agent imported successfully")
except ImportError as e:
    PERFORMANCE_AGENT_AVAILABLE = False
    logger.warning(f"⚠️ Performance Monitor Agent not available: {e}")

# Import Cache Manager Agent
try:
    from agents.cache_manager_agent import create_cache_manager_agent
    CACHE_AGENT_AVAILABLE = True
    logger.info("✅ Cache Manager Agent imported successfully")
except ImportError as e:
    CACHE_AGENT_AVAILABLE = False
    logger.warning(f"⚠️ Cache Manager Agent not available: {e}")

# Set specific loggers to be more verbose for better terminal visibility
logging.getLogger("crewai_myndy_pipeline").setLevel(logging.INFO)
logging.getLogger("tools.myndy_bridge").setLevel(logging.INFO)
logging.getLogger("qdrant").setLevel(logging.WARNING)  # Reduce qdrant noise
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)  # Reduce model loading noise


class IntelligentRouter:
    """Intelligent agent routing based on message content and tool requirements"""
    
    def __init__(self):
        self.agent_patterns = {
            "personal_assistant": {
                "keywords": [
                    # Calendar and time
                    "calendar", "schedule", "appointment", "meeting", "time", "date", "weather", "temperature", "forecast", 
                    "remind", "task", "todo", "organize", "plan", "event", "deadline",
                    # Contact and memory management
                    "remember", "contact", "person", "email", "phone", "address", "save", "store", "update", "delete", 
                    "information", "database", "knowledge", "entity", "relationship",
                    # Research and analysis
                    "research", "analyze", "document", "text", "sentiment", "language", "summarize", "extract", "study", 
                    "investigate", "report", "paper", "article", "analysis", "insights",
                    # Health tracking
                    "health", "fitness", "exercise", "sleep", "steps", "heart", "blood", "medical", "wellness", 
                    "workout", "activity", "calories",
                    # Finance management
                    "money", "expense", "cost", "budget", "spending", "transaction", "financial", "price", 
                    "payment", "bank", "account", "dollar", "finance"
                ],
                "patterns": [
                    # Time and weather
                    r"what.*time|current.*time|time.*now",
                    r"weather|temperature|forecast",
                    r"temperature.*in|weather.*in",
                    r"schedule|calendar|appointment",
                    r"remind.*me|set.*reminder",
                    r"what.*date|today.*date",
                    r"meeting|event",
                    # Contact and entity patterns
                    r"\b\w+@\w+\.\w+\b",  # email addresses
                    r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # phone numbers
                    r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # person names
                    r"works at|employed by|job at|company|organization",
                    r"lives in|address|location|located at",
                    # Analysis patterns
                    r"analyze.*sentiment|sentiment.*analysis",
                    r"summarize|summary",
                    r"extract.*from|parse.*document",
                    r"research.*topic|investigate",
                    r"what.*language|detect.*language",
                    r"document.*analysis",
                    # Health patterns
                    r"health.*data|fitness.*data",
                    r"sleep.*pattern|sleep.*quality",
                    r"exercise|workout|physical.*activity",
                    r"heart.*rate|blood.*pressure",
                    r"steps|calories|weight",
                    # Finance patterns
                    r"\$\d+|\d+.*dollar",  # money amounts
                    r"expense|spending|cost",
                    r"budget|financial|transaction",
                    r"paid|payment|bank|account"
                ],
                "description": "Comprehensive AI assistant handling all tasks: scheduling, weather, contacts, research, health, finance, and general assistance"
            },
            "performance_monitor": {
                "keywords": [
                    "performance", "monitor", "monitoring", "metrics", "system", "health", "status", "cpu", "memory", 
                    "disk", "load", "response", "time", "latency", "throughput", "error", "rate", "cache", "hit", 
                    "optimization", "optimize", "slow", "fast", "speed", "efficiency", "resource", "usage", 
                    "alerts", "warning", "critical", "threshold", "benchmark", "analytics", "statistics"
                ],
                "patterns": [
                    r"performance.*monitor|monitor.*performance",
                    r"system.*health|health.*status|system.*status",
                    r"cpu.*usage|memory.*usage|disk.*usage",
                    r"response.*time|latency|throughput",
                    r"error.*rate|failure.*rate|success.*rate",
                    r"cache.*hit.*rate|cache.*performance",
                    r"slow.*response|fast.*response|speed.*up",
                    r"optimize.*performance|performance.*issue",
                    r"resource.*usage|resource.*monitor",
                    r"alert.*threshold|critical.*alert|warning.*alert",
                    r"benchmark.*performance|performance.*test",
                    r"system.*metrics|collect.*metrics|performance.*data",
                    r"restart.*monitoring|monitoring.*status",
                    r"performance.*summary|performance.*analysis"
                ],
                "description": "Real-time system monitoring, performance analysis, and optimization recommendations",
                "priority_multiplier": 1.0
            },
            "cache_manager": {
                "keywords": [
                    "cache", "caching", "cached", "redis", "distributed", "memory", "storage", "hit", "miss", 
                    "warm", "warming", "invalidate", "invalidation", "clear", "eviction", "ttl", "expire", 
                    "namespace", "performance", "speed", "optimization", "hit rate", "statistics", "stats",
                    "compression", "size", "limit", "memory usage", "key", "value", "store", "retrieve"
                ],
                "patterns": [
                    r"cache.*hit.*rate|hit.*rate.*cache",
                    r"cache.*performance|performance.*cache",
                    r"cache.*statistics|cache.*stats|cache.*metrics",
                    r"cache.*warming|warm.*cache|preload.*cache",
                    r"cache.*invalidation|invalidate.*cache|clear.*cache",
                    r"cache.*memory|memory.*cache|cache.*usage",
                    r"redis.*cache|distributed.*cache|cache.*system",
                    r"cache.*optimization|optimize.*cache|cache.*tuning",
                    r"cache.*configuration|cache.*settings|cache.*config",
                    r"cache.*namespace|namespace.*cache",
                    r"cache.*compression|compress.*cache",
                    r"cache.*eviction|evict.*cache|cache.*limit",
                    r"cache.*health|cache.*status|cache.*monitoring",
                    r"cache.*key|cache.*value|store.*cache|retrieve.*cache"
                ],
                "description": "Distributed cache management, optimization, and performance monitoring",
                "priority_multiplier": 1.0
            },
            "shadow_agent": {
                "keywords": ["pattern", "behavior", "preference", "learn", "observe", "track", "monitor", "analyze behavior", "understanding", "insights"],
                "patterns": [
                    r"learn.*about.*me|understand.*me|analyze.*behavior",
                    r"what.*pattern|behavioral.*pattern",
                    r"preference|how.*I.*usually|my.*habit",
                    r"observe|monitor.*behavior|track.*pattern",
                    r"insight.*about|understand.*better"
                ],
                "description": "Silently observes user patterns, analyzes behavior, provides contextual insights (never primary responder)",
                "priority_multiplier": 0.0  # Never selected as primary agent
            }
        }
    
    def analyze_message(self, message: str, conversation_context: List[Dict] = None) -> 'RoutingDecision':
        """Analyze message and return routing decision"""
        message_lower = message.lower()
        
        # Score each agent
        agent_scores = {}
        
        for agent, config in self.agent_patterns.items():
            score = 0
            
            # Keyword matching
            for keyword in config["keywords"]:
                if keyword in message_lower:
                    score += 2
            
            # Pattern matching
            for pattern in config["patterns"]:
                if re.search(pattern, message, re.IGNORECASE):
                    score += 3
            
            # Apply priority multiplier (for shadow agent, this will be 0.0)
            priority_multiplier = config.get("priority_multiplier", 1.0)
            score *= priority_multiplier
            
            agent_scores[agent] = score
        
        # Find best match with tie-breaking
        max_score = max(agent_scores.values())
        tied_agents = [agent for agent, score in agent_scores.items() if score == max_score]
        
        # Tie-breaking logic for three agents
        if len(tied_agents) > 1:
            # Priority order: performance_monitor > personal_assistant > shadow_agent (never primary)
            if "performance_monitor" in tied_agents:
                best_agent = "performance_monitor"
            elif "personal_assistant" in tied_agents:
                best_agent = "personal_assistant"
            else:
                best_agent = tied_agents[0]  # Default to first
        else:
            best_agent = max(agent_scores, key=agent_scores.get)
        
        best_score = agent_scores[best_agent]
        
        # Debug logging (optional)
        # logger.debug(f"🎯 Agent scoring for message: '{message[:50]}...'")
        # for agent, score in sorted(agent_scores.items(), key=lambda x: x[1], reverse=True):
        #     logger.debug(f"   {agent}: {score} points")
        # logger.debug(f"🏆 Selected: {best_agent} (score: {best_score})")
        
        # Fallback logic for three agents
        if best_score == 0:
            # All queries go to personal assistant (comprehensive agent)
            best_agent = "personal_assistant"
            reasoning = "No specific patterns matched, routing to Personal Assistant (default for all tasks)"
            best_score = 1
        else:
            reasoning = f"Selected {best_agent} based on pattern matching (score: {best_score})"
        
        # Determine if collaboration is needed (multiple high scores)
        secondary_agents = []
        high_scores = [agent for agent, score in agent_scores.items() if score >= best_score * 0.7 and agent != best_agent]
        
        return RoutingDecision(
            primary_agent=best_agent,
            confidence=min(best_score / 10.0, 1.0),  # Normalize to 0-1
            reasoning=reasoning,
            complexity="simple" if best_score < 5 else "complex",
            requires_collaboration=len(high_scores) > 0,
            secondary_agents=high_scores
        )


class RoutingDecision:
    """Represents an agent routing decision"""
    
    def __init__(self, primary_agent: str, confidence: float, reasoning: str, 
                 complexity: str = "simple", requires_collaboration: bool = False, 
                 secondary_agents: List[str] = None):
        self.primary_agent = primary_agent
        self.confidence = confidence
        self.reasoning = reasoning
        self.complexity = complexity
        self.requires_collaboration = requires_collaboration
        self.secondary_agents = secondary_agents or []


class Pipeline:
    """Myndy AI v0.1 - Personal Intelligence Pipeline for OpenWebUI"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        enable_contact_management: bool = True
        enable_memory_search: bool = True
        debug_mode: bool = False
        memex_path: str = "/Users/jeremy/myndy-ai"
        api_key: str = "0p3n-w3bu!"  # Standard OpenWebUI pipeline key
        
    def __init__(self):
        """Initialize the pipeline"""
        self.type = "manifold"  # Manifold type for multiple agents
        self.id = "myndy_ai"
        self.name = "Myndy AI"
        self.version = "0.1.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # Import components
        self._import_components()
        
        # Initialize conversation sessions
        self.conversation_sessions = {}
        
        # Initialize Enhanced Shadow Agent if available
        self.enhanced_shadow_agent = None
        if SHADOW_AGENT_AVAILABLE:
            try:
                self.enhanced_shadow_agent = create_enhanced_shadow_agent()
                logger.info("🔮 Enhanced Shadow Agent initialized for behavioral observation")
            except Exception as e:
                logger.warning(f"Failed to initialize Enhanced Shadow Agent: {e}")
        
        # Initialize Performance Monitor Agent if available
        self.performance_monitor_agent = None
        if PERFORMANCE_AGENT_AVAILABLE:
            try:
                self.performance_monitor_agent = create_performance_monitor_agent()
                logger.info("📊 Performance Monitor Agent initialized for system monitoring")
            except Exception as e:
                logger.warning(f"Failed to initialize Performance Monitor Agent: {e}")
        
        # Initialize Cache Manager Agent if available
        self.cache_manager_agent = None
        if CACHE_AGENT_AVAILABLE:
            try:
                self.cache_manager_agent = create_cache_manager_agent()
                logger.info("🗄️ Cache Manager Agent initialized for distributed cache management")
            except Exception as e:
                logger.warning(f"Failed to initialize Cache Manager Agent: {e}")
        
        # Load tool-specific prompt engineering guides
        self.tool_prompt_cache = {}
        self._load_tool_specific_prompts()
        
        # Agent definitions - four specialized agents
        self.agents = {
            "personal_assistant": {
                "name": "Personal Assistant",
                "description": "Comprehensive AI assistant for all tasks including calendar, email, research, health tracking, finance management, and personal productivity",
                "model": "llama3.2",
                "capabilities": [
                    "calendar management", "email processing", "task coordination", "memory management", 
                    "entity relationships", "conversation history", "contact information", "web research", 
                    "fact verification", "document analysis", "health analysis", "fitness tracking", 
                    "expense tracking", "budget analysis", "financial planning", "text analysis"
                ]
            },
            "shadow_agent": {
                "name": "Shadow Intelligence Observer",
                "description": "Silently observes user behavior, analyzes patterns, and provides contextual insights to enhance the personal assistant",
                "model": "mixtral",
                "capabilities": ["behavioral analysis", "pattern recognition", "context synthesis", "silent learning", "preference modeling"]
            },
            "performance_monitor": {
                "name": "Performance Monitor",
                "description": "Real-time system performance monitoring, analysis, and optimization recommendations for the Myndy-AI system",
                "model": "mixtral",
                "capabilities": [
                    "system monitoring", "performance analysis", "resource tracking", "health assessment", 
                    "alert generation", "optimization recommendations", "trend analysis", "metric collection",
                    "cache performance", "error rate monitoring", "response time analysis", "capacity planning"
                ]
            },
            "cache_manager": {
                "name": "Cache Manager",
                "description": "Distributed Redis cache management, optimization, performance monitoring, and data organization specialist",
                "model": "mixtral",
                "capabilities": [
                    "cache management", "Redis optimization", "distributed caching", "hit rate analysis",
                    "cache warming", "invalidation strategies", "namespace management", "compression tuning",
                    "memory optimization", "TTL configuration", "eviction policies", "performance monitoring",
                    "cache statistics", "troubleshooting", "data organization", "bulk operations"
                ]
            }
        }
        
        # Tool registry initialization disabled - using direct tool execution
        # self._initialize_tool_registry()
        
        logger.info(f"🎉 Myndy AI v{self.version} - Personal Intelligence Pipeline initialized")
        logger.info(f"📊 Available agents: {list(self.agents.keys())}")
        logger.info(f"🔧 CrewAI available: {getattr(self, 'crewai_available', False)}")
        if hasattr(self, 'crewai_agents'):
            logger.info(f"🤖 CrewAI agents loaded: {list(self.crewai_agents.keys())}")
        logger.info(f"✅ 4 specialized agents: Personal Assistant + Performance Monitor + Cache Manager + Shadow Agent")
        
    async def on_startup(self):
        """Called when the pipeline is started"""
        logger.info("🚀 Pipeline startup initiated")
        logger.info(f"🎯 Ready to serve {len(self.agents)} agents")
        # Additional startup logic if needed
        pass
        
    async def on_shutdown(self):
        """Called when the pipeline is shut down"""
        logger.info("🛑 Pipeline shutdown initiated")
        logger.info("📝 Cleaning up resources...")
        # Cleanup logic if needed
        pass
        
    async def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info("⚙️ Pipeline valves updated")
        logger.info(f"🔧 Current valve settings: {self.valves.dict()}")
        # Additional logic to handle valve updates if needed
        pass
        
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models/agents for OpenWebUI compatibility"""
        return self._get_models()
        
    def get_manifest(self) -> Dict[str, Any]:
        """Return pipeline manifest for OpenWebUI"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "type": self.type,
            "description": "Myndy AI - Your personal intelligent assistant with conversation-driven learning",
            "author": "Jeremy",
            "license": "MIT",
            "models": self._get_models()
        }
        
    def _initialize_tool_registry(self):
        """Initialize and populate the myndy tool registry"""
        try:
            logger.info("Initializing tool registry...")
            
            # Import and directly populate the registry in this process
            if MYNDY_AI_ROOT.exists():
                sys.path.insert(0, str(MYNDY_AI_ROOT))
            else:
                logger.warning("Myndy AI root directory not found for tool registry initialization")
            
            # Import registry using contextual path
            import importlib.util
            registry_path = None
            
            # Try to find registry.py in various locations
            for base_path in [MYNDY_AI_ROOT, PIPELINE_ROOT.parent / "myndy-ai"]:
                if base_path.exists():
                    potential_path = base_path / "agents" / "tools" / "registry.py"
                    if potential_path.exists():
                        registry_path = potential_path
                        break
            
            if not registry_path:
                raise ImportError("Could not find myndy-ai registry.py")
            spec = importlib.util.spec_from_file_location("myndy_registry", registry_path)
            registry_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(registry_module)
            registry = registry_module.registry
            
            # Clear existing tools and repopulate
            logger.info("Populating tool registry with myndy tools...")
            
            # Run populate_registry script directly
            exec(open(str(PIPELINE_ROOT / "populate_registry.py")).read(), {'__name__': '__main__'})
            
            # Run register_monitoring_tools script directly  
            exec(open(str(PIPELINE_ROOT / "register_monitoring_tools.py")).read(), {'__name__': '__main__'})
            
            # Run register_conversation_tools script directly
            exec(open(str(PIPELINE_ROOT / "register_conversation_tools.py")).read(), {'__name__': '__main__'})
            
            # Verify tools are loaded
            total_tools = len(registry.get_all_tools())
            logger.info(f"Tool registry initialized with {total_tools} tools")
            
            # Check for format_weather specifically
            format_weather_tool = registry.get_tool('format_weather')
            if format_weather_tool:
                logger.info("✅ format_weather tool confirmed available")
            else:
                logger.warning("❌ format_weather tool not found in registry")
                
        except Exception as e:
            logger.error(f"Failed to initialize tool registry: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _import_components(self):
        """Import CrewAI and Myndy components"""
        try:
            # Add parent directory to path for imports
            import sys
            import os
            import importlib.util
            
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            # Create intelligent router for agent selection
            self.router = IntelligentRouter()
            
            # Define AgentRole enum locally - simplified to only 2 agents
            class AgentRole:
                PERSONAL_ASSISTANT = "personal_assistant"
                SHADOW_AGENT = "shadow_agent"
            
            self.AgentRole = AgentRole
            
            # Import CrewAI crews using contextual path
            crews_dir = Path(parent_dir) / "crews"
            crew_file = crews_dir / "personal_productivity_crew.py"
            
            if not crew_file.exists():
                # Try alternative locations
                for alt_dir in [PIPELINE_ROOT / "crews", Path(__file__).parent / "../crews"]:
                    alt_file = alt_dir / "personal_productivity_crew.py"
                    if alt_file.exists():
                        crew_file = alt_file
                        break
            
            crew_spec = importlib.util.spec_from_file_location(
                "personal_productivity_crew", str(crew_file)
            )
            crew_module = importlib.util.module_from_spec(crew_spec)
            crew_spec.loader.exec_module(crew_module)
            PersonalProductivityCrew = crew_module.PersonalProductivityCrew
            
            # Get agent creation functions from the crew module
            create_personal_assistant = crew_module.create_personal_assistant
            create_shadow_agent = crew_module.create_shadow_agent
            
            # Initialize CrewAI components - three specialized agents
            self.crew_manager = PersonalProductivityCrew(verbose=True)
            self.crewai_agents = {
                "personal_assistant": create_personal_assistant(),
                "shadow_agent": create_shadow_agent()
            }
            
            # Add Performance Monitor Agent if available
            if PERFORMANCE_AGENT_AVAILABLE:
                self.crewai_agents["performance_monitor"] = self.performance_monitor_agent
            
            # Add Cache Manager Agent if available
            if CACHE_AGENT_AVAILABLE:
                self.crewai_agents["cache_manager"] = self.cache_manager_agent
            
            self.crewai_available = True
            logger.info("CrewAI agents and crews imported successfully")
            
        except ImportError as e:
            logger.warning(f"Could not import CrewAI components: {e}")
            self.crewai_available = False
            self.router = None
            
    def _get_models(self) -> List[Dict[str, Any]]:
        """Return available models/agents"""
        models = []
        
        # Add auto-routing model
        models.append({
            "id": "auto",
            "name": "🧠 Myndy AI v0.1",
            "object": "model",
            "created": int(datetime.now().timestamp()),
            "owned_by": "crewai-myndy"
        })
        
        # Add individual agents
        for agent_id, agent_info in self.agents.items():
            models.append({
                "id": agent_id,
                "name": f"🎯 {agent_info['name']}",
                "object": "model", 
                "created": int(datetime.now().timestamp()),
                "owned_by": "crewai-myndy"
            })
            
        return models
        
    def pipe(self, body: Dict[str, Any], 
             __user__: Optional[Dict[str, Any]] = None,
             __request__: Optional[Any] = None,
             __event_emitter__: Optional[Any] = None,
             __event_call__: Optional[Any] = None,
             __task__: Optional[str] = None,
             __task_body__: Optional[dict] = None,
             __files__: Optional[list] = None,
             __metadata__: Optional[dict] = None,
             __tools__: Optional[dict] = None) -> Union[str, Generator, Iterator]:
        """Process messages through the pipeline with user context"""
        
        # Extract user information
        user_info = self._extract_user_info(__user__)
        request_headers = self._extract_request_headers(__request__)
        
        # Extract traditional parameters for backward compatibility
        messages = body.get("messages", [])
        model_id = body.get("model", "auto")
        
        user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break
        
        # Always log pipeline calls for visibility with user context
        logger.info(f"🎯 Pipeline called by {user_info['name']} (ID: {user_info['id']}): model={model_id}, message_length={len(user_message)} chars")
        if self.valves.debug_mode:
            logger.info(f"📝 Full message: {user_message[:200]}{'...' if len(user_message) > 200 else ''}")
            logger.info(f"👤 User context: {user_info}")
            
        try:
            # Get session ID for conversation tracking (now user-specific)
            session_id = self._get_user_session_id(messages, user_info['id'])
            logger.info(f"💬 User-specific Session ID: {session_id}")
            
            # Update conversation history with user context
            self._update_conversation_history(session_id, messages, user_info)
            logger.info(f"📚 Updated conversation history for {user_info['name']} ({len(messages)} messages)")
            
            # Enhance body with user context for agents
            enhanced_body = body.copy()
            enhanced_body["__user_context__"] = {
                "user_info": user_info,
                "headers": request_headers,
                "timestamp": datetime.now().isoformat()
            }
            
            # Use CrewAI to handle the entire conversation
            if self.crewai_available:
                logger.info(f"🤖 Routing to CrewAI agents for user {user_info['name']}...")
                # Route to appropriate CrewAI agent/crew with user context
                response = self._execute_crewai_pipeline(user_message, model_id, session_id, user_info)
                logger.info(f"✅ CrewAI response generated for {user_info['name']} (length: {len(response)} chars)")
            else:
                logger.warning("⚠️ CrewAI agents not available, using fallback")
                # Simple fallback response when CrewAI not available
                response = f"Hello {user_info['name']}, CrewAI agents are not available. Please ensure all dependencies are properly installed."
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Pipeline error for user {user_info['name']}: {e}")
            return f"Hello {user_info['name']}, I encountered an error while processing your request: {str(e)}"
    
    def _extract_user_info(self, __user__: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract and normalize user information from Open WebUI"""
        if not __user__:
            return {
                "id": "anonymous",
                "name": "Anonymous User",
                "email": None,
                "role": "user",
                "is_authenticated": False
            }
        
        return {
            "id": __user__.get("id", "unknown"),
            "name": __user__.get("name", "Unknown User"),
            "email": __user__.get("email"),
            "role": __user__.get("role", "user"),
            "is_authenticated": True
        }

    def _extract_request_headers(self, __request__: Optional[Any]) -> Dict[str, Any]:
        """Extract relevant headers from request"""
        if not __request__ or not hasattr(__request__, 'headers'):
            return {}
        
        headers = dict(__request__.headers)
        return {
            'user_agent': headers.get('user-agent'),
            'x_user_id': headers.get('x-user-id'),
            'x_user_email': headers.get('x-user-email'),
            'authorization': headers.get('authorization'),
            'client_ip': headers.get('x-forwarded-for') or headers.get('x-real-ip'),
        }
    
    def _get_user_session_id(self, messages: List[Dict[str, Any]], user_id: str) -> str:
        """Generate user-specific session ID for conversation tracking"""
        # Include user ID in session generation for user-specific sessions
        content_hash = str(abs(hash(str([msg.get("content", "") for msg in messages]))))
        return f"session_{user_id}_{content_hash[:8]}"
            
    def _get_session_id(self, messages: List[Dict[str, Any]]) -> str:
        """Generate session ID for conversation tracking"""
        # Simple approach: hash the conversation content
        content_hash = str(abs(hash(str([msg.get("content", "") for msg in messages]))))
        return f"session_{content_hash[:8]}"
        
    def _update_conversation_history(self, session_id: str, messages: List[Dict[str, Any]], user_info: Optional[Dict[str, Any]] = None):
        """Update conversation history for a session with user context"""
        if session_id not in self.conversation_sessions:
            self.conversation_sessions[session_id] = {
                "created_at": datetime.now(),
                "messages": [],
                "agent_history": [],
                "user_info": user_info or {"id": "anonymous", "name": "Anonymous User"}
            }
            
        # Update user info if provided
        if user_info:
            self.conversation_sessions[session_id]["user_info"] = user_info
            
        # Store recent messages
        self.conversation_sessions[session_id]["messages"] = messages[-20:]  # Keep last 20 messages
        
    def _execute_crewai_pipeline(self, user_message: str, model_id: str, session_id: str, user_info: Optional[Dict[str, Any]] = None) -> str:
        """Execute the full CrewAI pipeline with intelligent routing and tool execution"""
        try:
            # Determine which agent/crew to use
            if model_id == "auto" or model_id == "crewai-myndy-pipeline":
                logger.info(f"🧠 Using intelligent routing for message")
                # Use intelligent routing (default for our pipeline)
                selected_agent, routing_info = self._route_message(user_message, session_id)
                logger.info(f"🎯 Routed to: {selected_agent} (confidence: {routing_info.get('confidence', 'N/A')})")
                logger.info(f"💭 Reasoning: {routing_info.get('reasoning', 'No reasoning provided')}")
            else:
                logger.info(f"👤 Direct agent selection: {model_id}")
                # Use specific agent
                selected_agent = model_id
                routing_info = {
                    "reasoning": f"Direct selection of {self.agents.get(model_id, {}).get('name', model_id)}",
                    "confidence": 1.0,
                    "method": "direct"
                }
            
            # Get the CrewAI agent
            if selected_agent in self.crewai_agents:
                crewai_agent = self.crewai_agents[selected_agent]
                logger.info(f"🚀 Executing {selected_agent} agent...")
                
                # Execute the agent with the message and user context
                # CrewAI agents handle their own tool selection and execution
                result = self._execute_crewai_agent(crewai_agent, user_message, selected_agent, user_info)
                logger.info(f"✅ Agent {selected_agent} completed execution for user {user_info.get('name', 'Unknown') if user_info else 'Unknown'}")
                
                # Run Shadow Agent observation in background (MVP integration)
                self._execute_shadow_observation(user_message, result, selected_agent, session_id)
                
                # Format response with routing info
                return self._format_crewai_response(result, selected_agent, routing_info)
            else:
                logger.error(f"❌ Agent '{selected_agent}' not found in CrewAI system")
                # Fallback if agent not found
                return f"Agent '{selected_agent}' not available in CrewAI system."
                
        except Exception as e:
            logger.error(f"❌ CrewAI pipeline execution error: {e}")
            return f"CrewAI pipeline encountered an error: {str(e)}"
            
    def _execute_crewai_agent(self, agent, user_message: str, agent_role: str, user_info: Optional[Dict[str, Any]] = None) -> str:
        """Execute a specific CrewAI agent with the user message and user context"""
        try:
            # Create a task for the agent
            from crewai import Task
            
            # Define the task based on the message, agent role, and user context
            task_description = self._create_task_description(user_message, agent_role, user_info)
            
            task = Task(
                description=task_description,
                agent=agent,
                expected_output="A detailed response addressing the user's request with any relevant information found or actions taken."
            )
            
            # Execute the task
            result = task.execute()
            
            return str(result)
            
        except Exception as e:
            logger.error(f"CrewAI agent execution error: {e}")
            return f"Agent execution error: {str(e)}"
            
    def _create_task_description(self, user_message: str, agent_role: str, user_info: Optional[Dict[str, Any]] = None) -> str:
        """Create appropriate task description for CrewAI agent based on role and user context"""
        
        # Include user context in task description
        user_context = ""
        if user_info and user_info.get('is_authenticated', False):
            user_context = f"User Context: {user_info['name']} (ID: {user_info['id']}, Role: {user_info['role']})\n"
            if user_info.get('email'):
                user_context += f"Email: {user_info['email']}\n"
            user_context += "\n"
        
        # Add tool-specific guidance based on the message content
        tool_guidance = self._get_enhanced_tool_guidance(user_message, agent_role)
        
        base_description = f"{user_context}User message: '{user_message}'\n\n{tool_guidance}\n"
        
        if agent_role == "personal_assistant":
            return base_description + """
Your task as the Comprehensive Personal Assistant is to:

1. **Universal Task Management**: Handle ALL types of requests including:
   - Time management and scheduling
   - Weather and environmental information
   - Calendar organization and planning
   - Memory and contact management
   - Document analysis and research
   - Health tracking and insights
   - Financial management and analysis
   - General productivity assistance

2. **Multi-Tool Coordination**: Use multiple tools for comprehensive assistance:
   - Check time AND weather for meeting planning
   - Combine memory tools with research capabilities
   - Cross-reference calendar with contact information
   - Use analysis tools for document processing
   - Integrate health and finance data when relevant

3. **Proactive Information Management**: 
   - Extract and validate factual information mentioned in conversations
   - Update contact, memory, and status information automatically
   - Provide comprehensive responses using multiple data sources
   - Maintain context across different domains (health, finance, scheduling, etc.)

4. **Intelligent Tool Selection**: Choose the right combination of tools based on the request:
   - Time/calendar tools for scheduling
   - Weather tools for planning
   - Memory tools for information retrieval and storage
   - Analysis tools for research and document processing
   - Health tools for wellness queries
   - Finance tools for spending and budget analysis

Your available tools include: calendar queries, current time, time calculations, date formatting, weather information, memory management, entity extraction, document analysis, health tracking, financial management, and all organizational utilities. Use multiple tools together to provide comprehensive assistance for ANY type of request.
"""
        elif agent_role == "shadow_agent":
            return base_description + """
Your task as the Shadow Intelligence Observer is to:

1. **Silent Pattern Analysis**: Analyze user behavior patterns, preferences, and communication styles without being the primary responder

2. **Contextual Learning**: Extract insights about user habits, preferences, and decision-making patterns from the conversation

3. **Background Intelligence**: Provide contextual insights that enhance other agents' responses without dominating the conversation

4. **Behavioral Modeling**: Build understanding of user preferences, working styles, and communication patterns

5. **Preference Tracking**: Notice and remember user preferences for future reference by other agents

**Critical Constraint**: You are NEVER the primary responder. Your role is to observe, analyze, and provide background intelligence that other agents can use. Your responses should be brief, insightful, and focused on patterns rather than direct task completion.

Your available tools include behavioral analysis, pattern recognition, and preference modeling capabilities. Use them to enhance the overall system's understanding of the user.
"""
        elif agent_role == "performance_monitor":
            return base_description + """
Your task as the Performance Monitor and Analyst is to:

1. **Real-time System Monitoring**: Monitor system performance metrics including CPU, memory, disk usage, and network activity

2. **Performance Analysis**: Analyze API performance metrics such as response times, throughput, error rates, and cache effectiveness

3. **Health Assessment**: Evaluate overall system health and identify potential issues before they become critical

4. **Alert Management**: Generate appropriate alerts for performance degradation, resource exhaustion, or system issues

5. **Optimization Recommendations**: Provide specific, actionable recommendations for improving system performance

6. **Trend Analysis**: Identify performance trends and predict potential capacity or performance issues

7. **Metric Collection**: Record custom metrics and performance data for specialized monitoring needs

8. **Resource Tracking**: Monitor resource utilization and provide insights on efficiency improvements

**Your Performance Monitoring Tools Include**:
- get_system_performance_metrics() - Get comprehensive system and service metrics
- get_system_health_status() - Check current system health status
- record_custom_performance_metric() - Record application-specific metrics
- query_specific_performance_metrics() - Query filtered metrics data
- get_performance_monitoring_status() - Get monitoring system status
- get_performance_stats_summary() - Get comprehensive statistics summary
- restart_performance_monitoring() - Restart monitoring if needed

**Response Guidelines**:
- Provide clear, actionable performance insights
- Include specific metrics and thresholds in your analysis
- Explain the impact of performance issues on user experience
- Suggest concrete steps for optimization
- Use performance data to support your recommendations
- Format metrics in a clear, readable manner
"""
        elif agent_role == "cache_manager":
            return base_description + """
Your task as the Cache Manager and Performance Optimizer is to:

1. **Distributed Cache Management**: Monitor and manage the Redis distributed caching system across all namespaces

2. **Cache Performance Analysis**: Analyze cache hit rates, memory usage, response times, and efficiency metrics

3. **Cache Warming and Optimization**: Implement cache warming strategies, optimize TTL values, and tune cache configurations

4. **Namespace Management**: Organize cache data across different namespaces (tool_results, api_responses, memory_queries, etc.)

5. **Invalidation Strategies**: Implement intelligent cache invalidation patterns and maintain data consistency

6. **Memory Optimization**: Monitor cache memory usage, implement compression strategies, and manage eviction policies

7. **Troubleshooting and Health**: Diagnose cache issues, monitor Redis health, and provide optimization recommendations

8. **Performance Monitoring**: Track cache statistics, analyze trends, and provide data-driven optimization insights

**Your Cache Management Tools Include**:
- cache_get_value() - Retrieve values from distributed cache
- cache_set_value() - Store values in distributed cache with TTL
- cache_get_multiple_values() - Bulk cache retrieval operations
- cache_set_multiple_values() - Bulk cache storage operations
- cache_clear_namespace() - Clear entire cache namespaces
- cache_invalidate_pattern() - Pattern-based cache invalidation
- cache_get_statistics() - Comprehensive cache performance statistics
- cache_get_health_status() - Redis health and connectivity status
- cache_warm_data() - Cache warming with precomputed data
- cache_list_namespaces() - Available cache namespace information
- cache_get_namespace_info() - Detailed namespace statistics

**Response Guidelines**:
- Provide specific cache performance metrics and recommendations
- Explain cache hit rates, memory usage, and optimization opportunities
- Suggest concrete configuration changes for improved performance
- Use cache statistics to support optimization recommendations
- Identify bottlenecks and propose targeted solutions
- Monitor cache health and proactively address issues
- Format cache data in clear, actionable reports
"""
        else:
            return base_description + "Please assist the user with their request using your available tools and capabilities."
    
    def _get_tool_specific_guidance(self, user_message: str, agent_role: str) -> str:
        """Generate tool-specific guidance based on message content and agent role"""
        message_lower = user_message.lower()
        guidance_parts = []
        
        # Add general HTTP tool integration guidance
        guidance_parts.append("🔧 MYNDY-AI TOOL INTEGRATION:")
        guidance_parts.append("• ALL TOOLS → HTTP POST to /api/v1/tools/execute endpoint")
        guidance_parts.append("• PARAMETER VALIDATION → Always validate required vs optional parameters")
        guidance_parts.append("• ERROR HANDLING → Implement graceful fallbacks for API failures")
        guidance_parts.append("")
        
        # Time and scheduling guidance
        if any(keyword in message_lower for keyword in ['time', 'schedule', 'calendar', 'meeting', 'appointment', 'date', 'when']):
            guidance_parts.append("🕐 TIME & SCHEDULING TOOLS:")
            guidance_parts.append("• TIME QUERIES → use get_current_time with IANA timezone format")
            guidance_parts.append("• CALENDAR OPS → use calendar_query with action-specific parameters")
            guidance_parts.append("• DATE FORMATTING → use format_date for locale-appropriate display")
            guidance_parts.append("• TIME CALCULATIONS → use calculate_time_difference for durations")
            guidance_parts.append("REASONING: Always infer timezone from user context or explicitly ask")
            guidance_parts.append("")
        
        # Weather guidance
        if any(keyword in message_lower for keyword in ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy']):
            guidance_parts.append("🌤️ WEATHER TOOLS:")
            guidance_parts.append("• CURRENT WEATHER → use local_weather with precise location")
            guidance_parts.append("• DETAILED FORECASTS → use weather_api with forecast=true")
            guidance_parts.append("• WEATHER FORMATTING → use format_weather for user-friendly display")
            guidance_parts.append("REASONING: Infer location from context or user profile, ask if unclear")
            guidance_parts.append("")
        
        # Memory and conversation guidance
        if any(keyword in message_lower for keyword in ['remember', 'save', 'store', 'person', 'contact', 'know', 'relationship']):
            guidance_parts.append("🧠 MEMORY & CONVERSATION TOOLS:")
            guidance_parts.append("• ENTITY EXTRACTION → use extract_conversation_entities for people/organizations")
            guidance_parts.append("• INTENT ANALYSIS → use infer_conversation_intent for action detection")
            guidance_parts.append("• CONVERSATION HISTORY → use extract_from_conversation_history for insights")
            guidance_parts.append("• MEMORY SEARCH → use search_memory for information retrieval")
            guidance_parts.append("REASONING: Extract all entities and relationships automatically")
            guidance_parts.append("")
        
        # Finance guidance
        if any(keyword in message_lower for keyword in ['money', 'expense', 'cost', 'budget', 'spending', 'transaction', 'dollar', '$']):
            guidance_parts.append("💰 FINANCE TOOLS:")
            guidance_parts.append("• EXPENSE TRACKING → use get_recent_expenses with category filtering")
            guidance_parts.append("• TRANSACTION SEARCH → use search_transactions with date/amount ranges")
            guidance_parts.append("• SPENDING ANALYSIS → use get_spending_summary for insights")
            guidance_parts.append("• FINANCIAL OPS → use finance_tool for create/update/categorize actions")
            guidance_parts.append("REASONING: Convert natural language amounts to proper formats")
            guidance_parts.append("")
        
        # Health guidance
        if any(keyword in message_lower for keyword in ['health', 'fitness', 'sleep', 'exercise', 'steps', 'heart', 'activity']):
            guidance_parts.append("🏥 HEALTH TOOLS:")
            guidance_parts.append("• HEALTH QUERIES → use health_query with action-specific routing")
            guidance_parts.append("• SIMPLE SUMMARIES → use health_query_simple for quick overviews")
            guidance_parts.append("• HEALTH INSIGHTS → use health_summary_simple for trend analysis")
            guidance_parts.append("REASONING: Respect health data privacy, provide contextual insights")
            guidance_parts.append("")
        
        # Document processing guidance
        if any(keyword in message_lower for keyword in ['document', 'file', 'pdf', 'text', 'analyze', 'extract', 'summarize']):
            guidance_parts.append("📄 DOCUMENT PROCESSING TOOLS:")
            guidance_parts.append("• DOCUMENT ANALYSIS → use process_document with appropriate extraction flags")
            guidance_parts.append("• TEXT EXTRACTION → use extract_document_text for content retrieval")
            guidance_parts.append("• DOCUMENT SEARCH → use search_document for content queries")
            guidance_parts.append("• SUMMARIZATION → use summarize_document for key insights")
            guidance_parts.append("REASONING: Choose extraction methods based on document type and user needs")
            guidance_parts.append("")
        
        # Text analysis guidance
        if any(keyword in message_lower for keyword in ['sentiment', 'analyze', 'language', 'entities', 'keywords']):
            guidance_parts.append("📝 TEXT ANALYSIS TOOLS:")
            guidance_parts.append("• SENTIMENT ANALYSIS → use analyze_sentiment for emotional context")
            guidance_parts.append("• TEXT ANALYSIS → use analyze_text for comprehensive insights")
            guidance_parts.append("• LANGUAGE DETECTION → use detect_language for multilingual content")
            guidance_parts.append("• ENTITY EXTRACTION → use extract_entities for structured data")
            guidance_parts.append("REASONING: Combine multiple analysis tools for comprehensive understanding")
            guidance_parts.append("")
        
        # Agent-specific tool selection guidance
        if agent_role == "personal_assistant":
            guidance_parts.append("🎯 PERSONAL ASSISTANT TOOL SELECTION:")
            guidance_parts.append("• MULTI-TOOL COORDINATION → Use multiple tools together for comprehensive assistance")
            guidance_parts.append("• CONTEXT SYNTHESIS → Combine time + weather for meeting planning")
            guidance_parts.append("• PROACTIVE EXTRACTION → Automatically extract and validate factual information")
            guidance_parts.append("• INTELLIGENT ROUTING → Choose optimal tool combinations based on request complexity")
            guidance_parts.append("")
            
        elif agent_role == "shadow_agent":
            guidance_parts.append("🔮 SHADOW AGENT BEHAVIORAL ANALYSIS:")
            guidance_parts.append("• PATTERN RECOGNITION → Focus on behavioral patterns and preferences")
            guidance_parts.append("• SILENT LEARNING → Extract insights without being primary responder")
            guidance_parts.append("• CONTEXT ENHANCEMENT → Provide background intelligence for other agents")
            guidance_parts.append("• PREFERENCE MODELING → Build understanding of user habits and communication styles")
            guidance_parts.append("")
        
        # Critical agent-based tool selection reminder
        guidance_parts.append("⚠️ CRITICAL TOOL SELECTION PRINCIPLE:")
        guidance_parts.append("• AGENT-BASED SELECTION → Use LLM reasoning, NOT keyword patterns")
        guidance_parts.append("• REASONING TRANSPARENCY → Always explain why specific tools were chosen")
        guidance_parts.append("• CONTEXT AWARENESS → Consider user needs, timing, and expected outcomes")
        guidance_parts.append("• QUALITY OPTIMIZATION → Select tool combinations that maximize accuracy and usefulness")
        
        return "\n".join(guidance_parts)
            
    def _format_crewai_response(self, result: str, agent_role: str, routing_info: Dict) -> str:
        """Format the CrewAI response with routing information"""
        agent_info = self.agents.get(agent_role, {"name": "Unknown Agent"})
        
        response_parts = []
        
        # Agent header with routing info
        if routing_info.get("method") == "intelligent":
            response_parts.append(f"🧠 **{agent_info['name']}** (Myndy AI)")
            response_parts.append(f"**Routing:** {routing_info['reasoning']}")
        else:
            response_parts.append(f"🎯 **{agent_info['name']}** (Direct selection)")
            
        response_parts.append("")  # Empty line
        
        # CrewAI agent result
        response_parts.append(f"**Response:** {result}")
        
        # Collaboration suggestions
        if routing_info.get("collaboration"):
            collab_names = [self.agents.get(role, {}).get('name', role) for role in routing_info['collaboration']]
            response_parts.append(f"\n**💡 Collaboration Suggestion:** Consider working with {', '.join(collab_names)} for a comprehensive approach.")
            
        return "\n".join(response_parts)
        
        
    def _route_message(self, message: str, session_id: str) -> tuple:
        """Route message to appropriate agent using intelligent routing"""
        try:
            if not self.router:
                # Fallback routing
                return "memory_librarian", {
                    "reasoning": "Router not available, using Memory Librarian as fallback",
                    "confidence": 0.5,
                    "method": "fallback"
                }
                
            # Get conversation context
            conversation_context = self.conversation_sessions.get(session_id, {}).get("messages", [])
            
            # Analyze message and route
            routing_decision = self.router.analyze_message(message, conversation_context)
            
            # Track agent usage
            if session_id in self.conversation_sessions:
                self.conversation_sessions[session_id]["agent_history"].append({
                    "agent": routing_decision.primary_agent,
                    "confidence": routing_decision.confidence,
                    "reasoning": routing_decision.reasoning,
                    "timestamp": datetime.now().isoformat()
                })
            
            return routing_decision.primary_agent, {
                "reasoning": routing_decision.reasoning,
                "confidence": routing_decision.confidence,
                "complexity": routing_decision.complexity,
                "collaboration": routing_decision.secondary_agents if routing_decision.requires_collaboration else [],
                "method": "intelligent"
            }
            
        except Exception as e:
            logger.error(f"Routing error: {e}")
            return "memory_librarian", {
                "reasoning": f"Routing failed ({str(e)}), using Memory Librarian as fallback",
                "confidence": 0.5,
                "method": "error_fallback"
            }
    
    def _execute_shadow_observation(self, user_message: str, agent_response: str, 
                                  agent_type: str, session_id: str) -> None:
        """Execute Enhanced Shadow Agent observation in background"""
        if not self.enhanced_shadow_agent:
            return
            
        try:
            # Run Enhanced Shadow Agent observation asynchronously in background
            import threading
            
            def observe_conversation():
                try:
                    observation = self.enhanced_shadow_agent.observe_conversation(
                        user_message=user_message,
                        agent_response=agent_response,
                        agent_type=agent_type,
                        session_id=session_id
                    )
                    logger.debug(f"🔮 Enhanced shadow observation completed for session {session_id}")
                except Exception as e:
                    logger.warning(f"Shadow observation failed: {e}")
            
            # Start observation in background thread
            observer_thread = threading.Thread(target=observe_conversation, daemon=True)
            observer_thread.start()
            
        except Exception as e:
            logger.warning(f"Failed to start shadow observation: {e}")
    
    def _load_tool_specific_prompts(self):
        """Load tool-specific prompt engineering guides from documentation files"""
        try:
            docs_dir = PIPELINE_ROOT / "docs"
            
            # Load main tool-specific guide
            tool_guide_path = docs_dir / "TOOL_SPECIFIC_PROMPT_ENGINEERING_GUIDE.md"
            if tool_guide_path.exists():
                with open(tool_guide_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.tool_prompt_cache['tool_specific_guide'] = content
                    logger.info("✅ Loaded tool-specific prompt engineering guide")
            
            # Load API endpoints reference
            api_guide_path = docs_dir / "TOOL_API_ENDPOINTS_REFERENCE.md"
            if api_guide_path.exists():
                with open(api_guide_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.tool_prompt_cache['api_endpoints_guide'] = content
                    logger.info("✅ Loaded API endpoints reference guide")
            
            # Load enhanced agents summary
            enhanced_guide_path = docs_dir / "ENHANCED_AGENTS_SUMMARY.md"
            if enhanced_guide_path.exists():
                with open(enhanced_guide_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.tool_prompt_cache['enhanced_agents_guide'] = content
                    logger.info("✅ Loaded enhanced agents summary guide")
            
            # Load general prompt engineering guide
            prompt_guide_path = docs_dir / "PROMPT_ENGINEERING_GUIDE.md"
            if prompt_guide_path.exists():
                with open(prompt_guide_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.tool_prompt_cache['prompt_engineering_guide'] = content
                    logger.info("✅ Loaded general prompt engineering guide")
            
            logger.info(f"📚 Loaded {len(self.tool_prompt_cache)} prompt engineering guides")
            
        except Exception as e:
            logger.warning(f"Failed to load tool-specific prompts: {e}")
            self.tool_prompt_cache = {}
    
    def _get_enhanced_tool_guidance(self, user_message: str, agent_role: str) -> str:
        """Get enhanced tool guidance using loaded documentation"""
        try:
            # Use the cached tool-specific guide if available
            if 'tool_specific_guide' in self.tool_prompt_cache:
                # Extract relevant sections based on message content
                return self._extract_relevant_tool_guidance(user_message, agent_role)
            else:
                # Fallback to built-in guidance
                return self._get_tool_specific_guidance(user_message, agent_role)
        except Exception as e:
            logger.warning(f"Failed to get enhanced tool guidance: {e}")
            return self._get_tool_specific_guidance(user_message, agent_role)
    
    def _extract_relevant_tool_guidance(self, user_message: str, agent_role: str) -> str:
        """Extract relevant sections from the loaded tool-specific guide"""
        message_lower = user_message.lower()
        guidance_parts = []
        
        # Start with general HTTP integration
        guidance_parts.append("🔧 MYNDY-AI FASTAPI TOOL INTEGRATION:")
        guidance_parts.append("• HTTP ENDPOINT → POST /api/v1/tools/execute")
        guidance_parts.append("• REQUEST FORMAT → {\"tool_name\": \"name\", \"parameters\": {...}}")
        guidance_parts.append("• AUTHENTICATION → Include proper headers for authenticated access")
        guidance_parts.append("• ERROR HANDLING → Implement timeouts and graceful fallbacks")
        guidance_parts.append("")
        
        # Add contextual tool guidance based on message analysis
        tool_categories = self._analyze_message_for_tool_categories(message_lower)
        
        for category in tool_categories:
            category_guidance = self._get_category_specific_guidance(category, agent_role)
            if category_guidance:
                guidance_parts.extend(category_guidance)
                guidance_parts.append("")
        
        # Add agent-specific reasoning patterns
        agent_guidance = self._get_agent_specific_reasoning(agent_role)
        guidance_parts.extend(agent_guidance)
        
        return "\n".join(guidance_parts)
    
    def _analyze_message_for_tool_categories(self, message_lower: str) -> List[str]:
        """Use LLM reasoning to analyze message and determine relevant tool categories"""
        try:
            # Create a lightweight LLM for category analysis
            from config.llm_config import get_agent_llm
            analysis_llm = get_agent_llm("personal_assistant")
            
            # Define available tool categories with descriptions
            category_descriptions = {
                'time_scheduling': 'Time queries, scheduling, calendar management, dates, appointments, meetings, deadlines',
                'weather': 'Weather information, forecasts, temperature, climate conditions, location-based weather',
                'memory_conversation': 'Remembering information, storing facts about people, contacts, relationships, entity extraction',
                'finance': 'Money management, expenses, spending, transactions, budgets, financial analysis, costs, payments',
                'health': 'Health data, fitness tracking, sleep analysis, exercise, wellness, medical information, activity monitoring',
                'document_processing': 'Document analysis, text extraction, file processing, summarization, content analysis, PDF handling'
            }
            
            # Create analysis prompt
            analysis_prompt = f"""Analyze this user message and determine which tool categories are most relevant. 
            
Message: "{message_lower}"

Available tool categories:
{chr(10).join([f"- {cat}: {desc}" for cat, desc in category_descriptions.items()])}

Rules:
1. Select ONLY the categories that are directly relevant to fulfilling the user's request
2. Consider the user's intent and what tools would be needed to provide a complete response
3. Return category names as a comma-separated list (no explanations)
4. If multiple categories apply, include all relevant ones
5. If no categories clearly apply, return "general"

Categories needed:"""

            # Get LLM analysis
            response = analysis_llm.invoke(analysis_prompt)
            
            # Parse response
            if hasattr(response, 'content'):
                category_text = response.content.strip()
            else:
                category_text = str(response).strip()
            
            # Clean and parse categories
            if category_text.lower() == "general" or not category_text:
                return []
            
            categories = [cat.strip() for cat in category_text.split(',') if cat.strip() in category_descriptions]
            
            logger.info(f"🧠 LLM-analyzed categories for '{message_lower[:50]}...': {categories}")
            return categories
            
        except Exception as e:
            logger.warning(f"LLM category analysis failed, using fallback: {e}")
            # Fallback to minimal keyword detection only if LLM fails
            return self._fallback_category_detection(message_lower)
    
    def _fallback_category_detection(self, message_lower: str) -> List[str]:
        """Minimal fallback category detection if LLM analysis fails"""
        categories = []
        
        # Only detect the most obvious cases as fallback
        if any(word in message_lower for word in ['time', 'weather', 'remember', 'spend', 'health', 'document']):
            if 'time' in message_lower:
                categories.append('time_scheduling')
            if 'weather' in message_lower:
                categories.append('weather')
            if 'remember' in message_lower:
                categories.append('memory_conversation')
            if 'spend' in message_lower or '$' in message_lower:
                categories.append('finance')
            if 'health' in message_lower:
                categories.append('health')
            if 'document' in message_lower or 'pdf' in message_lower:
                categories.append('document_processing')
        
        return categories
    
    def _get_category_specific_guidance(self, category: str, agent_role: str) -> List[str]:
        """Get specific guidance for a tool category"""
        guidance_map = {
            'time_scheduling': [
                "🕐 TIME & SCHEDULING TOOLS:",
                "• get_current_time → Use IANA timezone format (e.g., 'America/Los_Angeles')",
                "• calculate_time_difference → For durations, deadlines, and time spans",
                "• format_date → Convert dates to user-friendly formats",
                "• calendar_query → Use action parameter: 'get_todays_events', 'get_upcoming_events'",
                "INTELLIGENT REASONING: Infer timezone from user context, ask if ambiguous"
            ],
            'weather': [
                "🌤️ WEATHER TOOLS:",
                "• local_weather → Current conditions with location parameter",
                "• weather_api → Detailed forecasts with forecast=true, days parameter",
                "• format_weather → User-friendly weather display formatting",
                "INTELLIGENT REASONING: Infer location from context or user profile"
            ],
            'memory_conversation': [
                "🧠 MEMORY & CONVERSATION TOOLS:",
                "• extract_conversation_entities → Extract people, organizations, relationships",
                "• infer_conversation_intent → Detect user intentions and required actions",
                "• extract_from_conversation_history → Process conversation for insights",
                "• search_memory → Query personal knowledge and relationship data",
                "INTELLIGENT REASONING: Automatically extract and validate all factual information"
            ],
            'finance': [
                "💰 FINANCE TOOLS:",
                "• get_recent_expenses → Filter by days, category, amount ranges",
                "• search_transactions → Query with date ranges and amount filters",
                "• get_spending_summary → Analyze spending patterns and trends",
                "• finance_tool → Create, update, categorize transactions",
                "INTELLIGENT REASONING: Convert natural language amounts to proper formats"
            ],
            'health': [
                "🏥 HEALTH TOOLS:",
                "• health_query → Use action parameter for specific data types",
                "• health_query_simple → Quick health overviews and summaries",
                "• health_summary_simple → Trend analysis and health insights",
                "INTELLIGENT REASONING: Respect privacy, provide contextual insights only"
            ],
            'document_processing': [
                "📄 DOCUMENT PROCESSING TOOLS:",
                "• process_document → Full document analysis with extraction options",
                "• extract_document_text → Content extraction from various formats",
                "• search_document → Query document content for specific information",
                "• summarize_document → Generate key insights and summaries",
                "INTELLIGENT REASONING: Choose extraction methods based on document type"
            ]
        }
        
        return guidance_map.get(category, [])
    
    def _get_agent_specific_reasoning(self, agent_role: str) -> List[str]:
        """Get agent-specific reasoning patterns"""
        if agent_role == "personal_assistant":
            return [
                "🎯 PERSONAL ASSISTANT INTELLIGENCE:",
                "• MULTI-TOOL ORCHESTRATION → Combine multiple tools for comprehensive assistance",
                "• CONTEXT SYNTHESIS → Merge time + weather + calendar for smart planning",
                "• PROACTIVE EXTRACTION → Automatically capture entities and relationships",
                "• INTELLIGENT PRIORITIZATION → Focus on user needs and expected outcomes",
                "",
                "⚠️ CRITICAL: Use LLM reasoning for tool selection, NOT keyword matching"
            ]
        elif agent_role == "shadow_agent":
            return [
                "🔮 SHADOW AGENT INTELLIGENCE:",
                "• BEHAVIORAL PATTERN ANALYSIS → Focus on user habits and preferences",
                "• SILENT LEARNING → Extract insights without direct user interaction",
                "• CONTEXT ENHANCEMENT → Provide background intelligence for other agents",
                "• PREFERENCE MODELING → Build understanding of communication styles",
                "",
                "⚠️ CRITICAL: Never be primary responder, enhance other agents' capabilities"
            ]
        else:
            return [
                "⚠️ CRITICAL TOOL SELECTION PRINCIPLES:",
                "• AGENT-BASED SELECTION → Use sophisticated LLM reasoning",
                "• REASONING TRANSPARENCY → Always explain tool choice rationale",
                "• CONTEXT AWARENESS → Consider user needs, timing, and expected outcomes"
            ]
            
            
