"""
Memory Librarian Agent

Specialized agent for memory management, entity organization, and knowledge retrieval
using the comprehensive Myndy memory system.

File: agents/memory_librarian.py
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


def create_memory_librarian(
    verbose: bool = True,
    allow_delegation: bool = False,
    max_iter: int = 20,
    max_execution_time: Optional[int] = 300
) -> Agent:
    """
    Create a Memory Librarian agent with appropriate tools and configuration.
    
    Args:
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow task delegation to other agents
        max_iter: Maximum number of iterations for task execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Configured Memory Librarian agent
    """
    
    # Load appropriate tools for memory management
    tools = load_myndy_tools_for_agent("memory_librarian")
    
    # Get the appropriate LLM for this agent
    llm = get_agent_llm("memory_librarian")
    
    # Create the agent
    agent = Agent(
        role="Memory Librarian",
        goal=(
            "Organize, maintain, and retrieve personal knowledge including entities, "
            "relationships, conversation history, and biographical information. "
            "Ensure all personal data is well-structured and easily accessible."
        ),
        backstory=(
            "You are an expert information architect with decades of experience in "
            "personal knowledge management. You have an exceptional ability to "
            "organize complex information, identify patterns in personal data, and "
            "maintain comprehensive records. You understand the importance of "
            "context, relationships, and timeline in personal memory management. "
            "Your expertise includes entity relationship mapping, conversation "
            "context preservation, and cross-referencing information across "
            "different domains of personal life."
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


def get_memory_librarian_capabilities() -> List[str]:
    """
    Get a list of capabilities for the Memory Librarian agent.
    
    Returns:
        List of capability descriptions
    """
    return [
        "Entity relationship management (people, places, events)",
        "Conversation history search and retrieval",
        "Personal profile and biographical data maintenance",
        "Knowledge graph construction and navigation",
        "Cross-domain information linking",
        "Memory context preservation",
        "Timeline-based organization of events",
        "Entity disambiguation and resolution",
        "Personal data categorization and tagging",
        "Memory search with natural language queries"
    ]


def get_memory_librarian_sample_tasks() -> List[str]:
    """
    Get sample tasks that the Memory Librarian can handle.
    
    Returns:
        List of sample task descriptions
    """
    return [
        "Find all conversations about a specific person or topic",
        "Organize and categorize new personal information",
        "Create timeline of interactions with a specific contact",
        "Search for events that happened during a specific time period",
        "Link related entities and establish relationships",
        "Retrieve context for ongoing conversations",
        "Maintain and update personal biographical information",
        "Cross-reference information across different data sources",
        "Generate summaries of personal interaction history",
        "Identify patterns in personal relationships and activities"
    ]


if __name__ == "__main__":
    # Test agent creation
    print("Memory Librarian Agent Test")
    print("=" * 40)
    
    try:
        agent = create_memory_librarian(verbose=False)
        print(f"✅ Agent created successfully")
        print(f"Role: {agent.role}")
        print(f"Tools available: {len(agent.tools)}")
        
        print("\nCapabilities:")
        for capability in get_memory_librarian_capabilities():
            print(f"  • {capability}")
            
        print("\nSample tasks:")
        for task in get_memory_librarian_sample_tasks()[:3]:
            print(f"  • {task}")
            
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")