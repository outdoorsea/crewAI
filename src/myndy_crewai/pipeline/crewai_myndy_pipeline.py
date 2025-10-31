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
        
        # Simplified tie-breaking logic for two agents
        if len(tied_agents) > 1:
            # Always prefer personal_assistant in ties (comprehensive agent)
            if "personal_assistant" in tied_agents:
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
        
        # Simplified fallback logic for only two agents
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
        
        # Agent definitions - simplified to only personal assistant and shadow agent
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
            }
        }
        
        # Tool registry initialization disabled - using direct tool execution
        # self._initialize_tool_registry()
        
        logger.info(f"🎉 Myndy AI v{self.version} - Personal Intelligence Pipeline initialized")
        logger.info(f"📊 Available agents: {list(self.agents.keys())}")
        logger.info(f"🔧 CrewAI available: {getattr(self, 'crewai_available', False)}")
        if hasattr(self, 'crewai_agents'):
            logger.info(f"🤖 CrewAI agents loaded: {list(self.crewai_agents.keys())}")
        logger.info(f"✅ Simplified to 2 agents: Personal Assistant + Shadow Agent")
        
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
            
            # Get agent creation functions from the crew module (only the two we need)
            create_personal_assistant = crew_module.create_personal_assistant
            create_shadow_agent = crew_module.create_shadow_agent
            
            # Initialize CrewAI components - simplified to only 2 agents
            self.crew_manager = PersonalProductivityCrew(verbose=True)
            self.crewai_agents = {
                "personal_assistant": create_personal_assistant(),
                "shadow_agent": create_shadow_agent()
            }
            
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
        
    def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], 
             body: Dict[str, Any]) -> Union[str, Generator, Iterator]:
        """Process messages through the pipeline"""
        
        # Always log pipeline calls for visibility
        logger.info(f"🎯 Pipeline called: model={model_id}, message_length={len(user_message)} chars")
        if self.valves.debug_mode:
            logger.info(f"📝 Full message: {user_message[:200]}{'...' if len(user_message) > 200 else ''}")
            
        try:
            # Get session ID for conversation tracking
            session_id = self._get_session_id(messages)
            logger.info(f"💬 Session ID: {session_id}")
            
            # Update conversation history
            self._update_conversation_history(session_id, messages)
            logger.info(f"📚 Updated conversation history ({len(messages)} messages)")
            
            # Use CrewAI to handle the entire conversation
            if self.crewai_available:
                logger.info(f"🤖 Routing to CrewAI agents...")
                # Route to appropriate CrewAI agent/crew
                response = self._execute_crewai_pipeline(user_message, model_id, session_id)
                logger.info(f"✅ CrewAI response generated (length: {len(response)} chars)")
            else:
                logger.warning("⚠️ CrewAI agents not available, using fallback")
                # Simple fallback response when CrewAI not available
                response = "CrewAI agents are not available. Please ensure all dependencies are properly installed."
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
            
    def _get_session_id(self, messages: List[Dict[str, Any]]) -> str:
        """Generate session ID for conversation tracking"""
        # Simple approach: hash the conversation content
        content_hash = str(abs(hash(str([msg.get("content", "") for msg in messages]))))
        return f"session_{content_hash[:8]}"
        
    def _update_conversation_history(self, session_id: str, messages: List[Dict[str, Any]]):
        """Update conversation history for a session"""
        if session_id not in self.conversation_sessions:
            self.conversation_sessions[session_id] = {
                "created_at": datetime.now(),
                "messages": [],
                "agent_history": []
            }
            
        # Store recent messages
        self.conversation_sessions[session_id]["messages"] = messages[-20:]  # Keep last 20 messages
        
    def _execute_crewai_pipeline(self, user_message: str, model_id: str, session_id: str) -> str:
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
                
                # Execute the agent with the message
                # CrewAI agents handle their own tool selection and execution
                result = self._execute_crewai_agent(crewai_agent, user_message, selected_agent)
                logger.info(f"✅ Agent {selected_agent} completed execution")
                
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
            
    def _execute_crewai_agent(self, agent, user_message: str, agent_role: str) -> str:
        """Execute a specific CrewAI agent with the user message"""
        try:
            # Create a task for the agent
            from crewai import Task
            
            # Define the task based on the message and agent role
            task_description = self._create_task_description(user_message, agent_role)
            
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
            
    def _create_task_description(self, user_message: str, agent_role: str) -> str:
        """Create appropriate task description for CrewAI agent based on role"""
        
        base_description = f"User message: '{user_message}'\n\n"
        
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
        else:
            return base_description + "Please assist the user with their request using your available tools and capabilities."
            
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


