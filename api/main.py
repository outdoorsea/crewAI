"""
CrewAI-Myndy OpenAPI Server

FastAPI server providing OpenAPI endpoints for the CrewAI-Myndy integration.
Compatible with Open WebUI and other front-end interfaces.

File: api/main.py
"""

import asyncio
import logging
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add myndy to path  
MYNDY_PATH = Path("/Users/jeremy/myndy")
sys.path.insert(0, str(MYNDY_PATH))

try:
    from api.models import *
    from tools.myndy_bridge import MyndyToolLoader, get_tool_loader
    from config.llm_config import LLMConfig, get_llm_config
    # Note: crews module has import issues, will implement basic functionality
    PersonalProductivityCrew = None
except ImportError as e:
    logger.warning(f"Some imports failed: {e}")
    # Define minimal fallbacks
    class AgentRole:
        MEMORY_LIBRARIAN = "memory_librarian"
        RESEARCH_SPECIALIST = "research_specialist"
        PERSONAL_ASSISTANT = "personal_assistant"
        HEALTH_ANALYST = "health_analyst"
        FINANCE_TRACKER = "finance_tracker"

# Security
security = HTTPBearer(auto_error=False)

# Global state
app_state = {
    "start_time": datetime.now(),
    "active_tasks": {},
    "tool_loader": None,
    "llm_config": None,
    "crew_manager": None
}

def initialize_system():
    """Initialize the CrewAI-Myndy system components."""
    try:
        logger.info("Initializing CrewAI-Myndy system...")
        
        # Initialize tool loader
        app_state["tool_loader"] = get_tool_loader()
        logger.info("Tool loader initialized")
        
        # Initialize LLM config
        app_state["llm_config"] = get_llm_config()
        logger.info("LLM config initialized")
        
        # Initialize crew manager
        app_state["crew_manager"] = PersonalProductivityCrew(verbose=False)
        logger.info("Crew manager initialized")
        
        logger.info("System initialization complete")
        return True
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        return False

