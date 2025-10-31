"""
title: Myndy AI Pipeline (Simplified)
author: Jeremy  
version: 0.1.0
license: MIT
description: Streamlined Myndy AI pipeline for Open WebUI integration without external dependencies
requirements: pydantic, fastapi, uvicorn
"""

import os
import sys
import logging
import time
import warnings
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Generator, Iterator
from pathlib import Path

# Suppress warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=UserWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/myndy_openwebui_pipeline.log')
    ]
)

logger = logging.getLogger("openwebui.pipeline")

from pydantic import BaseModel


class Pipeline:
    """Simplified Myndy AI Pipeline for Open WebUI"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_intelligent_responses: bool = True
        enable_memory_simulation: bool = True
        debug_mode: bool = False
        api_key: str = "0p3n-w3bu!"
        
    def __init__(self):
        """Initialize the simplified pipeline"""
        self.type = "manifold"
        self.id = "myndy_ai_simple"
        self.name = "Myndy AI (Simplified)"
        self.version = "0.1.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # Simple agent definitions
        self.agents = {
            "personal_assistant": {
                "name": "Personal Assistant",
                "description": "Comprehensive AI assistant for scheduling, productivity, and general assistance",
                "capabilities": ["time management", "general assistance", "planning", "information queries"]
            },
            "research_agent": {
                "name": "Research Specialist", 
                "description": "Information gathering and analysis specialist",
                "capabilities": ["research", "analysis", "fact checking", "summarization"]
            }
        }
        
        # Simple conversation memory
        self.conversation_memory = {}
        
        logger.info(f"🎉 Simplified Myndy AI v{self.version} initialized")
        logger.info(f"📊 Available agents: {list(self.agents.keys())}")
        
    async def on_startup(self):
        """Called when the pipeline starts"""
        logger.info("🚀 Pipeline startup initiated")
        logger.info(f"🎯 Ready to serve {len(self.agents)} agents")
        
    async def on_shutdown(self):
        """Called when the pipeline shuts down"""
        logger.info("🛑 Pipeline shutdown initiated")
        
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models/agents for Open WebUI"""
        models = []
        
        # Add auto-routing model
        models.append({
            "id": "auto",
            "name": "🧠 Myndy AI (Auto)",
            "object": "model",
            "created": int(datetime.now().timestamp()),
            "owned_by": "myndy-ai"
        })
        
        # Add individual agents
        for agent_id, agent_info in self.agents.items():
            models.append({
                "id": agent_id,
                "name": f"🎯 {agent_info['name']}",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "myndy-ai"
            })
            
        return models
        
    def get_manifest(self) -> Dict[str, Any]:
        """Return pipeline manifest for Open WebUI"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "type": self.type,
            "description": "Simplified Myndy AI - Personal assistant without external dependencies",
            "author": "Jeremy",
            "license": "MIT",
            "models": self.get_models()
        }
        
    def pipe(
        self, 
        user_message: str, 
        model_id: str, 
        messages: List[Dict[str, Any]], 
        body: Dict[str, Any]
    ) -> Union[str, Generator, Iterator]:
        """Process messages through the simplified pipeline"""
        
        logger.info(f"🎯 Pipeline processing: model={model_id}, message_length={len(user_message)}")
        
        try:
            # Simple routing logic
            if model_id == "auto":
                # Intelligent routing based on keywords
                selected_agent = self._route_message(user_message)
            else:
                selected_agent = model_id if model_id in self.agents else "personal_assistant"
            
            logger.info(f"🤖 Selected agent: {selected_agent}")
            
            # Store conversation in simple memory
            session_id = self._get_session_id(messages)
            self._update_conversation_memory(session_id, user_message, selected_agent)
            
            # Generate response based on agent type
            response = self._generate_response(user_message, selected_agent, messages)
            
            logger.info(f"✅ Response generated (length: {len(response)} chars)")
            return response
            
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
            
    def _route_message(self, message: str) -> str:
        """Simple routing based on message content"""
        message_lower = message.lower()
        
        # Research keywords
        research_keywords = ["research", "analyze", "study", "investigate", "find information", "look up", "search"]
        if any(keyword in message_lower for keyword in research_keywords):
            return "research_agent"
        
        # Default to personal assistant
        return "personal_assistant"
        
    def _get_session_id(self, messages: List[Dict[str, Any]]) -> str:
        """Generate simple session ID"""
        content_hash = str(abs(hash(str([msg.get("content", "") for msg in messages[-5:]]))))
        return f"session_{content_hash[:8]}"
        
    def _update_conversation_memory(self, session_id: str, message: str, agent: str):
        """Update simple conversation memory"""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = {
                "created_at": datetime.now(),
                "messages": [],
                "agent_history": []
            }
        
        self.conversation_memory[session_id]["messages"].append({
            "timestamp": datetime.now(),
            "message": message,
            "agent": agent
        })
        
        # Keep only last 10 messages per session
        if len(self.conversation_memory[session_id]["messages"]) > 10:
            self.conversation_memory[session_id]["messages"] = \
                self.conversation_memory[session_id]["messages"][-10:]
                
    def _generate_response(self, message: str, agent_type: str, messages: List[Dict]) -> str:
        """Generate response based on agent type"""
        
        agent_info = self.agents.get(agent_type, self.agents["personal_assistant"])
        
        # Get current time for context
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if agent_type == "research_agent":
            return self._generate_research_response(message, current_time)
        else:
            return self._generate_assistant_response(message, current_time)
            
    def _generate_research_response(self, message: str, current_time: str) -> str:
        """Generate research-focused response"""
        return f"""**🔍 Research Specialist Response**

