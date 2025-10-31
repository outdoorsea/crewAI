"""
title: Myndy AI Standalone Pipeline
author: Jeremy
version: 1.0.0
license: MIT
description: Standalone Myndy AI pipeline that doesn't require external server
requirements: requests
"""

import logging
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Generator, Iterator
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    """Standalone Myndy AI Pipeline for OpenWebUI Upload"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        debug_mode: bool = False
        # Option to connect to external CrewAI server
        use_external_server: bool = False
        external_server_url: str = "http://localhost:9091"
    
    def __init__(self):
        """Initialize the standalone pipeline"""
        self.type = "manifold"  # Enable multiple models
        self.name = "Myndy AI"
        self.version = "1.0.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # Define available agents (these work standalone)
        self.agents = [
            {
                "id": "personal_assistant",
                "name": "Personal Assistant",
                "description": "Comprehensive AI assistant for productivity and general tasks"
            },
            {
                "id": "memory_librarian", 
                "name": "Memory Librarian",
                "description": "Specialized in information organization and knowledge management"
            },
            {
                "id": "research_specialist",
                "name": "Research Specialist", 
                "description": "Expert in analysis and information gathering"
            },
            {
                "id": "health_analyst",
                "name": "Health Analyst",
                "description": "Specialized in health and wellness insights"
            },
            {
                "id": "finance_tracker",
                "name": "Finance Tracker",
                "description": "Expert in financial analysis and budget tracking"
            }
        ]
        
        logger.info(f"🚀 Standalone Myndy AI Pipeline initialized with {len(self.agents)} agents")
    
    async def on_startup(self):
        """Called when the pipeline starts up"""
        logger.info("🚀 Myndy AI Standalone Pipeline starting...")
        if self.valves.use_external_server:
            await self._test_external_connection()
        
    async def on_shutdown(self):
        """Called when the pipeline shuts down"""
        logger.info("🛑 Myndy AI Standalone Pipeline shutting down...")
        
    async def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info("⚙️ Pipeline valves updated")
        if self.valves.use_external_server:
            await self._test_external_connection()
    
    async def _test_external_connection(self):
        """Test connection to external CrewAI server"""
        try:
            response = requests.get(f"{self.valves.external_server_url}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Connected to external CrewAI server")
            else:
                logger.warning("⚠️ External server responded but with error status")
        except Exception as e:
            logger.warning(f"⚠️ Cannot connect to external server: {e}")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models for OpenWebUI"""
        models = []
        for agent in self.agents:
            models.append({
                "id": agent["id"],
                "name": f"{agent['name']}",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "myndy-ai",
                "description": agent["description"]
            })
        return models
    
    def _intelligent_route(self, user_message: str) -> str:
        """Simple keyword-based routing"""
        message_lower = user_message.lower()
        
        # Health keywords
        if any(keyword in message_lower for keyword in ['health', 'fitness', 'exercise', 'medical', 'wellness']):
            return "health_analyst"
        
        # Finance keywords  
        if any(keyword in message_lower for keyword in ['money', 'expense', 'budget', 'financial', 'cost', 'dollar']):
            return "finance_tracker"
        
        # Research keywords
        if any(keyword in message_lower for keyword in ['research', 'analyze', 'study', 'investigate']):
            return "research_specialist"
        
        # Memory keywords
        if any(keyword in message_lower for keyword in ['remember', 'save', 'contact', 'person', 'relationship']):
            return "memory_librarian"
        
        # Default to personal assistant
        return "personal_assistant"
    
    def _get_agent_response(self, agent_id: str, user_message: str, messages: List[Dict[str, Any]]) -> str:
        """Generate agent-specific responses"""
        
        agent_map = {agent["id"]: agent for agent in self.agents}
        agent = agent_map.get(agent_id, self.agents[0])
        
        # If external server is enabled, try that first
        if self.valves.use_external_server:
            try:
                response = requests.post(
                    f"{self.valves.external_server_url}/myndy_ai/chat/completions",
                    json={
                        "model": agent_id,
                        "messages": messages
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return f"**{agent['name']}** (via CrewAI): {result['choices'][0]['message']['content']}"
                    else:
                        return f"**{agent['name']}** (via CrewAI): {result.get('response', str(result))}"
            except Exception as e:
                logger.warning(f"External server failed: {e}, falling back to local response")
        
        # Fallback to local responses
        responses = {
            "personal_assistant": f"Hello! I'm your Personal Assistant. You asked: '{user_message}'\n\nI can help you with:\n• Calendar and scheduling\n• Email management\n• Task organization\n• General productivity\n• Information management\n\nTo access full functionality including real-time data, calendar integration, and tool execution, connect me to the Myndy AI backend server.",
            
            "memory_librarian": f"As your Memory Librarian, I'm analyzing: '{user_message}'\n\nI specialize in:\n• Contact and relationship management\n• Information organization\n• Knowledge base management\n• Entity relationship mapping\n• Memory search and retrieval\n\nFor full memory integration with your personal data, I need connection to the Myndy AI memory systems.",
            
            "research_specialist": f"Research Specialist here. You've asked me to research: '{user_message}'\n\nI can help with:\n• Information analysis\n• Document processing\n• Fact verification\n• Research methodology\n• Report generation\n\nFor live web research and document access, connect to the full Myndy AI research tools.",
            
            "health_analyst": f"Health Analyst responding to: '{user_message}'\n\nI focus on:\n• Health data analysis\n• Fitness tracking insights\n• Wellness recommendations\n• Activity monitoring\n• Medical information organization\n\nTo analyze your actual health data and provide personalized insights, I need access to the Myndy AI health tracking systems.",
            
            "finance_tracker": f"Finance Tracker analyzing: '{user_message}'\n\nI can assist with:\n• Expense categorization\n• Budget analysis\n• Spending pattern insights\n• Financial planning\n• Transaction management\n\nFor real financial data analysis and personalized recommendations, connect to the Myndy AI financial tracking backend."
        }
        
        base_response = responses.get(agent_id, f"Agent {agent['name']}: {user_message}")
        
        return f"**{agent['name']}**: {base_response}"
    
    def pipe(
        self, 
        user_message: str, 
        model_id: str, 
        messages: List[Dict[str, Any]], 
        body: Dict[str, Any]
    ) -> str:
        """Main pipeline processing"""
        
        logger.info(f"💬 Message: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
        logger.info(f"🤖 Selected agent: {model_id}")
        
        if self.valves.debug_mode:
            logger.info(f"📝 Full body: {json.dumps(body, indent=2)}")
        
        # Use intelligent routing if enabled
        if self.valves.enable_intelligent_routing and model_id not in [agent["id"] for agent in self.agents]:
            model_id = self._intelligent_route(user_message)
            logger.info(f"🧠 Auto-routed to: {model_id}")
        
        # Generate response
        response = self._get_agent_response(model_id, user_message, messages)
        
        # Add debug info if enabled
        if self.valves.debug_mode:
            response += f"\n\n---\n*Debug: Agent={model_id}, External Server={'Enabled' if self.valves.use_external_server else 'Disabled'}*"
        
        return response