# Create FastAPI app
app = FastAPI(
    title=API_METADATA["title"],
    description=API_METADATA["description"], 
    version=API_METADATA["version"],
    contact=API_METADATA["contact"],
    license_info=API_METADATA["license"],
    openapi_tags=API_METADATA["tags"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for authentication (optional)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication dependency."""
    # For now, no authentication required
    # In production, validate the token here
    return {"user": "anonymous"}

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    success = initialize_system()
    if not success:
        logger.error("Failed to initialize system - some features may not work")

# Health Check Endpoints

@app.get("/", response_model=HealthCheck, tags=["system"])
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        services={
            "tool_loader": "available" if app_state["tool_loader"] else "unavailable",
            "llm_config": "available" if app_state["llm_config"] else "unavailable", 
            "crew_manager": "available" if app_state["crew_manager"] else "unavailable"
        }
    )

@app.get("/status", response_model=SystemStatus, tags=["system"])
async def get_system_status():
    """Get comprehensive system status."""
    tool_loader = app_state.get("tool_loader")
    llm_config = app_state.get("llm_config")
    
    tools_count = 0
    memory_status = False
    ollama_status = False
    
    if tool_loader:
        info = tool_loader.get_tool_info()
        tools_count = info.get("total_tools", 0)
    
    if llm_config:
        ollama_status = llm_config.test_ollama_connection()
    
    uptime = str(datetime.now() - app_state["start_time"])
    
    return SystemStatus(
        status="operational",
        agents_available=5,
        tools_available=tools_count,
        memory_status=memory_status,
        ollama_status=ollama_status,
        active_tasks=len(app_state["active_tasks"]),
        uptime=uptime
    )

# Agent Endpoints

@app.get("/agents", response_model=List[AgentInfo], tags=["agents"])
async def list_agents():
    """List all available agents."""
    agents = [
        AgentInfo(
            role=AgentRole.MEMORY_LIBRARIAN,
            name="Memory Librarian",
            description="Organizes and retrieves personal knowledge, entities, and conversation history",
            capabilities=[
                "Entity relationship management",
                "Conversation history search", 
                "Knowledge graph navigation",
                "Personal data organization"
            ],
            tools_count=3,
            model="llama3"
        ),
        AgentInfo(
            role=AgentRole.RESEARCH_SPECIALIST,
            name="Research Specialist", 
            description="Conducts research, gathers information, and verifies facts",
            capabilities=[
                "Web search and analysis",
                "Fact verification",
                "Document processing",
                "Information synthesis"
            ],
            tools_count=5,
            model="mixtral"
        ),
        AgentInfo(
            role=AgentRole.PERSONAL_ASSISTANT,
            name="Personal Assistant",
            description="Manages calendar, email, contacts, and personal productivity",
            capabilities=[
                "Calendar management",
                "Email processing", 
                "Contact organization",
                "Task coordination"
            ],
            tools_count=4,
            model="gemma"
        ),
        AgentInfo(
            role=AgentRole.HEALTH_ANALYST,
            name="Health Analyst",
            description="Analyzes health data and provides wellness insights",
            capabilities=[
                "Health data analysis",
                "Fitness tracking",
                "Sleep optimization",
                "Wellness recommendations"
            ],
            tools_count=3,
            model="phi"
        ),
        AgentInfo(
            role=AgentRole.FINANCE_TRACKER,
            name="Finance Tracker",
            description="Tracks expenses, analyzes spending, and provides financial insights",
            capabilities=[
                "Expense categorization",
                "Budget analysis",
                "Financial reporting",
                "Investment tracking"
            ],
            tools_count=2,
            model="mistral"
        )
    ]
    return agents

@app.post("/agents/{agent_role}/chat", response_model=AgentChatResponse, tags=["agents"])
async def chat_with_agent(
    agent_role: AgentRole,
    request: AgentChatRequest,
    user = Depends(get_current_user)
):
    """Chat with a specific agent."""
    try:
        # For now, return a mock response
        # In full implementation, this would create and execute the agent
        
        return AgentChatResponse(
            agent_role=agent_role,
            message=f"Hello! I'm the {agent_role.value.replace('_', ' ').title()}. You said: '{request.message}'. I'm ready to help with my specialized capabilities.",
            tools_used=["conversation_analysis"],
            memory_accessed=request.memory_enabled
        )
        
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Task Endpoints

@app.post("/tasks", response_model=TaskResponse, tags=["tasks"])
async def create_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """Create and execute a task."""
    task_id = str(uuid.uuid4())
    
    try:
        # Store task in active tasks
        app_state["active_tasks"][task_id] = {
            "request": request,
            "status": TaskStatus.PENDING,
            "created_at": datetime.now()
        }
        
        # Add background task for execution
        background_tasks.add_task(execute_task_background, task_id, request)
        
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Task creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
async def get_task_status(task_id: str):
    """Get task execution status and results."""
    task = app_state["active_tasks"].get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        result=task.get("result"),
        error=task.get("error"),
        execution_time=task.get("execution_time"),
        timestamp=task.get("completed_at", task["created_at"])
    )

# Crew Endpoints

@app.post("/crews/execute", response_model=TaskResponse, tags=["crews"])
async def execute_crew_task(
    request: CrewTaskRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """Execute a multi-agent crew task."""
    task_id = str(uuid.uuid4())
    
    try:
        # Store crew task
        app_state["active_tasks"][task_id] = {
            "request": request,
            "status": TaskStatus.PENDING,
            "created_at": datetime.now(),
            "type": "crew"
        }
        
        # Add background task for crew execution
        background_tasks.add_task(execute_crew_task_background, task_id, request)
        
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Crew task creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Tool Endpoints

@app.get("/tools", response_model=List[ToolInfo], tags=["tools"])
async def list_tools():
    """List all available tools."""
    tool_loader = app_state.get("tool_loader")
    
    if not tool_loader:
        raise HTTPException(status_code=503, detail="Tool loader not available")
    
    try:
        info = tool_loader.get_tool_info()
        tools = []
        
        # Get sample tools for each category
        for category, details in info.get("tools_by_category", {}).items():
            for tool_name in details.get("tools", [])[:3]:  # Limit to 3 per category
                tools.append(ToolInfo(
                    name=tool_name,
                    description=f"Tool for {category} operations",
                    category=category,
                    parameters={"input": "string"}
                ))
        
        return tools
        
    except Exception as e:
        logger.error(f"Tool listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/execute", tags=["tools"])
async def execute_tool(
    request: ToolRequest,
    user = Depends(get_current_user)
):
    """Execute a specific tool."""
    try:
        # Mock tool execution for now
        return {
            "tool": request.tool_name,
            "result": f"Executed {request.tool_name} with parameters: {request.parameters}",
            "execution_time": 0.5
        }
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions

async def execute_task_background(task_id: str, request: TaskRequest):
    """Execute a task in the background."""
    start_time = time.time()
    
    try:
        # Update status
        app_state["active_tasks"][task_id]["status"] = TaskStatus.IN_PROGRESS
        
        # Mock task execution
        await asyncio.sleep(2)  # Simulate processing time
        
        # Generate mock result based on task type
        if request.task_type == TaskType.LIFE_ANALYSIS:
            result = f"Life analysis completed for: {request.description}"
        elif request.task_type == TaskType.RESEARCH_PROJECT:
            result = f"Research completed on: {request.description}"
        elif request.task_type == TaskType.HEALTH_OPTIMIZATION:
            result = f"Health optimization plan created for: {request.description}"
        elif request.task_type == TaskType.FINANCIAL_PLANNING:
            result = f"Financial plan developed for: {request.description}"
        else:
            result = f"Custom task completed: {request.description}"
        
        # Update task with results
        execution_time = time.time() - start_time
        app_state["active_tasks"][task_id].update({
            "status": TaskStatus.COMPLETED,
            "result": result,
            "execution_time": execution_time,
            "completed_at": datetime.now()
        })
        
    except Exception as e:
        # Handle errors
        app_state["active_tasks"][task_id].update({
            "status": TaskStatus.FAILED,
            "error": str(e),
            "completed_at": datetime.now()
        })

async def execute_crew_task_background(task_id: str, request: CrewTaskRequest):
    """Execute a crew task in the background."""
    start_time = time.time()
    
    try:
        app_state["active_tasks"][task_id]["status"] = TaskStatus.IN_PROGRESS
        
        # Mock crew execution
        await asyncio.sleep(5)  # Crew tasks take longer
        
        result = f"Crew task completed with {len(request.agents or [])} agents: {request.description}"
        
        execution_time = time.time() - start_time
        app_state["active_tasks"][task_id].update({
            "status": TaskStatus.COMPLETED,
            "result": result,
            "execution_time": execution_time,
            "completed_at": datetime.now()
        })
        
    except Exception as e:
        app_state["active_tasks"][task_id].update({
            "status": TaskStatus.FAILED,
            "error": str(e),
            "completed_at": datetime.now()
        })

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )