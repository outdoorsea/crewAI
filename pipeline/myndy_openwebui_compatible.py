"""
title: Myndy AI - Multi-Agent Pipeline
author: Jeremy
version: 1.0.0
license: MIT
description: Complete Myndy AI pipeline with 5 specialized agents and intelligent routing for OpenWebUI
requirements: crewai, fastapi, uvicorn, pydantic, requests
"""

import os
import sys
import logging
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Generator, Iterator
from pathlib import Path
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    """OpenWebUI-compatible Myndy AI Pipeline with Multiple Agents"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        enable_contact_management: bool = True
        enable_memory_search: bool = True
        debug_mode: bool = False
        myndy_api_url: str = "http://localhost:9091"
        api_endpoint: str = "/myndy_ai/chat/completions"
        api_key: str = "myndy-api-key"
    
    def __init__(self):
        """Initialize the pipeline"""
        self.type = "manifold"  # Enable multiple models
        self.name = "Myndy AI: "  # Base name with colon for manifold
        self.version = "1.0.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # Define available agents/models
        self.agents = [
            {
                "id": "personal_assistant",
                "name": "Personal Assistant",
                "description": "Comprehensive AI assistant for calendar, email, tasks, and general productivity",
                "model": "llama3.2"
            },
            {
                "id": "memory_librarian", 
                "name": "Memory Librarian",
                "description": "Specialized in memory management, entity relationships, and information organization",
                "model": "llama3.2"
            },
            {
                "id": "research_specialist",
                "name": "Research Specialist", 
                "description": "Expert in web research, document analysis, and fact verification",
                "model": "mixtral"
            },
            {
                "id": "health_analyst",
                "name": "Health Analyst",
                "description": "Specialized in health data analysis, fitness tracking, and wellness insights",
                "model": "llama3.2"
            },
            {
                "id": "finance_tracker",
                "name": "Finance Tracker",
                "description": "Expert in expense tracking, budget analysis, and financial planning",
                "model": "llama3.2"
            },
            {
                "id": "auto_router",
                "name": "Auto Router",
                "description": "Intelligent routing that automatically selects the best agent for your request",
                "model": "mixtral"
            }
        ]
        
        logger.info(f"🚀 Myndy AI Pipeline initialized with {len(self.agents)} agents")
    
    async def on_startup(self):
        """Called when the pipeline starts up"""
        logger.info("🚀 Myndy AI Pipeline starting up...")
        logger.info(f"📡 Myndy API URL: {self.valves.myndy_api_url}")
        
    async def on_shutdown(self):
        """Called when the pipeline shuts down"""
        logger.info("🛑 Myndy AI Pipeline shutting down...")
        
    async def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info("⚙️ Pipeline valves updated")
        logger.info(f"🔧 Debug mode: {self.valves.debug_mode}")
        logger.info(f"🛠️ Tool execution: {self.valves.enable_tool_execution}")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models for OpenWebUI"""
        models = []
        for agent in self.agents:
            models.append({
                "id": agent["id"],
                "name": f"{self.name}{agent['name']}",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "myndy-ai",
                "description": agent["description"]
            })
        return models
    
    def _route_to_agent(self, user_message: str, model_id: str) -> str:
        """Route message to appropriate agent based on content and selected model"""
        
        # If auto_router is selected, use intelligent routing
        if model_id == "auto_router":
            model_id = self._intelligent_route(user_message)
            logger.info(f"🧠 Auto-router selected agent: {model_id}")
        
        # Map model_id to agent
        agent_map = {agent["id"]: agent for agent in self.agents}
        selected_agent = agent_map.get(model_id, self.agents[0])  # Default to personal assistant
        
        logger.info(f"🎯 Routing to: {selected_agent['name']} (model: {selected_agent['model']})")
        
        return selected_agent["name"]
    
    def _intelligent_route(self, user_message: str) -> str:
        """Intelligent routing based on message content"""
        message_lower = user_message.lower()
        
        # Health-related keywords
        if any(keyword in message_lower for keyword in ['health', 'fitness', 'exercise', 'sleep', 'steps', 'heart', 'medical', 'wellness']):
            return "health_analyst"
        
        # Finance-related keywords  
        if any(keyword in message_lower for keyword in ['money', 'expense', 'cost', 'budget', 'spending', 'transaction', 'financial', 'dollar']):
            return "finance_tracker"
        
        # Research-related keywords
        if any(keyword in message_lower for keyword in ['research', 'analyze', 'document', 'study', 'investigate', 'report', 'article']):
            return "research_specialist"
        
        # Memory/contact-related keywords
        if any(keyword in message_lower for keyword in ['remember', 'contact', 'person', 'save', 'store', 'relationship', 'know']):
            return "memory_librarian"
        
        # Default to personal assistant
        return "personal_assistant"
    
    def _call_myndy_api(self, agent_name: str, user_message: str, messages: List[Dict[str, Any]]) -> str:
        """Call the Myndy AI backend API"""
        try:
            # Try to call your CrewAI/Myndy API using the configurable endpoint
            response = requests.post(
                f"{self.valves.myndy_api_url}{self.valves.api_endpoint}",
                json={
                    "model": agent_name.lower().replace(" ", "_"),
                    "messages": messages,
                    "agent": agent_name,
                    "enable_tools": self.valves.enable_tool_execution
                },
                timeout=30,
                headers={"Authorization": f"Bearer {self.valves.api_key}"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return result.get("response", str(result))
            else:
                logger.warning(f"API call failed: {response.status_code}")
                return self._fallback_response(agent_name, user_message)
                
        except Exception as e:
            logger.warning(f"Myndy API call failed: {e}")
            return self._fallback_response(agent_name, user_message)
    
    def _fallback_response(self, agent_name: str, user_message: str) -> str:
        """Fallback response when API is unavailable"""
        agent_responses = {
            "Personal Assistant": f"I'm your personal assistant. You asked: '{user_message}'\n\nI would help you with calendar, email, tasks, and general productivity, but the backend API is currently unavailable. Please ensure the Myndy AI backend is running on {self.valves.myndy_api_url}",
            
            "Memory Librarian": f"As your memory librarian, I would help you manage information about: '{user_message}'\n\nI specialize in organizing contacts, relationships, and knowledge management, but I need the backend API to access your memory systems.",
            
            "Research Specialist": f"I would research and analyze: '{user_message}'\n\nAs your research specialist, I normally provide web research, document analysis, and fact verification, but the backend services are needed for full functionality.",
            
            "Health Analyst": f"I would analyze your health query: '{user_message}'\n\nI specialize in health data analysis and wellness insights, but I need access to the backend health tracking systems.",
            
            "Finance Tracker": f"I would help with your financial query: '{user_message}'\n\nAs your finance tracker, I normally provide expense tracking and budget analysis, but I need the backend financial APIs to access your data."
        }
        
        return agent_responses.get(agent_name, f"Agent {agent_name} received: '{user_message}'\n\nFull functionality requires the Myndy AI backend API.")
    
    def pipe(
        self, 
        user_message: str, 
        model_id: str, 
        messages: List[Dict[str, Any]], 
        body: Dict[str, Any]
    ) -> str:
        """Main pipeline processing - OpenWebUI standard signature"""
        
        logger.info(f"💬 Received message: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
        logger.info(f"🤖 Selected model: {model_id}")
        
        if self.valves.debug_mode:
            logger.info(f"📝 Full request body: {json.dumps(body, indent=2)}")
        
        # Route to appropriate agent
        agent_name = self._route_to_agent(user_message, model_id)
        
        # Call backend API or return fallback
        if self.valves.enable_tool_execution:
            response = self._call_myndy_api(agent_name, user_message, messages)
        else:
            response = self._fallback_response(agent_name, user_message)
        
        # Add agent signature to response
        response_with_signature = f"**{agent_name}**: {response}"
        
        if self.valves.debug_mode:
            response_with_signature += f"\n\n---\n*Debug: Routed to {agent_name} via {model_id}*"
        
        return response_with_signature