**Your Query:** {message}

**Research Analysis:**
I'm your research specialist and I can help you investigate this topic. Based on your query, here's what I can assist with:

• **Information Gathering**: I can help you structure your research approach
• **Analysis Framework**: I can suggest analytical methods for your topic  
• **Source Evaluation**: I can guide you on evaluating information sources
• **Summary Creation**: I can help organize findings into clear summaries

**Next Steps:**
To provide more targeted research assistance, could you specify:
- What specific aspects you'd like to focus on?
- What type of sources you prefer (academic, news, general web)?
- How detailed should the analysis be?

**Time:** {current_time}
**Agent:** Research Specialist (Simplified Mode)

*Note: This is a simplified version. For full research capabilities with web search, document analysis, and fact verification, the complete Myndy AI system with external integrations would be needed.*"""

    def _generate_assistant_response(self, message: str, current_time: str) -> str:
        """Generate personal assistant response"""
        
        # Simple keyword detection for specific responses
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["time", "what time", "current time"]):
            return f"""**🕐 Time Information**

**Current Time:** {current_time}

I can help you with time-related queries! In the full system, I have access to:
• World time zones
• Calendar integration  
• Schedule management
• Time calculations
• Reminder setting

**Note:** This is a simplified demonstration. The complete Myndy AI system includes full calendar integration and scheduling capabilities."""

        elif any(word in message_lower for word in ["weather", "temperature", "forecast"]):
            return f"""**🌤️ Weather Information**

I'd be happy to help with weather information! In the complete Myndy AI system, I can provide:
• Current weather conditions
• Detailed forecasts
• Weather alerts
• Climate data
• Location-based weather

**Current Time:** {current_time}

**Note:** This simplified version doesn't include live weather data. The full system integrates with weather APIs for real-time information."""

        elif any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return f"""**👋 Hello! Welcome to Myndy AI**

I'm your personal assistant, ready to help with:

**🎯 Core Capabilities:**
• Time and scheduling assistance
• Information organization  
• Task planning and management
• General productivity support

**🔧 System Status:**
• Mode: Simplified Open WebUI Integration
• Agent: Personal Assistant
• Time: {current_time}

**💡 Tips:**
Try asking about time, weather, research topics, or general assistance questions. The full Myndy AI system includes comprehensive tool integration, memory management, and advanced agent collaboration.

How can I assist you today?"""

        else:
            return f"""**🤖 Personal Assistant Response**

**Your Message:** {message}

I'm here to help as your personal assistant! While this is a simplified version for Open WebUI demonstration, I can assist with:

**📋 Available Services:**
• General information and guidance
• Task planning and organization
• Time management support  
• Basic research coordination
• Productivity assistance

**🔧 System Features (Full Version):**
• Calendar integration
• Memory management
• Tool execution (30+ tools)
• Multi-agent collaboration
• Persistent learning

**Current Time:** {current_time}

**Next Steps:**
Could you provide more details about what you'd like help with? I can offer guidance on planning, organization, research approaches, or general assistance.

*This simplified pipeline demonstrates Open WebUI integration. The complete Myndy AI system includes extensive tool integration, persistent memory, and advanced agent capabilities.*"""


# Create the pipeline instance for Open WebUI
pipeline = Pipeline()


if __name__ == "__main__":
    import sys
    import uvicorn
    import os
    import signal
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from contextlib import asynccontextmanager
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Testing Simplified Myndy AI Pipeline...")
        try:
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
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan manager"""
        logger.info("🚀 Simplified Myndy AI Pipeline server starting up...")
        await pipeline.on_startup()
        yield
        logger.info("🛑 Simplified Myndy AI Pipeline server shutting down...")
        await pipeline.on_shutdown()

    # Create FastAPI app
    app = FastAPI(
        title="Myndy AI Pipeline (Simplified)",
        description="Simplified Myndy AI for Open WebUI without external dependencies",
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
                # TODO: Implement streaming response if needed
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
            "external_dependencies": False,
            "simplified_mode": True
        }

    print("🚀 Starting Simplified Myndy AI Pipeline Server")
    print("=" * 60)
    print(f"📊 Pipeline: {pipeline.name} v{pipeline.version}")
    print(f"🤖 Available models: {len(pipeline.get_models())}")
    print("🌐 Server will be available at: http://localhost:9099")
    print("🔗 Add to Open WebUI: http://localhost:9099")
    print("🔑 Pipeline API Key: 0p3n-w3bu!")
    print("💡 This is a simplified version without external dependencies")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Enhanced port handling
    import subprocess
    
    def kill_process_on_port(port):
        """Kill any process using the specified port"""
        try:
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
                        time.sleep(1)
                    except (ValueError, ProcessLookupError, PermissionError) as e:
                        logger.warning(f"⚠️ Could not kill process {pid}: {e}")
                return True
        except Exception as e:
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
                    logger.info(f"📍 Port {port} in use, attempting cleanup...")
                    print(f"📍 Port {port} in use, attempting cleanup...")
                    if kill_process_on_port(port):
                        continue
                
                if attempt < max_attempts - 1:
                    port += 1
                    logger.warning(f"⚠️ Trying port {port}")
                    print(f"⚠️ Trying port {port}")
                else:
                    logger.error(f"❌ Failed to start server after {max_attempts} attempts")
                    print(f"❌ Failed to start server after {max_attempts} attempts")
                    raise
            else:
                logger.error(f"❌ Failed to start server: {e}")
                raise