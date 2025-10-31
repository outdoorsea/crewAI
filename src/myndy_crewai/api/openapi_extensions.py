"""
OpenAPI Extensions for Open WebUI Compatibility

Additional endpoints and compatibility layer for Open WebUI integration.

File: api/openapi_extensions.py
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api.models import AgentRole


class OpenAIMessage(BaseModel):
    """OpenAI-compatible message format."""
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    """OpenAI-compatible chat request."""
    model: str
    messages: List[OpenAIMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False
    user: Optional[str] = None


class OpenAIChatResponse(BaseModel):
    """OpenAI-compatible chat response."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class OpenAIModel(BaseModel):
    """OpenAI-compatible model representation."""
    id: str
    object: str = "model"
    created: int
    owned_by: str = "crewai-myndy"


def add_openai_compatibility(app: FastAPI):
    """Add OpenAI-compatible endpoints for Open WebUI integration."""
    
    @app.get("/models")
    async def list_models():
        """List available models (OpenAI-compatible)."""
        models = [
            OpenAIModel(
                id="memory_librarian",
                created=int(datetime.now().timestamp())
            ),
            OpenAIModel(
                id="research_specialist", 
                created=int(datetime.now().timestamp())
            ),
            OpenAIModel(
                id="personal_assistant",
                created=int(datetime.now().timestamp())
            ),
            OpenAIModel(
                id="health_analyst",
                created=int(datetime.now().timestamp())
            ),
            OpenAIModel(
                id="finance_tracker",
                created=int(datetime.now().timestamp())
            )
        ]
        
        return {"object": "list", "data": models}
    
    @app.post("/chat/completions")
    async def chat_completions(request: OpenAIChatRequest):
        """OpenAI-compatible chat completions endpoint."""
        try:
            # Extract the agent role from model name
            agent_role = request.model
            
            # Get the last user message
            user_messages = [msg for msg in request.messages if msg.role == "user"]
            if not user_messages:
                raise HTTPException(status_code=400, detail="No user message found")
            
            last_message = user_messages[-1].content
            
            # Generate response based on agent
            if agent_role == "memory_librarian":
                response_content = f"As your Memory Librarian, I can help you organize and retrieve information. You asked: '{last_message}'. I have access to your knowledge base and conversation history."
            elif agent_role == "research_specialist":
                response_content = f"As your Research Specialist, I can conduct thorough research and fact-checking. Regarding '{last_message}', I can gather information from multiple sources and verify facts."
            elif agent_role == "personal_assistant":
                response_content = f"As your Personal Assistant, I can help with calendar, email, and productivity tasks. For '{last_message}', I can coordinate your schedule and manage your communications."
            elif agent_role == "health_analyst":
                response_content = f"As your Health Analyst, I can analyze your health data and provide wellness insights. About '{last_message}', I can review your health metrics and suggest improvements."
            elif agent_role == "finance_tracker":
                response_content = f"As your Finance Tracker, I can analyze your spending and provide financial insights. Regarding '{last_message}', I can review your financial data and offer recommendations."
            else:
                response_content = f"I'm an AI agent from the CrewAI-Myndy system. You said: '{last_message}'. How can I assist you with my specialized capabilities?"
            
            return OpenAIChatResponse(
                id=f"chatcmpl-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                created=int(datetime.now().timestamp()),
                model=request.model,
                choices=[{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }],
                usage={
                    "prompt_tokens": sum(len(msg.content.split()) for msg in request.messages),
                    "completion_tokens": len(response_content.split()),
                    "total_tokens": sum(len(msg.content.split()) for msg in request.messages) + len(response_content.split())
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app