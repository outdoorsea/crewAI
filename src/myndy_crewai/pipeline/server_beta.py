"""
Beta Pipeline Server for OpenWebUI

This creates a FastAPI server for the enhanced Myndy AI Beta pipeline
to compete with the main version.

File: pipeline/server_beta.py
"""

import logging
import os
import signal
import subprocess
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from myndy_ai_beta import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Myndy AI Beta v0.2.0",
    description="Enhanced personal intelligent assistant with optimized routing and performance competition",
    version="0.2.0-beta"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "pipeline": "myndy-ai-beta",
        "version": "0.2.0-beta",
        "name": "Myndy AI Beta",
        "agents_available": len(pipeline.agents),
        "features": ["enhanced_routing", "performance_optimization", "competitive_testing"]
    }

# Pipeline endpoints for OpenWebUI
@app.get("/models")
async def get_models():
    """Get available models/agents"""
    return {
        "data": pipeline.get_models(),
        "pipelines": True
    }

@app.get("/v1/models")
async def get_v1_models():
    """Get available models/agents (OpenAI v1 compatible)"""
    return {
        "data": pipeline.get_models(),
        "pipelines": True
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
        "description": "Myndy AI Beta - Enhanced intelligent assistant with competitive performance testing",
        "models": pipeline.get_models(),
        "status": "active"
    }

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
                "description": "Enhanced intelligent agent routing with performance optimization",
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
                "description": "Enhanced intelligent agent routing with performance optimization",
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
                "description": "Enhanced intelligent agent routing with performance optimization",
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
                "enable_enhanced_routing": {
                    "type": "boolean",
                    "default": True,
                    "title": "Enable Enhanced Routing (Beta)"
                },
                "enable_tool_execution": {
                    "type": "boolean", 
                    "default": True,
                    "title": "Enable Tool Execution"
                },
                "enable_learning": {
                    "type": "boolean",
                    "default": True,
                    "title": "Enable Learning from Feedback (Beta)"
                },
                "enable_fast_mode": {
                    "type": "boolean",
                    "default": True,
                    "title": "Enable Fast Mode (Beta)"
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
            "enable_enhanced_routing": pipeline.valves.enable_enhanced_routing,
            "enable_tool_execution": pipeline.valves.enable_tool_execution,
            "enable_learning": pipeline.valves.enable_learning,
            "enable_fast_mode": pipeline.valves.enable_fast_mode,
            "debug_mode": pipeline.valves.debug_mode
        }
    else:
        return {"error": "Pipeline not found"}

async def _handle_chat_completions(request: dict):
    """Handle chat completions logic"""
    try:
        messages = request.get("messages", [])
        model = request.get("model", "auto_beta")
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Process through enhanced pipeline
        response = pipeline.pipe(
            user_message=user_message,
            model_id=model,
            messages=messages,
            body=request
        )
        
        # Return OpenAI-compatible response
        return {
            "id": f"chatcmpl-beta-{int(__import__('time').time())}",
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
        logger.error(f"Beta chat completion error: {e}")
        return {
            "error": {
                "message": str(e),
                "type": "beta_pipeline_error"
            }
        }

@app.post("/chat/completions")
async def chat_completions(request: dict):
    """Handle chat completions"""
    logger.info("🚀 BETA CHAT REQUEST RECEIVED!")
    logger.info(f"📝 Model: {request.get('model', 'unknown')}")
    messages = request.get('messages', [])
    if messages:
        last_msg = messages[-1].get('content', '')[:100]
        logger.info(f"💬 Message: {last_msg}...")
    return await _handle_chat_completions(request)

@app.post("/v1/chat/completions")
async def v1_chat_completions(request: dict):
    """Handle chat completions (OpenAI v1 compatible)"""
    logger.info("🚀 BETA V1 CHAT REQUEST RECEIVED!")
    logger.info(f"📝 Model: {request.get('model', 'unknown')}")
    messages = request.get('messages', [])
    if messages:
        last_msg = messages[-1].get('content', '')[:100]
        logger.info(f"💬 Message: {last_msg}...")
    return await _handle_chat_completions(request)

def shutdown_existing_servers():
    """Shutdown any existing server instances on port 9100"""
    try:
        # Find processes using port 9100
        result = subprocess.run(
            ["lsof", "-ti:9100"], 
            capture_output=True, 
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    logger.info(f"🔄 Shutting down existing beta server (PID: {pid})")
                    os.kill(int(pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
                except Exception as e:
                    logger.warning(f"Failed to kill process {pid}: {e}")
                    
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.warning(f"Error checking for existing beta servers: {e}")

def main():
    """Run the beta pipeline server"""
    shutdown_existing_servers()
    
    logger.info("Starting Myndy AI Beta Pipeline Server")
    logger.info("🚀 Features: Enhanced Routing + Performance Optimization + Competitive Testing")
    logger.info("🤖 Available agents: 5 enhanced agents + optimized auto-routing")
    logger.info("🌐 Beta server starting on http://localhost:9100")
    logger.info("📋 Add this URL to OpenWebUI Pipelines: http://localhost:9100")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9100,
        log_level="info"
    )

if __name__ == "__main__":
    main()