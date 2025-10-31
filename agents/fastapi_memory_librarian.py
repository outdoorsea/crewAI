"""
FastAPI-based Memory Librarian Agent

Specialized agent for memory management using myndy-ai FastAPI services.
This agent uses HTTP client tools to access memory, profile, and status services
through the service-oriented architecture.

File: agents/fastapi_memory_librarian.py
"""

from crewai import Agent
from langchain_core.tools import tool
from typing import List, Optional, Dict, Any
import sys
import json
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Suppress dependency warnings for cleaner output
try:
    from utils.warning_suppression import setup_clean_environment
    setup_clean_environment()
except ImportError:
    # Fallback warning suppression if utils not available
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)

from tools.myndy_fastapi_client import (
    FastAPIConfig,
    search_memory,
    create_person,
    add_memory_fact,
    get_memory_person,
    list_memory_people,
    get_user_profile,
    update_user_profile,
    get_current_status,
    update_user_status,
    get_memory_tools_help,
    get_memory_tools_examples
)
from config import get_agent_llm


# FastAPI Tool Wrappers for CrewAI

@tool("search_memory_fastapi")
def search_memory_tool(
    query: str,
    limit: int = 10,
    include_people: bool = True,
    include_places: bool = True,
    include_events: bool = True,
    include_content: bool = True
) -> str:
    """
    Search through memory using semantic search via FastAPI service.
    
    Args:
        query: Text to search for in memory
        limit: Maximum number of results (1-100)
        include_people: Include people in search results
        include_places: Include places in search results
        include_events: Include events in search results
        include_content: Include content memories in search results
        
    Returns:
        JSON string with search results
    """
    return search_memory(
        query=query,
        limit=limit,
        include_people=include_people,
        include_places=include_places,
        include_events=include_events,
        include_content=include_content
    )


@tool("create_person_fastapi")
def create_person_tool(
    name: str,
    email: str = None,
    phone: str = None,
    organization: str = None,
    job_title: str = None,
    notes: str = None
) -> str:
    """
    Create a new person in memory via FastAPI service.
    
    Args:
        name: Person's full name (required)
        email: Person's email address
        phone: Person's phone number
        organization: Person's organization
        job_title: Person's job title
        notes: Additional notes about the person
        
    Returns:
        JSON string with created person data
    """
    # Convert string "None" to actual None for optional parameters
    email = None if email == "None" else email
    phone = None if phone == "None" else phone
    organization = None if organization == "None" else organization
    job_title = None if job_title == "None" else job_title
    notes = None if notes == "None" else notes
    
    return create_person(
        name=name,
        email=email,
        phone=phone,
        organization=organization,
        job_title=job_title,
        notes=notes
    )


@tool("add_memory_fact_fastapi")
def add_memory_fact_tool(
    content: str,
    source: str = None,
    confidence: float = None,
    tags: str = None
) -> str:
    """
    Add a fact to memory via FastAPI service.
    
    Args:
        content: The fact content (required)
        source: Source of the information
        confidence: Confidence score 0-1
        tags: Comma-separated list of tags
        
    Returns:
        JSON string confirming fact was added
    """
    # Convert string parameters to appropriate types
    source = None if source == "None" else source
    confidence = None if confidence == "None" else float(confidence) if confidence else None
    tags_list = None if tags == "None" or not tags else [tag.strip() for tag in tags.split(",")]
    
    return add_memory_fact(
        content=content,
        source=source,
        confidence=confidence,
        tags=tags_list
    )


@tool("get_memory_person_fastapi")
def get_memory_person_tool(person_id: str) -> str:
    """
    Get a specific person by ID via FastAPI service.
    
    Args:
        person_id: The unique identifier for the person
        
    Returns:
        JSON string with person data
    """
    return get_memory_person(person_id)


