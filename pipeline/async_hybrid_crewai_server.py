#!/usr/bin/env python3
"""
Async-Optimized Hybrid CrewAI Pipeline Server for OpenWebUI
Performance-optimized version with async agent execution patterns, shared resource management,
and aggressive timeout controls for maximum throughput.

File: pipeline/async_hybrid_crewai_server.py
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
import weakref
from dataclasses import dataclass

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

# Import CrewAI components and performance optimizations
try:
    from agents.simple_agents import create_simple_agents
    from tools.myndy_bridge import get_bridge_performance_metrics, get_tool_documentation
    from core.shared_resource_manager import get_resource_manager, get_shared_metrics
    CREWAI_AVAILABLE = True
    logger.info("✅ CrewAI components imported successfully")
except ImportError as e:
    CREWAI_AVAILABLE = False
    logger.warning(f"⚠️ CrewAI components not available: {e}")

@dataclass
class AgentExecutionResult:
    """Result from agent execution with performance metrics"""
    response: Optional[str]
    execution_time: float
    agent_role: str
    success: bool
    error_message: Optional[str] = None
    cached: bool = False

class SharedResourceManager:
    """Singleton resource manager for LLMs, tools, and agents"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.agent_cache = {}  # Shared agent instances
            self.llm_cache = {}    # Shared LLM instances  
            self.tool_cache = {}   # Shared tool instances
            self.response_cache = {} # Simple response cache for identical queries
            self.cache_ttl = 300   # 5 minutes
            
            # Performance tracking
            self.execution_stats = {
                "total_requests": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "avg_execution_time": 0.0,
                "total_execution_time": 0.0
            }
            
            # Async coordination
            self.agent_semaphore = asyncio.Semaphore(10)  # Limit concurrent agent executions
            self.initialization_lock = asyncio.Lock()
            
            SharedResourceManager._initialized = True
            logger.info("🔧 SharedResourceManager initialized")
    
    async def get_agent(self, agent_role: str):
        """Get or create agent with caching"""
        if agent_role in self.agent_cache:
            return self.agent_cache[agent_role]
        
        async with self.initialization_lock:
            # Double-check after acquiring lock
            if agent_role in self.agent_cache:
                return self.agent_cache[agent_role]
            
            # Create new agent
            try:
                if CREWAI_AVAILABLE:
                    agents = create_simple_agents(
                        verbose=False,
                        allow_delegation=False,
                        max_iter=3,  # Reduced for performance
                        max_execution_time=30  # Aggressive timeout
                    )
                    if agents and agent_role in agents:
                        self.agent_cache[agent_role] = agents[agent_role]
                        logger.debug(f"🤖 Cached agent: {agent_role}")
                        return self.agent_cache[agent_role]
            except Exception as e:
                logger.warning(f"⚠️ Failed to create agent {agent_role}: {e}")
            
            return None
    
    def cache_response(self, key: str, response: str):
        """Cache response with TTL"""
        self.response_cache[key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        # Simple cleanup of old entries
        current_time = time.time()
        expired_keys = [
            k for k, v in self.response_cache.items()
            if current_time - v["timestamp"] > self.cache_ttl
        ]
        for k in expired_keys:
            del self.response_cache[k]
    
    def get_cached_response(self, key: str) -> Optional[str]:
        """Get cached response if valid"""
        if key in self.response_cache:
            entry = self.response_cache[key]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                self.execution_stats["cache_hits"] += 1
                return entry["response"]
            else:
                del self.response_cache[key]
        
        self.execution_stats["cache_misses"] += 1
        return None
    
    def update_stats(self, execution_time: float):
        """Update execution statistics"""
        self.execution_stats["total_requests"] += 1
        self.execution_stats["total_execution_time"] += execution_time
        self.execution_stats["avg_execution_time"] = (
            self.execution_stats["total_execution_time"] / 
            self.execution_stats["total_requests"]
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get resource manager performance statistics"""
        return {
            "resource_manager": {
                "cached_agents": len(self.agent_cache),
                "cached_responses": len(self.response_cache),
                "cache_hit_rate": round(
                    (self.execution_stats["cache_hits"] / 
                     (self.execution_stats["cache_hits"] + self.execution_stats["cache_misses"]) * 100)
                    if (self.execution_stats["cache_hits"] + self.execution_stats["cache_misses"]) > 0 else 0, 2
                ),
                "avg_execution_time": round(self.execution_stats["avg_execution_time"], 3),
                "total_requests": self.execution_stats["total_requests"]
            }
        }

class AsyncHybridCrewAIPipeline:
    """Async-optimized hybrid pipeline with shared resource management"""
    
    def __init__(self):
        self.id = "myndy_ai_async"
        self.name = "Myndy AI Async CrewAI"
        self.version = "2.0.0"
        self.type = "manifold"
        
        # Performance-optimized timeout settings
        self.agent_timeout = 30    # Reduced from 60s for faster response
        self.fallback_timeout = 1  # Very fast fallback
        self.max_concurrent_agents = 10
        
        # Use the global shared resource manager
        self.resource_manager = get_resource_manager()
        
        # Agent configurations (optimized for speed)
        self.agent_configs = {
            "personal_assistant": {
                "name": "Personal Assistant",
                "description": "Fast AI assistant for productivity, calendar, email, and general tasks",
                "role": "personal_assistant",
                "model": "llama3.2",
                "priority": "high"
            },
            "memory_librarian": {
                "name": "Memory Librarian", 
                "description": "Quick memory management and entity organization",
                "role": "memory_librarian",
                "model": "llama3.2",
                "priority": "high"
            },
            "research_specialist": {
                "name": "Research Specialist",
                "description": "Fast research and document analysis", 
                "role": "research_specialist",
                "model": "llama3.2",  # Changed to faster model
                "priority": "medium"
            },
            "health_analyst": {
                "name": "Health Analyst",
                "description": "Quick health data analysis and wellness insights",
                "role": "health_analyst", 
                "model": "llama3.2",
                "priority": "medium"
            },
            "finance_tracker": {
                "name": "Finance Tracker",
                "description": "Fast expense tracking and financial analysis",
                "role": "finance_tracker",
                "model": "llama3.2",
                "priority": "medium"
            },
            "shadow_agent": {
                "name": "Shadow Agent",
                "description": "Background conversation analysis and memory updates",
                "role": "shadow_agent", 
                "model": "llama3.2",
                "priority": "low"
            },
            "auto": {
                "name": "Auto Router",
                "description": "Intelligent agent selection with fast routing",
                "role": "auto_router",
                "model": "llama3.2",  # Faster routing
                "priority": "high"
            }
        }
        
        logger.info(f"🚀 Async Pipeline initialized with {len(self.agent_configs)} agents")
        logger.info(f"⚡ Max concurrent agents: {self.max_concurrent_agents}")
        logger.info(f"🎯 Agent timeout: {self.agent_timeout}s")
    
    def _intelligent_route(self, user_message: str) -> str:
        """Fast keyword-based routing with caching"""
        # Create cache key for routing decisions
        route_key = f"route:{hash(user_message.lower()[:100])}"
        cached_route = self.resource_manager.get_cached_response(route_key)
        if cached_route:
            return cached_route
        
        message_lower = user_message.lower()
        
        # Health keywords (high priority)
        if any(keyword in message_lower for keyword in ['health', 'fitness', 'exercise', 'bmi', 'sleep', 'medical', 'wellness', 'workout']):
            route = "health_analyst"
        # Finance keywords (high priority)
        elif any(keyword in message_lower for keyword in ['money', 'expense', 'budget', 'financial', 'cost', 'dollar', 'payment', 'spending']):
            route = "finance_tracker"
        # Memory keywords (high priority)
        elif any(keyword in message_lower for keyword in ['remember', 'save', 'contact', 'person', 'relationship', 'entity', 'extract']):
            route = "memory_librarian"
        # Research keywords (medium priority)
        elif any(keyword in message_lower for keyword in ['research', 'analyze', 'study', 'investigate', 'document', 'web', 'search']):
            route = "research_specialist"
        # Default to personal assistant
        else:
            route = "personal_assistant"
        
        # Cache routing decision
        self.resource_manager.cache_response(route_key, route)
        return route
    
    async def _execute_agent_async(self, agent_role: str, user_message: str, messages: List[Dict]) -> AgentExecutionResult:
        """Execute agent asynchronously with resource management"""
        start_time = time.time()
        
        # Check for cached response first
        response_key = f"agent:{agent_role}:{hash(user_message[:200])}"
        cached_response = self.resource_manager.get_cached_response(response_key)
        if cached_response:
            execution_time = time.time() - start_time
            return AgentExecutionResult(
                response=cached_response,
                execution_time=execution_time,
                agent_role=agent_role,
                success=True,
                cached=True
            )
        
        # Acquire semaphore for concurrent execution control
        async with self.resource_manager.agent_semaphore:
            try:
                # Get agent from shared resource manager
                agent = await self.resource_manager.get_agent(agent_role, allow_delegation=False, max_iter=3)
                if not agent:
                    execution_time = time.time() - start_time
                    return AgentExecutionResult(
                        response=None,
                        execution_time=execution_time,
                        agent_role=agent_role,
                        success=False,
                        error_message="Agent not available"
                    )
                
                # Create task description
                task_description = f"User message: {user_message}\n\nProvide a helpful, concise response."
                
                # Execute agent with timeout using asyncio
                try:
                    # Run agent execution in thread pool with timeout
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(
                            None,  # Use default thread pool
                            agent.execute_task,
                            task_description
                        ),
                        timeout=self.agent_timeout
                    )
                    
                    execution_time = time.time() - start_time
                    
                    if result and isinstance(result, str):
                        # Cache successful result
                        self.resource_manager.cache_response(response_key, result)
                        
                        return AgentExecutionResult(
                            response=result,
                            execution_time=execution_time,
                            agent_role=agent_role,
                            success=True
                        )
                    else:
                        return AgentExecutionResult(
                            response=None,
                            execution_time=execution_time,
                            agent_role=agent_role,
                            success=False,
                            error_message="Agent returned invalid result"
                        )
                        
                except asyncio.TimeoutError:
                    execution_time = time.time() - start_time
                    logger.warning(f"⏰ Agent {agent_role} timed out after {self.agent_timeout}s")
                    return AgentExecutionResult(
                        response=None,
                        execution_time=execution_time,
                        agent_role=agent_role,
                        success=False,
                        error_message=f"Timeout after {self.agent_timeout}s"
                    )
                    
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ Agent {agent_role} execution failed: {e}")
                return AgentExecutionResult(
                    response=None,
                    execution_time=execution_time,
                    agent_role=agent_role,
                    success=False,
                    error_message=str(e)
                )
    
    def _generate_optimized_fallback(self, agent_role: str, user_message: str) -> str:
        """Generate fast, optimized fallback response"""
        config = self.agent_configs.get(agent_role, self.agent_configs["personal_assistant"])
        agent_name = config["name"]
        
        # Shortened fallback responses for speed
        fallback_responses = {
            "personal_assistant": f"**{agent_name}**: I can help with '{user_message}'\n\n✅ **Quick Actions Available:**\n• Time & scheduling\n• Task management\n• General productivity\n\n*Fast mode active - connect backend for full features*",
            
            "memory_librarian": f"**{agent_name}**: Processing '{user_message}'\n\n✅ **Memory Services:**\n• Contact management\n• Information organization\n• Knowledge relationships\n\n*Connect to Myndy AI for full memory integration*",
            
            "research_specialist": f"**{agent_name}**: Ready to research '{user_message}'\n\n✅ **Research Capabilities:**\n• Information analysis\n• Document processing\n• Fact verification\n\n*Enable research tools for live capabilities*",
            
            "health_analyst": f"**{agent_name}**: Analyzing '{user_message}'\n\n✅ **Health Analysis:**\n• Health data insights\n• Fitness tracking\n• Wellness monitoring\n\n*Connect health data for personalized insights*",
            
            "finance_tracker": f"**{agent_name}**: Processing '{user_message}'\n\n✅ **Financial Services:**\n• Expense tracking\n• Budget analysis\n• Financial planning\n\n*Connect financial data for real analysis*",
            
            "shadow_agent": f"**{agent_name}**: Monitoring '{user_message}'\n\n✅ **Background Analysis:**\n• Conversation analysis\n• Entity extraction\n• Behavioral monitoring\n\n*Enable conversation processing for full analysis*"
        }
        
        return fallback_responses.get(agent_role, fallback_responses["personal_assistant"])
    
    async def pipe(self, body: Dict[str, Any]) -> str:
        """Main async pipeline processing with performance optimization"""
        start_time = time.time()
        
        messages = body.get("messages", [])
        model = body.get("model", "auto")
        
        # Extract user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Route to appropriate agent
        if model == "auto":
            agent_role = self._intelligent_route(user_message)
            logger.debug(f"🧠 Auto-routed to {agent_role}")
        else:
            agent_role = model
        
        # Map to actual agent role
        config = self.agent_configs.get(agent_role, self.agent_configs["personal_assistant"])
        actual_role = config["role"] if config["role"] != "auto_router" else "personal_assistant"
        
        # Try async agent execution
        if CREWAI_AVAILABLE:
            result = await self._execute_agent_async(actual_role, user_message, messages)
            
            if result.success and result.response:
                total_time = time.time() - start_time
                cache_indicator = " (cached)" if result.cached else ""
                logger.info(f"✅ Agent {actual_role} responded in {total_time:.2f}s{cache_indicator}")
                return f"**{config['name']}**: {result.response}"
        
        # Fast fallback response
        fallback_response = self._generate_optimized_fallback(agent_role, user_message)
        total_time = time.time() - start_time
        logger.info(f"⚡ Fallback response for {agent_role} in {total_time:.2f}s")
        return fallback_response
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models for OpenWebUI"""
        models = []
        for agent_id, config in self.agent_configs.items():
            models.append({
                "id": agent_id,
                "name": config["name"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "myndy-ai-async",
                "description": config["description"],
                "priority": config.get("priority", "medium")
            })
        return models
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        try:
            # Get bridge metrics
            bridge_metrics = get_bridge_performance_metrics()
            
            # Get shared resource manager metrics
            shared_metrics = get_shared_metrics()
            
            return {
                "pipeline": {
                    "version": self.version,
                    "type": "async-optimized",
                    "agent_timeout": self.agent_timeout,
                    "max_concurrent": self.max_concurrent_agents,
                    "available_agents": len(self.agent_configs)
                },
                "bridge_performance": bridge_metrics,
                "shared_resource_management": shared_metrics,
                "optimization_status": {
                    "async_execution": "enabled",
                    "shared_resources": "enabled", 
                    "response_caching": "enabled",
                    "concurrent_agents": "enabled",
                    "performance_monitoring": "enabled"
                }
            }
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}

# Initialize async pipeline
pipeline = AsyncHybridCrewAIPipeline()

# Create FastAPI app
app = FastAPI(
    title="Myndy AI Async Hybrid CrewAI Pipeline",
    description="Performance-optimized async CrewAI agents with shared resource management",
    version="2.0.0"
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
        "pipeline": "myndy-ai-async-hybrid-crewai",
        "version": "2.0.0",
        "agents_available": len(pipeline.agent_configs),
        "crewai_active": CREWAI_AVAILABLE,
        "optimizations": [
            "async_execution",
            "shared_resources", 
            "response_caching",
            "concurrent_agents"
        ]
    }

# Performance metrics endpoint
@app.get("/metrics")
async def get_performance_metrics():
    """Get comprehensive performance metrics"""
    return await pipeline.get_performance_metrics()

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
    """Handle chat completions with async processing"""
    try:
        messages = request.get("messages", [])
        model = request.get("model", "auto")
        
        # Get user message for logging
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        logger.info(f"💬 Async processing: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
        
        # Process through async pipeline
        start_time = time.time()
        response = await pipeline.pipe(request)
        processing_time = time.time() - start_time
        
        logger.info(f"⚡ Total async response time: {processing_time:.2f}s")
        
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
            },
            "performance": {
                "processing_time": round(processing_time, 3),
                "pipeline_version": "2.0.0-async"
            }
        }
            
    except Exception as e:
        logger.error(f"Async chat completion error: {e}")
        return {
            "error": {
                "message": str(e),
                "type": "async_pipeline_error"
            }
        }

# Chat completions endpoints
@app.post("/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    body["stream"] = False  # Force non-streaming
    return await _handle_chat_completions(body)

@app.post("/v1/chat/completions")
async def v1_chat_completions(request: Request):
    body = await request.json()
    body["stream"] = False  # Force non-streaming
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
            "description": "Async-optimized CrewAI pipeline with shared resource management",
            "author": "Jeremy",
            "license": "MIT",
            "status": "active",
            "models": pipeline.get_models(),
            "crewai_active": CREWAI_AVAILABLE,
            "optimizations": [
                "async_execution",
                "shared_resources",
                "response_caching", 
                "concurrent_agents",
                "performance_monitoring"
            ]
        }]
    }

# Tool documentation endpoint
@app.get("/tools")
async def get_tools_documentation():
    try:
        return get_tool_documentation()
    except Exception as e:
        return {"error": str(e), "available": False}

def main():
    """Run the async hybrid CrewAI pipeline server"""
    logger.info("🚀 Starting Myndy AI Async Hybrid CrewAI Pipeline Server")
    logger.info("⚡ Performance-optimized with async execution patterns")
    logger.info(f"🎯 Agent timeout: {pipeline.agent_timeout}s (optimized)")
    logger.info(f"🔄 Max concurrent agents: {pipeline.max_concurrent_agents}")
    logger.info(f"🎯 Available agents: {list(pipeline.agent_configs.keys())}")
    logger.info(f"✅ CrewAI active: {CREWAI_AVAILABLE}")
    logger.info("🌐 Server starting on http://localhost:9092")
    logger.info("💡 Add this URL to OpenWebUI: http://localhost:9092")
    logger.info("📊 Performance metrics: http://localhost:9092/metrics")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9092,  # Different port to avoid conflicts
        log_level="info"
    )

if __name__ == "__main__":
    main()