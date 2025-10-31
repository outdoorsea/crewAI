#!/usr/bin/env python3
"""
Simple Pipeline Server for OpenWebUI
A lightweight version that doesn't require heavy ML dependencies initially
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Union, Generator, Iterator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Myndy AI Pipeline (Simple)",
    description="Lightweight Myndy AI integration for OpenWebUI",
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

class SimplePipeline:
    """Simplified version of the Myndy AI pipeline"""
    
    def __init__(self):
        self.type = "manifold"
        self.id = "myndy_ai_simple"
        self.name = "Myndy AI (Simple)"
        self.version = "1.0.0"
        
        # Agent definitions
        self.agents = {
            "memory_librarian": {
                "name": "Memory Librarian",
                "description": "Organizes and retrieves personal knowledge and contacts",
            },
            "research_specialist": {
                "name": "Research Specialist", 
                "description": "Conducts research and gathers information",
            },
            "personal_assistant": {
                "name": "Personal Assistant",
                "description": "Manages calendar, weather, and productivity",
            },
            "health_analyst": {
                "name": "Health Analyst",
                "description": "Analyzes health data and provides wellness insights", 
            },
            "finance_tracker": {
                "name": "Finance Tracker",
                "description": "Tracks expenses and provides financial insights",
            }
        }
        
        logger.info(f"Simple Myndy AI Pipeline {self.version} initialized")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models/agents"""
        models = []
        
        # Add auto-routing model
        models.append({
            "id": "auto",
            "name": "🧠 Myndy AI (Simple)",
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
    
    def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], 
             body: Dict[str, Any]) -> str:
        """Process messages through the simplified pipeline"""
        
        logger.info(f"Processing message with model: {model_id}")
        
        # Simple routing logic
        if model_id == "auto":
            # Basic keyword routing
            message_lower = user_message.lower()
            if any(word in message_lower for word in ["contact", "person", "remember", "know"]):
                selected_agent = "memory_librarian"
            elif any(word in message_lower for word in ["weather", "time", "schedule", "calendar"]):
                selected_agent = "personal_assistant"
            elif any(word in message_lower for word in ["research", "analyze", "find", "search"]):
                selected_agent = "research_specialist"
            elif any(word in message_lower for word in ["health", "fitness", "exercise", "sleep"]):
                selected_agent = "health_analyst"
            elif any(word in message_lower for word in ["money", "expense", "budget", "finance"]):
                selected_agent = "finance_tracker"
            else:
                selected_agent = "personal_assistant"  # Default
        else:
            selected_agent = model_id
        
        # Get agent info
        agent_info = self.agents.get(selected_agent, {"name": "Unknown Agent"})
        
        # Generate response
        response_parts = []
        response_parts.append(f"🤖 **{agent_info['name']}** (Simple Mode)")
        
        if model_id == "auto":
            response_parts.append(f"**Routing:** Auto-selected {agent_info['name']} based on message content")
        
        response_parts.append("")  # Empty line
        
        # Simple response based on agent type
        if selected_agent == "memory_librarian":
            response_parts.append("📚 **Memory Search**: I would search for contacts and personal information in your knowledge base.")
            response_parts.append("💡 **Note**: Full functionality requires complete installation with CrewAI and Myndy tools.")
        elif selected_agent == "personal_assistant":
            response_parts.append("🗓️ **Personal Assistant**: I would help with scheduling, weather, and productivity tasks.")
            response_parts.append("💡 **Note**: Full functionality requires complete installation with weather and calendar tools.")
        elif selected_agent == "research_specialist":
            response_parts.append("🔍 **Research**: I would conduct research and analysis on your topic.")
            response_parts.append("💡 **Note**: Full functionality requires complete installation with research and analysis tools.")
        elif selected_agent == "health_analyst":
            response_parts.append("🏥 **Health Analysis**: I would analyze your health data and provide wellness insights.")
            response_parts.append("💡 **Note**: Full functionality requires complete installation with health tracking tools.")
        elif selected_agent == "finance_tracker":
            response_parts.append("💰 **Finance Tracking**: I would track your expenses and provide financial analysis.")
            response_parts.append("💡 **Note**: Full functionality requires complete installation with financial tools.")
        
        response_parts.append(f"\n**Your message**: {user_message}")
        response_parts.append("\n**🚀 Upgrade Instructions**:")
        response_parts.append("To get full functionality, install all dependencies:")
        response_parts.append("```bash")
        response_parts.append("cd /Users/jeremy/crewAI")
        response_parts.append("source venv/bin/activate")
        response_parts.append("pip install crewai sentence-transformers qdrant-client langchain")
        response_parts.append("python -m uvicorn server:app --port 9099")
        response_parts.append("```")
        
        return "\n".join(response_parts)

# Initialize pipeline
pipeline = SimplePipeline()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Myndy AI Pipeline (Simple Mode)", 
        "version": pipeline.version,
        "status": "running"
    }

@app.get("/v1/models")
async def get_models():
    """Get available models"""
    return {"data": pipeline.get_models()}

@app.get("/models")
async def get_models_simple():
    """Get available models (alternative endpoint)"""
    return {"data": pipeline.get_models()}

@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """Handle chat completion requests"""
    try:
        # Extract information from request
        messages = request.get("messages", [])
        model_id = request.get("model", "auto")
        
        # Get the last user message
        user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break
        
        # Process through pipeline
        response = pipeline.pipe(
            user_message=user_message,
            model_id=model_id,
            messages=messages,
            body=request
        )
        
        # Return OpenAI-compatible response
        return {
            "id": f"chatcmpl-{datetime.now().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": model_id,
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
        logger.error(f"Error processing request: {e}")
        return {
            "error": {
                "message": str(e),
                "type": "pipeline_error",
                "code": "processing_failed"
            }
        }

if __name__ == "__main__":
    print("🚀 Starting Myndy AI Pipeline (Simple Mode)")
    print("=" * 50)
    print("This is a lightweight version that works without heavy ML dependencies.")
    print("For full functionality, install all dependencies and use the main server.")
    print("=" * 50)
    print("Server will be available at: http://localhost:9099")
    print("Add this URL to OpenWebUI pipelines to use.")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=9099)