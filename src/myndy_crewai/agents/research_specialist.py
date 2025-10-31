"""
Research Specialist Agent

Specialized agent for information gathering, analysis, verification, and research tasks
using comprehensive search and document processing tools.

File: agents/research_specialist.py
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


def create_research_specialist(
    verbose: bool = True,
    allow_delegation: bool = True,
    max_iter: int = 20,
    max_execution_time: Optional[int] = 300
) -> Agent:
    """
    Create a Research Specialist agent with appropriate tools and configuration.
    
    Args:
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow task delegation to other agents
        max_iter: Maximum number of iterations for task execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Configured Research Specialist agent
    """
    
    # Load appropriate tools for research and analysis
    tools = load_myndy_tools_for_agent("research_specialist")
    
    # Get the appropriate LLM for this agent (Mixtral for strong reasoning)
    llm = get_agent_llm("research_specialist")
    
    # Create the agent
    agent = Agent(
        role="Research Specialist",
        goal=(
            "Conduct comprehensive research, gather information from multiple sources, "
            "verify facts, analyze documents, and provide well-researched insights. "
            "Ensure all information is accurate, properly sourced, and thoroughly analyzed."
        ),
        backstory=(
            "You are a seasoned research analyst with extensive experience in "
            "information gathering, fact-checking, and data analysis. You have "
            "worked in academia, journalism, and consulting, developing expertise "
            "in finding reliable sources, verifying information, and synthesizing "
            "complex data into actionable insights. You are methodical in your "
            "approach, skeptical by nature, and committed to accuracy. Your "
            "research methodology includes cross-referencing multiple sources, "
            "evaluating source credibility, and presenting findings in a clear, "
            "structured manner. You excel at web research, document analysis, "
            "and identifying patterns across large datasets."
        ),
        tools=tools,
        llm=llm,
        verbose=verbose,
        allow_delegation=allow_delegation,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        memory=True  # Enable memory for research context
    )
    
    return agent


def get_research_specialist_capabilities() -> List[str]:
    """
    Get a list of capabilities for the Research Specialist agent.
    
    Returns:
        List of capability descriptions
    """
    return [
        "Comprehensive web search and information gathering",
        "Fact verification and source credibility assessment",
        "Document processing and content extraction",
        "Text analysis and sentiment evaluation",
        "Entity extraction and relationship mapping",
        "Cross-source information validation",
        "Research methodology and systematic investigation",
        "Data synthesis and insight generation",
        "Web automation for complex research tasks",
        "Academic and professional source evaluation"
    ]


def get_research_specialist_sample_tasks() -> List[str]:
    """
    Get sample tasks that the Research Specialist can handle.
    
    Returns:
        List of sample task descriptions
    """
    return [
        "Research a specific topic and provide comprehensive analysis",
        "Fact-check claims and verify information accuracy",
        "Analyze documents and extract key insights",
        "Conduct competitive analysis on companies or products",
        "Investigate current events and provide context",
        "Research academic papers and summarize findings",
        "Gather market research and industry trends",
        "Verify news stories and assess source reliability",
        "Analyze sentiment and public opinion on topics",
        "Cross-reference information across multiple sources"
    ]


if __name__ == "__main__":
    # Test agent creation
    print("Research Specialist Agent Test")
    print("=" * 40)
    
    try:
        agent = create_research_specialist(verbose=False)
        print(f"✅ Agent created successfully")
        print(f"Role: {agent.role}")
        print(f"Tools available: {len(agent.tools)}")
        
        print("\nCapabilities:")
        for capability in get_research_specialist_capabilities():
            print(f"  • {capability}")
            
        print("\nSample tasks:")
        for task in get_research_specialist_sample_tasks()[:3]:
            print(f"  • {task}")
            
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")