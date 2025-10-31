#!/usr/bin/env python3
"""
Simple OpenAPI Server for CrewAI-Myndy Integration

Simplified server that works independently for testing with Open WebUI.

File: api/simple_server.py
"""

import json
import logging
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple models for the API
class AgentRole:
    MEMORY_LIBRARIAN = "memory_librarian"
    RESEARCH_SPECIALIST = "research_specialist"
    PERSONAL_ASSISTANT = "personal_assistant"
    HEALTH_ANALYST = "health_analyst"
    FINANCE_TRACKER = "finance_tracker"

class OpenAIMessage(BaseModel):
    role: str
    content: str

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False

class OpenAIModel(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "crewai-myndy"

class HealthCheck(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"

# Create FastAPI app
app = FastAPI(
    title="CrewAI-Myndy Integration API",
    description="Multi-agent AI system with specialized agents for personal productivity",
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

# Agent information
AGENTS = {
    AgentRole.MEMORY_LIBRARIAN: {
        "name": "Memory Librarian",
        "description": "Organizes and retrieves personal knowledge, entities, and conversation history",
        "model": "llama3",
        "capabilities": ["memory management", "entity relationships", "conversation history"]
    },
    AgentRole.RESEARCH_SPECIALIST: {
        "name": "Research Specialist", 
        "description": "Conducts research, gathers information, and verifies facts",
        "model": "mixtral",
        "capabilities": ["web research", "fact verification", "document analysis"]
    },
    AgentRole.PERSONAL_ASSISTANT: {
        "name": "Personal Assistant",
        "description": "Manages calendar, email, contacts, and personal productivity",
        "model": "gemma", 
        "capabilities": ["calendar management", "email processing", "task coordination"]
    },
    AgentRole.HEALTH_ANALYST: {
        "name": "Health Analyst",
        "description": "Analyzes health data and provides wellness insights",
        "model": "phi",
        "capabilities": ["health analysis", "fitness tracking", "wellness optimization"]
    },
    AgentRole.FINANCE_TRACKER: {
        "name": "Finance Tracker", 
        "description": "Tracks expenses, analyzes spending, and provides financial insights",
        "model": "mistral",
        "capabilities": ["expense tracking", "budget analysis", "financial planning"]
    }
}

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now()
    )

@app.get("/status")
async def get_status():
    """Get system status."""
    return {
        "status": "operational",
        "agents_available": len(AGENTS),
        "tools_available": 31,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    models = []
    for agent_id, agent_info in AGENTS.items():
        models.append(OpenAIModel(
            id=agent_id,
            created=int(datetime.now().timestamp())
        ))
    
    return {"object": "list", "data": models}

@app.post("/chat/completions")
async def chat_completions(request: OpenAIChatRequest):
    """OpenAI-compatible chat completions endpoint."""
    try:
        # Get agent info
        agent_info = AGENTS.get(request.model)
        if not agent_info:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")
        
        # Get the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_message = user_messages[-1].content
        
        # Generate response based on agent
        agent_name = agent_info["name"]
        agent_desc = agent_info["description"]
        capabilities = ", ".join(agent_info["capabilities"])
        
        response_content = f"""Hello! I'm the {agent_name}. {agent_desc}

You asked: "{last_message}"

My capabilities include: {capabilities}

I'm part of the CrewAI-Myndy integration system with access to 31+ specialized tools. I can help you with tasks related to my expertise area.

How can I assist you today?"""
        
        return {
            "id": f"chatcmpl-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant", 
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": sum(len(msg.content.split()) for msg in request.messages),
                "completion_tokens": len(response_content.split()),
                "total_tokens": sum(len(msg.content.split()) for msg in request.messages) + len(response_content.split())
            }
        }
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List all available agents."""
    return [
        {
            "id": agent_id,
            "name": agent_info["name"],
            "description": agent_info["description"],
            "model": agent_info["model"],
            "capabilities": agent_info["capabilities"]
        }
        for agent_id, agent_info in AGENTS.items()
    ]

@app.get("/docs-info")
async def get_docs_info():
    """Information about API documentation."""
    return {
        "openapi_url": "/openapi.json",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "description": "CrewAI-Myndy Integration API - Multi-agent system for personal productivity"
    }

def main():
    """Run the server."""
    logger.info("Starting CrewAI-Myndy OpenAPI Server (Simple)")
    logger.info("Compatible with Open WebUI")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()