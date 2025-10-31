"""
title: Myndy AI v0.1 - Personal Intelligence Pipeline with Feedback Analytics
author: Jeremy
version: 0.1.1
license: MIT
description: Myndy AI - Your personal intelligent assistant with conversation-driven learning and feedback analytics. Features 5 specialized agents, automatic status/profile updates, comprehensive tool integration, and performance tracking.
requirements: crewai, fastapi, uvicorn, pydantic
"""

import os
import sys
import logging
import uuid
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Generator, Iterator
from pathlib import Path

# Add project paths
PIPELINE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path("/Users/jeremy/myndy")))

from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentRouter:
    """Intelligent agent routing based on message content and tool requirements"""
    
    def __init__(self):
        self.agent_patterns = {
            "memory_librarian": {
                "keywords": ["remember", "contact", "person", "email", "phone", "address", "remember", "save", "store", "update", "delete", "information", "database", "knowledge", "entity", "relationship"],
                "patterns": [
                    r"\b\w+@\w+\.\w+\b",  # email addresses
                    r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # phone numbers
                    r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # person names
                    r"works at|employed by|job at|company|organization",
                    r"lives in|address|location|located at"
                ],
                "description": "Handles contact management, person/entity tracking, conversation analysis"
            },
            "research_specialist": {
                "keywords": ["research", "analyze", "document", "text", "sentiment", "language", "summarize", "extract", "study", "investigate", "report", "paper", "article", "analysis", "insights"],
                "patterns": [
                    r"analyze.*sentiment|sentiment.*analysis",
                    r"summarize|summary",
                    r"extract.*from|parse.*document",
                    r"research.*topic|investigate",
                    r"what.*language|detect.*language",
                    r"document.*analysis"
                ],
                "description": "Handles text analysis, document processing, research, sentiment analysis"
            },
            "personal_assistant": {
                "keywords": ["calendar", "schedule", "appointment", "meeting", "time", "date", "weather", "temperature", "forecast", "remind", "task", "todo", "organize", "plan", "event", "deadline"],
                "patterns": [
                    r"what.*time|current.*time|time.*now",
                    r"weather|temperature|forecast",
                    r"temperature.*in|weather.*in",  # High priority for location-based weather
                    r"schedule|calendar|appointment",
                    r"remind.*me|set.*reminder",
                    r"what.*date|today.*date",
                    r"meeting|event"
                ],
                "description": "Handles scheduling, time management, weather, reminders, organization"
            },
            "health_analyst": {
                "keywords": ["health", "fitness", "exercise", "sleep", "steps", "heart", "blood", "medical", "wellness", "workout", "activity", "calories"],
                "patterns": [
                    r"health.*data|fitness.*data",
                    r"sleep.*pattern|sleep.*quality",
                    r"exercise|workout|physical.*activity",
                    r"heart.*rate|blood.*pressure",
                    r"steps|calories|weight"
                ],
                "description": "Handles health data analysis, fitness tracking, wellness monitoring"
            },
            "finance_tracker": {
                "keywords": ["money", "expense", "cost", "budget", "spending", "transaction", "financial", "price", "payment", "bank", "account", "dollar", "finance"],
                "patterns": [
                    r"\$\d+|\d+.*dollar",  # money amounts
                    r"expense|spending|cost",
                    r"budget|financial|transaction",
                    r"paid|payment|bank|account"
                ],
                "description": "Handles financial tracking, expense analysis, budgeting, transactions"
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
            
            agent_scores[agent] = score
        
        # Find best match with tie-breaking
        max_score = max(agent_scores.values())
        tied_agents = [agent for agent, score in agent_scores.items() if score == max_score]
        
        # Tie-breaking logic based on message content
        if len(tied_agents) > 1:
            # Prefer personal_assistant for weather/time queries
            if any(word in message_lower for word in ["weather", "temperature", "forecast", "time"]) and "personal_assistant" in tied_agents:
                best_agent = "personal_assistant"
            # Prefer memory_librarian for contact/person queries
            elif any(word in message_lower for word in ["contact", "person", "remember", "save"]) and "memory_librarian" in tied_agents:
                best_agent = "memory_librarian"
            # Prefer research_specialist for analysis queries
            elif any(word in message_lower for word in ["analyze", "research", "document"]) and "research_specialist" in tied_agents:
                best_agent = "research_specialist"
            else:
                best_agent = tied_agents[0]  # Default to first
        else:
            best_agent = max(agent_scores, key=agent_scores.get)
        
        best_score = agent_scores[best_agent]
        
        # Improved fallback logic based on message content
        if best_score == 0:
            # Smart fallback based on common query types
            if any(word in message_lower for word in ["weather", "temperature", "forecast", "time", "date", "schedule", "calendar"]):
                best_agent = "personal_assistant"
                reasoning = "Weather/time query detected, routing to Personal Assistant"
            elif any(word in message_lower for word in ["health", "fitness", "exercise", "sleep", "medical"]):
                best_agent = "health_analyst"
                reasoning = "Health query detected, routing to Health Analyst"
            elif any(word in message_lower for word in ["money", "cost", "expense", "budget", "financial", "price", "dollar"]):
                best_agent = "finance_tracker"
                reasoning = "Financial query detected, routing to Finance Tracker"
            elif any(word in message_lower for word in ["analyze", "research", "document", "text", "sentiment"]):
                best_agent = "research_specialist"
                reasoning = "Analysis query detected, routing to Research Specialist"
            else:
                best_agent = "personal_assistant"  # Changed default from memory_librarian
                reasoning = "General query, routing to Personal Assistant as default"
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
    """Myndy AI v0.1.1 - Personal Intelligence Pipeline with Feedback Analytics for OpenWebUI"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        enable_contact_management: bool = True
        enable_memory_search: bool = True
        enable_feedback_analytics: bool = True  # New: Enable feedback tracking
        debug_mode: bool = False
        memex_path: str = "/Users/jeremy/myndy"
        api_key: str = "0p3n-w3bu!"  # Standard OpenWebUI pipeline key
        
    def __init__(self):
        """Initialize the pipeline"""
        self.type = "manifold"  # Manifold type for multiple agents
        self.id = "myndy_ai_feedback"
        self.name = "Myndy AI"
        self.version = "0.1.1"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # Import components
        self._import_components()
        
        # Initialize conversation sessions
        self.conversation_sessions = {}
        
        # Initialize feedback analytics
        self._initialize_feedback_analytics()
        
        # Agent definitions
        self.agents = {
            "memory_librarian": {
                "name": "Memory Librarian",
                "description": "Organizes and retrieves personal knowledge, entities, conversation history, and manages contact information",
                "model": "llama3",
                "capabilities": ["memory management", "entity relationships", "conversation history", "contact information", "contact updates", "company tracking"]
            },
            "research_specialist": {
                "name": "Research Specialist",
                "description": "Conducts research, gathers information, and verifies facts",
                "model": "mixtral", 
                "capabilities": ["web research", "fact verification", "document analysis"]
            },
            "personal_assistant": {
                "name": "Personal Assistant",
                "description": "Manages calendar, email, contacts, and personal productivity",
                "model": "gemma",
                "capabilities": ["calendar management", "email processing", "task coordination"]
            },
            "health_analyst": {
                "name": "Health Analyst", 
                "description": "Analyzes health data and provides wellness insights",
                "model": "phi",
                "capabilities": ["health analysis", "fitness tracking", "wellness optimization"]
            },
            "finance_tracker": {
                "name": "Finance Tracker",
                "description": "Tracks expenses, analyzes spending, and provides financial insights", 
                "model": "mistral",
                "capabilities": ["expense tracking", "budget analysis", "financial planning"]
            }
        }
        
        logger.info(f"Myndy AI v{self.version} - Personal Intelligence Pipeline with Feedback Analytics initialized")
        
    def _initialize_feedback_analytics(self):
        """Initialize feedback analytics system."""
        try:
            # Import feedback analytics
            sys.path.insert(0, str(PIPELINE_ROOT / "tools"))
            from feedback_analytics import FeedbackAnalytics
            
            self.feedback_analytics = FeedbackAnalytics()
            self.feedback_enabled = True
            logger.info("Feedback analytics system initialized")
            
        except Exception as e:
            logger.warning(f"Could not initialize feedback analytics: {e}")
            self.feedback_analytics = None
            self.feedback_enabled = False
        
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
            "description": "Myndy AI - Your personal intelligent assistant with conversation-driven learning and feedback analytics",
            "author": "Jeremy",
            "license": "MIT",
            "models": self._get_models(),
            "features": ["intelligent_routing", "feedback_analytics", "performance_tracking", "agent_collaboration"]
        }
        
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
            
            # Define AgentRole enum locally
            class AgentRole:
                MEMORY_LIBRARIAN = "memory_librarian"
                RESEARCH_SPECIALIST = "research_specialist"
                PERSONAL_ASSISTANT = "personal_assistant"
                HEALTH_ANALYST = "health_analyst"
                FINANCE_TRACKER = "finance_tracker"
            
            self.AgentRole = AgentRole
            
            # Import CrewAI crews using explicit path
            crew_spec = importlib.util.spec_from_file_location(
                "personal_productivity_crew", os.path.join(parent_dir, "crews", "personal_productivity_crew.py")
            )
            crew_module = importlib.util.module_from_spec(crew_spec)
            crew_spec.loader.exec_module(crew_module)
            PersonalProductivityCrew = crew_module.PersonalProductivityCrew
            
            # Get agent creation functions from the crew module
            create_memory_librarian = crew_module.create_memory_librarian
            create_research_specialist = crew_module.create_research_specialist
            create_personal_assistant = crew_module.create_personal_assistant
            create_health_analyst = crew_module.create_health_analyst
            create_finance_tracker = crew_module.create_finance_tracker
            
            # Initialize CrewAI components
            self.crew_manager = PersonalProductivityCrew(verbose=True)
            self.crewai_agents = {
                "memory_librarian": create_memory_librarian(),
                "research_specialist": create_research_specialist(),
                "personal_assistant": create_personal_assistant(),
                "health_analyst": create_health_analyst(),
                "finance_tracker": create_finance_tracker()
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
            "name": "🧠 Myndy AI v0.1.1 (with Analytics)",
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
        """Process messages through the pipeline with feedback tracking"""
        
        if self.valves.debug_mode:
            logger.info(f"Pipeline called with model: {model_id}, message: {user_message}")
            
        # Track response timing
        start_time = time.time()
        
        try:
            # Get session ID for conversation tracking
            session_id = self._get_session_id(messages)
            
            # Update conversation history
            self._update_conversation_history(session_id, messages)
            
            # Generate response ID for feedback tracking
            response_id = f"response_{uuid.uuid4()}"
            
            # Use CrewAI to handle the entire conversation
            if self.crewai_available:
                # Route to appropriate CrewAI agent/crew
                response, routing_info = self._execute_crewai_pipeline(user_message, model_id, session_id, response_id)
            else:
                # Simple fallback response when CrewAI not available
                response = "CrewAI agents are not available. Please ensure all dependencies are properly installed."
                routing_info = {
                    "agent_id": "system",
                    "agent_name": "System",
                    "routing_confidence": 0.0,
                    "tools_used": []
                }
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Store response metadata for potential feedback
            if self.feedback_enabled and self.feedback_analytics:
                self._store_response_metadata(
                    session_id=session_id,
                    response_id=response_id,
                    user_message=user_message,
                    response_content=response,
                    routing_info=routing_info,
                    response_time_ms=response_time_ms
                )
            
            # Add feedback tracking information to response
            if self.valves.enable_feedback_analytics and self.feedback_enabled:
                response += f"\n\n---\n*Response ID: {response_id} | Time: {response_time_ms}ms | Agent: {routing_info.get('agent_name', 'Unknown')}*"
            
            return response
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _store_response_metadata(self, session_id: str, response_id: str, user_message: str,
                                response_content: str, routing_info: Dict[str, Any], response_time_ms: int):
        """Store response metadata for potential feedback collection."""
        try:
            if session_id not in self.conversation_sessions:
                self.conversation_sessions[session_id] = {
                    "created_at": datetime.now(),
                    "messages": [],
                    "agent_history": [],
                    "response_metadata": {}
                }
            
            # Store response metadata
            self.conversation_sessions[session_id]["response_metadata"][response_id] = {
                "user_message": user_message,
                "response_content": response_content,
                "agent_id": routing_info.get("agent_id", "unknown"),
                "agent_name": routing_info.get("agent_name", "Unknown"),
                "routing_confidence": routing_info.get("routing_confidence", 0.0),
                "response_time_ms": response_time_ms,
                "tools_used": routing_info.get("tools_used", []),
                "collaboration_agents": routing_info.get("collaboration_agents", []),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error storing response metadata: {e}")
    
    def collect_feedback(self, response_id: str, feedback_type: str, feedback_value: Any = None,
                        feedback_text: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Collect user feedback for a specific response.
        
        This method would be called by OpenWebUI when users click thumbs up/down.
        Note: This is a conceptual implementation - actual integration would depend
        on OpenWebUI's feedback mechanism.
        """
        try:
            if not self.feedback_enabled or not self.feedback_analytics:
                return {"success": False, "error": "Feedback analytics not enabled"}
            
            # Find response metadata
            response_metadata = None
            found_session_id = session_id
            
            if not found_session_id:
                # Search all sessions for the response_id
                for sid, session_data in self.conversation_sessions.items():
                    if response_id in session_data.get("response_metadata", {}):
                        found_session_id = sid
                        break
            
            if found_session_id and found_session_id in self.conversation_sessions:
                session_data = self.conversation_sessions[found_session_id]
                response_metadata = session_data.get("response_metadata", {}).get(response_id)
            
            if not response_metadata:
                return {"success": False, "error": f"Response metadata not found for {response_id}"}
            
            # Map feedback types
            from feedback_analytics import FeedbackType
            feedback_type_map = {
                "thumbs_up": FeedbackType.THUMBS_UP,
                "thumbs_down": FeedbackType.THUMBS_DOWN,
                "rating": FeedbackType.RATING,
                "text": FeedbackType.TEXT_FEEDBACK
            }
            
            if feedback_type not in feedback_type_map:
                return {"success": False, "error": f"Invalid feedback type: {feedback_type}"}
            
            # Record feedback
            feedback_id = self.feedback_analytics.record_feedback(
                session_id=found_session_id,
                agent_id=response_metadata["agent_id"],
                agent_name=response_metadata["agent_name"],
                response_id=response_id,
                response_content=response_metadata["response_content"],
                user_message=response_metadata["user_message"],
                feedback_type=feedback_type_map[feedback_type],
                feedback_value=feedback_value,
                routing_confidence=response_metadata["routing_confidence"],
                response_time_ms=response_metadata["response_time_ms"],
                feedback_text=feedback_text,
                tools_used=response_metadata["tools_used"],
                collaboration_agents=response_metadata["collaboration_agents"]
            )
            
            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": f"Feedback recorded for response {response_id}"
            }
            
        except Exception as e:
            logger.error(f"Error collecting feedback: {e}")
            return {"success": False, "error": str(e)}
            
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
                "agent_history": [],
                "response_metadata": {}
            }
            
        # Store recent messages
        self.conversation_sessions[session_id]["messages"] = messages[-20:]  # Keep last 20 messages
        
    def _execute_crewai_pipeline(self, user_message: str, model_id: str, session_id: str, response_id: str) -> tuple:
        """Execute the full CrewAI pipeline with intelligent routing and tool execution"""
        try:
            # Determine which agent/crew to use
            if model_id == "auto" or model_id == "crewai-myndy-pipeline":
                # Use intelligent routing (default for our pipeline)
                selected_agent, routing_info = self._route_message(user_message, session_id)
            else:
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
                
                # Execute the agent with the message
                # CrewAI agents handle their own tool selection and execution
                result = self._execute_crewai_agent(crewai_agent, user_message, selected_agent)
                
                # Format response with routing info
                formatted_response = self._format_crewai_response(result, selected_agent, routing_info)
                
                # Prepare routing info for feedback
                feedback_routing_info = {
                    "agent_id": selected_agent,
                    "agent_name": self.agents.get(selected_agent, {}).get("name", selected_agent),
                    "routing_confidence": routing_info.get("confidence", 0.0),
                    "tools_used": [],  # TODO: Extract from CrewAI execution
                    "collaboration_agents": routing_info.get("collaboration", [])
                }
                
                return formatted_response, feedback_routing_info
            else:
                # Fallback if agent not found
                fallback_response = f"Agent '{selected_agent}' not available in CrewAI system."
                fallback_routing_info = {
                    "agent_id": "system",
                    "agent_name": "System",
                    "routing_confidence": 0.0,
                    "tools_used": [],
                    "collaboration_agents": []
                }
                return fallback_response, fallback_routing_info
                
        except Exception as e:
            logger.error(f"CrewAI pipeline execution error: {e}")
            error_response = f"CrewAI pipeline encountered an error: {str(e)}"
            error_routing_info = {
                "agent_id": "error",
                "agent_name": "Error Handler",
                "routing_confidence": 0.0,
                "tools_used": [],
                "collaboration_agents": []
            }
            return error_response, error_routing_info
            
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
        
        if agent_role == "memory_librarian":
            return base_description + """
Your task as the Memory Librarian is to:

1. **Proactive Information Analysis**: Analyze every message for factual claims about people, places, companies, employment, contact information, and personal details

2. **Database Validation**: Use your memory search tools to validate any factual claims against existing database information

3. **Conflict Detection**: When you find conflicts between stated information and database records:
   - Alert the user with the specific conflict
   - Show what's currently in the database vs what was stated
   - Ask for confirmation before making updates
   - Example: "You said Bryan works at Geocaching HQ, but I have him listed as working at OpenAI. Should I update this?"

4. **Automatic Updates**: For new information that doesn't conflict with existing data:
   - Automatically save it to the appropriate collection using your tools
   - Inform the user what was added
   - Example: "Added new contact: Sarah Chen works at Anthropic"

5. **Information Retrieval**: When users ask about people, companies, or information:
   - Search all relevant collections (contacts, people, memories)
   - Provide comprehensive information including relationships and context

6. **Contact Management**: Handle natural language requests to update contact information, track relationships, and manage organizational changes

**Key Requirement**: Be proactive in every conversation. Extract and validate ALL factual information mentioned, not just direct questions. Use your myndy tools for all database operations - never rely on the pipeline to handle validation or updates.

Your tools include contact search, people search, memory search, contact creation/update, and knowledge base management. Use them actively in every interaction.
"""
        elif agent_role == "research_specialist":
            return base_description + """
Your task as the Research Specialist is to:

1. **Comprehensive Analysis**: Use multiple analysis tools to thoroughly examine the request:
   - Use sentiment analysis tools for emotional content
   - Use language detection for multilingual text
   - Use text analysis tools for detailed insights
   - Use entity extraction to identify key subjects

2. **Document Processing**: When dealing with documents or text:
   - Extract and summarize key information
   - Parse tables and structured data
   - Convert formats if needed
   - Search within documents for specific information

3. **Multi-Tool Approach**: Combine multiple tools for comprehensive analysis:
   - Start with text analysis to understand the content
   - Use specialized tools based on what you find
   - Cross-reference findings using different analytical approaches
   - Provide detailed, well-researched responses

Your available tools include: text analysis, sentiment analysis, language detection, document processing, entity extraction, keyword extraction, summarization, and search capabilities. Use multiple tools as needed to provide thorough analysis.
"""
        elif agent_role == "personal_assistant":
            return base_description + """
Your task as the Personal Assistant is to:

1. **Time Management**: Use time-related tools to help with scheduling:
   - Check current time when needed
   - Calculate time differences for scheduling
   - Format dates and times appropriately
   - Handle timezone conversions

2. **Weather & Environment**: Provide contextual environmental information:
   - Check local weather conditions
   - Format weather data for readability
   - Integrate weather into planning decisions

3. **Calendar & Organization**: Use calendar tools for productivity:
   - Query calendar information
   - Help schedule meetings and events
   - Provide scheduling recommendations
   - Organize tasks and priorities

4. **Multi-Tool Coordination**: Combine tools for comprehensive assistance:
   - Check time AND weather for meeting planning
   - Use multiple formatting tools for consistent output
   - Cross-reference calendar with other data sources

Your available tools include: calendar queries, current time, time calculations, date formatting, weather information, and organizational utilities. Use multiple tools together to provide comprehensive assistance.
"""
        elif agent_role == "health_analyst":
            return base_description + """
Your task is to:
1. Analyze health and fitness data
2. Provide wellness insights and recommendations
3. Track health metrics and progress
4. Suggest health optimizations
5. Monitor and report on health goals
"""
        elif agent_role == "finance_tracker":
            return base_description + """
Your task is to:
1. Analyze financial data and spending patterns
2. Track expenses and categorize transactions
3. Provide budget analysis and recommendations
4. Monitor financial goals and progress
5. Generate financial reports and insights
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