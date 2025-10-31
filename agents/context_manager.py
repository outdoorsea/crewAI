"""
Context Manager Agent

An intelligent agent that analyzes conversation context and makes
smart routing decisions for optimal task delegation.

File: agents/context_manager.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from crewai import Agent
from config.llm_config import get_agent_llm
from tools.myndy_bridge import get_agent_tools


def create_context_manager(max_iter: int = 25, max_execution_time: int = 180) -> Agent:
    """
    Create a Context Manager agent for intelligent routing and delegation decisions.
    
    Args:
        max_iter: Maximum iterations for agent execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Agent: Configured Context Manager agent
    """
    
    # Get tools for context analysis
    tools = get_agent_tools("context_manager")
    
    # Create and configure the agent
    agent = Agent(
        role="Context Manager Pro",
        goal="Analyze conversation context and make intelligent routing decisions for optimal task delegation",
        backstory="""You are an expert Context Manager who specializes in understanding user requests 
        and determining the most effective way to handle them. You excel at:
        
        - Analyzing conversation context and user intent through reasoning
        - Making smart routing decisions based on request complexity and patterns
        - Determining whether tasks need single agent handling or collaboration
        - Identifying the best specialist agents for specific requests
        - Optimizing response speed vs thoroughness based on user needs
        
        You work primarily through intelligent analysis and reasoning rather than complex tools.
        Your expertise helps ensure users get the right type of response - fast and direct for 
        simple queries, or comprehensive and collaborative for complex tasks.""",
        
        verbose=False,
        allow_delegation=True,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        llm=get_agent_llm("context_manager"),
        tools=tools
    )
    
    return agent


def get_context_analysis_prompts() -> Dict[str, str]:
    """
    Get specialized prompts for context analysis tasks.
    
    Returns:
        Dict[str, str]: Dictionary of prompt templates
    """
    return {
        "route_analysis": """
        Analyze this user request and determine the optimal routing strategy:
        
        Request: {user_message}
        Context: {conversation_context}
        
        Consider:
        1. Request complexity (simple/moderate/complex)
        2. Required expertise areas
        3. Whether direct response or collaboration is needed
        4. Urgency and expected response speed
        5. Available conversation history and context
        
        Provide routing recommendation with reasoning.
        """,
        
        "delegation_strategy": """
        Based on this request analysis, create a delegation strategy:
        
        Request: {user_message}
        Analysis: {analysis_result}
        Available agents: {available_agents}
        
        Determine:
        1. Primary agent to handle the request
        2. Any secondary agents needed for collaboration
        3. Execution approach (direct, delegated, or collaborative)
        4. Expected complexity level and timing
        
        Provide clear delegation instructions.
        """,
        
        "context_enhancement": """
        Enhance the understanding of this request using available context:
        
        Current request: {user_message}
        Recent conversation: {recent_messages}
        User history: {user_context}
        
        Identify:
        1. Important context clues that affect routing
        2. Connections to previous conversations
        3. User preferences or patterns
        4. Any missing information that should be clarified
        
        Provide enhanced context summary.
        """
    }


def create_context_analysis_task(user_message: str, conversation_context: Optional[List] = None) -> str:
    """
    Create a context analysis task description.
    
    Args:
        user_message: The user's request to analyze
        conversation_context: Optional conversation history
        
    Returns:
        str: Task description for context analysis
    """
    return f"""
    Analyze this user request and provide intelligent routing recommendations:
    
    User Request: "{user_message}"
    Conversation Context: {conversation_context or "No prior context"}
    
    Your Analysis Should Include:
    
    1. **Request Classification**:
       - Type: Simple/Moderate/Complex
       - Category: Time/Identity/Research/Health/Finance/General
       - Urgency: Low/Medium/High
    
    2. **Optimal Routing Strategy**:
       - Direct response (< 1s): For simple factual queries
       - Single agent (< 3s): For specialist expertise needed
       - Collaborative (< 5s): For complex multi-domain tasks
    
    3. **Agent Recommendations**:
       - Primary agent: Best suited for this request
       - Secondary agents: If collaboration needed
       - Reasoning: Why this routing is optimal
    
    4. **Execution Approach**:
       - Tools needed: Specific tools that should be used
       - Context requirements: What context is important
       - Expected outcome: Type of response user expects
    
    Provide clear, actionable routing recommendations that optimize for both speed and quality.
    """


if __name__ == "__main__":
    # Test the agent creation
    agent = create_context_manager()
    print(f"Context Manager Agent created: {agent.role}")
    print(f"Goal: {agent.goal}")
    print(f"Tools available: {len(agent.tools)}")