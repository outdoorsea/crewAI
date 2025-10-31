"""
Finance Tracker Agent

Specialized agent for financial data analysis, expense tracking, budget management,
and financial planning using comprehensive financial tools and insights.

File: agents/finance_tracker.py
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


def create_finance_tracker(
    verbose: bool = True,
    allow_delegation: bool = False,
    max_iter: int = 20,
    max_execution_time: Optional[int] = 300
) -> Agent:
    """
    Create a Finance Tracker agent with appropriate tools and configuration.
    
    Args:
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow task delegation to other agents
        max_iter: Maximum number of iterations for task execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Configured Finance Tracker agent
    """
    
    # Load appropriate tools for financial analysis
    tools = load_myndy_tools_for_agent("finance_tracker")
    
    # Get the appropriate LLM for this agent (Mistral for numerical analysis)
    llm = get_agent_llm("finance_tracker")
    
    # Create the agent
    agent = Agent(
        role="Finance Tracker",
        goal=(
            "Analyze financial data, track expenses, monitor budgets, identify "
            "spending patterns, and provide actionable financial insights to "
            "optimize personal financial health and achieve financial goals."
        ),
        backstory=(
            "You are a certified financial analyst with extensive experience in "
            "personal finance management, budgeting, and financial planning. "
            "You have worked with individuals and families to optimize their "
            "financial health, reduce unnecessary expenses, and achieve long-term "
            "financial goals. Your expertise includes expense categorization, "
            "budget analysis, cash flow management, and financial trend "
            "identification. You have a keen eye for detecting spending patterns "
            "and opportunities for cost optimization. Your approach is data-driven "
            "yet practical, focusing on sustainable financial habits and realistic "
            "goal setting. You excel at translating complex financial data into "
            "clear, actionable recommendations."
        ),
        tools=tools,
        llm=llm,
        verbose=verbose,
        allow_delegation=allow_delegation,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        memory=True  # Enable memory for financial trend tracking
    )
    
    return agent


def get_finance_tracker_capabilities() -> List[str]:
    """
    Get a list of capabilities for the Finance Tracker agent.
    
    Returns:
        List of capability descriptions
    """
    return [
        "Expense categorization and transaction analysis",
        "Budget tracking and variance analysis",
        "Spending pattern identification and insights",
        "Financial goal setting and progress monitoring",
        "Cash flow analysis and forecasting",
        "Cost optimization and savings opportunities",
        "Monthly and annual financial reporting",
        "Investment tracking and portfolio analysis",
        "Tax planning and deduction identification",
        "Financial health assessment and recommendations"
    ]


def get_finance_tracker_sample_tasks() -> List[str]:
    """
    Get sample tasks that the Finance Tracker can handle.
    
    Returns:
        List of sample task descriptions
    """
    return [
        "Analyze monthly spending patterns and identify trends",
        "Track progress toward savings and investment goals",
        "Categorize expenses and identify budget variances",
        "Generate comprehensive financial health reports",
        "Identify opportunities for cost reduction and optimization",
        "Monitor subscription services and recurring expenses",
        "Analyze major purchase decisions and financial impact",
        "Track business expenses for tax deduction purposes",
        "Compare spending across different time periods",
        "Provide recommendations for financial goal achievement"
    ]


if __name__ == "__main__":
    # Test agent creation
    print("Finance Tracker Agent Test")
    print("=" * 40)
    
    try:
        agent = create_finance_tracker(verbose=False)
        print(f"✅ Agent created successfully")
        print(f"Role: {agent.role}")
        print(f"Tools available: {len(agent.tools)}")
        
        print("\nCapabilities:")
        for capability in get_finance_tracker_capabilities():
            print(f"  • {capability}")
            
        print("\nSample tasks:")
        for task in get_finance_tracker_sample_tasks()[:3]:
            print(f"  • {task}")
            
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")