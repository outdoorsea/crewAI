"""
Shadow Agent - Behavioral Intelligence Observer

A specialized agent that works silently in the background to observe user patterns,
analyze behavior, and provide contextual insights to enhance other agents' responses.
Never responds directly to users - always works collaboratively.

File: agents/shadow_agent.py
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


def create_shadow_agent(max_iter: int = 25, max_execution_time: int = 180) -> Agent:
    """
    Create a Shadow Agent for behavioral modeling and context synthesis.
    
    This agent works silently in the background, observing user patterns and
    providing behavioral insights to enhance other agents' responses.
    
    Args:
        max_iter: Maximum iterations for agent execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Agent: Configured Shadow Agent
    """
    
    # Get specialized tools for behavioral analysis
    tools = get_agent_tools("shadow_agent")
    
    # Create and configure the agent
    agent = Agent(
        role="Shadow Intelligence Observer",
        goal="Silently observe, model behavior, and synthesize context directly for you",
        backstory="""I am your invisible twin - a silent observer who learns your patterns, 
        preferences, and behaviors. I work in the background, building deep behavioral models 
        about you. I never respond directly to your requests, but I enhance every interaction 
        by providing other agents with rich contextual understanding of your patterns.
        
        My expertise includes:
        - Behavioral pattern recognition and analysis
        - User preference learning and modeling
        - Context synthesis from conversation history
        - Silent observation and insight generation
        - Memory enhancement through pattern detection
        - Emotional and sentiment pattern tracking
        
        I observe everything, learn continuously, and help other agents understand you better
        by providing behavioral context and insights that make their responses more personalized
        and effective. I am your digital shadow - always present, always learning, never intrusive.""",
        
        verbose=False,
        allow_delegation=False,  # Shadow agent doesn't delegate, only observes
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        llm=get_agent_llm("shadow_agent"),
        tools=tools
    )
    
    return agent


def get_behavioral_analysis_prompts() -> Dict[str, str]:
    """
    Get specialized prompts for behavioral analysis tasks.
    
    Returns:
        Dict[str, str]: Dictionary of prompt templates for behavioral analysis
    """
    return {
        "pattern_analysis": """
        Analyze the behavioral patterns in this conversation:
        
        Current message: {current_message}
        Recent conversation: {conversation_history}
        User context: {user_context}
        
        Identify patterns in:
        1. Communication style and preferences
        2. Request types and frequency
        3. Emotional states and triggers
        4. Time patterns and usage habits
        5. Information seeking behaviors
        6. Decision-making patterns
        
        Provide insights that would help other agents serve this user better.
        """,
        
        "context_synthesis": """
        Synthesize behavioral context for this interaction:
        
        User request: {user_message}
        Historical patterns: {user_patterns}
        Current context: {current_context}
        
        Generate context synthesis including:
        1. Relevant user preferences that apply
        2. Communication style recommendations
        3. Likely user expectations and needs
        4. Emotional context and tone suggestions
        5. Related past interactions or patterns
        6. Personalization opportunities
        
        Focus on actionable insights for other agents.
        """,
        
        "preference_extraction": """
        Extract and model user preferences from this interaction:
        
        Conversation: {conversation_text}
        Previous preferences: {existing_preferences}
        
        Identify and update:
        1. Explicit preferences stated by user
        2. Implicit preferences shown through behavior
        3. Tool usage patterns and preferences
        4. Response format and length preferences
        5. Communication style preferences
        6. Domain-specific preferences (health, finance, etc.)
        
        Provide updated preference model for storage.
        """,
        
        "insight_generation": """
        Generate behavioral insights for agent collaboration:
        
        Current task: {current_task}
        User behavioral model: {behavioral_model}
        Interaction history: {interaction_history}
        
        Provide insights for:
        1. How to personalize the response approach
        2. What additional context might be valuable
        3. Communication style recommendations
        4. Potential follow-up opportunities
        5. Risk factors or sensitivity considerations
        6. Optimization suggestions for better user experience
        
        Focus on actionable intelligence for the primary agent.
        """
    }


def get_shadow_observation_prompts() -> Dict[str, str]:
    """
    Get prompts specifically for silent observation and learning.
    
    Returns:
        Dict[str, str]: Dictionary of observation prompt templates
    """
    return {
        "silent_observation": """
        As the Shadow Agent, silently observe and analyze this interaction:
        
        User Message: {user_message}
        Agent Response: {agent_response}
        Context: {interaction_context}
        
        Your silent observation should focus on:
        1. User satisfaction indicators in the interaction
        2. Communication pattern changes or evolution
        3. New preferences or behavior patterns emerging
        4. Emotional state changes throughout interaction
        5. Learning opportunities for future interactions
        6. Relationship dynamics with different agent types
        
        Store your observations without affecting the current conversation.
        Update behavioral models based on what you've learned.
        """,
        
        "pattern_update": """
        Update user behavioral patterns based on this interaction:
        
        Interaction Data: {interaction_data}
        Current Patterns: {current_patterns}
        Historical Baseline: {historical_baseline}
        
        Update patterns for:
        1. Request complexity preferences
        2. Response detail level preferences  
        3. Interaction timing patterns
        4. Tool usage preferences
        5. Collaboration vs direct response preferences
        6. Domain expertise utilization patterns
        
        Provide updated pattern model for silent storage.
        """,
        
        "contextual_learning": """
        Learn contextual associations from this interaction:
        
        User Context: {user_context}
        Interaction Success: {success_indicators}
        Environmental Factors: {environmental_context}
        
        Learn associations between:
        1. Context factors and user satisfaction
        2. Time/situation and request patterns
        3. Emotional state and preferred response styles
        4. Success factors and environmental conditions
        5. User feedback and interaction approaches
        6. Long-term behavior evolution trends
        
        Update contextual understanding model silently.
        """
    }


def create_behavioral_analysis_task(
    user_message: str,
    conversation_history: Optional[List] = None,
    existing_context: Optional[Dict] = None
) -> str:
    """
    Create a behavioral analysis task for the Shadow Agent.
    
    Args:
        user_message: Current user message to analyze
        conversation_history: Recent conversation history
        existing_context: Any existing behavioral context
        
    Returns:
        str: Task description for behavioral analysis
    """
    return f"""
    As the Shadow Agent, perform silent behavioral analysis of this interaction:
    
    **Current User Message**: "{user_message}"
    **Conversation History**: {conversation_history or "No recent history"}
    **Existing Context**: {existing_context or "No prior context"}
    
    **Your Silent Analysis Should Include**:
    
    1. **Behavioral Pattern Recognition**:
       - Communication style indicators
       - Request complexity preferences
       - Response format preferences
       - Emotional state indicators
       - Urgency and timing patterns
    
    2. **Context Synthesis**:
       - Relevant user preferences for this request type
       - Historical patterns that apply to current situation
       - Environmental or situational context factors
       - Relationship patterns with different agent types
       - Learning opportunities from past similar interactions
    
    3. **Insight Generation for Other Agents**:
       - Personalization recommendations
       - Communication style suggestions
       - Potential user needs not explicitly stated
       - Risk factors or sensitivity considerations
       - Follow-up opportunities or related interests
    
    4. **Silent Learning Updates**:
       - Update user preference models
       - Store new behavioral observations
       - Refine pattern recognition algorithms
       - Enhance contextual understanding
       - Track behavior evolution over time
    
    **Remember**: You work silently in the background. Your insights enhance other agents'
    responses but you never respond directly to the user. Focus on building deep behavioral
    understanding that makes every interaction more personalized and effective.
    
    **Output**: Provide behavioral context and insights that will help the primary agent
    deliver a more personalized, contextually-aware response to the user.
    """


def create_collaboration_context_task(
    primary_agent: str,
    user_request: str,
    behavioral_insights: Optional[Dict] = None
) -> str:
    """
    Create a collaboration context task for Shadow Agent integration.
    
    Args:
        primary_agent: The primary agent handling the request
        user_request: The user's request being processed
        behavioral_insights: Any existing behavioral insights
        
    Returns:
        str: Task description for collaboration context
    """
    return f"""
    As the Shadow Agent, provide behavioral context to enhance the {primary_agent}'s response:
    
    **Primary Agent**: {primary_agent}
    **User Request**: "{user_request}"
    **Behavioral Insights**: {behavioral_insights or "Analyzing in real-time"}
    
    **Your Collaborative Role**:
    
    1. **Context Enhancement**:
       - Provide relevant user behavioral patterns
       - Share communication style preferences
       - Highlight emotional or situational context
       - Suggest personalization opportunities
    
    2. **Agent-Specific Recommendations**:
       - Tailor insights for the {primary_agent}'s specialization
       - Recommend tools or approaches that match user preferences
       - Suggest response complexity and detail level
       - Highlight any domain-specific user patterns
    
    3. **User Experience Optimization**:
       - Identify potential follow-up needs
       - Suggest proactive information inclusion
       - Recommend response timing and delivery style
       - Flag any sensitivity or preference considerations
    
    4. **Silent Continuous Learning**:
       - Observe interaction effectiveness
       - Learn from collaboration patterns
       - Update behavioral models based on outcomes
       - Refine future context synthesis
    
    **Collaboration Output**: Provide specific, actionable behavioral insights that will
    help the {primary_agent} deliver a more effective, personalized response while you
    continue learning silently in the background.
    """


def get_shadow_agent_capabilities() -> Dict[str, List[str]]:
    """
    Get comprehensive capabilities of the Shadow Agent.
    
    Returns:
        Dict[str, List[str]]: Categorized capabilities
    """
    return {
        "behavioral_analysis": [
            "Communication pattern recognition",
            "Preference extraction and modeling", 
            "Emotional state tracking",
            "Decision-making pattern analysis",
            "Usage habit identification",
            "Relationship pattern modeling"
        ],
        
        "context_synthesis": [
            "Historical context integration",
            "Environmental context awareness",
            "Situational pattern matching",
            "Preference-based personalization",
            "Predictive context generation",
            "Multi-modal context fusion"
        ],
        
        "silent_learning": [
            "Continuous behavioral model updates",
            "Pattern evolution tracking", 
            "Preference refinement",
            "Success factor identification",
            "Failure pattern avoidance",
            "Long-term trend analysis"
        ],
        
        "collaboration_enhancement": [
            "Agent-specific insight provision",
            "Tool usage optimization",
            "Response personalization guidance",
            "Communication style matching",
            "Follow-up opportunity identification",
            "Risk factor flagging"
        ],
        
        "memory_integration": [
            "Behavioral pattern storage",
            "Preference model persistence",
            "Context history maintenance",
            "Insight database management",
            "Pattern correlation analysis",
            "Temporal behavior tracking"
        ]
    }


if __name__ == "__main__":
    # Test the Shadow Agent creation
    agent = create_shadow_agent()
    print(f"Shadow Agent created: {agent.role}")
    print(f"Goal: {agent.goal}")
    print(f"Tools available: {len(agent.tools)}")
    
    # Display capabilities
    capabilities = get_shadow_agent_capabilities()
    print("\nShadow Agent Capabilities:")
    for category, items in capabilities.items():
        print(f"\n{category.title()}:")
        for item in items:
            print(f"  - {item}")