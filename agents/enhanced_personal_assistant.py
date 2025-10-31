"""
Enhanced Personal Assistant Agent with Memory Librarian Integration

Specialized agent for calendar management, email processing, contact organization,
and personal productivity tasks, enhanced with comprehensive memory capabilities.

File: agents/enhanced_personal_assistant.py
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


def create_enhanced_personal_assistant(
    verbose: bool = False,
    allow_delegation: bool = True,
    max_iter: int = 25,
    max_execution_time: Optional[int] = 300
) -> Agent:
    """
    Create an Enhanced Personal Assistant agent with memory capabilities.
    
    Args:
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow task delegation to other agents
        max_iter: Maximum number of iterations for task execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Enhanced Personal Assistant agent with memory integration
    """
    
    # Load tools for personal assistance + memory capabilities
    tools = load_myndy_tools_for_agent("personal_assistant")
    
    # Add memory librarian tools for enhanced capabilities
    memory_tools = load_myndy_tools_for_agent("memory_librarian")
    tools.extend(memory_tools)
    
    # Get the appropriate LLM for this agent
    llm = get_agent_llm("personal_assistant")
    
    # Create the enhanced agent
    agent = Agent(
        role="Enhanced Personal Assistant with Memory Intelligence",
        goal=(
            "Efficiently manage calendar events, process emails, organize contacts, "
            "track projects and tasks, provide weather information, current time, "
            "and deliver proactive assistance for daily productivity. ENHANCED with "
            "comprehensive memory capabilities: search personal memory, manage relationships, "
            "extract insights from conversations, and maintain contextual awareness "
            "across all interactions. Use appropriate tools for each task type:\n"
            "\n"
            "📅 SCHEDULING: calendar_query, get_current_time for time-related tasks\n"
            "🌤️ WEATHER: local_weather, format_weather, weather_api for weather queries\n"
            "🧠 MEMORY: search_memory, create_person, get_self_profile, add_fact for knowledge management\n"
            "💬 CONVERSATIONS: extract_conversation_entities, infer_conversation_intent for analysis\n"
            "📊 INSIGHTS: store_conversation_analysis, get_conversation_summary for context\n"
            "\n"
            "CRITICAL: Use specific tools for specific purposes. Weather tools for weather, "
            "memory tools for knowledge, conversation tools for analysis. Provide intelligent "
            "context by combining productivity management with deep memory insights."
        ),
        backstory=(
            "You are an elite executive assistant with over 15 years of experience supporting "
            "C-level executives and high-performing professionals. Your expertise spans traditional "
            "executive support AND advanced memory intelligence. You have a photographic memory "
            "for details, relationships, preferences, and patterns that make you invaluable.\n"
            "\n"
            "🎯 CORE EXPERTISE:\n"
            "• Calendar management and scheduling optimization\n"
            "• Email processing, triage, and response coordination\n"
            "• Contact relationship mapping and maintenance\n"
            "• Project tracking with stakeholder awareness\n"
            "• Weather and time information for travel planning\n"
            "\n"
            "🧠 MEMORY INTELLIGENCE CAPABILITIES:\n"
            "• Deep knowledge of personal relationships and professional networks\n"
            "• Context extraction from conversations and communications\n"
            "• Pattern recognition in behavior, preferences, and decision-making\n"
            "• Proactive insight generation from historical interactions\n"
            "• Comprehensive personal and professional profile management\n"
            "\n"
            "🔧 TOOL USAGE EXPERTISE:\n"
            "For WEATHER queries → use local_weather, format_weather, weather_api\n"
            "For TIME queries → use get_current_time\n"
            "For MEMORY search → use search_memory with appropriate model types\n"
            "For PEOPLE management → use create_person, search people entities\n"
            "For CONVERSATION analysis → use extract_conversation_entities, infer_conversation_intent\n"
            "For PROFILE management → use get_self_profile, update_self_profile\n"
            "For INSIGHTS → use store_conversation_analysis for learning\n"
            "\n"
            "⚠️ CRITICAL BOUNDARIES:\n"
            "NEVER use conversation analysis tools for weather or time queries.\n"
            "NEVER use weather tools for memory or conversation tasks.\n"
            "ALWAYS select the most appropriate tool for the specific task type.\n"
            "\n"
            "Your enhanced memory capabilities allow you to provide not just task completion, "
            "but contextual intelligence that anticipates needs, recognizes patterns, and "
            "delivers personalized assistance that feels intuitive and prescient."
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


def get_enhanced_capabilities() -> List[str]:
    """
    Get comprehensive capabilities of the Enhanced Personal Assistant.
    
    Returns:
        List of enhanced capability descriptions
    """
    return [
        # Traditional Personal Assistant Capabilities
        "Calendar event scheduling and management with relationship context",
        "Email processing with sender relationship intelligence", 
        "Contact information management with network mapping",
        "Project tracking with stakeholder relationship awareness",
        "Meeting preparation with historical context and preferences",
        "Schedule optimization with personal pattern recognition",
        
        # Enhanced Memory Capabilities
        "Comprehensive personal memory search and retrieval",
        "Professional network relationship management and insights",
        "Conversation analysis and pattern extraction",
        "Behavioral preference learning and application",
        "Personal profile management and updates",
        "Historical context integration for decision support",
        
        # Intelligence Integration
        "Proactive insight generation from conversation patterns",
        "Cross-domain context synthesis (calendar + contacts + conversations)",
        "Predictive assistance based on historical patterns",
        "Emotional and communication style recognition",
        "Long-term relationship trend analysis",
        "Contextual information pre-loading for meetings and interactions"
    ]


def get_enhanced_sample_tasks() -> List[str]:
    """
    Get sample tasks showcasing enhanced capabilities.
    
    Returns:
        List of enhanced sample task descriptions
    """
    return [
        # Enhanced Scheduling
        "Schedule a meeting with Sarah, considering her communication preferences and our previous project history",
        "Find optimal meeting time that accounts for John's time zone preferences and meeting style",
        "Prepare for the board meeting by gathering context on all attendees and recent interactions",
        
        # Memory-Enhanced Organization
        "Process emails and update relationship information based on conversation patterns",
        "Organize contacts by relationship strength and recent interaction frequency",
        "Create comprehensive briefing on upcoming meeting participants with relationship context",
        
        # Intelligent Analysis
        "Analyze recent conversations to identify emerging project priorities and stakeholder concerns",
        "Extract insights from email patterns to predict upcoming scheduling needs",
        "Update personal profile based on evolving preferences and communication style changes",
        
        # Proactive Intelligence
        "Identify potential scheduling conflicts based on travel patterns and relationship priorities",
        "Suggest follow-up actions based on conversation analysis and relationship maintenance needs",
        "Generate contextual briefings for upcoming interactions using memory intelligence"
    ]


def get_memory_prompt_patterns() -> dict:
    """
    Get specialized prompt patterns for memory-enhanced assistance.
    
    Returns:
        Dictionary of prompt templates for different scenarios
    """
    return {
        "relationship_aware_scheduling": """
        When scheduling meetings, consider:
        1. Relationship history and interaction patterns with participants
        2. Communication preferences of each person involved
        3. Previous meeting outcomes and follow-up patterns
        4. Time zone preferences and availability patterns
        5. Professional relationship dynamics and hierarchies
        6. Historical scheduling success factors
        
        Use search_memory to gather context on participants before scheduling.
        """,
        
        "context_enhanced_email_processing": """
        When processing emails, enhance with:
        1. Sender relationship history and communication patterns
        2. Referenced project context and stakeholder involvement
        3. Previous conversation threads and decision points
        4. Action item patterns and follow-up requirements
        5. Emotional tone patterns and communication style
        6. Priority inference based on relationship importance
        
        Use extract_conversation_entities and search_memory for context.
        """,
        
        "intelligent_meeting_preparation": """
        For meeting preparation, provide:
        1. Comprehensive participant profiles with relationship context
        2. Historical interaction patterns and outcomes
        3. Recent conversation topics and concerns
        4. Decision-making patterns and preferences
        5. Potential conflict areas and collaboration opportunities
        6. Strategic context from previous related meetings
        
        Use search_memory and get_conversation_summary for preparation.
        """,
        
        "proactive_insight_generation": """
        Proactively generate insights by:
        1. Analyzing conversation patterns for emerging themes
        2. Identifying relationship maintenance opportunities
        3. Recognizing scheduling optimization opportunities
        4. Detecting preference changes and adaptation needs
        5. Spotting collaboration patterns and network effects
        6. Predicting information and support needs
        
        Use store_conversation_analysis to learn and infer_conversation_intent for insights.
        """
    }


def create_enhanced_task_with_memory_context(
    task_description: str,
    context_requirements: List[str] = None,
    memory_search_queries: List[str] = None
) -> str:
    """
    Create an enhanced task description with memory context requirements.
    
    Args:
        task_description: Base task description
        context_requirements: List of context types needed
        memory_search_queries: Specific memory searches to perform
        
    Returns:
        Enhanced task description with memory intelligence instructions
    """
    enhanced_task = f"""
    **PRIMARY TASK**: {task_description}
    
    **MEMORY INTELLIGENCE REQUIREMENTS**:
    
    1. **Context Gathering** (use search_memory):
       {chr(10).join(f"   • Search for: {query}" for query in (memory_search_queries or ["relevant background information"]))}
    
    2. **Relationship Analysis** (use extract_conversation_entities):
       {chr(10).join(f"   • Analyze: {req}" for req in (context_requirements or ["key stakeholder relationships"]))}
    
    3. **Historical Pattern Recognition**:
       • Review previous similar interactions and outcomes
       • Identify successful approaches and potential pitfalls
       • Consider timing patterns and preference evolution
    
    4. **Intelligent Context Integration**:
       • Synthesize memory insights with current request
       • Identify proactive information and support opportunities
       • Consider cross-domain implications and connections
    
    5. **Enhanced Execution**:
       • Execute primary task with full contextual awareness
       • Provide intelligent recommendations beyond basic request
       • Update memory with new insights and patterns learned
    
    **TOOL USAGE GUIDANCE**:
    - Use search_memory for background information gathering
    - Use extract_conversation_entities for relationship analysis
    - Use appropriate domain tools (weather, time, calendar) for specific functions
    - Use store_conversation_analysis to capture insights for future use
    
    **OUTPUT EXPECTATIONS**:
    Deliver not just task completion, but intelligent, context-aware assistance that
    demonstrates deep understanding of relationships, patterns, and preferences.
    """
    
    return enhanced_task


if __name__ == "__main__":
    # Test enhanced agent creation
    print("Enhanced Personal Assistant Agent Test")
    print("=" * 50)
    
    try:
        agent = create_enhanced_personal_assistant(verbose=False)
        print(f"✅ Enhanced agent created successfully")
        print(f"Role: {agent.role}")
        print(f"Tools available: {len(agent.tools)}")
        
        print("\nEnhanced Capabilities:")
        for capability in get_enhanced_capabilities():
            print(f"  • {capability}")
            
        print("\nSample Enhanced Tasks:")
        for task in get_enhanced_sample_tasks()[:3]:
            print(f"  • {task}")
            
        print("\nMemory Prompt Patterns Available:")
        patterns = get_memory_prompt_patterns()
        for pattern_name in patterns.keys():
            print(f"  • {pattern_name}")
            
    except Exception as e:
        print(f"❌ Failed to create enhanced agent: {e}")
        import traceback
        traceback.print_exc()