#!/usr/bin/env python3
"""
Pure HTTP-based OpenWebUI Pipeline Server

Provides all required endpoints for OpenWebUI pipeline detection without
loading the full CrewAI pipeline to avoid tool validation issues.

File: src/myndy_crewai/pipeline/http_only_server.py
"""

import os
import sys
import logging
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Union, Generator, Iterator
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/myndy_openwebui_http.log')
    ]
)
logger = logging.getLogger(__name__)

class HTTPOnlyPipeline:
    """Simplified pipeline that uses only HTTP calls to myndy-ai backend"""
    
    def __init__(self):
        self.id = "myndy_ai_http_pipeline"
        self.name = "🚀 Myndy AI HTTP Pipeline"
        self.version = "1.0.0"
        self.type = "manifold"
        
        # Get configuration from environment
        self.api_base_url = os.getenv("MYNDY_API_BASE_URL", "http://localhost:8000")
        self.api_timeout = int(os.getenv("MYNDY_API_TIMEOUT", "30"))
        
        logger.info(f"🔧 Initialized HTTP-only pipeline: {self.name}")
        logger.info(f"🔗 Backend API: {self.api_base_url}")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models/agents"""
        return [
            {
                "id": "auto",
                "name": "🧠 Myndy AI Auto-Router",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "myndy-ai-http"
            },
            {
                "id": "personal_assistant", 
                "name": "🎯 Personal Assistant",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "myndy-ai-http"
            },
            {
                "id": "research_specialist",
                "name": "🔍 Research Specialist", 
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "myndy-ai-http"
            },
            {
                "id": "memory_librarian",
                "name": "📚 Memory Librarian",
                "object": "model", 
                "created": int(datetime.now().timestamp()),
                "owned_by": "myndy-ai-http"
            },
            {
                "id": "health_analyst",
                "name": "💊 Health Analyst",
                "object": "model",
                "created": int(datetime.now().timestamp()), 
                "owned_by": "myndy-ai-http"
            }
        ]
    
    def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], 
             body: Dict[str, Any]) -> Union[str, Generator, Iterator]:
        """Process chat completion via HTTP to myndy-ai backend"""
        try:
            logger.info(f"💬 Processing message via HTTP: {user_message[:50]}...")
            logger.info(f"🎯 Model: {model_id}")
            
            # Call myndy-ai chat endpoint
            response = requests.post(
                f"{self.api_base_url}/api/v1/chat/completions",
                json={
                    "messages": messages,
                    "model": model_id,
                    "agent_type": model_id if model_id != "auto" else "personal_assistant"
                },
                timeout=self.api_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract content from OpenAI-style response
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return result.get("response", str(result))
            else:
                logger.error(f"Backend API error: {response.status_code}")
                return f"❌ **Backend Error**\n\nThe myndy-ai backend returned an error: {response.status_code}\n\nPlease check that the backend is running at {self.api_base_url}"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return f"❌ **Connection Error**\n\nCould not connect to myndy-ai backend at {self.api_base_url}\n\nError: {str(e)}"
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return f"❌ **Processing Error**\n\nAn error occurred while processing your request: {str(e)}"

# Create pipeline instance
pipeline = HTTPOnlyPipeline()

# Create FastAPI app
app = FastAPI(
    title="Myndy AI HTTP Pipeline",
    description="HTTP-only pipeline for OpenWebUI integration",
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

@app.get("/")
async def get_manifest():
    """Get pipeline manifest"""
    return {
        "id": pipeline.id,
        "name": pipeline.name,
        "version": pipeline.version,
        "type": pipeline.type,
        "description": "HTTP-only pipeline for myndy-ai integration"
    }

@app.get("/status")
async def get_status():
    """System status and metrics"""
    logger.info("📊 Status endpoint accessed")
    
    # Test backend connectivity
    backend_status = False
    try:
        response = requests.get(f"{pipeline.api_base_url}/health", timeout=5)
        backend_status = response.status_code == 200
    except:
        pass
    
    return {
        "status": "healthy" if backend_status else "degraded",
        "agents_available": len(pipeline.get_models()),
        "tools_available": "31+",
        "backend_status": backend_status,
        "backend_url": pipeline.api_base_url,
        "pipeline_type": pipeline.type,
        "pipeline_id": pipeline.id
    }

@app.get("/models")
async def get_models():
    """Get available models (with pipeline metadata)"""
    logger.info("📋 Models endpoint accessed")
    models = pipeline.get_models()
    logger.info(f"📊 Returning {len(models)} models")
    return {
        "data": models,
        "pipeline": True,
        "pipeline_type": "manifold",
        "pipeline_id": pipeline.id,
        "pipeline_name": pipeline.name,
        "type": "pipeline"
    }

@app.get("/v1/models")
async def get_v1_models():
    """Get available models (OpenAI v1 compatible)"""
    logger.info("📋 V1 models endpoint accessed")
    models = pipeline.get_models()
    return {
        "data": models,
        "pipeline": True,
        "pipeline_type": "manifold",
        "pipeline_id": pipeline.id,
        "pipeline_name": pipeline.name
    }

@app.get("/agents")
async def get_agents():
    """List all available agents"""
    logger.info("🤖 Agents endpoint accessed")
    return {
        "agents": pipeline.get_models(),
        "total": len(pipeline.get_models())
    }

@app.post("/agents/{agent_role}/chat")
async def chat_with_agent(agent_role: str, request: dict):
    """Chat with specific agent"""
    logger.info(f"🗣️ Direct chat with agent: {agent_role}")
    
    messages = request.get("messages", [])
    
    # Get user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    response = pipeline.pipe(user_message, agent_role, messages, request)
    
    return {
        "id": f"chatcmpl-{int(datetime.now().timestamp())}",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": agent_role,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response
            },
            "finish_reason": "stop"
        }]
    }

@app.get("/tools")
async def get_tools():
    """List available tools"""
    logger.info("🔧 Tools endpoint accessed")
    try:
        response = requests.get(
            f"{pipeline.api_base_url}/api/v1/tools",
            timeout=10
        )
        if response.status_code == 200:
            tools_data = response.json()
            logger.info(f"📋 Retrieved {len(tools_data.get('tools', []))} tools from backend")
            return tools_data
        else:
            logger.warning(f"Failed to get tools from backend: {response.status_code}")
            return {"tools": [], "total": 0, "error": "Backend unavailable"}
    except Exception as e:
        logger.error(f"Error connecting to backend tools API: {e}")
        return {"tools": [], "total": 0, "error": str(e)}

@app.post("/tools/execute")
async def execute_tool(request: dict):
    """Execute specific tool"""
    logger.info(f"⚡ Tool execution request: {request.get('tool_name', 'unknown')}")
    try:
        response = requests.post(
            f"{pipeline.api_base_url}/api/v1/tools/execute",
            json=request,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Tool execution successful")
            return result
        else:
            logger.error(f"Tool execution failed: {response.status_code}")
            return {"error": f"Tool execution failed: {response.status_code}"}
    except Exception as e:
        logger.error(f"Error executing tool via backend API: {e}")
        return {"error": str(e)}

@app.post("/tasks")
async def create_task(request: dict):
    """Create and execute a task"""
    logger.info(f"📋 Task creation request: {request.get('task_type', 'unknown')}")
    try:
        response = requests.post(
            f"{pipeline.api_base_url}/api/v1/tasks",
            json=request,
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Task created successfully")
            return result
        else:
            logger.error(f"Task creation failed: {response.status_code}")
            return {"error": f"Task creation failed: {response.status_code}"}
    except Exception as e:
        logger.error(f"Error creating task via backend API: {e}")
        return {"error": str(e)}

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task status and results"""
    logger.info(f"📊 Task status request: {task_id}")
    try:
        response = requests.get(
            f"{pipeline.api_base_url}/api/v1/tasks/{task_id}",
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"📋 Task status retrieved")
            return result
        else:
            logger.error(f"Task retrieval failed: {response.status_code}")
            return {"error": f"Task not found: {response.status_code}"}
    except Exception as e:
        logger.error(f"Error getting task via backend API: {e}")
        return {"error": str(e)}