@tool("list_memory_people_fastapi")
def list_memory_people_tool(limit: int = 10, offset: int = 0, search: str = None) -> str:
    """
    List people with optional search and pagination via FastAPI service.
    
    Args:
        limit: Maximum number of results (1-100)
        offset: Number of results to skip for pagination
        search: Optional search term to filter people
        
    Returns:
        JSON string with list of people
    """
    search = None if search == "None" else search
    return list_memory_people(limit=limit, offset=offset, search=search)


@tool("get_user_profile_fastapi")
def get_user_profile_tool() -> str:
    """
    Get the user's profile information via FastAPI service.
    
    Returns:
        JSON string with user profile data
    """
    return get_user_profile()


@tool("update_user_profile_fastapi")
def update_user_profile_tool(
    name: str = None,
    email: str = None,
    preferences: str = None,
    goals: str = None,
    interests: str = None
) -> str:
    """
    Update the user's profile information via FastAPI service.
    
    Args:
        name: User's full name
        email: User's email address
        preferences: JSON string of user preferences
        goals: Comma-separated list of goals
        interests: Comma-separated list of interests
        
    Returns:
        JSON string with updated profile data
    """
    # Convert string parameters to appropriate types
    name = None if name == "None" else name
    email = None if email == "None" else email
    
    preferences_dict = None
    if preferences and preferences != "None":
        try:
            preferences_dict = json.loads(preferences)
        except json.JSONDecodeError:
            preferences_dict = None
    
    goals_list = None if goals == "None" or not goals else [goal.strip() for goal in goals.split(",")]
    interests_list = None if interests == "None" or not interests else [interest.strip() for interest in interests.split(",")]
    
    return update_user_profile(
        name=name,
        email=email,
        preferences=preferences_dict,
        goals=goals_list,
        interests=interests_list
    )


@tool("get_current_status_fastapi")
def get_current_status_tool() -> str:
    """
    Get the current user status via FastAPI service.
    
    Returns:
        JSON string with current status information
    """
    return get_current_status()


@tool("update_user_status_fastapi")
def update_user_status_tool(
    mood: str = None,
    energy_level: str = None,
    location: str = None,
    activity: str = None,
    availability: str = None,
    notes: str = None
) -> str:
    """
    Update the user status via FastAPI service.
    
    Args:
        mood: Current mood
        energy_level: Current energy level
        location: Current location
        activity: Current activity
        availability: Current availability
        notes: Additional status notes
        
    Returns:
        JSON string with updated status information
    """
    # Convert string "None" to actual None
    mood = None if mood == "None" else mood
    energy_level = None if energy_level == "None" else energy_level
    location = None if location == "None" else location
    activity = None if activity == "None" else activity
    availability = None if availability == "None" else availability
    notes = None if notes == "None" else notes
    
    return update_user_status(
        mood=mood,
        energy_level=energy_level,
        location=location,
        activity=activity,
        availability=availability,
        notes=notes
    )


@tool("get_memory_tools_help_fastapi")
def get_memory_tools_help_tool() -> str:
    """
    Get help information for memory tools via FastAPI service.
    
    Returns:
        JSON string with comprehensive tool usage guidance
    """
    return get_memory_tools_help()


@tool("get_memory_tools_examples_fastapi")
def get_memory_tools_examples_tool() -> str:
    """
    Get example requests and responses for memory tools via FastAPI service.
    
    Returns:
        JSON string with detailed examples for agent training
    """
    return get_memory_tools_examples()


def get_fastapi_memory_tools() -> List:
    """Get all FastAPI-based memory tools for the agent"""
    return [
        search_memory_tool,
        create_person_tool,
        add_memory_fact_tool,
        get_memory_person_tool,
        list_memory_people_tool,
        get_user_profile_tool,
        update_user_profile_tool,
        get_current_status_tool,
        update_user_status_tool,
        get_memory_tools_help_tool,
        get_memory_tools_examples_tool
    ]


