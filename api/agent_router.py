"""
Intelligent Agent Router for CrewAI-Myndy Integration

Analyzes conversations and automatically selects the best agent or crew
to handle each user query based on content analysis and context.

File: api/agent_router.py
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Available agent roles."""
    MEMORY_LIBRARIAN = "memory_librarian"
    RESEARCH_SPECIALIST = "research_specialist" 
    PERSONAL_ASSISTANT = "personal_assistant"
    HEALTH_ANALYST = "health_analyst"
    FINANCE_TRACKER = "finance_tracker"


class TaskComplexity(str, Enum):
    """Task complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    MULTI_AGENT = "multi_agent"


@dataclass
class AgentCapability:
    """Defines an agent's capabilities and keywords."""
    role: AgentRole
    name: str
    description: str
    keywords: List[str]
    capabilities: List[str]
    confidence_threshold: float = 0.3


@dataclass
class RoutingDecision:
    """Result of agent routing analysis."""
    primary_agent: AgentRole
    secondary_agents: List[AgentRole]
    confidence: float
    reasoning: str
    complexity: TaskComplexity
    requires_collaboration: bool = False


class AgentRouter:
    """
    Intelligent router that analyzes conversations and selects appropriate agents.
    """
    
    def __init__(self):
        """Initialize the agent router with capability definitions."""
        self.agents = self._define_agent_capabilities()
        self.conversation_history = []
        
    def _define_agent_capabilities(self) -> Dict[AgentRole, AgentCapability]:
        """Define capabilities and keywords for each agent."""
        return {
            AgentRole.MEMORY_LIBRARIAN: AgentCapability(
                role=AgentRole.MEMORY_LIBRARIAN,
                name="Memory Librarian",
                description="Organizes and retrieves personal knowledge, entities, and conversation history",
                keywords=[
                    "remember", "recall", "memory", "history", "conversation", "past", "previous",
                    "notes", "knowledge", "organize", "find", "search", "lookup", "retrieve",
                    "entities", "relationships", "connections", "context", "reference",
                    "archive", "database", "store", "save", "documented", "recorded",
                    "contact", "contacts", "person", "people", "know", "phone", "email", "address",
                    "works for", "works at", "company", "organization", "job", "title", "update"
                ],
                capabilities=[
                    "Entity relationship management",
                    "Conversation history search",
                    "Knowledge organization", 
                    "Personal data retrieval",
                    "Context preservation",
                    "Information categorization"
                ]
            ),
            
            AgentRole.RESEARCH_SPECIALIST: AgentCapability(
                role=AgentRole.RESEARCH_SPECIALIST,
                name="Research Specialist",
                description="Conducts research, gathers information, and verifies facts",
                keywords=[
                    "research", "investigate", "study", "analyze", "explore", "examine",
                    "fact", "verify", "validate", "check", "confirm", "evidence", "source",
                    "information", "data", "statistics", "reports", "articles", "papers",
                    "trends", "analysis", "comparison", "evaluation", "assessment",
                    "background", "details", "comprehensive", "thorough", "deep dive"
                ],
                capabilities=[
                    "Web research and analysis",
                    "Fact verification",
                    "Document processing",
                    "Information synthesis",
                    "Source validation",
                    "Trend analysis"
                ]
            ),
            
            AgentRole.PERSONAL_ASSISTANT: AgentCapability(
                role=AgentRole.PERSONAL_ASSISTANT,
                name="Personal Assistant",
                description="Manages calendar, email, contacts, and personal productivity",
                keywords=[
                    "schedule", "calendar", "appointment", "meeting", "event", "time",
                    "email", "message", "contact", "phone", "address", "communication",
                    "task", "todo", "remind", "deadline", "priority", "urgent",
                    "organize", "plan", "coordinate", "manage", "workflow", "productivity",
                    "project", "timeline", "milestone", "agenda", "booking", "reservation"
                ],
                capabilities=[
                    "Calendar management",
                    "Email processing",
                    "Contact organization", 
                    "Task coordination",
                    "Meeting scheduling",
                    "Workflow optimization"
                ]
            ),
            
            AgentRole.HEALTH_ANALYST: AgentCapability(
                role=AgentRole.HEALTH_ANALYST,
                name="Health Analyst",
                description="Analyzes health data and provides wellness insights",
                keywords=[
                    "health", "fitness", "wellness", "exercise", "workout", "activity",
                    "steps", "calories", "heart", "sleep", "rest", "recovery", "stress",
                    "weight", "nutrition", "diet", "food", "hydration", "water",
                    "medical", "symptoms", "medication", "doctor", "appointment",
                    "metrics", "tracking", "progress", "goals", "improvement", "optimization"
                ],
                capabilities=[
                    "Health data analysis",
                    "Fitness tracking",
                    "Sleep optimization",
                    "Wellness recommendations",
                    "Activity monitoring",
                    "Health goal setting"
                ]
            ),
            
            AgentRole.FINANCE_TRACKER: AgentCapability(
                role=AgentRole.FINANCE_TRACKER,
                name="Finance Tracker", 
                description="Tracks expenses, analyzes spending, and provides financial insights",
                keywords=[
                    "money", "budget", "expense", "spending", "cost", "price", "financial",
                    "income", "salary", "payment", "transaction", "purchase", "buy", "sell",
                    "investment", "savings", "bank", "account", "credit", "debt", "loan",
                    "tax", "finance", "economic", "analysis", "tracking", "planning",
                    "portfolio", "stocks", "retirement", "emergency fund", "bills"
                ],
                capabilities=[
                    "Expense categorization",
                    "Budget analysis", 
                    "Financial reporting",
                    "Investment tracking",
                    "Spending optimization",
                    "Financial goal planning"
                ]
            )
        }
    
    def analyze_message(self, message: str, conversation_context: List[Dict] = None) -> RoutingDecision:
        """
        Analyze a message and determine the best agent to handle it.
        
        Args:
            message: User message to analyze
            conversation_context: Previous conversation messages for context
            
        Returns:
            RoutingDecision with primary agent and reasoning
        """
        message_lower = message.lower()
        scores = {}
        
        # Score each agent based on keyword matches
        for role, agent in self.agents.items():
            score = self._calculate_agent_score(message_lower, agent)
            scores[role] = score
        
        # Analyze conversation context for additional signals
        context_scores = self._analyze_conversation_context(message, conversation_context)
        
        # Combine scores
        for role in scores:
            if role in context_scores:
                scores[role] = (scores[role] + context_scores[role]) / 2
        
        # Determine task complexity
        complexity = self._assess_complexity(message, conversation_context)
        
        # Select primary agent
        primary_agent = max(scores, key=scores.get)
        confidence = scores[primary_agent]
        
        # Determine if collaboration is needed
        requires_collaboration = complexity == TaskComplexity.MULTI_AGENT or confidence < 0.6
        
        # Select secondary agents for collaboration
        secondary_agents = []
        if requires_collaboration:
            secondary_agents = [
                role for role, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[1:3]
                if score > 0.2
            ]
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            message, primary_agent, secondary_agents, confidence, complexity
        )
        
        return RoutingDecision(
            primary_agent=primary_agent,
            secondary_agents=secondary_agents,
            confidence=confidence,
            reasoning=reasoning,
            complexity=complexity,
            requires_collaboration=requires_collaboration
        )
    
    def _calculate_agent_score(self, message: str, agent: AgentCapability) -> float:
        """Calculate relevance score for an agent based on keyword matches."""
        matches = 0
        total_keywords = len(agent.keywords)
        
        for keyword in agent.keywords:
            if keyword in message:
                # Give higher weight to exact matches
                if f" {keyword} " in f" {message} ":
                    matches += 1.5
                else:
                    matches += 1
        
        # Normalize score
        score = min(matches / total_keywords, 1.0)
        
        # Boost score for multiple keyword matches
        if matches > 3:
            score *= 1.2
        
        return min(score, 1.0)
    
    def _analyze_conversation_context(self, message: str, context: List[Dict] = None) -> Dict[AgentRole, float]:
        """Analyze conversation context for additional routing signals."""
        context_scores = {role: 0.0 for role in AgentRole}
        
        if not context:
            return context_scores
        
        # Look at recent messages for context
        recent_messages = context[-5:] if len(context) > 5 else context
        
        for msg in recent_messages:
            if msg.get("role") == "assistant":
                # If we were recently using a specific agent, give it a small boost
                agent_mentioned = self._detect_agent_in_message(msg.get("content", ""))
                if agent_mentioned:
                    context_scores[agent_mentioned] += 0.1
        
        return context_scores
    
    def _detect_agent_in_message(self, message: str) -> Optional[AgentRole]:
        """Detect if a specific agent was mentioned in a message."""
        message_lower = message.lower()
        
        for role, agent in self.agents.items():
            if agent.name.lower() in message_lower:
                return role
            
        return None
    
    def _assess_complexity(self, message: str, context: List[Dict] = None) -> TaskComplexity:
        """Assess the complexity of the task based on message content."""
        message_lower = message.lower()
        
        # Multi-agent indicators
        multi_agent_keywords = [
            "comprehensive", "complete", "full", "detailed", "thorough", "analyze everything",
            "all aspects", "overall", "holistic", "across", "multiple", "various", "different"
        ]
        
        # Complex task indicators  
        complex_keywords = [
            "analyze", "compare", "evaluate", "assess", "research", "investigate",
            "plan", "strategy", "optimize", "improve", "solve", "complex", "detailed"
        ]
        
        # Simple task indicators
        simple_keywords = [
            "what", "how", "when", "where", "who", "quick", "simple", "basic", "just"
        ]
        
        multi_agent_score = sum(1 for keyword in multi_agent_keywords if keyword in message_lower)
        complex_score = sum(1 for keyword in complex_keywords if keyword in message_lower)
        simple_score = sum(1 for keyword in simple_keywords if keyword in message_lower)
        
        # Length-based complexity
        word_count = len(message.split())
        
        if multi_agent_score > 1 or word_count > 50:
            return TaskComplexity.MULTI_AGENT
        elif complex_score > simple_score and word_count > 20:
            return TaskComplexity.COMPLEX
        elif simple_score > 0 and word_count < 15:
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MODERATE
    
    def _generate_reasoning(
        self, 
        message: str, 
        primary_agent: AgentRole, 
        secondary_agents: List[AgentRole],
        confidence: float,
        complexity: TaskComplexity
    ) -> str:
        """Generate human-readable reasoning for the routing decision."""
        primary_name = self.agents[primary_agent].name
        
        reasoning_parts = [
            f"Selected {primary_name} as primary agent (confidence: {confidence:.2f})"
        ]
        
        # Add keyword-based reasoning
        matched_keywords = []
        message_lower = message.lower()
        for keyword in self.agents[primary_agent].keywords:
            if keyword in message_lower:
                matched_keywords.append(keyword)
        
        if matched_keywords:
            reasoning_parts.append(
                f"Keywords matched: {', '.join(matched_keywords[:3])}"
                + (f" (+{len(matched_keywords)-3} more)" if len(matched_keywords) > 3 else "")
            )
        
        # Add complexity reasoning
        reasoning_parts.append(f"Task complexity: {complexity.value}")
        
        # Add collaboration reasoning
        if secondary_agents:
            secondary_names = [self.agents[role].name for role in secondary_agents]
            reasoning_parts.append(
                f"Collaboration suggested with: {', '.join(secondary_names)}"
            )
        
        return " | ".join(reasoning_parts)
    
    def get_agent_info(self, role: AgentRole) -> AgentCapability:
        """Get detailed information about a specific agent."""
        return self.agents[role]
    
    def get_all_agents(self) -> Dict[AgentRole, AgentCapability]:
        """Get information about all available agents."""
        return self.agents
    
    def update_conversation_history(self, message: Dict):
        """Update the conversation history for context analysis."""
        self.conversation_history.append(message)
        
        # Keep only recent history to avoid memory bloat
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]


# Global router instance
_router = None

def get_agent_router() -> AgentRouter:
    """Get the global agent router instance."""
    global _router
    if _router is None:
        _router = AgentRouter()
    return _router


if __name__ == "__main__":
    # Test the agent router
    router = AgentRouter()
    
    test_messages = [
        "Help me organize my notes from last week's meetings",
        "What are the latest trends in artificial intelligence?",
        "Schedule a meeting with John for tomorrow at 2 PM",
        "Analyze my sleep patterns and suggest improvements",
        "How much did I spend on groceries this month?",
        "I need a comprehensive analysis of my life - health, finances, and productivity"
    ]
    
    print("Agent Router Test")
    print("=" * 50)
    
    for message in test_messages:
        decision = router.analyze_message(message)
        print(f"\nMessage: '{message}'")
        print(f"Primary Agent: {decision.primary_agent}")
        print(f"Confidence: {decision.confidence:.2f}")
        print(f"Complexity: {decision.complexity}")
        print(f"Reasoning: {decision.reasoning}")
        if decision.secondary_agents:
            print(f"Collaboration: {decision.secondary_agents}")
        print("-" * 50)