#!/usr/bin/env python3
"""
Hybrid CrewAI Pipeline Server for OpenWebUI
Real CrewAI agents with timeout protection and fallback responses
"""

import os
import sys
import json
import time
import asyncio
import logging
import signal
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Generator, Iterator
from pathlib import Path
import threading
import concurrent.futures

# Add project paths
PIPELINE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PIPELINE_ROOT))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import CrewAI components
try:
    from agents.simple_agents import create_simple_agents
    CREWAI_AVAILABLE = True
    logger.info("✅ CrewAI components imported successfully")
except ImportError as e:
    CREWAI_AVAILABLE = False
    logger.warning(f"⚠️ CrewAI components not available: {e}")

class HybridCrewAIPipeline:
    """Hybrid pipeline with real CrewAI agents and timeout protection"""
    
    def __init__(self):
        self.id = "myndy_ai"
        self.name = "Myndy AI CrewAI"
        self.version = "1.0.0"
        self.type = "manifold"
        
        # Timeout settings (allow time for tool usage)
        self.agent_timeout = 60  # seconds - allow time for SpaCy tool execution
        self.fallback_timeout = 2  # seconds for fallback responses
        
        # Available agents
        self.agent_configs = {
            "personal_assistant": {
                "name": "Personal Assistant",
                "description": "Comprehensive AI assistant for productivity, calendar, email, and general tasks",
                "role": "personal_assistant",
                "model": "llama3.2"
            },
            "memory_librarian": {
                "name": "Memory Librarian", 
                "description": "Specialized in memory management, entity relationships, and information organization",
                "role": "memory_librarian",
                "model": "llama3.2"
            },
            "research_specialist": {
                "name": "Research Specialist",
                "description": "Expert in web research, document analysis, and fact verification", 
                "role": "research_specialist",
                "model": "mixtral"
            },
            "health_analyst": {
                "name": "Health Analyst",
                "description": "Specialized in health data analysis, fitness tracking, and wellness insights",
                "role": "health_analyst", 
                "model": "llama3.2"
            },
            "finance_tracker": {
                "name": "Finance Tracker",
                "description": "Expert in expense tracking, budget analysis, and financial planning",
                "role": "finance_tracker",
                "model": "llama3.2"
            },
            "shadow_agent": {
                "name": "Shadow Agent",
                "description": "Behavioral analysis, conversation monitoring, and memory updates in background",
                "role": "shadow_agent", 
                "model": "llama3.2"
            },
            "auto": {
                "name": "Auto Router",
                "description": "Automatically selects the best agent for your request using intelligent routing",
                "role": "auto_router",
                "model": "mixtral"
            }
        }
        
        # Initialize CrewAI agents if available
        self.crewai_agents = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        
        if CREWAI_AVAILABLE:
            self._initialize_crewai_agents()
        
        logger.info(f"🚀 Hybrid Pipeline initialized with {len(self.agent_configs)} agents")
        logger.info(f"🤖 CrewAI agents: {'✅ Active' if self.crewai_agents else '❌ Fallback mode'}")
    
    def _initialize_crewai_agents(self):
        """Initialize real CrewAI agents with timeout protection"""
        try:
            # Create simple agents (faster than full crews)
            agents = create_simple_agents(
                verbose=False,  # Reduce logging for speed
                allow_delegation=False,  # Prevent complex delegation chains
                max_iter=5,  # Limit iterations for speed
                max_execution_time=self.agent_timeout
            )
            
            if agents:
                self.crewai_agents = agents
                logger.info(f"✅ Initialized {len(self.crewai_agents)} CrewAI agents")
            else:
                logger.warning("⚠️ No CrewAI agents returned from initialization")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize CrewAI agents: {e}")
            self.crewai_agents = {}
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models for OpenWebUI"""
        models = []
        for agent_id, config in self.agent_configs.items():
            models.append({
                "id": agent_id,
                "name": config["name"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "myndy-ai",
                "description": config["description"]
            })
        return models
    
    def _intelligent_route(self, user_message: str) -> str:
        """Quick keyword-based routing for auto selection"""
        message_lower = user_message.lower()
        
        # Health keywords
        if any(keyword in message_lower for keyword in ['health', 'fitness', 'exercise', 'sleep', 'medical', 'wellness']):
            return "health_analyst"
        
        # Finance keywords  
        if any(keyword in message_lower for keyword in ['money', 'expense', 'budget', 'financial', 'cost', 'dollar']):
            return "finance_tracker"
        
        # Research keywords
        if any(keyword in message_lower for keyword in ['research', 'analyze', 'study', 'investigate', 'document']):
            return "research_specialist"
        
        # Memory keywords
        if any(keyword in message_lower for keyword in ['remember', 'save', 'contact', 'person', 'relationship']):
            return "memory_librarian"
        
        # Default to personal assistant
        return "personal_assistant"
    
    def _execute_crewai_agent(self, agent_role: str, user_message: str, messages: List[Dict]) -> Optional[str]:
        """Execute CrewAI agent with timeout protection"""
        if not self.crewai_agents or agent_role not in self.crewai_agents:
            return None
        
        try:
            agent = self.crewai_agents[agent_role]
            
            # Create a simple task for the agent
            task_description = f"User message: {user_message}\n\nProvide a helpful response."
            
            # Execute with timeout
            future = self.executor.submit(agent.execute_task, task_description)
            result = future.result(timeout=self.agent_timeout)
            
            if result and isinstance(result, str):
                return result
            else:
                return None
                
        except concurrent.futures.TimeoutError:
            logger.warning(f"⏰ Agent {agent_role} timed out after {self.agent_timeout}s")
            return None
        except Exception as e:
            logger.error(f"❌ Agent {agent_role} execution failed: {e}")
            return None
    
    def _generate_fallback_response(self, agent_role: str, user_message: str) -> str:
        """Generate fast fallback response when CrewAI agents fail or timeout"""
        config = self.agent_configs.get(agent_role, self.agent_configs["personal_assistant"])
        agent_name = config["name"]
        
        fallback_responses = {
            "personal_assistant": f"**{agent_name}**: I can help you with: '{user_message}'\n\nI specialize in:\n• Calendar and scheduling\n• Email management\n• Task organization\n• General productivity\n\nCurrently operating in fast mode. For full tool integration, ensure the Myndy AI backend is running.",
            
            "memory_librarian": f"**{agent_name}**: I can help organize information about: '{user_message}'\n\nI specialize in:\n• Contact management\n• Information organization\n• Knowledge relationships\n• Memory search\n\nFor full memory integration, connect to the Myndy AI memory systems.",
            
            "research_specialist": f"**{agent_name}**: I can research: '{user_message}'\n\nI specialize in:\n• Information analysis\n• Document processing\n• Fact verification\n• Research methodology\n\nFor live research capabilities, ensure web access and research tools are enabled.",
            
            "health_analyst": f"**{agent_name}**: I can analyze your health query: '{user_message}'\n\nI specialize in:\n• Health data analysis\n• Fitness tracking\n• Wellness insights\n• Activity monitoring\n\nFor personalized health insights, connect to health data sources.",
            
            "finance_tracker": f"**{agent_name}**: I can help with your financial query: '{user_message}'\n\nI specialize in:\n• Expense tracking\n• Budget analysis\n• Financial planning\n• Transaction management\n\nFor real financial data analysis, connect to financial data sources."
        }
        
        # Add shadow_agent fallback if not in dict
        if "shadow_agent" not in fallback_responses:
            fallback_responses["shadow_agent"] = f"**{agent_name}**: I can analyze this conversation: '{user_message}'\\n\\nI specialize in:\\n• Conversation analysis\\n• Entity extraction\\n• Behavioral monitoring\\n• Memory updates\\n\\nFor full conversation analysis, enable conversation processing tools."
        
        return fallback_responses.get(agent_role, fallback_responses["personal_assistant"])
    
    async def pipe(self, body: Dict[str, Any]) -> str:
        """Main pipeline processing with hybrid CrewAI/fallback approach"""
        messages = body.get("messages", [])
        model = body.get("model", "auto")
        
        # Get user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Route to appropriate agent
        if model == "auto":
            agent_role = self._intelligent_route(user_message)
            logger.info(f"🧠 Auto-routed '{user_message[:50]}...' to {agent_role}")
        else:
            agent_role = model
        
        # Map model to actual agent role
        config = self.agent_configs.get(agent_role, self.agent_configs["personal_assistant"])
        actual_role = config["role"] if config["role"] != "auto_router" else "personal_assistant"
        
        start_time = time.time()
        
        # Try CrewAI agent first (with timeout)
        crewai_response = None
        if self.crewai_agents:
            try:
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                crewai_response = await loop.run_in_executor(
                    self.executor,
                    self._execute_crewai_agent,
                    actual_role,
                    user_message,
                    messages
                )
            except Exception as e:
                logger.warning(f"⚠️ CrewAI execution failed: {e}")
        
        processing_time = time.time() - start_time
        
        # Use CrewAI response if available and fast enough
        if crewai_response and processing_time < self.agent_timeout:
            logger.info(f"✅ CrewAI agent {actual_role} responded in {processing_time:.2f}s")
            return f"**{config['name']}**: {crewai_response}"
        else:
            # Fall back to fast response
            fallback_response = self._generate_fallback_response(agent_role, user_message)
            logger.info(f"⚡ Fallback response for {agent_role} in {processing_time:.2f}s")
            return fallback_response

# Initialize pipeline
pipeline = HybridCrewAIPipeline()

# Create FastAPI app
app = FastAPI(
    title="Myndy AI Hybrid CrewAI Pipeline",
    description="Real CrewAI agents with timeout protection and fallback responses for OpenWebUI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "pipeline": "myndy-ai-hybrid-crewai",
        "version": "1.0.0",
        "agents_available": len(pipeline.agent_configs),
        "crewai_active": len(pipeline.crewai_agents) > 0
    }

# Models endpoint
@app.get("/models")
async def get_models():
    return {
        "data": pipeline.get_models(),
        "object": "list"
    }

@app.get("/v1/models")
async def get_v1_models():
    return {
        "data": pipeline.get_models(),
        "object": "list"
    }

# Chat completions handler
async def _handle_chat_completions(request: dict) -> dict:
    """Handle chat completions with hybrid CrewAI processing"""
    try:
        messages = request.get("messages", [])
        model = request.get("model", "auto")
        
        # Get user message for logging
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        logger.info(f"💬 Hybrid processing: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
        
        # Process through hybrid pipeline
        start_time = time.time()
        response = await pipeline.pipe(request)
        processing_time = time.time() - start_time
        
        logger.info(f"⚡ Total response time: {processing_time:.2f}s")
        
        # Return OpenAI-compatible response
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(user_message.split()) + len(response.split())
            }
        }
            
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        return {
            "error": {
                "message": str(e),
                "type": "pipeline_error"
            }
        }

# Chat completions endpoints
@app.post("/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    # Force non-streaming for OpenWebUI compatibility
    body["stream"] = False
    return await _handle_chat_completions(body)

@app.post("/v1/chat/completions")
async def v1_chat_completions(request: Request):
    body = await request.json()
    # Force non-streaming for OpenWebUI compatibility  
    body["stream"] = False
    return await _handle_chat_completions(body)

# Pipeline info endpoints
@app.get("/pipelines")
async def get_pipelines():
    return {
        "data": [{
            "id": pipeline.id,
            "name": pipeline.name,
            "type": pipeline.type,
            "version": pipeline.version,
            "description": "Hybrid CrewAI pipeline with real agents and timeout protection",
            "author": "Jeremy",
            "license": "MIT",
            "status": "active",
            "models": pipeline.get_models(),
            "crewai_active": len(pipeline.crewai_agents) > 0
        }]
    }

# Tool documentation endpoint
@app.get("/tools")
async def get_tools_documentation():
    try:
        # Import here to avoid circular imports
        from tools.myndy_bridge import get_tool_documentation
        return get_tool_documentation()
    except Exception as e:
        return {"error": str(e), "available": False}

def main():
    """Run the hybrid CrewAI pipeline server"""
    logger.info("🚀 Starting Myndy AI Hybrid CrewAI Pipeline Server")
    logger.info("🤖 Real CrewAI agents with timeout protection and fallback responses")
    logger.info(f"⚡ Agent timeout: {pipeline.agent_timeout}s")
    logger.info(f"🔄 Fallback timeout: {pipeline.fallback_timeout}s")
    logger.info(f"🎯 Available agents: {list(pipeline.agent_configs.keys())}")
    logger.info(f"✅ CrewAI active: {len(pipeline.crewai_agents) > 0}")
    logger.info("🌐 Server starting on http://localhost:9091")
    logger.info("💡 Add this URL to OpenWebUI: http://localhost:9091")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9091,
        log_level="info"
    )

if __name__ == "__main__":
    main()