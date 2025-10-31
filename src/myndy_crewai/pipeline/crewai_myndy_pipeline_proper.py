"""
title: CrewAI-Myndy Intelligence Pipeline
author: Jeremy
version: 1.0.0
license: MIT
description: Intelligent agent routing and myndy tool execution for OpenWebUI. Provides 5 specialized AI agents with proactive learning and memory management.
requirements: crewai, fastapi, uvicorn, pydantic
"""

import os
import sys
import logging
import uuid
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

class Pipeline:
    """CrewAI-Myndy Pipeline for OpenWebUI"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        enable_contact_management: bool = True
        enable_memory_search: bool = True
        debug_mode: bool = False
        myndy_path: str = "/Users/jeremy/myndy"
        
    def __init__(self):
        """Initialize the pipeline"""
        self.type = "manifold"  # Manifold type for multiple agents
        self.id = "crewai_myndy"
        self.name = "CrewAI-Myndy"
        self.version = "1.0.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # Import components
        self._import_components()
        
        # Initialize conversation sessions
        self.conversation_sessions = {}
        
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
        
        logger.info(f"CrewAI-Myndy Pipeline {self.version} initialized")
        
    def on_startup(self):
        """Called when the pipeline starts up"""
        logger.info("CrewAI-Myndy Pipeline starting up...")
        
    def on_shutdown(self):
        """Called when the pipeline shuts down"""
        logger.info("CrewAI-Myndy Pipeline shutting down...")
        
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models/agents for OpenWebUI compatibility"""
        models = []
        
        # Add auto-routing model
        models.append({
            "id": "auto",
            "name": "🤖 Auto (Intelligent Routing)",
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
        
    def _import_components(self):
        """Import CrewAI and Myndy components"""
        try:
            # Add parent directory to path for imports
            import sys
            import os
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            # Import agent router
            from api.agent_router import get_agent_router, AgentRole
            self.router = get_agent_router()
            self.AgentRole = AgentRole
            
            # Import CrewAI crews and agent factory functions
            from crews.personal_productivity_crew import PersonalProductivityCrew
            from agents import (
                create_memory_librarian,
                create_research_specialist,
                create_personal_assistant,
                create_health_analyst,
                create_finance_tracker
            )
            
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
        
    def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], 
             body: Dict[str, Any]) -> Union[str, Generator, Iterator]:
        """Process messages through the pipeline"""
        
        if self.valves.debug_mode:
            logger.info(f"Pipeline called with model: {model_id}, message: {user_message}")
            
        try:
            # Get session ID for conversation tracking
            session_id = self._get_session_id(messages)
            
            # Update conversation history
            self._update_conversation_history(session_id, messages)
            
            # Use CrewAI to handle the entire conversation
            if self.crewai_available:
                # Route to appropriate CrewAI agent/crew
                response = self._execute_crewai_pipeline(user_message, model_id, session_id)
            else:
                # Simple fallback response when CrewAI not available
                response = "CrewAI agents are not available. Please ensure all dependencies are properly installed."
            
            return response
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
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
            if model_id == "auto":
                # Use intelligent routing
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
                return self._format_crewai_response(result, selected_agent, routing_info)
            else:
                # Fallback if agent not found
                return f"Agent '{selected_agent}' not available in CrewAI system."
                
        except Exception as e:
            logger.error(f"CrewAI pipeline execution error: {e}")
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
                expected_output="A detailed response addressing the user's request with any relevant information found, actions taken, and proactive updates made to the knowledge base."
            )
            
            # Execute the task - the agent will handle tool selection and execution
            result = task.execute()
            
            return str(result)
            
        except Exception as e:
            logger.error(f"CrewAI agent execution error: {e}")
            return f"Agent execution error: {str(e)}"
            
    def _create_task_description(self, user_message: str, agent_role: str) -> str:
        """Create appropriate task description for CrewAI agent based on role"""
        
        base_description = f"User message: '{user_message}'\\n\\n"
        
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
Your task is to:
1. Conduct thorough research on the topic mentioned
2. Gather information from reliable sources
3. Analyze and synthesize the findings
4. Provide comprehensive, well-sourced information
5. Verify facts and identify any conflicting information
"""
        elif agent_role == "personal_assistant":
            return base_description + """
Your task is to:
1. Help with scheduling, calendar management, and productivity
2. Organize tasks and priorities
3. Manage contacts and communications
4. Coordinate meetings and events
5. Provide workflow optimization suggestions
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
            response_parts.append(f"🤖 **{agent_info['name']}** (Auto-selected)")
            response_parts.append(f"**Routing:** {routing_info['reasoning']}")
        else:
            response_parts.append(f"🎯 **{agent_info['name']}** (Direct selection)")
            
        response_parts.append("")  # Empty line
        
        # CrewAI agent result
        response_parts.append(f"**Response:** {result}")
        
        # Collaboration suggestions
        if routing_info.get("collaboration"):
            collab_names = [self.agents.get(role, {}).get('name', role) for role in routing_info['collaboration']]
            response_parts.append(f"\\n**💡 Collaboration Suggestion:** Consider working with {', '.join(collab_names)} for a comprehensive approach.")
            
        return "\\n".join(response_parts)
        
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