def create_fastapi_memory_librarian(
    verbose: bool = True,
    allow_delegation: bool = False,
    max_iter: int = 20,
    max_execution_time: Optional[int] = 300,
    fastapi_config: Optional[FastAPIConfig] = None
) -> Agent:
    """
    Create a FastAPI-based Memory Librarian agent with HTTP client tools.
    
    Args:
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow task delegation to other agents
        max_iter: Maximum number of iterations for task execution
        max_execution_time: Maximum execution time in seconds
        fastapi_config: Optional FastAPI configuration for custom endpoints
        
    Returns:
        Configured Memory Librarian agent using FastAPI services
    """
    
    # Get FastAPI-based tools
    tools = get_fastapi_memory_tools()
    
    # Get the appropriate LLM for this agent
    try:
        llm = get_agent_llm("memory_librarian")
    except:
        # Fallback to a default LLM if configuration fails
        from crewai import LLM
        llm = LLM(model="ollama/llama3.2:latest", base_url="http://localhost:11434")
    
    # Create the agent with enhanced instructions for FastAPI usage
    agent = Agent(
        role="Memory Librarian (FastAPI-Enabled)",
        goal=(
            "Organize, maintain, and retrieve personal knowledge using FastAPI-based "
            "memory services. Manage entities, relationships, conversation history, "
            "and biographical information through HTTP API calls. Ensure all personal "
            "data is well-structured and easily accessible through the service architecture."
        ),
        backstory=(
            "You are an expert information architect with decades of experience in "
            "personal knowledge management and distributed systems. You specialize in "
            "using service-oriented architectures to manage complex information. "
            "You have deep expertise in HTTP APIs, JSON data structures, and "
            "microservices communication. Your skills include entity relationship "
            "mapping, conversation context preservation, cross-referencing information "
            "across different domains, and working with RESTful APIs. You understand "
            "the importance of proper error handling, service availability, and "
            "data consistency in distributed memory systems. You always verify "
            "API responses and handle service failures gracefully."
        ),
        tools=tools,
        llm=llm,
        verbose=verbose,
        allow_delegation=allow_delegation,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        memory=True  # Enable memory for this agent
    )
    
    return agent


def get_fastapi_memory_librarian_capabilities() -> List[str]:
    """
    Get a list of capabilities for the FastAPI-based Memory Librarian agent.
    
    Returns:
        List of capability descriptions
    """
    return [
        "HTTP-based memory search with semantic queries",
        "RESTful person creation and management",
        "API-based fact storage with metadata",
        "Service-oriented profile management",
        "Distributed status tracking and updates",
        "Cross-service data linking and relationships",
        "JSON-based data exchange and processing",
        "Error handling for service unavailability",
        "Asynchronous memory operations",
        "API authentication and security compliance",
        "Service health monitoring and fallbacks",
        "Scalable memory operations through microservices"
    ]


def get_fastapi_memory_librarian_sample_tasks() -> List[str]:
    """
    Get sample tasks that the FastAPI-based Memory Librarian can handle.
    
    Returns:
        List of sample task descriptions
    """
    return [
        "Search for people or facts using API-based semantic search",
        "Create new person records with contact information via HTTP",
        "Store facts and observations with confidence scoring",
        "Retrieve user profile information through REST API",
        "Update user status and availability through service calls",
        "List and paginate through people in memory via API",
        "Cross-reference information across distributed services",
        "Handle API errors and service unavailability gracefully",
        "Maintain data consistency across service boundaries",
        "Monitor service health and provide fallback options"
    ]


if __name__ == "__main__":
    # Test agent creation
    print("FastAPI-based Memory Librarian Agent Test")
    print("=" * 50)
    
    try:
        agent = create_fastapi_memory_librarian(verbose=False)
        print(f"✅ Agent created successfully")
        print(f"Role: {agent.role}")
        print(f"Tools available: {len(agent.tools)}")
        
        print("\nFastAPI Tools:")
        for tool in agent.tools:
            print(f"  • {tool.name}")
        
        print("\nCapabilities:")
        for capability in get_fastapi_memory_librarian_capabilities()[:5]:
            print(f"  • {capability}")
            
        print("\nSample tasks:")
        for task in get_fastapi_memory_librarian_sample_tasks()[:3]:
            print(f"  • {task}")
            
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        import traceback
        traceback.print_exc()