"""
MCP Prompts Provider

Provides pre-configured agent workflow prompts for common tasks.
Exposes 5 specialized agent personas with their workflows.

File: myndy_crewai_mcp/prompts_provider.py
"""

import logging
from typing import Any, Dict, List, Optional

from .schemas import (
    PromptDefinition,
    PromptArgument,
    PromptMessage,
    PromptResult,
)
from .config import MCPConfig

logger = logging.getLogger(__name__)


class PromptsProvider:
    """
    MCP Prompts Provider

    Provides pre-configured agent workflow prompts for common tasks.
    Each prompt represents a specialized agent persona with specific capabilities.
    """

    def __init__(self, config: MCPConfig):
        """Initialize prompts provider"""
        self.config = config
        self.prompts: Dict[str, PromptDefinition] = {}

        logger.info("Prompts Provider Initializing")

    async def initialize(self):
        """Initialize and register available prompts"""
        logger.info("Registering agent workflow prompts")

        # Register agent prompts
        self._register_personal_assistant_prompts()
        self._register_memory_librarian_prompts()
        self._register_research_specialist_prompts()
        self._register_health_analyst_prompts()
        self._register_finance_tracker_prompts()

        logger.info(f"Registered {len(self.prompts)} prompts")

    def _register_personal_assistant_prompts(self):
        """Register personal assistant agent prompts"""

        # Main personal assistant prompt
        self.prompts["personal_assistant"] = PromptDefinition(
            name="personal_assistant",
            description="Personal assistant for calendar, email, weather, and time management tasks",
            arguments=[
                PromptArgument(
                    name="task",
                    description="The task or query for the personal assistant (e.g., 'check my schedule', 'what's the weather')",
                    required=False
                ),
                PromptArgument(
                    name="context",
                    description="Additional context or details about the task",
                    required=False
                )
            ]
        )

        # Schedule management prompt
        self.prompts["schedule_management"] = PromptDefinition(
            name="schedule_management",
            description="Manage calendar events and schedule",
            arguments=[
                PromptArgument(
                    name="action",
                    description="Action to perform: 'view', 'add', 'update', or 'delete'",
                    required=True
                ),
                PromptArgument(
                    name="date",
                    description="Date for the schedule action (e.g., 'today', 'tomorrow', '2025-10-15')",
                    required=False
                )
            ]
        )

        # Time and timezone prompt
        self.prompts["time_query"] = PromptDefinition(
            name="time_query",
            description="Query current time in different timezones",
            arguments=[
                PromptArgument(
                    name="timezone",
                    description="Timezone to query (e.g., 'UTC', 'America/New_York', 'Asia/Tokyo')",
                    required=False
                )
            ]
        )

        logger.debug("Registered 3 personal assistant prompts")

    def _register_memory_librarian_prompts(self):
        """Register memory librarian agent prompts"""

        # Main memory librarian prompt
        self.prompts["memory_librarian"] = PromptDefinition(
            name="memory_librarian",
            description="Memory librarian for entity management, memory search, and knowledge organization",
            arguments=[
                PromptArgument(
                    name="query",
                    description="Memory query or task (e.g., 'find all people I know', 'remember this fact')",
                    required=False
                ),
                PromptArgument(
                    name="entity_type",
                    description="Type of entity: 'person', 'place', 'event', 'thing', etc.",
                    required=False
                )
            ]
        )

        # Memory search prompt
        self.prompts["memory_search"] = PromptDefinition(
            name="memory_search",
            description="Search through all memory entities",
            arguments=[
                PromptArgument(
                    name="query",
                    description="Search query or keywords",
                    required=True
                ),
                PromptArgument(
                    name="limit",
                    description="Maximum number of results to return",
                    required=False
                )
            ]
        )

        # Entity management prompt
        self.prompts["entity_management"] = PromptDefinition(
            name="entity_management",
            description="Manage memory entities (people, places, events, things)",
            arguments=[
                PromptArgument(
                    name="action",
                    description="Action: 'create', 'update', 'delete', or 'list'",
                    required=True
                ),
                PromptArgument(
                    name="entity_type",
                    description="Entity type: 'person', 'place', 'event', 'thing', 'movie', etc.",
                    required=True
                )
            ]
        )

        # Conversation analysis prompt
        self.prompts["conversation_analysis"] = PromptDefinition(
            name="conversation_analysis",
            description="Analyze conversations and extract insights",
            arguments=[
                PromptArgument(
                    name="text",
                    description="Conversation text to analyze",
                    required=True
                )
            ]
        )

        logger.debug("Registered 4 memory librarian prompts")

    def _register_research_specialist_prompts(self):
        """Register research specialist agent prompts"""

        # Main research specialist prompt
        self.prompts["research_specialist"] = PromptDefinition(
            name="research_specialist",
            description="Research specialist for information gathering, document analysis, and fact verification",
            arguments=[
                PromptArgument(
                    name="topic",
                    description="Research topic or question",
                    required=False
                ),
                PromptArgument(
                    name="depth",
                    description="Depth of research: 'quick', 'thorough', or 'comprehensive'",
                    required=False
                )
            ]
        )

        # Information gathering prompt
        self.prompts["information_gathering"] = PromptDefinition(
            name="information_gathering",
            description="Gather information on a specific topic",
            arguments=[
                PromptArgument(
                    name="topic",
                    description="Topic to research",
                    required=True
                ),
                PromptArgument(
                    name="sources",
                    description="Preferred information sources",
                    required=False
                )
            ]
        )

        # Document analysis prompt
        self.prompts["document_analysis"] = PromptDefinition(
            name="document_analysis",
            description="Analyze documents and extract key information",
            arguments=[
                PromptArgument(
                    name="document",
                    description="Document content or path to analyze",
                    required=True
                ),
                PromptArgument(
                    name="focus",
                    description="What to focus on in the analysis",
                    required=False
                )
            ]
        )

        logger.debug("Registered 3 research specialist prompts")

    def _register_health_analyst_prompts(self):
        """Register health analyst agent prompts"""

        # Main health analyst prompt
        self.prompts["health_analyst"] = PromptDefinition(
            name="health_analyst",
            description="Health analyst for health data analysis, wellness insights, and activity tracking",
            arguments=[
                PromptArgument(
                    name="query",
                    description="Health query or task (e.g., 'analyze my sleep', 'track my exercise')",
                    required=False
                ),
                PromptArgument(
                    name="metric",
                    description="Specific health metric to analyze",
                    required=False
                )
            ]
        )

        # Health metrics analysis prompt
        self.prompts["health_metrics"] = PromptDefinition(
            name="health_metrics",
            description="Analyze health metrics and provide insights",
            arguments=[
                PromptArgument(
                    name="metric_type",
                    description="Type of metric: 'activity', 'sleep', 'mood', 'weight', etc.",
                    required=False
                ),
                PromptArgument(
                    name="time_range",
                    description="Time range for analysis: 'today', 'week', 'month', 'year'",
                    required=False
                )
            ]
        )

        # Wellness insights prompt
        self.prompts["wellness_insights"] = PromptDefinition(
            name="wellness_insights",
            description="Generate wellness insights and recommendations",
            arguments=[
                PromptArgument(
                    name="focus_area",
                    description="Area to focus on: 'sleep', 'exercise', 'nutrition', 'stress', 'overall'",
                    required=False
                )
            ]
        )

        logger.debug("Registered 3 health analyst prompts")

    def _register_finance_tracker_prompts(self):
        """Register finance tracker agent prompts"""

        # Main finance tracker prompt
        self.prompts["finance_tracker"] = PromptDefinition(
            name="finance_tracker",
            description="Finance tracker for expense tracking, financial analysis, and budget management",
            arguments=[
                PromptArgument(
                    name="query",
                    description="Finance query or task (e.g., 'show my expenses', 'analyze spending')",
                    required=False
                ),
                PromptArgument(
                    name="category",
                    description="Expense category to focus on",
                    required=False
                )
            ]
        )

        # Expense tracking prompt
        self.prompts["expense_tracking"] = PromptDefinition(
            name="expense_tracking",
            description="Track and categorize expenses",
            arguments=[
                PromptArgument(
                    name="action",
                    description="Action: 'add', 'view', 'analyze', or 'categorize'",
                    required=True
                ),
                PromptArgument(
                    name="time_range",
                    description="Time range: 'today', 'week', 'month', 'year'",
                    required=False
                )
            ]
        )

        # Budget analysis prompt
        self.prompts["budget_analysis"] = PromptDefinition(
            name="budget_analysis",
            description="Analyze budget and spending patterns",
            arguments=[
                PromptArgument(
                    name="period",
                    description="Period to analyze: 'current', 'last_month', 'year_to_date'",
                    required=False
                )
            ]
        )

        logger.debug("Registered 3 finance tracker prompts")

    async def get_prompt(self, name: str, arguments: Optional[Dict[str, str]] = None) -> PromptResult:
        """Get a prompt with optional arguments"""
        logger.info(f"Getting prompt: {name}")

        if name not in self.prompts:
            raise ValueError(f"Prompt not found: {name}")

        prompt_def = self.prompts[name]
        args = arguments or {}

        # Build the prompt messages based on the prompt type
        messages = self._build_prompt_messages(name, prompt_def, args)

        return PromptResult(
            description=prompt_def.description,
            messages=messages
        )

    def _build_prompt_messages(
        self,
        name: str,
        prompt_def: PromptDefinition,
        args: Dict[str, str]
    ) -> List[PromptMessage]:
        """Build prompt messages based on prompt type and arguments"""

        # Get the agent category
        if name in ["personal_assistant", "schedule_management", "time_query"]:
            return self._build_personal_assistant_messages(name, args)
        elif name in ["memory_librarian", "memory_search", "entity_management", "conversation_analysis"]:
            return self._build_memory_librarian_messages(name, args)
        elif name in ["research_specialist", "information_gathering", "document_analysis"]:
            return self._build_research_specialist_messages(name, args)
        elif name in ["health_analyst", "health_metrics", "wellness_insights"]:
            return self._build_health_analyst_messages(name, args)
        elif name in ["finance_tracker", "expense_tracking", "budget_analysis"]:
            return self._build_finance_tracker_messages(name, args)
        else:
            # Generic prompt
            return self._build_generic_messages(name, prompt_def, args)

    def _build_personal_assistant_messages(self, name: str, args: Dict[str, str]) -> List[PromptMessage]:
        """Build personal assistant prompt messages"""
        messages = [
            PromptMessage(
                role="system",
                content="""You are a Personal Assistant AI specializing in calendar management, email handling,
weather updates, and time coordination. You have access to tools for:
- Managing calendar events and schedules
- Checking current time in any timezone
- Getting weather forecasts
- Handling email and communication tasks

Always be proactive, organized, and detail-oriented. When given a task, break it down into steps
and use the appropriate tools to complete it efficiently."""
            )
        ]

        if name == "schedule_management":
            action = args.get("action", "view")
            date = args.get("date", "today")
            messages.append(PromptMessage(
                role="user",
                content=f"I need to {action} my schedule for {date}. Please help me with this."
            ))
        elif name == "time_query":
            timezone = args.get("timezone", "UTC")
            messages.append(PromptMessage(
                role="user",
                content=f"What time is it in {timezone}?"
            ))
        else:  # personal_assistant
            task = args.get("task", "")
            context = args.get("context", "")
            if task:
                content = task
                if context:
                    content += f"\n\nAdditional context: {context}"
                messages.append(PromptMessage(role="user", content=content))

        return messages

    def _build_memory_librarian_messages(self, name: str, args: Dict[str, str]) -> List[PromptMessage]:
        """Build memory librarian prompt messages"""
        messages = [
            PromptMessage(
                role="system",
                content="""You are a Memory Librarian AI specializing in knowledge organization and entity management.
You have access to tools for:
- Searching and retrieving memory entities (people, places, events, things)
- Creating and updating entities in memory
- Analyzing conversations to extract entities and relationships
- Managing short-term and long-term memory

Always be thorough and precise in managing information. When searching memory, consider all relevant
entity types and relationships. When storing information, ensure proper categorization and linking."""
            )
        ]

        if name == "memory_search":
            query = args.get("query", "")
            limit = args.get("limit", "10")
            messages.append(PromptMessage(
                role="user",
                content=f"Search memory for: {query} (limit: {limit} results)"
            ))
        elif name == "entity_management":
            action = args.get("action", "list")
            entity_type = args.get("entity_type", "entity")
            messages.append(PromptMessage(
                role="user",
                content=f"I need to {action} {entity_type} entities. Please help me with this."
            ))
        elif name == "conversation_analysis":
            text = args.get("text", "")
            messages.append(PromptMessage(
                role="user",
                content=f"Analyze this conversation and extract key entities and insights:\n\n{text}"
            ))
        else:  # memory_librarian
            query = args.get("query", "")
            entity_type = args.get("entity_type", "")
            content = query or "Help me manage my memory and knowledge."
            if entity_type:
                content += f"\n\nFocus on {entity_type} entities."
            messages.append(PromptMessage(role="user", content=content))

        return messages

    def _build_research_specialist_messages(self, name: str, args: Dict[str, str]) -> List[PromptMessage]:
        """Build research specialist prompt messages"""
        messages = [
            PromptMessage(
                role="system",
                content="""You are a Research Specialist AI focused on information gathering, document analysis,
and fact verification. You have access to tools for:
- Searching knowledge bases and Wikipedia
- Analyzing documents and extracting key information
- Verifying facts and cross-referencing sources
- Synthesizing information from multiple sources

Always prioritize accuracy and cite sources when possible. Provide structured, well-organized research
results with clear conclusions and supporting evidence."""
            )
        ]

        if name == "information_gathering":
            topic = args.get("topic", "")
            sources = args.get("sources", "")
            content = f"Research this topic: {topic}"
            if sources:
                content += f"\n\nPreferred sources: {sources}"
            messages.append(PromptMessage(role="user", content=content))
        elif name == "document_analysis":
            document = args.get("document", "")
            focus = args.get("focus", "")
            content = f"Analyze this document:\n\n{document}"
            if focus:
                content += f"\n\nFocus on: {focus}"
            messages.append(PromptMessage(role="user", content=content))
        else:  # research_specialist
            topic = args.get("topic", "")
            depth = args.get("depth", "thorough")
            content = topic or "Help me research a topic."
            content += f"\n\nResearch depth: {depth}"
            messages.append(PromptMessage(role="user", content=content))

        return messages

    def _build_health_analyst_messages(self, name: str, args: Dict[str, str]) -> List[PromptMessage]:
        """Build health analyst prompt messages"""
        messages = [
            PromptMessage(
                role="system",
                content="""You are a Health Analyst AI specializing in health data analysis and wellness insights.
You have access to tools for:
- Tracking and analyzing health metrics (activity, sleep, mood, etc.)
- Managing health status entries
- Generating wellness insights and recommendations
- Analyzing trends and patterns in health data

Always respect user privacy and provide evidence-based insights. When making recommendations,
consider individual context and avoid medical advice."""
            )
        ]

        if name == "health_metrics":
            metric_type = args.get("metric_type", "overall")
            time_range = args.get("time_range", "week")
            messages.append(PromptMessage(
                role="user",
                content=f"Analyze my {metric_type} metrics for the past {time_range}."
            ))
        elif name == "wellness_insights":
            focus_area = args.get("focus_area", "overall")
            messages.append(PromptMessage(
                role="user",
                content=f"Provide wellness insights focused on {focus_area}."
            ))
        else:  # health_analyst
            query = args.get("query", "")
            metric = args.get("metric", "")
            content = query or "Help me analyze my health data."
            if metric:
                content += f"\n\nSpecific metric: {metric}"
            messages.append(PromptMessage(role="user", content=content))

        return messages

    def _build_finance_tracker_messages(self, name: str, args: Dict[str, str]) -> List[PromptMessage]:
        """Build finance tracker prompt messages"""
        messages = [
            PromptMessage(
                role="system",
                content="""You are a Finance Tracker AI specializing in expense tracking and budget management.
You have access to tools for:
- Tracking expenses and income
- Categorizing transactions
- Analyzing spending patterns
- Managing budgets and financial goals

Always maintain financial data accuracy and provide actionable insights. When analyzing spending,
identify trends and suggest optimizations."""
            )
        ]

        if name == "expense_tracking":
            action = args.get("action", "view")
            time_range = args.get("time_range", "month")
            messages.append(PromptMessage(
                role="user",
                content=f"I need to {action} my expenses for the past {time_range}."
            ))
        elif name == "budget_analysis":
            period = args.get("period", "current")
            messages.append(PromptMessage(
                role="user",
                content=f"Analyze my budget for the {period} period."
            ))
        else:  # finance_tracker
            query = args.get("query", "")
            category = args.get("category", "")
            content = query or "Help me track my finances."
            if category:
                content += f"\n\nFocus on category: {category}"
            messages.append(PromptMessage(role="user", content=content))

        return messages

    def _build_generic_messages(
        self,
        name: str,
        prompt_def: PromptDefinition,
        args: Dict[str, str]
    ) -> List[PromptMessage]:
        """Build generic prompt messages"""
        messages = [
            PromptMessage(
                role="system",
                content=f"You are an AI assistant. {prompt_def.description}"
            )
        ]

        if args:
            content = "\n".join([f"{k}: {v}" for k, v in args.items()])
            messages.append(PromptMessage(role="user", content=content))

        return messages

    def get_prompt_definitions(self) -> List[PromptDefinition]:
        """Get all registered prompt definitions"""
        return list(self.prompts.values())

    def get_prompt_by_name(self, name: str) -> Optional[PromptDefinition]:
        """Get a specific prompt definition by name"""
        return self.prompts.get(name)

    def get_prompt_count(self) -> int:
        """Get the number of registered prompts"""
        return len(self.prompts)

    def get_prompts_by_category(self) -> Dict[str, List[str]]:
        """Get prompts organized by category"""
        categories = {
            "Personal Assistant": ["personal_assistant", "schedule_management", "time_query"],
            "Memory Librarian": ["memory_librarian", "memory_search", "entity_management", "conversation_analysis"],
            "Research Specialist": ["research_specialist", "information_gathering", "document_analysis"],
            "Health Analyst": ["health_analyst", "health_metrics", "wellness_insights"],
            "Finance Tracker": ["finance_tracker", "expense_tracking", "budget_analysis"]
        }

        return {
            category: [p for p in prompts if p in self.prompts]
            for category, prompts in categories.items()
        }


# ============================================================================
# Utility Functions
# ============================================================================

async def create_prompts_provider(config: MCPConfig) -> PromptsProvider:
    """Create and initialize a prompts provider"""
    provider = PromptsProvider(config)
    await provider.initialize()
    return provider
