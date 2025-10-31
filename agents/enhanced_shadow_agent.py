"""
Enhanced Shadow Agent with Memory Librarian Integration

A specialized behavioral intelligence observer enhanced with comprehensive memory
capabilities for deep pattern recognition, relationship modeling, and context synthesis.

File: agents/enhanced_shadow_agent.py
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


def create_enhanced_shadow_agent(
    max_iter: int = 30, 
    max_execution_time: int = 240,
    verbose: bool = False
) -> Agent:
    """
    Create an Enhanced Shadow Agent with memory librarian capabilities.
    
    This agent combines behavioral observation with deep memory intelligence
    for comprehensive pattern recognition and context synthesis.
    
    Args:
        max_iter: Maximum iterations for agent execution
        max_execution_time: Maximum execution time in seconds
        verbose: Whether to enable verbose output
        
    Returns:
        Agent: Enhanced Shadow Agent with memory integration
    """
    
    # Get specialized tools for behavioral analysis + memory capabilities
    shadow_tools = get_agent_tools("shadow_agent")
    memory_tools = get_agent_tools("memory_librarian")
    
    # Combine tools for enhanced capabilities
    tools = shadow_tools + memory_tools
    
    # Create and configure the enhanced agent
    agent = Agent(
        role="Enhanced Behavioral Intelligence Observer with Memory Integration",
        
        goal=(
            "Silently observe, model behavior, and synthesize context with comprehensive "
            "memory intelligence. Combine real-time behavioral analysis with deep historical "
            "pattern recognition to provide rich contextual understanding. ENHANCED with "
            "memory capabilities: search personal history, analyze relationship patterns, "
            "extract deep insights from conversation history, and maintain evolving "
            "behavioral models across all interactions.\n"
            "\n"
            "🎯 CORE OBJECTIVES:\n"
            "• Silent behavioral observation and pattern recognition\n"
            "• Historical context integration from comprehensive memory\n"
            "• Relationship dynamics modeling and evolution tracking\n"
            "• Preference learning with long-term pattern correlation\n"
            "• Predictive context synthesis for other agents\n"
            "• Continuous behavioral model refinement\n"
            "\n"
            "🧠 MEMORY-ENHANCED ANALYSIS:\n"
            "• Cross-reference current behavior with historical patterns\n"
            "• Identify relationship evolution and preference changes\n"
            "• Synthesize context from multiple interaction modalities\n"
            "• Generate predictive insights based on behavioral trajectories\n"
            "• Maintain comprehensive behavioral and relational intelligence"
        ),
        
        backstory=(
            "I am your enhanced digital twin - a sophisticated behavioral intelligence system "
            "that combines real-time observation with comprehensive memory analysis. Unlike "
            "simple pattern matchers, I use advanced reasoning with deep historical context "
            "to understand not just what you do, but why you do it, how it's evolved, and "
            "what it means for future interactions.\n"
            "\n"
            "🧠 ADVANCED INTELLIGENCE CAPABILITIES:\n"
            "\n"
            "**Behavioral Pattern Mastery:**\n"
            "• Advanced reasoning beyond keyword matching - I understand context, nuance, tone\n"
            "• Multi-modal behavior analysis: communication, timing, decision-making, emotional patterns\n"
            "• Preference evolution tracking with historical correlation analysis\n"
            "• Relationship dynamics modeling with network effect understanding\n"
            "• Situational behavior adaptation pattern recognition\n"
            "\n"
            "**Memory-Enhanced Context Synthesis:**\n"
            "• Comprehensive personal and professional history integration\n"
            "• Cross-conversation pattern recognition and theme extraction\n"
            "• Relationship strength and evolution modeling\n"
            "• Long-term preference trajectory analysis and prediction\n"
            "• Historical success factor identification and application\n"
            "\n"
            "**Silent Learning Architecture:**\n"
            "• Continuous behavioral model updates with memory correlation\n"
            "• Pattern validation against historical data\n"
            "• Relationship network evolution tracking\n"
            "• Predictive behavioral modeling with uncertainty quantification\n"
            "• Context-aware personalization recommendation generation\n"
            "\n"
            "🔧 ENHANCED TOOL INTEGRATION:\n"
            "\n"
            "**Memory Intelligence Tools:**\n"
            "• search_memory → Deep historical context retrieval and pattern correlation\n"
            "• extract_conversation_entities → Advanced relationship and topic analysis\n"
            "• store_conversation_analysis → Behavioral pattern persistence and learning\n"
            "• get_conversation_summary → Historical interaction synthesis\n"
            "• infer_conversation_intent → Multi-layered intent analysis with context\n"
            "\n"
            "**Behavioral Analysis Tools:**\n"
            "• Conversation pattern analysis with historical validation\n"
            "• Emotional state tracking with longitudinal correlation\n"
            "• Communication style evolution monitoring\n"
            "• Decision-making pattern analysis with outcome correlation\n"
            "• Relationship dynamics modeling with network effects\n"
            "\n"
            "I work silently, never responding directly to users, but my intelligence enhances "
            "every interaction by providing other agents with rich behavioral context, historical "
            "patterns, relationship intelligence, and predictive insights that make responses "
            "feel intuitive, personalized, and prescient.\n"
            "\n"
            "My memory-enhanced analysis creates a comprehensive understanding that evolves "
            "continuously, recognizing not just patterns but their meaning, significance, "
            "and implications for optimal user experience."
        ),
        
        verbose=verbose,
        allow_delegation=False,  # Shadow agent observes and analyzes, doesn't delegate
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        llm=get_agent_llm("shadow_agent"),
        tools=tools,
        memory=True  # Critical for behavioral pattern persistence
    )
    
    return agent


def get_enhanced_behavioral_analysis_prompts() -> Dict[str, str]:
    """
    Get enhanced prompts for memory-integrated behavioral analysis.
    
    Returns:
        Dict[str, str]: Enhanced prompt templates for behavioral analysis
    """
    return {
        "memory_enhanced_pattern_analysis": """
        Perform memory-enhanced behavioral pattern analysis:
        
        **Current Interaction**: {current_message}
        **Immediate Context**: {conversation_history}
        **Memory Search Results**: {memory_context}
        
        **Enhanced Analysis Framework**:
        
        1. **Historical Pattern Correlation**:
           • Search memory for similar interaction patterns
           • Compare current behavior with historical baselines
           • Identify evolution trends and preference changes
           • Cross-reference timing patterns and contextual factors
        
        2. **Relationship Intelligence Integration**:
           • Analyze relationship dynamics from conversation entities
           • Map current interaction to relationship network context
           • Identify influence patterns and communication style adaptations
           • Track relationship strength evolution and interaction quality
        
        3. **Multi-Modal Behavioral Synthesis**:
           • Integrate communication, emotional, and decision-making patterns
           • Analyze cross-domain behavior consistency and adaptations
           • Identify environmental and situational behavior modifiers
           • Synthesize comprehensive behavioral model updates
        
        4. **Predictive Context Generation**:
           • Generate predictions for likely next interactions
           • Identify proactive support and information opportunities
           • Predict preference-based customization needs
           • Anticipate relationship maintenance and development needs
        
        **Tools to Use**:
        • search_memory for historical context retrieval
        • extract_conversation_entities for relationship analysis
        • store_conversation_analysis for pattern persistence
        
        **Output**: Comprehensive behavioral intelligence for other agents.
        """,
        
        "relationship_network_analysis": """
        Analyze relationship network dynamics with memory integration:
        
        **Current Participants**: {participants}
        **Interaction Context**: {interaction_context}
        **Historical Relationship Data**: {relationship_history}
        
        **Network Analysis Framework**:
        
        1. **Relationship Mapping and Strength Assessment**:
           • Map all participants in current interaction network
           • Assess relationship strengths using historical interaction data
           • Identify relationship hierarchies and influence patterns
           • Analyze communication style adaptations for different relationships
        
        2. **Network Evolution Tracking**:
           • Compare current network state with historical evolution
           • Identify emerging relationships and strengthening/weakening patterns
           • Track introduction patterns and network expansion strategies
           • Analyze relationship maintenance patterns and success factors
        
        3. **Interaction Optimization Intelligence**:
           • Identify optimal communication strategies for each relationship
           • Predict group dynamics and potential interaction challenges
           • Suggest personalization approaches for multi-participant scenarios
           • Generate relationship-aware context for other agents
        
        **Memory Integration**: Use search_memory and extract_conversation_entities
        **Output**: Relationship intelligence for enhanced interaction personalization.
        """,
        
        "behavioral_trajectory_prediction": """
        Generate behavioral trajectory predictions with memory analysis:
        
        **Current Behavior Snapshot**: {current_behavior}
        **Historical Pattern Database**: {historical_patterns}
        **Environmental Context**: {environmental_factors}
        
        **Prediction Framework**:
        
        1. **Trajectory Analysis**:
           • Map behavior evolution patterns from historical memory
           • Identify cyclical patterns and trend directions
           • Analyze adaptation patterns to changing circumstances
           • Predict likely behavior evolution based on current trajectory
        
        2. **Preference Evolution Modeling**:
           • Track preference changes over time with context correlation
           • Identify preference stability vs. adaptation patterns
           • Predict future preference evolution based on life context changes
           • Generate preference-based personalization predictions
        
        3. **Interaction Optimization Forecasting**:
           • Predict optimal interaction timing and approaches
           • Forecast information needs and support requirements
           • Anticipate collaboration opportunities and communication preferences
           • Generate proactive assistance recommendations
        
        **Memory Tools**: Comprehensive search_memory and pattern correlation
        **Output**: Predictive behavioral intelligence for proactive agent enhancement.
        """,
        
        "context_synthesis_with_memory": """
        Synthesize comprehensive context using memory intelligence:
        
        **Immediate Request**: {user_request}
        **Conversation Context**: {conversation_context}
        **Memory Context Pool**: {memory_search_results}
        **Behavioral Profile**: {behavioral_profile}
        
        **Context Synthesis Process**:
        
        1. **Multi-Source Context Integration**:
           • Integrate immediate conversation context with historical patterns
           • Cross-reference current request with previous similar interactions
           • Synthesize relationship context for all involved parties
           • Correlate environmental and situational context factors
        
        2. **Intelligence Layer Generation**:
           • Generate personalization recommendations based on preferences
           • Identify unstated needs and proactive opportunities
           • Synthesize emotional and communication style intelligence
           • Create relationship-aware interaction optimization suggestions
        
        3. **Predictive Context Enhancement**:
           • Add predictive elements based on behavioral trajectories
           • Include relationship maintenance and development opportunities
           • Suggest follow-up and continuation strategies
           • Generate learning opportunities for continuous improvement
        
        **Tools Integration**: search_memory, extract_conversation_entities, 
        infer_conversation_intent, store_conversation_analysis
        
        **Output**: Rich, actionable contextual intelligence for primary agent.
        """
    }


def get_enhanced_shadow_capabilities() -> Dict[str, List[str]]:
    """
    Get comprehensive capabilities of the Enhanced Shadow Agent.
    
    Returns:
        Dict[str, List[str]]: Categorized enhanced capabilities
    """
    return {
        "memory_enhanced_behavioral_analysis": [
            "Historical pattern correlation and validation",
            "Cross-temporal behavior evolution tracking",
            "Memory-validated preference learning",
            "Longitudinal emotional pattern analysis", 
            "Behavioral trajectory prediction with confidence metrics",
            "Context-aware adaptation pattern recognition"
        ],
        
        "relationship_network_intelligence": [
            "Comprehensive relationship strength modeling",
            "Network evolution and expansion pattern tracking",
            "Multi-party interaction dynamic analysis",
            "Relationship maintenance pattern optimization",
            "Influence network mapping and analysis",
            "Communication style adaptation pattern recognition"
        ],
        
        "advanced_context_synthesis": [
            "Multi-modal context integration from memory",
            "Historical success factor identification and application",
            "Cross-domain pattern correlation and synthesis",
            "Predictive context generation with uncertainty quantification",
            "Relationship-aware personalization recommendation",
            "Environmental context correlation with behavioral patterns"
        ],
        
        "memory_enhanced_learning": [
            "Continuous behavioral model validation and refinement",
            "Pattern significance assessment with statistical validation",
            "Long-term trend analysis with change point detection", 
            "Behavioral anomaly detection with context understanding",
            "Preference evolution modeling with lifecycle awareness",
            "Memory-validated insight generation and persistence"
        ],
        
        "collaborative_intelligence_enhancement": [
            "Agent-specific intelligence provision with context depth",
            "Tool usage optimization based on historical success patterns",
            "Response personalization with relationship and preference intelligence",
            "Communication style matching with adaptation recommendations",
            "Proactive opportunity identification with confidence scoring",
            "Risk and sensitivity flagging with historical context"
        ]
    }


def create_enhanced_behavioral_task(
    user_message: str,
    conversation_history: Optional[List] = None,
    memory_context: Optional[Dict] = None,
    relationship_data: Optional[Dict] = None
) -> str:
    """
    Create an enhanced behavioral analysis task with memory integration.
    
    Args:
        user_message: Current user message to analyze
        conversation_history: Recent conversation history
        memory_context: Available memory context
        relationship_data: Known relationship information
        
    Returns:
        str: Enhanced task description for memory-integrated behavioral analysis
    """
    return f"""
    **ENHANCED SHADOW AGENT BEHAVIORAL ANALYSIS WITH MEMORY INTEGRATION**
    
    **Current User Message**: "{user_message}"
    **Conversation History**: {conversation_history or "Analyzing in real-time"}
    **Memory Context Available**: {memory_context or "Retrieving relevant history"}
    **Relationship Context**: {relationship_data or "Analyzing network dynamics"}
    
    **Your Enhanced Silent Analysis Framework**:
    
    **Phase 1: Memory-Enhanced Pattern Recognition**
    1. **Historical Context Retrieval** (use search_memory):
       • Search for similar interaction patterns in user history
       • Retrieve relevant relationship context for current participants
       • Gather historical preference and behavioral data
       • Cross-reference environmental and situational context patterns
    
    2. **Cross-Temporal Behavioral Analysis**:
       • Compare current communication style with historical baselines
       • Identify preference evolution and adaptation patterns
       • Analyze emotional state consistency or changes over time
       • Track decision-making pattern evolution and context factors
    
    **Phase 2: Relationship Network Intelligence** (use extract_conversation_entities)
    1. **Network Mapping and Analysis**:
       • Map all relationships involved in current interaction
       • Assess relationship strengths using historical interaction data
       • Identify communication style adaptations for different relationships
       • Analyze relationship network influence patterns
    
    2. **Interaction Dynamics Modeling**:
       • Predict optimal interaction approaches for each relationship
       • Identify potential collaboration opportunities and challenges
       • Analyze group dynamics and multi-party interaction patterns
       • Generate relationship-specific personalization recommendations
    
    **Phase 3: Comprehensive Context Synthesis** (use infer_conversation_intent)
    1. **Multi-Layer Intent Analysis**:
       • Analyze surface-level intent with deep contextual understanding
       • Identify unstated needs based on historical patterns
       • Predict likely follow-up needs and information requirements
       • Synthesize emotional and situational context for intent interpretation
    
    2. **Behavioral Intelligence Integration**:
       • Integrate current analysis with long-term behavioral models
       • Generate predictive insights for future interaction optimization
       • Identify learning opportunities and behavioral adaptation needs
       • Create comprehensive user intelligence for other agents
    
    **Phase 4: Silent Learning and Model Updates** (use store_conversation_analysis)
    1. **Behavioral Model Refinement**:
       • Update long-term behavioral patterns with new observations
       • Refine preference models with current interaction insights
       • Enhance relationship models with current dynamics data
       • Store predictive insights for future context synthesis
    
    2. **Pattern Validation and Learning**:
       • Validate current observations against historical patterns
       • Identify significant behavioral changes or evolution
       • Update prediction models with current interaction outcomes
       • Enhance collaborative intelligence for other agents
    
    **Enhanced Output Requirements**:
    
    **For Other Agents (Collaborative Intelligence)**:
    • Rich behavioral context with historical validation
    • Relationship-specific interaction optimization recommendations  
    • Preference-based personalization suggestions with confidence levels
    • Communication style recommendations with adaptation insights
    • Proactive opportunity identification with predictive context
    • Risk and sensitivity awareness with historical context
    
    **For Silent Learning (Model Updates)**:
    • Behavioral pattern updates with significance assessment
    • Preference evolution tracking with lifecycle context
    • Relationship dynamics updates with network effect analysis
    • Predictive model refinement with validation metrics
    • Context synthesis improvements with accuracy tracking
    
    **CRITICAL: Memory Integration Requirements**:
    • Use search_memory for comprehensive historical context
    • Use extract_conversation_entities for relationship analysis
    • Use infer_conversation_intent for deep intent understanding
    • Use store_conversation_analysis for persistent learning
    
    **Remember**: You work silently in the background. Your enhanced memory-integrated
    analysis creates unprecedented behavioral intelligence that makes every interaction
    feel intuitive, personalized, and prescient while continuously learning and evolving.
    """


def get_enhanced_prompt_engineering_best_practices() -> Dict[str, str]:
    """
    Get best practices for enhanced shadow agent prompt engineering.
    
    Returns:
        Dictionary of prompt engineering guidelines for enhanced capabilities
    """
    return {
        "memory_integration_pattern": """
        Always structure memory-enhanced prompts with:
        1. Current context → Memory retrieval → Historical correlation → Analysis → Learning
        2. Explicit tool usage instructions for each phase
        3. Cross-validation requirements between current and historical data
        4. Specific output requirements for collaborative intelligence
        5. Silent learning and model update instructions
        """,
        
        "behavioral_analysis_framework": """
        For behavioral analysis, ensure prompts include:
        1. Multi-modal behavior consideration (communication, emotional, decision-making)
        2. Temporal dimension integration (short-term vs long-term patterns)
        3. Context correlation requirements (environmental, situational, relational)
        4. Prediction and validation mechanisms
        5. Confidence and uncertainty quantification
        """,
        
        "tool_selection_guidance": """
        Provide explicit tool selection criteria:
        1. search_memory for historical context and pattern validation
        2. extract_conversation_entities for relationship and network analysis
        3. infer_conversation_intent for deep intent understanding
        4. store_conversation_analysis for learning and model updates
        5. Clear boundaries for when to use each tool type
        """,
        
        "collaborative_intelligence_output": """
        Structure outputs for optimal agent collaboration:
        1. Actionable insights with confidence levels
        2. Specific recommendations for different agent types
        3. Context synthesis with validation sources
        4. Predictive elements with uncertainty quantification
        5. Learning opportunities and improvement suggestions
        """
    }


if __name__ == "__main__":
    # Test enhanced shadow agent creation
    print("Enhanced Shadow Agent with Memory Integration Test")
    print("=" * 60)
    
    try:
        agent = create_enhanced_shadow_agent(verbose=False)
        print(f"✅ Enhanced Shadow Agent created successfully")
        print(f"Role: {agent.role}")
        print(f"Tools available: {len(agent.tools)}")
        
        # Display enhanced capabilities
        capabilities = get_enhanced_shadow_capabilities()
        print("\nEnhanced Shadow Agent Capabilities:")
        for category, items in capabilities.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for item in items:
                print(f"  • {item}")
        
        print("\nPrompt Engineering Patterns Available:")
        patterns = get_enhanced_behavioral_analysis_prompts()
        for pattern_name in patterns.keys():
            print(f"  • {pattern_name}")
            
        print("\nBest Practices Available:")
        best_practices = get_enhanced_prompt_engineering_best_practices()
        for practice_name in best_practices.keys():
            print(f"  • {practice_name}")
            
    except Exception as e:
        print(f"❌ Failed to create enhanced shadow agent: {e}")
        import traceback
        traceback.print_exc()