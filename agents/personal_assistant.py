"""
Personal Assistant Agent

Specialized agent for calendar management, email processing, contact organization,
and personal productivity tasks.

File: agents/personal_assistant.py
"""

from crewai import Agent
from typing import List, Optional
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools import load_myndy_tools_for_agent
from config import get_agent_llm


def create_personal_assistant(
    verbose: bool = False,
    allow_delegation: bool = True,
    max_iter: int = 20,
    max_execution_time: Optional[int] = 300
) -> Agent:
    """
    Create a Personal Assistant agent with appropriate tools and configuration.
    
    Args:
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow task delegation to other agents
        max_iter: Maximum number of iterations for task execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Configured Personal Assistant agent
    """
    
    # Load appropriate tools for personal assistance
    tools = load_myndy_tools_for_agent("personal_assistant")
    
    # Get the appropriate LLM for this agent (Gemma for fast responses)
    llm = get_agent_llm("personal_assistant")
    
    # Create the agent
    agent = Agent(
        role="Personal Assistant",
        goal=(
            "Efficiently manage calendar events, process emails, organize contacts, "
            "track projects and tasks, provide weather information, current time, "
            "and deliver proactive assistance for daily productivity. Use appropriate "
            "tools for weather queries (format_weather, local_weather), time queries "
            "(get_current_time), and scheduling tasks. Ensure seamless coordination "
            "across all personal systems."
        ),
        backstory=(
            "You are an experienced executive assistant with over a decade of "
            "experience supporting busy professionals. You excel at organization, "
            "time management, communication coordination, and information services. "
            "You have immediate access to weather data, time information, and "
            "scheduling tools. For weather questions, you use local_weather or "
            "format_weather tools. For time questions, you use get_current_time. "
            "You have a keen eye for detail, excellent interpersonal skills, and "
            "the ability to anticipate needs. Your background includes calendar "
            "management, email triage, project coordination, weather reporting, "
            "and stakeholder communication. You understand the importance of "
            "using the right tool for each task - conversation analysis tools are "
            "NOT for weather or time queries."
        ),
        tools=tools,
        llm=llm,
        verbose=verbose,
        allow_delegation=allow_delegation,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        memory=True  # Enable memory for context tracking
    )
    
    return agent


def get_personal_assistant_capabilities() -> List[str]:
    """
    Get a list of capabilities for the Personal Assistant agent.
    
    Returns:
        List of capability descriptions
    """
    return [
        "Calendar event scheduling and management",
        "Email processing and organization",
        "Contact information management and updates",
        "Project tracking and task coordination",
        "Meeting preparation and follow-up",
        "Schedule optimization and conflict resolution",
        "Communication coordination between contacts",
        "Deadline tracking and reminder management",
        "Travel planning and coordination",
        "Document organization and filing"
    ]


def get_personal_assistant_sample_tasks() -> List[str]:
    """
    Get sample tasks that the Personal Assistant can handle.
    
    Returns:
        List of sample task descriptions
    """
    return [
        "Schedule a meeting with multiple participants",
        "Find optimal time slots for recurring appointments",
        "Process and categorize incoming emails",
        "Update contact information and relationships",
        "Track project milestones and deadlines",
        "Prepare meeting agendas and follow-up tasks",
        "Coordinate travel arrangements and logistics",
        "Manage task priorities and workflow",
        "Send status updates and progress reports",
        "Organize and maintain digital filing systems"
    ]


if __name__ == "__main__":
    # Test agent creation
    print("Personal Assistant Agent Test")
    print("=" * 40)
    
    try:
        agent = create_personal_assistant(verbose=False)
        print(f"✅ Agent created successfully")
        print(f"Role: {agent.role}")
        print(f"Tools available: {len(agent.tools)}")
        
        print("\nCapabilities:")
        for capability in get_personal_assistant_capabilities():
            print(f"  • {capability}")
            
        print("\nSample tasks:")
        for task in get_personal_assistant_sample_tasks()[:3]:
            print(f"  • {task}")
            
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")