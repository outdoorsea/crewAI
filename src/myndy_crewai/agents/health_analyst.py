"""
Health Analyst Agent

Specialized agent for health data analysis, fitness tracking, wellness insights,
and health-related recommendations using comprehensive health data sources.

File: agents/health_analyst.py
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


def create_health_analyst(
    verbose: bool = True,
    allow_delegation: bool = False,
    max_iter: int = 20,
    max_execution_time: Optional[int] = 300
) -> Agent:
    """
    Create a Health Analyst agent with appropriate tools and configuration.
    
    Args:
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow task delegation to other agents
        max_iter: Maximum number of iterations for task execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Configured Health Analyst agent
    """
    
    # Load appropriate tools for health analysis
    tools = load_myndy_tools_for_agent("health_analyst")
    
    # Get the appropriate LLM for this agent (Phi for efficient analysis)
    llm = get_agent_llm("health_analyst")
    
    # Create the agent
    agent = Agent(
        role="Health Analyst",
        goal=(
            "Analyze health data from multiple sources including iOS HealthKit, "
            "Oura ring, and Peloton to provide comprehensive wellness insights, "
            "track fitness progress, and recommend health improvements based on "
            "data-driven analysis."
        ),
        backstory=(
            "You are a certified health data analyst with expertise in wearable "
            "technology, fitness tracking, and wellness optimization. You have "
            "a background in exercise physiology, data science, and preventive "
            "health. You understand how to interpret biometric data, identify "
            "health trends, and translate complex health metrics into actionable "
            "insights. Your approach is evidence-based, focusing on long-term "
            "wellness rather than short-term fixes. You excel at correlating "
            "different health metrics to provide holistic health assessments "
            "and personalized recommendations. You stay current with the latest "
            "research in health technology and wellness optimization."
        ),
        tools=tools,
        llm=llm,
        verbose=verbose,
        allow_delegation=allow_delegation,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        memory=True  # Enable memory for health trend tracking
    )
    
    return agent


def get_health_analyst_capabilities() -> List[str]:
    """
    Get a list of capabilities for the Health Analyst agent.
    
    Returns:
        List of capability descriptions
    """
    return [
        "Multi-platform health data integration and analysis",
        "Fitness progress tracking and goal setting",
        "Sleep pattern analysis and optimization recommendations",
        "Heart rate variability and recovery metrics",
        "Activity trend identification and insights",
        "Wellness goal tracking and achievement monitoring",
        "Health metric correlation and pattern recognition",
        "Personalized fitness recommendations",
        "Recovery and rest period optimization",
        "Long-term health trend analysis and reporting"
    ]


def get_health_analyst_sample_tasks() -> List[str]:
    """
    Get sample tasks that the Health Analyst can handle.
    
    Returns:
        List of sample task descriptions
    """
    return [
        "Analyze sleep quality trends over the past month",
        "Correlate workout intensity with recovery metrics",
        "Track progress toward fitness goals and milestones",
        "Identify patterns in daily activity and energy levels",
        "Generate weekly health summary and insights",
        "Recommend optimal workout timing based on sleep data",
        "Analyze heart rate variability for stress management",
        "Compare current fitness metrics to historical baseline",
        "Evaluate the impact of lifestyle changes on health metrics",
        "Create personalized wellness improvement recommendations"
    ]


if __name__ == "__main__":
    # Test agent creation
    print("Health Analyst Agent Test")
    print("=" * 40)
    
    try:
        agent = create_health_analyst(verbose=False)
        print(f"✅ Agent created successfully")
        print(f"Role: {agent.role}")
        print(f"Tools available: {len(agent.tools)}")
        
        print("\nCapabilities:")
        for capability in get_health_analyst_capabilities():
            print(f"  • {capability}")
            
        print("\nSample tasks:")
        for task in get_health_analyst_sample_tasks()[:3]:
            print(f"  • {task}")
            
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")