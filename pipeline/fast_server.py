#!/usr/bin/env python3
"""
Fast CrewAI Pipeline Server for OpenWebUI
Optimized for quick responses and streaming support
"""

import os
import sys
import json
import time
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Generator, Iterator
from pathlib import Path

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

class FastPipeline:
    """Fast, lightweight pipeline for OpenWebUI"""
    
    def __init__(self):
        self.id = "myndy_ai"
        self.name = "Myndy AI Fast"
        self.version = "1.0.0"
        self.type = "manifold"
        
        # Available agents
        self.agents = {
            "personal_assistant": {
                "name": "Personal Assistant",
                "description": "Your comprehensive AI assistant for all tasks"
            },
            "auto": {
                "name": "Auto Router", 
                "description": "Automatically selects the best agent for your request"
            }
        }
        
        logger.info(f"🚀 Fast Pipeline initialized with {len(self.agents)} agents")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models for OpenWebUI"""
        models = []
        for agent_id, agent_info in self.agents.items():
            models.append({
                "id": agent_id,
                "name": agent_info["name"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "myndy-ai",
                "description": agent_info["description"]
            })
        return models
    
    def pipe(self, body: Dict[str, Any]) -> str:
        """Fast processing pipeline"""
        messages = body.get("messages", [])
        model = body.get("model", "auto")
        
        # Get user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Quick response generation
        agent_name = self.agents.get(model, self.agents["personal_assistant"])["name"]
        
        # Simple intelligent routing based on keywords
        if model == "auto":
            if any(keyword in user_message.lower() for keyword in ['time', 'clock', 'schedule', 'calendar']):
                response = f"**Personal Assistant**: I can help you with time and scheduling queries. You asked about: '{user_message}'\n\nCurrently, I need connection to the full Myndy AI backend to provide real-time data. For full functionality including calendar integration and tool execution, please start the complete Myndy AI system."
            elif any(keyword in user_message.lower() for keyword in ['weather', 'temperature', 'forecast']):
                response = f"**Personal Assistant**: I can help with weather queries. You asked: '{user_message}'\n\nTo provide current weather data and forecasts, I need access to the full Myndy AI backend with weather APIs enabled."
            else:
                response = f"**Personal Assistant**: I'm your AI assistant. You said: '{user_message}'\n\nI can help with various tasks including:\n• Calendar and scheduling\n• Information management\n• Research and analysis\n• General productivity\n\nFor full tool integration and real-time data access, connect to the complete Myndy AI backend system."
        else:
            response = f"**{agent_name}**: I received your message: '{user_message}'\n\nI'm operating in fast mode for quick responses. For full functionality including tool execution, memory access, and real-time data, please use the complete CrewAI pipeline with backend integration."
        
        return response

# Initialize pipeline
pipeline = FastPipeline()

# Create FastAPI app
app = FastAPI(
    title="Myndy AI Fast Pipeline",
    description="Fast, lightweight CrewAI pipeline for OpenWebUI with quick responses",
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
        "pipeline": "myndy-ai-fast",
        "version": "1.0.0",
        "agents_available": len(pipeline.agents)
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

# Fast chat completions
async def _handle_chat_completions(request: dict) -> dict:
    """Handle chat completions with fast processing"""
    try:
        messages = request.get("messages", [])
        model = request.get("model", "auto")
        stream = request.get("stream", False)
        
        # Get user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        logger.info(f"💬 Fast processing: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
        
        # Fast processing
        start_time = time.time()
        response = pipeline.pipe(request)
        processing_time = time.time() - start_time
        
        logger.info(f"⚡ Response generated in {processing_time:.2f}s")
        
        # Always return standard JSON response (streaming handled in endpoints)
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

async def _generate_stream_response(request: dict):
    """Generate streaming response for endpoints"""
    messages = request.get("messages", [])
    model = request.get("model", "auto")
    
    # Get user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    # Generate response
    response = pipeline.pipe(request)
    
    # Stream the response
    words = response.split()
    for i, word in enumerate(words):
        chunk = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"content": word + " " if i < len(words) - 1 else word},
                "finish_reason": None if i < len(words) - 1 else "stop"
            }]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.05)  # Small delay for streaming effect
    
    yield "data: [DONE]\n\n"

# Chat completions endpoints
@app.post("/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    # Force non-streaming for now to fix OpenWebUI compatibility
    body["stream"] = False
    # Return JSON response
    return await _handle_chat_completions(body)

@app.post("/v1/chat/completions")
async def v1_chat_completions(request: Request):
    body = await request.json()
    # Force non-streaming for now to fix OpenWebUI compatibility  
    body["stream"] = False
    # Return JSON response
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
            "description": "Fast Myndy AI pipeline optimized for quick responses",
            "author": "Jeremy",
            "license": "MIT",
            "status": "active",
            "models": pipeline.get_models()
        }]
    }

def main():
    """Run the fast pipeline server"""
    logger.info("🚀 Starting Myndy AI Fast Pipeline Server")
    logger.info("⚡ Optimized for quick responses and OpenWebUI compatibility")
    logger.info(f"🤖 Available agents: {list(pipeline.agents.keys())}")
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