@app.post("/crews/execute")
async def execute_crew(request: dict):
    """Execute multi-agent crew task"""
    logger.info(f"👥 Crew execution request")
    try:
        response = requests.post(
            f"{pipeline.api_base_url}/api/v1/crews/execute",
            json=request,
            timeout=120
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Crew execution successful")
            return result
        else:
            logger.error(f"Crew execution failed: {response.status_code}")
            return {"error": f"Crew execution failed: {response.status_code}"}
    except Exception as e:
        logger.error(f"Error executing crew via backend API: {e}")
        return {"error": str(e)}

@app.get("/pipelines")
async def get_pipelines():
    """Get pipelines for OpenWebUI detection"""
    logger.info("📋 Pipelines endpoint accessed")
    return {
        "data": [
            {
                "id": pipeline.id,
                "name": pipeline.name,
                "version": pipeline.version,
                "type": pipeline.type,
                "description": "HTTP-only pipeline for myndy-ai integration",
                "author": "Jeremy",
                "license": "MIT",
                "status": "active",
                "models": pipeline.get_models()
            }
        ]
    }

# Chat completions endpoint
async def _handle_chat_request(request: dict):
    """Handle chat completions requests"""
    try:
        messages = request.get("messages", [])
        model = request.get("model", "auto")
        
        # Get user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        response = pipeline.pipe(user_message, model, messages, request)
        
        return {
            "id": f"chatcmpl-{int(datetime.now().timestamp())}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
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
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
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

@app.post("/v1/chat/crewai")
async def crewai_pipeline_chat(request: dict):
    """Custom CrewAI pipeline endpoint"""
    logger.info("🤖 CrewAI custom endpoint accessed")
    return await _handle_chat_request(request)

@app.get("/v1/chat/crewai/models")
async def crewai_pipeline_models():
    """Models endpoint for CrewAI pipeline"""
    logger.info("📋 CrewAI models endpoint accessed")
    models = pipeline.get_models()
    return {
        "data": models,
        "object": "list"
    }

if __name__ == "__main__":
    print("🚀 Starting HTTP-Only Myndy AI Pipeline Server")
    print("=" * 60)
    print(f"🔗 Backend API: {pipeline.api_base_url}")
    print("🌐 Server will be available at: http://localhost:9099")
    print("🔗 Add to OpenWebUI: http://localhost:9099")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9099,
        log_level="info"
    )