if __name__ == "__main__":
    import sys
    import uvicorn
    import os
    import signal
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from contextlib import asynccontextmanager
    import time
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode - verify pipeline can be created
        print("🧪 Testing Myndy AI Pipeline...")
        try:
            pipeline = Pipeline()
            models = pipeline.get_models()
            print(f"✅ Pipeline created successfully with {len(models)} models")
            print("🎯 Available models:")
            for model in models:
                print(f"   - {model['name']} ({model['id']})")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Pipeline test failed: {e}")
            sys.exit(1)
    
    # Server mode (default)
    pipeline = Pipeline()
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan manager"""
        logger.info("🚀 Myndy AI Pipeline server starting up...")
        if hasattr(pipeline, 'on_startup'):
            await pipeline.on_startup()
        yield
        logger.info("🛑 Myndy AI Pipeline server shutting down...")
        if hasattr(pipeline, 'on_shutdown'):
            await pipeline.on_shutdown()

    # Create FastAPI app
    app = FastAPI(
        title="Myndy AI Pipeline",
        description="Myndy AI - Personal Intelligence Pipeline for Open WebUI",
        version=pipeline.version,
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests with timing"""
        start_time = time.time()
        logger.info(f"📥 {request.method} {request.url.path}")
        response = await call_next(request)
        process_time = time.time() - start_time
        status_emoji = "✅" if response.status_code < 400 else "❌"
        logger.info(f"📤 {status_emoji} {response.status_code} | {process_time:.3f}s")
        return response

    # Root endpoint - pipeline manifest
    @app.get("/")
    async def get_pipeline_manifest():
        """Get pipeline manifest for Open WebUI"""
        return pipeline.get_manifest()

    # Models endpoint for Open WebUI
    @app.get("/models")
    async def get_models():
        """Get available models"""
        logger.info("📋 Models endpoint accessed")
        models = pipeline.get_models()
        return {
            "data": models,
            "object": "list"
        }

    # Alternative models endpoint
    @app.get("/v1/models")
    async def get_models_v1():
        """Get available models (OpenAI compatible)"""
        logger.info("📋 Models endpoint (v1) accessed")
        models = pipeline.get_models()
        return {
            "data": models,
            "object": "list"
        }

    # Chat completions endpoint
    @app.post("/v1/chat/completions")
    async def chat_completions(request: dict):
        """Handle chat completions (OpenAI compatible)"""
        logger.info("💬 Chat completions endpoint accessed")
        
        try:
            messages = request.get("messages", [])
            model_id = request.get("model", "auto")
            stream = request.get("stream", False)
            
            # Extract user message
            user_message = ""
            for message in reversed(messages):
                if message.get("role") == "user":
                    user_message = message.get("content", "")
                    break
            
            if not user_message:
                raise HTTPException(status_code=400, detail="No user message found")
            
            logger.info(f"💬 Processing: {user_message[:50]}...")
            
            # Process through pipeline
            response_text = pipeline.pipe(
                user_message=user_message,
                model_id=model_id,
                messages=messages,
                body=request
            )
            
            # Format response
            from datetime import datetime
            response = {
                "id": f"chatcmpl-{int(datetime.now().timestamp())}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": model_id,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(user_message.split()),
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": len(user_message.split()) + len(response_text.split())
                }
            }
            
            if stream:
                # TODO: Implement streaming response
                pass
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Chat completion error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "pipeline": pipeline.name,
            "version": pipeline.version,
            "models": len(pipeline.get_models())
        }

    # Status endpoint
    @app.get("/status")
    async def get_status():
        """System status and metrics"""
        logger.info("📊 Status endpoint accessed")
        return {
            "status": "healthy",
            "pipeline": pipeline.name,
            "version": pipeline.version,
            "type": pipeline.type,
            "models_available": len(pipeline.get_models()),
            "crewai_available": getattr(pipeline, 'crewai_available', False)
        }

    print("🚀 Starting Myndy AI Pipeline Server")
    print("=" * 50)
    print(f"📊 Pipeline: {pipeline.name} v{pipeline.version}")
    print(f"🤖 Available models: {len(pipeline.get_models())}")
    print("🌐 Server will be available at: http://localhost:9099")
    print("🔗 Add to Open WebUI: http://localhost:9099")
    print("🔑 Pipeline API Key: 0p3n-w3bu!")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    print()
    
    # Enhanced port handling with automatic process cleanup
    import subprocess
    
    def kill_process_on_port(port):
        """Kill any process using the specified port"""
        try:
            # Find process using the port
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        pid = int(pid.strip())
                        logger.info(f"🔄 Killing existing process {pid} on port {port}")
                        print(f"🔄 Killing existing process {pid} on port {port}")
                        os.kill(pid, signal.SIGTERM)
                        # Give it a moment to cleanly shut down
                        time.sleep(1)
                    except (ValueError, ProcessLookupError, PermissionError) as e:
                        logger.warning(f"⚠️ Could not kill process {pid}: {e}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.warning(f"⚠️ Could not check port {port}: {e}")
        return False
    
    port = 9099
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            uvicorn.run(
                app, 
                host="0.0.0.0", 
                port=port,
                log_config=None,
                access_log=False
            )
            break
        except OSError as e:
            if "address already in use" in str(e).lower():
                if attempt == 0:
                    # First attempt: try to kill existing process
                    logger.info(f"📍 Port {port} in use, attempting to clean up existing process...")
                    print(f"📍 Port {port} in use, attempting to clean up existing process...")
                    if kill_process_on_port(port):
                        # Try the same port again after cleanup
                        continue
                
                if attempt < max_attempts - 1:
                    # Subsequent attempts: try next port
                    port += 1
                    logger.warning(f"⚠️ Port {port-1} still in use, trying port {port}")
                    print(f"⚠️ Port {port-1} still in use, trying port {port}")
                else:
                    logger.error(f"❌ Failed to start server after {max_attempts} attempts")
                    print(f"❌ Failed to start server after {max_attempts} attempts")
                    print(f"💡 Manual cleanup: pkill -f 'crewai_myndy_pipeline.py'")
                    raise
            else:
                logger.error(f"❌ Failed to start server: {e}")
                raise

