"""
Pipeline Server for OpenWebUI

This creates a simple FastAPI server that hosts the CrewAI-Myndy pipeline
for integration with OpenWebUI.

File: pipeline/server.py
"""

import logging
import os
import signal
import subprocess
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from crewai_memex_pipeline import Pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Myndy AI v0.1",
    description="Your personal intelligent assistant with conversation-driven learning",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = Pipeline()

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "pipeline": "myndy-ai",
        "version": "0.1.0",
        "name": "Myndy AI",
        "agents_available": len(pipeline.agents)
    }

# Pipeline endpoints for OpenWebUI
@app.get("/models")
async def get_models():
    """Get available models/agents"""
    return {
        "data": pipeline.get_models(),
        "pipelines": True  # This tells OpenWebUI that pipelines are supported
    }

@app.get("/v1/models")
async def get_v1_models():
    """Get available models/agents (OpenAI v1 compatible)"""
    return {
        "data": pipeline.get_models(),
        "pipelines": True  # This tells OpenWebUI that pipelines are supported
    }

@app.get("/manifest")
async def get_manifest():
    """Get pipeline manifest for OpenWebUI"""
    return pipeline.get_manifest()

@app.get("/pipeline")
async def get_pipeline_info():
    """Get pipeline information for OpenWebUI"""
    return {
        "id": pipeline.id,
        "name": pipeline.name,
        "type": pipeline.type,
        "version": pipeline.version,
        "description": "Myndy AI - Your personal intelligent assistant with conversation-driven learning",
        "models": pipeline.get_models(),
        "status": "active"
    }

# OpenWebUI Pipeline API endpoints
@app.get("/api/v1/pipelines/list")
async def list_pipelines():
    """List available pipelines for OpenWebUI"""
    return {
        "data": [
            {
                "id": pipeline.id,
                "name": pipeline.name,
                "type": pipeline.type,
                "version": pipeline.version,
                "description": "Intelligent agent routing and myndy tool execution",
                "author": "Jeremy",
                "license": "MIT",
                "status": "active",
                "models": pipeline.get_models()
            }
        ]
    }

@app.get("/api/pipelines")
async def get_pipelines():
    """Get pipelines for OpenWebUI"""
    return {
        "data": [
            {
                "id": pipeline.id,
                "name": pipeline.name,
                "type": pipeline.type,
                "version": pipeline.version,
                "description": "Intelligent agent routing and myndy tool execution",
                "author": "Jeremy",
                "license": "MIT",
                "status": "active"
            }
        ]
    }

@app.get("/pipelines")
async def get_pipelines_root():
    """Get pipelines at root level for OpenWebUI"""
    return {
        "data": [
            {
                "id": pipeline.id,
                "name": pipeline.name,
                "type": pipeline.type,
                "version": pipeline.version,
                "description": "Intelligent agent routing and myndy tool execution",
                "author": "Jeremy",
                "license": "MIT",
                "status": "active",
                "models": pipeline.get_models()
            }
        ]
    }

@app.get("/{pipeline_id}/valves/spec")
async def get_valves_spec(pipeline_id: str):
    """Get pipeline valves specification"""
    if pipeline_id == pipeline.id:
        return {
            "type": "object",
            "properties": {
                "enable_intelligent_routing": {
                    "type": "boolean",
                    "default": True,
                    "title": "Enable Intelligent Routing"
                },
                "enable_tool_execution": {
                    "type": "boolean", 
                    "default": True,
                    "title": "Enable Tool Execution"
                },
                "debug_mode": {
                    "type": "boolean",
                    "default": False,
                    "title": "Debug Mode"
                }
            }
        }
    else:
        return {"error": "Pipeline not found"}

@app.get("/{pipeline_id}/valves")
async def get_valves(pipeline_id: str):
    """Get current pipeline valves values"""
    if pipeline_id == pipeline.id:
        return {
            "enable_intelligent_routing": pipeline.valves.enable_intelligent_routing,
            "enable_tool_execution": pipeline.valves.enable_tool_execution,
            "debug_mode": pipeline.valves.debug_mode
        }
    else:
        return {"error": "Pipeline not found"}

async def _handle_chat_completions(request: dict):
    """Handle chat completions logic"""
    try:
        messages = request.get("messages", [])
        model = request.get("model", "auto")
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Process through pipeline
        response = pipeline.pipe(
            user_message=user_message,
            model_id=model,
            messages=messages,
            body=request
        )
        
        # Return OpenAI-compatible response
        return {
            "id": f"chatcmpl-{int(__import__('time').time())}",
            "object": "chat.completion", 
            "created": int(__import__('time').time()),
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
                "completion_tokens": len(str(response).split()),
                "total_tokens": len(user_message.split()) + len(str(response).split())
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

@app.post("/chat/completions")
async def chat_completions(request: dict):
    """Handle chat completions"""
    logger.info("🔥 CHAT REQUEST RECEIVED!")
    logger.info(f"📝 Model: {request.get('model', 'unknown')}")
    messages = request.get('messages', [])
    if messages:
        last_msg = messages[-1].get('content', '')[:100]
        logger.info(f"💬 Message: {last_msg}...")
    return await _handle_chat_completions(request)

@app.post("/v1/chat/completions")
async def v1_chat_completions(request: dict):
    """Handle chat completions (OpenAI v1 compatible)"""
    logger.info("🔥 V1 CHAT REQUEST RECEIVED!")
    logger.info(f"📝 Model: {request.get('model', 'unknown')}")
    messages = request.get('messages', [])
    if messages:
        last_msg = messages[-1].get('content', '')[:100]
        logger.info(f"💬 Message: {last_msg}...")
    return await _handle_chat_completions(request)

def shutdown_existing_servers():
    """Shutdown any existing server instances on port 9099"""
    try:
        # Find processes using port 9099
        result = subprocess.run(
            ["lsof", "-ti:9099"], 
            capture_output=True, 
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    logger.info(f"🔄 Shutting down existing server (PID: {pid})")
                    os.kill(int(pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass  # Process already dead
                except Exception as e:
                    logger.warning(f"Failed to kill process {pid}: {e}")
        
        # Also check for python processes running server files
        result = subprocess.run(
            ["pgrep", "-f", "server.*py"], 
            capture_output=True, 
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    # Check if it's actually our server
                    cmd_result = subprocess.run(
                        ["ps", "-p", pid, "-o", "command="], 
                        capture_output=True, 
                        text=True
                    )
                    if "server" in cmd_result.stdout and "9099" in cmd_result.stdout:
                        logger.info(f"🔄 Shutting down existing server process (PID: {pid})")
                        os.kill(int(pid), signal.SIGTERM)
                except (ProcessLookupError, ValueError):
                    pass
                except Exception as e:
                    logger.warning(f"Failed to kill process {pid}: {e}")
                    
    except FileNotFoundError:
        # lsof or pgrep not available
        pass
    except Exception as e:
        logger.warning(f"Error checking for existing servers: {e}")

def main():
    """Run the pipeline server"""
    # Shutdown any existing servers first
    shutdown_existing_servers()
    
    logger.info("Starting CrewAI-Myndy Pipeline Server")
    logger.info("🚀 Features: Intelligent Agent Routing + Contact Management + Memory Search")
    logger.info("🤖 Available agents: 5 specialized agents + auto-routing")
    logger.info("🌐 Server starting on http://localhost:9099")
    logger.info("📋 Add this URL to OpenWebUI Pipelines: http://localhost:9099")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9099,
        log_level="info"
    )

if __name__ == "__main__":
    main()