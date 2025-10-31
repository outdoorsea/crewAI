"""
API Models for CrewAI-Myndy OpenAPI Server

Pydantic models for request/response validation and OpenAPI documentation.

File: api/models.py
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Available agent roles in the CrewAI-Myndy system."""
    
    MEMORY_LIBRARIAN = "memory_librarian"
    RESEARCH_SPECIALIST = "research_specialist"
    PERSONAL_ASSISTANT = "personal_assistant"
    HEALTH_ANALYST = "health_analyst"
    FINANCE_TRACKER = "finance_tracker"
    SHADOW_AGENT = "shadow_agent"


class TaskType(str, Enum):
    """Available task types for agent execution."""
    
    LIFE_ANALYSIS = "life_analysis"
    RESEARCH_PROJECT = "research_project" 
    HEALTH_OPTIMIZATION = "health_optimization"
    FINANCIAL_PLANNING = "financial_planning"
    CUSTOM = "custom"


class Priority(str, Enum):
    """Task priority levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task execution status."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Request Models

class ChatMessage(BaseModel):
    """A single chat message."""
    
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class AgentChatRequest(BaseModel):
    """Request for chatting with a specific agent."""
    
    agent_role: AgentRole = Field(..., description="Which agent to chat with")
    message: str = Field(..., description="User message to the agent")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the agent")
    stream: bool = Field(default=False, description="Whether to stream the response")
    memory_enabled: bool = Field(default=True, description="Whether to use memory for context")


class TaskRequest(BaseModel):
    """Request for creating and executing a task."""
    
    task_type: TaskType = Field(..., description="Type of task to execute")
    description: str = Field(..., description="Detailed task description")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Task-specific parameters")
    agent_role: Optional[AgentRole] = Field(default=None, description="Specific agent to use (optional)")
    priority: Priority = Field(default=Priority.MEDIUM, description="Task priority")
    timeout: Optional[int] = Field(default=300, description="Task timeout in seconds")


class CrewTaskRequest(BaseModel):
    """Request for executing a multi-agent crew task."""
    
    task_type: TaskType = Field(..., description="Type of crew task")
    description: str = Field(..., description="Task description")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Task parameters")
    agents: Optional[List[AgentRole]] = Field(default=None, description="Specific agents to include")
    collaboration_mode: str = Field(default="sequential", description="How agents should collaborate")


class ToolRequest(BaseModel):
    """Request for executing a specific tool."""
    
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    agent_context: Optional[str] = Field(default=None, description="Agent context for tool execution")


class MemorySearchRequest(BaseModel):
    """Request for searching memory."""
    
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, description="Maximum number of results")
    entity_types: Optional[List[str]] = Field(default=None, description="Filter by entity types")
    time_range: Optional[Dict[str, str]] = Field(default=None, description="Time range filter")


# Response Models

class AgentInfo(BaseModel):
    """Information about an agent."""
    
    role: AgentRole
    name: str
    description: str
    capabilities: List[str]
    tools_count: int
    model: str
    status: str = Field(default="available")


class ToolInfo(BaseModel):
    """Information about a tool."""
    
    name: str
    description: str
    category: str
    parameters: Dict[str, Any]
    examples: Optional[List[Dict[str, Any]]] = None


class TaskResponse(BaseModel):
    """Response from task execution."""
    
    task_id: str
    status: TaskStatus
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class AgentChatResponse(BaseModel):
    """Response from agent chat."""
    
    agent_role: AgentRole
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tools_used: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    memory_accessed: bool = False


class SystemStatus(BaseModel):
    """Overall system status."""
    
    status: str
    agents_available: int
    tools_available: int
    memory_status: bool
    ollama_status: bool
    active_tasks: int
    uptime: str
    version: str = "1.0.0"


class MemorySearchResponse(BaseModel):
    """Response from memory search."""
    
    results: List[Dict[str, Any]]
    total_count: int
    query: str
    execution_time: float


class HealthCheck(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None


class StreamResponse(BaseModel):
    """Streaming response chunk."""
    
    chunk: str
    finished: bool = False
    metadata: Optional[Dict[str, Any]] = None


# Configuration Models

class AgentConfig(BaseModel):
    """Configuration for an agent."""
    
    role: AgentRole
    model: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 2048
    tools_enabled: bool = True
    memory_enabled: bool = True
    verbose: bool = False


class APIConfig(BaseModel):
    """API server configuration."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["*"]
    api_key_required: bool = False
    rate_limit: Optional[int] = None
    log_level: str = "INFO"


# OpenAPI Metadata

API_METADATA = {
    "title": "CrewAI-Myndy Integration API",
    "description": """
    OpenAPI server for the CrewAI-Myndy integration, providing access to:
    
    - **5 Specialized AI Agents** with distinct roles and capabilities
    - **31+ Myndy Tools** for personal productivity and data analysis  
    - **Multi-Agent Workflows** for complex task orchestration
    - **Memory System** with persistent context and knowledge graphs
    - **Local LLM Inference** via Ollama (privacy-first approach)
    
    Perfect for integration with Open WebUI and other front-end interfaces.
    """,
    "version": "1.0.0",
    "contact": {
        "name": "CrewAI-Myndy Integration",
        "url": "https://github.com/your-repo/crewai-myndy"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    "tags": [
        {
            "name": "agents",
            "description": "Individual agent interactions and management"
        },
        {
            "name": "tasks", 
            "description": "Task creation and execution"
        },
        {
            "name": "crews",
            "description": "Multi-agent crew workflows"
        },
        {
            "name": "tools",
            "description": "Tool discovery and execution"
        },
        {
            "name": "memory",
            "description": "Memory system and knowledge management"
        },
        {
            "name": "system",
            "description": "System status and configuration"
        }
    ]
}