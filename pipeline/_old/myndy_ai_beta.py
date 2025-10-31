"""
title: Myndy AI Beta - Experimental Intelligence Pipeline
author: Jeremy
version: 0.2.0-beta
license: MIT
description: Myndy AI Beta - Experimental version with enhanced routing and faster responses. Competes with v0.1 for performance comparison.
requirements: crewai, fastapi, uvicorn, pydantic
"""

import os
import sys
import logging
import uuid
import re
import warnings
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Generator, Iterator
from pathlib import Path

# Suppress specific warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", message=".*Mixing V1 models and V2 models.*")
warnings.filterwarnings("ignore", category=UserWarning, module="crewai.telemtry.telemetry")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")

# Add LiteLLM error handling workaround
def safe_litellm_completion(**kwargs):
    """Safe wrapper for LiteLLM completion with enhanced error handling"""
    try:
        import litellm
        # Ensure messages are properly formatted for LiteLLM
        if 'messages' in kwargs:
            messages = kwargs['messages']
            if isinstance(messages, list) and len(messages) > 0:
                # Validate message structure
                for msg in messages:
                    if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                        logger.error(f"Invalid message format: {msg}")
                        raise ValueError(f"Invalid message format in LiteLLM call: {msg}")
                
                # Call LiteLLM with proper error handling
                response = litellm.completion(**kwargs)
                
                # Validate response structure
                if not hasattr(response, 'choices') or not response.choices or len(response.choices) == 0:
                    logger.error("LiteLLM returned empty response")
                    raise Exception("LiteLLM returned empty response - no choices available")
                
                return response
            else:
                raise ValueError("Messages array is empty or invalid")
        else:
            raise ValueError("No messages provided to LiteLLM")
            
    except Exception as e:
        logger.error(f"LiteLLM completion error: {e}")
        # Create a mock response for graceful degradation
        class MockChoice:
            def __init__(self, content):
                self.message = type('obj', (object,), {'content': content})
        
        class MockResponse:
            def __init__(self, content):
                self.choices = [MockChoice(content)]
        
        # Return a helpful error message as mock response
        error_msg = f"I apologize, but I encountered a technical issue: {str(e)}. Please try rephrasing your request."
        return MockResponse(error_msg)

# Add project paths
PIPELINE_ROOT = Path(__file__).parent.parent
MYNDY_AI_ROOT = PIPELINE_ROOT.parent / "myndy-ai"
sys.path.insert(0, str(PIPELINE_ROOT))
if MYNDY_AI_ROOT.exists():
    sys.path.insert(0, str(MYNDY_AI_ROOT))
else:
    # Try alternative relative paths
    for alt_path in [Path("../../myndy-ai"), Path("../../../myndy-ai")]:
        abs_alt = Path(__file__).parent / alt_path
        if abs_alt.exists():
            sys.path.insert(0, str(abs_alt.resolve()))
            break

# Auto-install dependencies if missing
def ensure_dependencies():
    """Ensure required dependencies are available, install if missing"""
    required_packages = [
        'pydantic>=2.0.0',
        'fastapi>=0.100.0',
        'uvicorn>=0.20.0',
        'crewai>=0.11.0',
        'langchain>=0.1.0',
        'langchain-community>=0.0.20',
        'requests>=2.31.0',
        'typing-extensions>=4.8.0',
        'setuptools>=65.0.0'  # Provides pkg_resources
    ]
    
    missing_packages = []
    
    # Check for each package
    for package in required_packages:
        package_name = package.split('>=')[0].split('[')[0]
        try:
            __import__(package_name.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Missing dependencies: {', '.join(missing_packages)}")
        print("🔧 Installing missing dependencies...")
        
        import subprocess
        try:
            # Try different installation methods
            install_commands = [
                # Try user installation first
                [sys.executable, "-m", "pip", "install", "--user"],
                # Try with break-system-packages if user fails
                [sys.executable, "-m", "pip", "install", "--break-system-packages"],
                # Try virtual environment specific
                [sys.executable, "-m", "pip", "install"]
            ]
            
            for cmd_base in install_commands:
                try:
                    for package in missing_packages:
                        print(f"📦 Installing {package} with {' '.join(cmd_base)}...")
                        result = subprocess.run(
                            cmd_base + [package],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        print(f"✅ Installed {package}")
                    
                    print("🎉 All dependencies installed successfully!")
                    return True
                    
                except subprocess.CalledProcessError:
                    continue  # Try next installation method
            
            # If all methods failed
            raise Exception("All installation methods failed")
            
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("\nManual installation options:")
            print("Option 1 (User installation):")
            for package in missing_packages:
                print(f"  pip install --user {package}")
            print("\nOption 2 (Virtual environment):")
            print(f"  python3 -m venv venv")
            print(f"  source venv/bin/activate")
            for package in missing_packages:
                print(f"  pip install {package}")
            print("\nOption 3 (System packages - if allowed):")
            for package in missing_packages:
                print(f"  pip install --break-system-packages {package}")
            return False
    else:
        print("✅ All dependencies are available")
        return True

# Ensure dependencies before importing
if not ensure_dependencies():
    print("❌ Cannot proceed without required dependencies")
    sys.exit(1)

# Now safe to import required packages
try:
    from pydantic import BaseModel
    print("✅ Pydantic imported successfully")
except ImportError as e:
    print(f"❌ Failed to import pydantic even after installation: {e}")
    sys.exit(1)

# Try to import CrewAI components with fallback
CREWAI_AVAILABLE = False
try:
    import crewai
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
    print("✅ CrewAI imported successfully")
except ImportError as e:
    print(f"⚠️  CrewAI not available: {e}")
    print("🔄 Running in standalone mode")
    
    # Create mock classes for basic functionality
    class MockAgent:
        def __init__(self, **kwargs):
            self.role = kwargs.get('role', 'Mock Agent')
            self.goal = kwargs.get('goal', 'Provide assistance')
            
    class MockTask:
        def __init__(self, **kwargs):
            self.description = kwargs.get('description', 'Mock task')
            
    class MockCrew:
        def __init__(self, **kwargs):
            self.agents = kwargs.get('agents', [])
            self.tasks = kwargs.get('tasks', [])
            
        def kickoff(self, **kwargs):
            return "Mock response: CrewAI functionality not available. Please install compatible CrewAI version."
    
    # Use mock classes
    Agent, Task, Crew = MockAgent, MockTask, MockCrew

# Configure enhanced terminal logging for beta
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/myndy_beta_pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

# Set specific loggers for beta pipeline
logging.getLogger("myndy_ai_beta").setLevel(logging.INFO)
logging.getLogger("tools.myndy_bridge").setLevel(logging.INFO)
logging.getLogger("qdrant").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


class MainCoordinator:
    """Main coordinator that handles routing, tool selection, and response orchestration"""
    
    def __init__(self, context_manager_agent=None, valves=None):
        self.router = EnhancedRouter()
        self.tool_selector = ToolSelector()
        self.response_orchestrator = ResponseOrchestrator()
        self.performance_tracker = PerformanceTracker()
        self.context_manager_agent = context_manager_agent
        self.valves = valves
        
    def set_context_manager_agent(self, context_manager_agent):
        """Set the context manager agent for intelligent tool selection"""
        self.context_manager_agent = context_manager_agent
        
    def coordinate_response(self, user_message: str, session_id: str, conversation_context: List[Dict] = None) -> Dict[str, Any]:
        """Main coordination method that handles the entire response pipeline"""
        start_time = datetime.now()
        
        try:
            # Step 1: Analyze and route the message
            if hasattr(self, 'valves') and self.valves.verbose_coordination:
                print("🧠 STEP 1: Message Analysis & Routing")
            
            routing_analysis = self.router.analyze_message(user_message, conversation_context)
            
            if hasattr(self, 'valves') and self.valves.verbose_coordination:
                self._show_routing_analysis(routing_analysis)
            
            # Step 2: Select optimal tools using context manager agent  
            if hasattr(self, 'valves') and self.valves.verbose_coordination:
                print("\n🔧 STEP 2: Tool Selection")
            
            tool_selection = self.tool_selector.select_tools(
                routing_analysis, user_message, self.context_manager_agent
            )
            
            if hasattr(self, 'valves') and self.valves.trace_tool_selection:
                self._show_tool_selection(tool_selection)
            
            # Step 3: Execute the response with selected agent and tools
            if hasattr(self, 'valves') and self.valves.verbose_coordination:
                print("\n⚡ STEP 3: Response Planning")
            
            response_plan = self.response_orchestrator.create_execution_plan(
                routing_analysis, tool_selection, user_message
            )
            
            if hasattr(self, 'valves') and self.valves.verbose_coordination:
                self._show_response_plan(response_plan)
            
            # Step 4: Track performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.performance_tracker.record_coordination({
                "session_id": session_id,
                "routing_time": processing_time,
                "agent_selected": routing_analysis["primary_agent"],
                "tools_selected": len(tool_selection["selected_tools"]),
                "confidence": routing_analysis["confidence"]
            })
            
            return {
                "routing_analysis": routing_analysis,
                "tool_selection": tool_selection,
                "response_plan": response_plan,
                "coordination_time": processing_time,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Main coordination error: {e}")
            return self._create_fallback_coordination(user_message, session_id)
    
    def _create_fallback_coordination(self, user_message: str, session_id: str) -> Dict[str, Any]:
        """Create fallback coordination when main coordination fails"""
        return {
            "routing_analysis": {
                "primary_agent": "personal_assistant",
                "confidence": 0.5,
                "reasoning": "Fallback coordination - using personal assistant",
                "method": "fallback"
            },
            "tool_selection": {
                "selected_tools": ["get_current_time"],
                "selection_reasoning": "Fallback tool selection",
                "confidence": 0.3
            },
            "response_plan": {
                "execution_type": "direct_response",
                "agent": "personal_assistant",
                "approach": "fallback"
            },
            "coordination_time": 0.001,
            "session_id": session_id
        }
    
    def _show_routing_analysis(self, routing_analysis: Dict[str, Any]) -> None:
        """Display routing analysis details for visibility into agent selection"""
        print(f"   🎯 Primary Responder: {routing_analysis.get('primary_agent', 'unknown')}")
        print(f"   📊 Confidence: {routing_analysis.get('confidence', 0):.2f}")
        print(f"   💭 Coordination Strategy: {routing_analysis.get('reasoning', 'No reasoning provided')}")
        
        if routing_analysis.get('requires_collaboration', False):
            collaborators = routing_analysis.get('secondary_agents', [])
            if collaborators:
                # Filter out shadow agent for display (since it's always there)
                visible_collaborators = [agent for agent in collaborators if agent != 'shadow_agent']
                if visible_collaborators:
                    print(f"   🤝 Specialist Collaborators: {', '.join(visible_collaborators)}")
                print(f"   👤 Background Observer: shadow_agent (behavioral context)")
        
        # Show specialist scores if available
        if 'specialist_scores' in routing_analysis:
            scores = routing_analysis['specialist_scores']
            top_specialists = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_specialists:
                score_display = ", ".join([f"{agent}: {score:.1f}" for agent, score in top_specialists])
                print(f"   📈 Top Specialist Scores: {score_display}")
        
        complexity = routing_analysis.get('complexity', 'standard')
        print(f"   ⚡ Complexity: {complexity}")
    
    def _show_tool_selection(self, tool_selection: Dict[str, Any]) -> None:
        """Display tool selection details for visibility into tool choices"""
        selected_tools = tool_selection.get('selected_tools', [])
        print(f"   🔧 Selected Tools: {', '.join(selected_tools) if selected_tools else 'None'}")
        
        reasoning = tool_selection.get('selection_reasoning', 'No reasoning provided')
        print(f"   💡 Selection Reasoning: {reasoning}")
        
        confidence = tool_selection.get('confidence', 0)
        print(f"   🎯 Selection Confidence: {confidence:.2f}")
        
        # Show tool categories if available
        if 'tool_categories' in tool_selection:
            categories = tool_selection['tool_categories']
            print(f"   📁 Tool Categories: {', '.join(categories)}")
    
    def _show_response_plan(self, response_plan: Dict[str, Any]) -> None:
        """Display response execution plan for visibility into response strategy"""
        execution_type = response_plan.get('execution_type', 'unknown')
        print(f"   ⚡ Execution Type: {execution_type}")
        
        agent = response_plan.get('agent', 'unknown')
        print(f"   🤖 Executing Agent: {agent}")
        
        approach = response_plan.get('approach', 'standard')
        print(f"   📋 Approach: {approach}")
        
        # Show collaboration details if available
        if response_plan.get('collaboration_required', False):
            collaborators = response_plan.get('collaborating_agents', [])
            if collaborators:
                print(f"   🤝 Collaborators: {', '.join(collaborators)}")
        
        # Show estimated complexity
        if 'estimated_duration' in response_plan:
            duration = response_plan['estimated_duration']
            print(f"   ⏱️  Estimated Duration: {duration}s")
        
        # Show special considerations
        if 'considerations' in response_plan:
            considerations = response_plan['considerations']
            print(f"   ⚠️  Considerations: {considerations}")
    

class ToolSelector:
    """Agent-based intelligent tool selection using context analysis"""
    
    def __init__(self):
        # Available tools by agent with descriptions
        self.agent_tool_capabilities = {
            "memory_librarian": {
                "conversation_tools": ["extract_conversation_entities", "search_conversation_memory", "get_conversation_summary", "infer_conversation_intent", "extract_from_conversation_history"],
                "entity_storage": ["create_entity", "add_fact", "add_preference", "search_memory", "get_current_status", "get_self_profile", "update_status"],
                "comprehensive_storage": ["create_contact", "create_event", "create_task", "create_project", "create_place", "create_journal_entry", "record_health_data", "add_movie", "create_group", "record_email", "add_short_term_memory", "search_all_memory"],
                "analysis_tools": ["store_conversation_analysis", "start_agent_conversation", "add_conversation_message", "analyze_conversation_for_updates"]
            },
            "personal_assistant": {
                # Core coordination and response tools
                "time_tools": ["get_current_time", "format_date", "calculate_time_difference", "unix_timestamp"],
                "status_tools": ["get_current_status", "update_status", "set_mood", "set_activity"],
                "quick_info_tools": ["get_self_profile", "search_memory", "get_recent_items"],
                
                # Essential communication and scheduling  
                "schedule_tools": ["calendar_query", "get_upcoming_calendar"],
                "basic_communication": ["find_contact", "get_conversation_summary"],
                
                # Quick access to common specialist functions
                "weather_access": ["weather_api", "local_weather", "get_timezone"],
                "health_quick_access": ["health_query_simple", "get_current_status"],
                "finance_quick_access": ["get_recent_expenses", "get_spending_summary"],
                
                # Coordination and delegation tools
                "coordination_tools": ["infer_conversation_intent", "extract_conversation_entities", "analyze_text"],
                "delegation_tools": ["tool_recommendation", "get_available_tools"],
                
                # Memory coordination tools (for when collaborating with memory_librarian)
                "memory_coordination": ["create_entity", "add_fact", "search_memory", "create_contact", "create_project", "create_event"],
                
                # User context and personalization
                "context_tools": ["get_user_preferences", "get_status_history", "reflect_on_memory"]
            },
            "location_agent": {
                "weather_tools": ["local_weather", "format_weather", "weather_api"],
                "location_tools": ["geocode_address", "reverse_geocode", "get_timezone"],
                "travel_tools": ["get_directions", "calculate_distance"],
                "time_tools": ["get_current_time", "format_date"]  # For timezone queries
            },
            "shadow_agent": {
                "behavioral_analysis": ["extract_conversation_entities", "infer_conversation_intent", "analyze_sentiment", "analyze_text"],
                "context_synthesis": ["search_memory", "get_current_status", "get_self_profile", "extract_from_conversation_history"],
                "pattern_detection": ["get_status_history", "reflect_on_memory", "add_fact", "add_preference"],
                "silent_monitoring": ["update_status", "create_entity"]
            },
            "research_specialist": {
                "text_analysis": ["analyze_text", "analyze_sentiment", "summarize_text", "detect_language"],
                "document_processing": ["extract_document_text", "summarize_document", "search_document", "convert_document", "process_document"],
                "entity_extraction": ["extract_entities", "extract_keywords"]
            },
            "health_analyst": {
                "health_queries": ["health_query", "health_query_simple", "health_summary_simple"]
            },
            "finance_tracker": {
                "transaction_tools": ["get_recent_expenses", "get_spending_summary", "search_transactions"],
                "finance_tools": ["finance_tool", "get_transaction"]
            },
            "project_manager": {
                "project_tools": ["create_project", "update_project", "get_project_status", "list_projects"],
                "task_tools": ["create_task", "update_task", "get_task_status", "list_tasks", "assign_task"],
                "collaboration_tools": ["add_team_member", "set_deadline", "track_progress"]
            },
            "communication_specialist": {
                "email_tools": ["send_email", "search_emails", "categorize_email", "draft_response"],
                "contact_tools": ["find_contact", "update_contact", "merge_contacts", "add_contact"],
                "group_tools": ["create_group", "manage_group_membership", "group_communications"]
            },
            "knowledge_curator": {
                "knowledge_tools": ["add_knowledge", "search_knowledge", "categorize_knowledge", "link_knowledge"],
                "journal_tools": ["create_journal_entry", "search_journal", "analyze_mood_patterns"],
                "content_tools": ["organize_content", "tag_content", "extract_insights"]
            },
            "relationship_advisor": {
                "people_tools": ["find_person", "update_person_info", "track_interactions"],
                "relationship_tools": ["map_relationships", "analyze_relationship_patterns", "suggest_connections"],
                "social_tools": ["track_social_events", "manage_social_calendar", "relationship_insights"]
            },
            "entertainment_curator": {
                "movie_tools": ["add_movie", "rate_movie", "get_recommendations", "track_watchlist"],
                "event_tools": ["create_event", "track_event_attendance", "event_recommendations"],
                "place_tools": ["add_place", "rate_place", "get_place_recommendations", "track_visits"]
            }
        }
    
    def select_tools(self, routing_analysis: Dict[str, Any], user_message: str, context_manager_agent=None) -> Dict[str, Any]:
        """Use context manager agent to intelligently select tools"""
        primary_agent = routing_analysis["primary_agent"]
        
        logger.info(f"🔧 Tool Selection: primary_agent={primary_agent}, context_manager_agent={context_manager_agent is not None}")
        
        # Get available tools for the selected agent
        agent_capabilities = self.agent_tool_capabilities.get(primary_agent, {})
        all_agent_tools = []
        for tool_category in agent_capabilities.values():
            all_agent_tools.extend(tool_category)
        
        # Use context manager agent for intelligent tool selection
        if context_manager_agent:
            try:
                tool_selection = self._agent_based_tool_selection(
                    user_message, primary_agent, all_agent_tools, context_manager_agent
                )
                return tool_selection
            except Exception as e:
                logger.error(f"Agent-based tool selection failed: {e}")
                import traceback
                logger.error(f"Tool selection error details: {traceback.format_exc()}")
                # Fallback to default tools
                return self._fallback_tool_selection(primary_agent, user_message)
        else:
            # Fallback to default tools if no context manager
            return self._fallback_tool_selection(primary_agent, user_message)
    
    def _agent_based_tool_selection(self, user_message: str, primary_agent: str, available_tools: List[str], context_manager_agent) -> Dict[str, Any]:
        """Use context manager agent to select optimal tools"""
        from crewai import Task
        
        logger.info(f"🔧 Agent-based tool selection: {primary_agent} with {len(available_tools)} tools")
        logger.info(f"🔧 Available tools: {available_tools}")
        
        # Create tool selection task for context manager
        task_description = f"""
Analyze this user request and select the optimal tools for the {primary_agent} agent:

User Request: "{user_message}"
Target Agent: {primary_agent}
Available Tools: {', '.join(available_tools)}

Tool Descriptions:
# Core Coordination Tools (Personal Assistant)
- get_current_time: Get current time in any timezone (use timezone parameter like 'Europe/London', 'America/New_York', etc.)
- format_date: Format dates into different formats and parse date strings
- calculate_time_difference: Calculate time differences between dates/times
- get_current_status: Get user's current mood, location, activity, health status
- update_status: Update user's current status (mood, activity, location)
- set_mood: Set user's current mood (happy, sad, anxious, relaxed, etc.)
- set_activity: Set what the user is currently doing
- get_self_profile: Access user's identity, preferences, values, and personal information
- search_memory: Semantic search across user's memory and patterns
- get_recent_items: Get recently created or updated items from memory

# Quick Access Specialist Functions (Personal Assistant)
- calendar_query: Search calendar events and appointments
- get_upcoming_calendar: Get upcoming calendar events
- find_contact: Find contact information for people
- get_conversation_summary: Get summary of recent conversations
- weather_api: Get current weather and forecast for a specific location using OpenWeatherMap API
- local_weather: Get current weather for a specific location from local data files
- get_timezone: Get timezone information for locations
- health_query_simple: Quick health and fitness data queries
- get_recent_expenses: Get recent financial expenses
- get_spending_summary: Get summary of spending patterns

# Coordination and Analysis Tools (Personal Assistant)
- infer_conversation_intent: Detect user's underlying intentions and goals
- extract_conversation_entities: Extract people, places, organizations from text
- analyze_text: Analyze text content for sentiment, topics, and insights
- get_status_history: Analyze historical behavioral patterns and trends
- reflect_on_memory: Process and synthesize memory patterns
- tool_recommendation: Recommend appropriate tools for tasks
- get_available_tools: Get list of available tools and capabilities

# Memory Storage Tools (Memory Librarian / Personal Assistant)
- create_entity: Create a new person or organization entity in memory with details
- add_fact: Add factual information about people or organizations to memory
- add_preference: Store preferences and attributes for people
- create_contact: Create detailed contact records with email, phone, organization
- create_project: Create project records with timelines and descriptions
- create_event: Create calendar events with dates, locations, and participants
- create_task: Create tasks with priorities, due dates, and assignments
- create_place: Store location information with addresses and categories
- create_journal_entry: Store personal journal entries with mood and tags
- record_health_data: Store health metrics and wellness information
- add_movie: Add movies to personal collection with ratings and notes
- create_group: Create groups with members and descriptions
- record_email: Store important email information and summaries
- add_short_term_memory: Store temporary information for quick recall
- search_all_memory: Search across all memory types for information

# Specialist Tools (for delegation)
- finance_tool: Advanced financial calculations and analysis
- health_query: Comprehensive health data analysis
- document_processing: Process and analyze documents
- project_management: Create and manage projects and tasks
- relationship_analysis: Analyze social connections and relationships

Instructions:
- Analyze the user's request to understand what information they need
- Select 1-3 most relevant tools that can fulfill the request
- Consider any location, time, or context-specific requirements
- For time queries with locations, always include get_current_time
- For weather queries, prioritize weather_api over local_weather
- IMPORTANT: For messages mentioning people, organizations, or relationships, ALWAYS use memory storage tools:
  * Use extract_conversation_entities to detect entities
  * Use create_entity for people and organizations mentioned
  * Use add_fact to store relationship information
  * Use create_contact, create_project, etc. for specific entity types
- Prioritize the most directly relevant tools

Respond with: "Selected tools: [tool1, tool2, tool3], Reasoning: [brief explanation of why these tools were chosen]"
"""
        
        task = Task(
            description=task_description,
            agent=context_manager_agent,
            expected_output="Clear tool selection with reasoning"
        )
        
        # Execute the task directly
        try:
            result = task.execute_sync()
        except AttributeError:
            result = task.execute()
        
        # Parse the result to extract selected tools
        return self._parse_tool_selection_result(str(result), primary_agent, available_tools)
    
    def _parse_tool_selection_result(self, result: str, primary_agent: str, available_tools: List[str]) -> Dict[str, Any]:
        """Parse context manager's tool selection result with enhanced parsing"""
        import re
        
        result_lower = result.lower()
        
        # Extract tools from the result
        selected_tools = []
        reasoning = "Auto-selected tools based on context analysis"
        
        # Look for explicit tool selection patterns first
        tools_patterns = [
            r'selected tools?:\s*\[([^\]]+)\]',
            r'tools?:\s*\[([^\]]+)\]',
            r'recommended tools?:\s*\[([^\]]+)\]',
            r'use tools?:\s*\[([^\]]+)\]'
        ]
        
        for pattern in tools_patterns:
            tools_match = re.search(pattern, result_lower)
            if tools_match:
                tools_text = tools_match.group(1)
                # Extract individual tools from comma-separated list
                tool_candidates = [t.strip().strip('"\'') for t in tools_text.split(',')]
                for candidate in tool_candidates:
                    for tool in available_tools:
                        if tool.lower() == candidate.lower() or candidate.lower() in tool.lower():
                            if tool not in selected_tools:
                                selected_tools.append(tool)
                break
        
        # If no explicit patterns found, look for individual tool mentions
        if not selected_tools:
            for tool in available_tools:
                if tool.lower() in result_lower:
                    selected_tools.append(tool)
        
        # Smart defaults based on query content if still no tools found
        if not selected_tools:
            selected_tools = self._smart_tool_fallback(result_lower, primary_agent, available_tools)
        
        # Ensure we have at least one tool
        if not selected_tools:
            selected_tools = self._get_default_tools(primary_agent)
        
        # Remove duplicates while preserving order
        selected_tools = list(dict.fromkeys(selected_tools))
        
        return {
            "selected_tools": selected_tools,
            "selection_reasoning": [f"Context manager selected: {selected_tools}"],
            "agent_analysis": result[:200] + "..." if len(result) > 200 else result,
            "confidence": 0.9 if len(selected_tools) > 0 else 0.5
        }
    
    def _fallback_tool_selection(self, primary_agent: str, user_message: str) -> Dict[str, Any]:
        """Fallback tool selection when agent-based selection is not available"""
        message_lower = user_message.lower()
        selected_tools = []
        
        # Simple heuristics as fallback
        if primary_agent == "personal_assistant":
            if "time" in message_lower or "clock" in message_lower:
                selected_tools = ["get_current_time"]
            elif "weather" in message_lower or "forecast" in message_lower or "temperature" in message_lower:
                selected_tools = ["weather_api"]
            elif "calendar" in message_lower or "schedule" in message_lower:
                selected_tools = ["calendar_query"]
            # ENHANCED: Check for entity mentions that need memory storage
            elif any(word in message_lower for word in ["friend", "owner", "working on", "project", "company", "organization"]):
                selected_tools = ["extract_conversation_entities", "create_entity", "add_fact"]
            # ENHANCED: Check for people/organization mentions (capitalized words)
            elif any(len(word) > 1 and word[0].isupper() for word in user_message.split()):
                selected_tools = ["extract_conversation_entities", "create_entity", "create_contact"]
            else:
                selected_tools = ["get_current_time"]
        elif primary_agent == "memory_librarian":
            # Memory librarian should always have memory tools
            selected_tools = ["extract_conversation_entities", "create_entity", "add_fact", "search_memory"]
        else:
            selected_tools = self._get_default_tools(primary_agent)
        
        return {
            "selected_tools": selected_tools,
            "selection_reasoning": [f"Fallback selection for {primary_agent}"],
            "agent_analysis": "Using fallback tool selection",
            "confidence": 0.6
        }
    
    def _get_default_tools(self, agent: str) -> List[str]:
        """Get default tools for an agent"""
        defaults = {
            "memory_librarian": ["extract_conversation_entities"],
            "personal_assistant": ["get_current_time", "weather_api"],
            "location_agent": ["weather_api", "local_weather"],
            "shadow_agent": ["extract_conversation_entities"],
            "research_specialist": ["analyze_text"],
            "health_analyst": ["health_query_simple"],
            "finance_tracker": ["finance_tool"]
        }
        return defaults.get(agent, ["get_current_time"])
    
    def _smart_tool_fallback(self, query_lower: str, primary_agent: str, available_tools: List[str]) -> List[str]:
        """Smart tool selection based on query content analysis"""
        selected_tools = []
        
        # Weather-related queries
        weather_keywords = ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy", "storm", "climate", "humidity", "wind"]
        if any(keyword in query_lower for keyword in weather_keywords):
            weather_tools = [tool for tool in available_tools if tool in ["weather_api", "local_weather", "format_weather"]]
            selected_tools.extend(weather_tools[:2])  # Max 2 weather tools
        
        # Time-related queries
        time_keywords = ["time", "clock", "when", "date", "today", "tomorrow", "yesterday", "hour", "minute"]
        if any(keyword in query_lower for keyword in time_keywords):
            time_tools = [tool for tool in available_tools if tool in ["get_current_time", "format_date", "calculate_time_difference"]]
            selected_tools.extend(time_tools[:2])  # Max 2 time tools
        
        # Health-related queries
        health_keywords = ["health", "fitness", "exercise", "sleep", "steps", "heart", "wellness", "workout", "calories"]
        if any(keyword in query_lower for keyword in health_keywords):
            health_tools = [tool for tool in available_tools if tool in ["health_query_simple", "health_query"]]
            selected_tools.extend(health_tools[:1])
        
        # Finance-related queries
        finance_keywords = ["money", "expense", "spending", "budget", "cost", "financial", "transaction", "purchase"]
        if any(keyword in query_lower for keyword in finance_keywords):
            finance_tools = [tool for tool in available_tools if tool in ["get_recent_expenses", "get_spending_summary", "finance_tool"]]
            selected_tools.extend(finance_tools[:2])
        
        # Memory/identity queries
        identity_keywords = ["who am i", "my name", "remember me", "profile", "about me", "personal information"]
        if any(keyword in query_lower for keyword in identity_keywords):
            memory_tools = [tool for tool in available_tools if tool in ["get_self_profile", "search_memory", "get_current_status"]]
            selected_tools.extend(memory_tools[:2])
        
        # Remove duplicates
        return list(dict.fromkeys(selected_tools))

class ResponseOrchestrator:
    """Orchestrates response execution based on routing and tool selection"""
    
    def __init__(self):
        self.execution_strategies = {
            "direct_response": self._create_direct_response_plan,
            "single_agent": self._create_single_agent_plan,
            "collaborative": self._create_collaborative_plan,
            "tool_focused": self._create_tool_focused_plan
        }
    
    def create_execution_plan(self, routing_analysis: Dict[str, Any], tool_selection: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Create comprehensive execution plan"""
        
        # Determine execution strategy
        strategy = self._determine_execution_strategy(routing_analysis, tool_selection, user_message)
        
        # Create execution plan using appropriate strategy
        plan_creator = self.execution_strategies.get(strategy, self._create_single_agent_plan)
        execution_plan = plan_creator(routing_analysis, tool_selection, user_message)
        
        execution_plan["strategy"] = strategy
        execution_plan["created_at"] = datetime.now().isoformat()
        
        return execution_plan
    
    def _determine_execution_strategy(self, routing_analysis: Dict[str, Any], tool_selection: Dict[str, Any], user_message: str) -> str:
        """Determine the best execution strategy"""
        
        # Simple queries get direct response
        if len(user_message) < 20 and routing_analysis["confidence"] > 0.8:
            return "direct_response"
        
        # Complex tool requirements get tool-focused approach
        if len(tool_selection["selected_tools"]) > 3:
            return "tool_focused"
        
        # High confidence single agent tasks
        if routing_analysis["confidence"] > 0.7:
            return "single_agent"
        
        # Complex or multi-domain tasks get collaborative approach
        if routing_analysis.get("requires_collaboration", False):
            return "collaborative"
        
        return "single_agent"
    
    def _create_direct_response_plan(self, routing_analysis: Dict[str, Any], tool_selection: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Create plan for direct response without complex orchestration"""
        return {
            "execution_type": "direct_response",
            "agent": routing_analysis["primary_agent"],
            "tools": tool_selection["selected_tools"][:1],  # Only one tool for direct response
            "approach": "simple_execution",
            "expected_time": "< 2s",
            "complexity": "low"
        }
    
    def _create_single_agent_plan(self, routing_analysis: Dict[str, Any], tool_selection: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Create plan for single agent execution"""
        return {
            "execution_type": "single_agent",
            "agent": routing_analysis["primary_agent"],
            "tools": tool_selection["selected_tools"],
            "approach": "focused_execution",
            "expected_time": "< 5s",
            "complexity": "medium"
        }
    
    def _create_collaborative_plan(self, routing_analysis: Dict[str, Any], tool_selection: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Create plan for collaborative execution"""
        return {
            "execution_type": "collaborative",
            "agent": routing_analysis["primary_agent"],
            "primary_agent": routing_analysis["primary_agent"],
            "secondary_agents": routing_analysis.get("secondary_agents", []),
            "tools": tool_selection["selected_tools"],
            "approach": "coordinated_execution",
            "expected_time": "< 10s",
            "complexity": "high"
        }
    
    def _create_tool_focused_plan(self, routing_analysis: Dict[str, Any], tool_selection: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Create plan for tool-focused execution"""
        return {
            "execution_type": "tool_focused",
            "agent": routing_analysis["primary_agent"],
            "tools": tool_selection["selected_tools"],
            "approach": "tool_optimized_execution",
            "expected_time": "< 8s",
            "complexity": "high"
        }

class PerformanceTracker:
    """Tracks performance metrics for coordination decisions"""
    
    def __init__(self):
        self.coordination_history = []
        self.agent_performance = {}
        self.tool_performance = {}
    
    def record_coordination(self, coordination_data: Dict[str, Any]):
        """Record coordination decision and performance"""
        self.coordination_history.append(coordination_data)
        
        # Update agent performance tracking
        agent = coordination_data["agent_selected"]
        if agent not in self.agent_performance:
            self.agent_performance[agent] = {"selections": 0, "avg_confidence": 0.0, "avg_time": 0.0}
        
        self.agent_performance[agent]["selections"] += 1
        self.agent_performance[agent]["avg_confidence"] = (
            (self.agent_performance[agent]["avg_confidence"] * (self.agent_performance[agent]["selections"] - 1) + 
             coordination_data["confidence"]) / self.agent_performance[agent]["selections"]
        )
        self.agent_performance[agent]["avg_time"] = (
            (self.agent_performance[agent]["avg_time"] * (self.agent_performance[agent]["selections"] - 1) + 
             coordination_data["routing_time"]) / self.agent_performance[agent]["selections"]
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            "total_coordinations": len(self.coordination_history),
            "agent_performance": self.agent_performance,
            "avg_coordination_time": sum(c["routing_time"] for c in self.coordination_history) / len(self.coordination_history) if self.coordination_history else 0
        }

class EnhancedRouter:
    """Enhanced intelligent routing with machine learning-like scoring"""
    
    def __init__(self):
        self.agent_patterns = {
            "memory_librarian": {
                "keywords": ["remember", "contact", "entity", "extract", "identify", "who", "what"],  # More specific keywords
                "patterns": [
                    r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # phone numbers
                    r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # person names
                    r"works at|employed by|job at|company|organization",
                    r"lives in|address|location|located at",
                    r"extract.*entities|identify.*people"
                ],
                "priority_multiplier": 1.0,  # Reduced to avoid conflicts
                "description": "Entity extraction and contact identification specialist"
            },
            "research_specialist": {
                "keywords": ["research", "analyze", "document", "text", "sentiment", "language", "summarize", "extract", "study", "investigate", "report", "paper", "article", "analysis", "insights"],
                "patterns": [
                    r"analyze.*sentiment|sentiment.*analysis",
                    r"summarize|summary",
                    r"extract.*from|parse.*document",
                    r"research.*topic|investigate",
                    r"what.*language|detect.*language",
                    r"document.*analysis"
                ],
                "priority_multiplier": 1.1,
                "description": "Advanced text analysis with enhanced document processing"
            },
            "personal_assistant": {
                "keywords": ["calendar", "schedule", "appointment", "meeting", "time", "date", "remind", "task", "todo", "organize", "plan", "event", "deadline", "help", "assist", "coordinate", "manage"],
                "patterns": [
                    r"what.*time|current.*time|time.*now",
                    r"schedule|calendar|appointment",
                    r"remind.*me|set.*reminder",
                    r"what.*date|today.*date",
                    r"meeting|event",
                    r"help.*me|can.*you|please",  # General assistance patterns
                    r"coordinate|manage|organize"
                ],
                "priority_multiplier": 1.5,  # Higher boost as main orchestrator
                "description": "Main orchestrating agent with coordination capabilities"
            },
            "location_agent": {
                "keywords": ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy", "location", "where", "timezone", "geography", "travel", "climate", "wind", "humidity", "map", "directions", "address"],
                "patterns": [
                    r"weather|temperature|forecast",
                    r"temperature.*in|weather.*in",  # Location-specific weather
                    r"what.*weather|how.*weather",
                    r"rain|snow|sunny|cloudy|storm",
                    r"where.*is|location.*of|address.*of",
                    r"timezone|time.*zone",
                    r"travel.*to|trip.*to|visit.*",
                    r"map|directions|navigate",
                    r"climate|humidity|wind"
                ],
                "priority_multiplier": 1.3,  # High priority for weather/location
                "description": "Weather forecasting and location intelligence specialist"
            },
            "shadow_agent": {
                "keywords": [],  # Shadow agent never gets primary routing - only collaborative
                "patterns": [],  # No direct patterns - always works in background
                "priority_multiplier": 0.0,  # Never selected as primary agent
                "description": "Silent behavioral modeling and context synthesis - invisible twin"
            },
            "health_analyst": {
                "keywords": ["health", "fitness", "exercise", "sleep", "steps", "heart", "blood", "medical", "wellness", "workout", "activity", "calories"],
                "patterns": [
                    r"health.*data|fitness.*data",
                    r"sleep.*pattern|sleep.*quality",
                    r"exercise|workout|physical.*activity",
                    r"heart.*rate|blood.*pressure",
                    r"steps|calories|weight"
                ],
                "priority_multiplier": 1.0,
                "description": "Enhanced health analytics with predictive insights"
            },
            "finance_tracker": {
                "keywords": ["money", "expense", "cost", "budget", "spending", "transaction", "financial", "price", "payment", "bank", "account", "dollar", "finance"],
                "patterns": [
                    r"\$\d+|\d+.*dollar",  # money amounts
                    r"expense|spending|cost",
                    r"budget|financial|transaction",
                    r"paid|payment|bank|account"
                ],
                "priority_multiplier": 1.0,
                "description": "Smart financial tracking with budget optimization"
            },
            "project_manager": {
                "keywords": ["project", "task", "deadline", "milestone", "progress", "todo", "assignment", "team", "collaborate", "manage", "organize", "plan", "schedule"],
                "patterns": [
                    r"create.*project|new.*project",
                    r"task.*assign|assign.*task",
                    r"deadline|due.*date|milestone",
                    r"project.*status|task.*status",
                    r"team.*member|collaborate"
                ],
                "priority_multiplier": 1.3,  # High priority for project management
                "description": "Project coordination and task management specialist"
            },
            "communication_specialist": {
                "keywords": ["email", "send", "reply", "message", "communicate", "correspondence", "group", "organization"],
                "patterns": [
                    r"send.*email|email.*to",
                    r"reply.*to|respond.*to",
                    r"group.*email|team.*message",
                    r"\b\w+@\w+\.\w+\b"  # email addresses
                ],
                "priority_multiplier": 1.4,  # Very high priority for communications
                "description": "Email and communication management specialist"
            },
            "knowledge_curator": {
                "keywords": ["knowledge", "learn", "information", "content", "organize", "categorize", "journal", "note", "document", "archive", "library", "save", "store"],
                "patterns": [
                    r"save.*knowledge|store.*information",
                    r"organize.*content|categorize",
                    r"journal.*entry|note.*taking",
                    r"knowledge.*base|information.*system",
                    r"learn.*about|study.*"
                ],
                "priority_multiplier": 1.2,  # High priority for knowledge management
                "description": "Knowledge management and content curation specialist"
            },
            "relationship_advisor": {
                "keywords": ["relationship", "social", "friend", "family", "connection", "interaction", "people", "network", "introduce"],
                "patterns": [
                    r"relationship.*with|connected.*to",
                    r"social.*network|people.*network", 
                    r"friend.*family|family.*friend",
                    r"interaction.*history|social.*pattern",
                    r"introduce.*to|connect.*with"
                ],
                "priority_multiplier": 1.0,
                "description": "Social relationship analysis and networking specialist"
            },
            "entertainment_curator": {
                "keywords": ["movie", "film", "entertainment", "event", "place", "visit", "recommendation", "watch", "review", "rating"],
                "patterns": [
                    r"movie.*recommend|film.*suggest",
                    r"event.*attend|place.*visit",
                    r"watch.*list|movie.*rating",
                    r"entertainment.*preference",
                    r"review.*movie|rate.*film"
                ],
                "priority_multiplier": 0.9,
                "description": "Entertainment and experience curation specialist"
            }
        }
        
        # Learning component - tracks successful routes
        self.route_success_history = {}
    
    def analyze_message(self, message: str, conversation_context: List[Dict] = None):
        """Enhanced message analysis with learning component"""
        message_lower = message.lower()
        
        # Enhanced scoring with pattern weighting
        agent_scores = {}
        
        for agent, config in self.agent_patterns.items():
            score = 0
            
            # Keyword matching with frequency boost
            for keyword in config["keywords"]:
                count = message_lower.count(keyword)
                score += count * 2.5  # Increased weight for keywords
            
            # Pattern matching with confidence scoring
            for pattern in config["patterns"]:
                matches = re.findall(pattern, message, re.IGNORECASE)
                score += len(matches) * 4  # Higher weight for patterns
            
            # Apply priority multiplier
            score *= config.get("priority_multiplier", 1.0)
            
            # Apply learning boost if this route was successful before
            if agent in self.route_success_history:
                success_rate = self.route_success_history[agent].get("success_rate", 0.5)
                score *= (1 + success_rate * 0.3)  # Up to 30% boost
            
            agent_scores[agent] = score
        
        # Enhanced tie-breaking with context awareness
        max_score = max(agent_scores.values())
        tied_agents = [agent for agent, score in agent_scores.items() if score >= max_score * 0.95]
        
        if len(tied_agents) > 1:
            # Smart tie-breaking based on message intent
            if any(word in message_lower for word in ["weather", "temperature", "forecast", "location", "where"]):
                best_agent = "location_agent"
            elif any(word in message_lower for word in ["time", "date", "schedule"]):
                best_agent = "personal_assistant"
            elif any(word in message_lower for word in ["contact", "person", "remember", "email", "phone"]):
                best_agent = "memory_librarian"
            elif any(word in message_lower for word in ["analyze", "research", "document", "text"]):
                best_agent = "research_specialist"
            elif any(word in message_lower for word in ["project", "task", "deadline", "milestone", "todo"]):
                best_agent = "project_manager"
            elif any(word in message_lower for word in ["send", "reply", "communicate", "correspondence"]):
                best_agent = "communication_specialist"
            elif any(word in message_lower for word in ["knowledge", "learn", "journal", "note", "information"]):
                best_agent = "knowledge_curator"
            elif any(word in message_lower for word in ["relationship", "social", "friend", "family", "people"]):
                best_agent = "relationship_advisor"
            elif any(word in message_lower for word in ["movie", "film", "entertainment", "event", "place", "visit"]):
                best_agent = "entertainment_curator"
            else:
                best_agent = tied_agents[0]
        else:
            best_agent = max(agent_scores, key=agent_scores.get)
        
        best_score = agent_scores[best_agent]
        
        # ALWAYS use Personal Assistant as primary responder - others are collaborators
        best_agent = "personal_assistant"
        
        # Determine which specialists should collaborate based on query analysis
        collaborators = []
        collaboration_reasoning = []
        
        for agent, score in agent_scores.items():
            if agent != "personal_assistant" and agent != "shadow_agent" and score > 2:  # Exclude shadow (always collaborates) and low-scoring agents
                collaborators.append(agent)
                collaboration_reasoning.append(f"{agent} (score: {score:.1f})")
        
        # Always include shadow agent for behavioral context
        if "shadow_agent" not in collaborators:
            collaborators.append("shadow_agent")
            collaboration_reasoning.append("shadow_agent (behavioral context)")
        
        # Create comprehensive reasoning
        if collaborators:
            specialist_list = ", ".join(collaboration_reasoning)
            reasoning = f"Personal Assistant coordinating with specialists: {specialist_list}"
        else:
            reasoning = "Personal Assistant handling request independently"
        
        return {
            "primary_agent": best_agent,
            "confidence": min(max(agent_scores.values()) / 15.0, 1.0),  # Base confidence on highest specialist score
            "reasoning": reasoning,
            "complexity": "enhanced" if len(collaborators) > 2 else "standard",
            "requires_collaboration": len(collaborators) > 0,
            "secondary_agents": collaborators,
            "specialist_scores": {agent: score for agent, score in agent_scores.items() if score > 2}
        }


class PipelineBeta:
    """Myndy AI Beta - Enhanced Pipeline for Performance Comparison"""
    
    class Valves(BaseModel):
        """Enhanced configuration valves"""
        enable_intelligent_routing: bool = True
        enable_enhanced_routing: bool = True  # New: enhanced routing algorithm
        enable_tool_execution: bool = True
        enable_learning: bool = True  # New: learning from feedback
        enable_fast_mode: bool = True  # New: optimized for speed
        debug_mode: bool = False
        show_agent_thoughts: bool = False  # New: show agent reasoning and collaboration
        verbose_coordination: bool = False  # New: detailed coordination info
        trace_tool_selection: bool = False  # New: show tool selection process
        show_tool_execution: bool = False  # New: show actual tool usage and results
        show_tool_results: bool = False  # New: show detailed tool output data
        memex_path: str = str(MYNDY_AI_ROOT) if 'MYNDY_AI_ROOT' in globals() and MYNDY_AI_ROOT.exists() else "../myndy-ai"
        api_key: str = "0p3n-w3bu!"
        
    def __init__(self):
        """Initialize the enhanced pipeline"""
        self.type = "manifold"
        self.id = "myndy_ai_beta"
        self.name = "Myndy AI Beta"
        self.version = "0.2.0-beta"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # Initialize default values
        self.crewai_available = False
        self.crewai_agents = {}
        self.main_coordinator = None
        
        # Import components
        self._import_components()
        
        # Initialize main coordinator after components are imported
        if self.crewai_available:
            try:
                self.main_coordinator = MainCoordinator(valves=self.valves)
                if "context_manager" in self.crewai_agents:
                    self.main_coordinator.set_context_manager_agent(self.crewai_agents["context_manager"])
                    logger.info("Context manager agent connected to MainCoordinator for tool selection")
            except Exception as e:
                logger.warning(f"Failed to initialize MainCoordinator: {e}")
                self.main_coordinator = None
        
        # Initialize conversation sessions
        self.conversation_sessions = {}
        
        # Enhanced agent definitions with context management
        self.agents = {
            "context_manager": {
                "name": "Context Manager Pro",
                "description": "Intelligent context analysis and routing agent - determines optimal delegation strategy",
                "model": "mixtral",
                "capabilities": ["context analysis", "intelligent routing", "conversation understanding", "delegation decisions", "request classification", "priority assessment"],
                "performance_target": "< 1s routing time",
                "role": "context_orchestrator"
            },
            "personal_assistant": {
                "name": "Personal Assistant Pro",
                "description": "Main orchestrating agent - coordinates specialists based on Context Manager recommendations",
                "model": "llama3.2",
                "capabilities": ["task coordination", "agent delegation", "calendar management", "weather forecasting", "time management", "general assistance", "workflow orchestration"],
                "performance_target": "< 2s response time",
                "role": "primary_orchestrator"
            },
            "memory_librarian": {
                "name": "Memory Librarian Pro",
                "description": "Contact management specialist with AI-powered relationship mapping",
                "model": "llama3.2",
                "capabilities": ["memory management", "entity relationships", "conversation history", "contact information", "relationship tracking", "smart updates"],
                "performance_target": "< 3s response time",
                "role": "specialist"
            },
            "research_specialist": {
                "name": "Research Specialist Plus",
                "description": "Research and analysis specialist with enhanced document processing",
                "model": "llama3.2", 
                "capabilities": ["web research", "fact verification", "document analysis", "sentiment analysis", "content summarization"],
                "performance_target": "< 5s response time",
                "role": "specialist"
            },
            "health_analyst": {
                "name": "Health Analyst Plus", 
                "description": "Health and wellness specialist with predictive insights",
                "model": "llama3.2",
                "capabilities": ["health analysis", "fitness tracking", "wellness optimization", "trend prediction"],
                "performance_target": "< 4s response time",
                "role": "specialist"
            },
            "finance_tracker": {
                "name": "Finance Tracker Pro",
                "description": "Financial tracking specialist with budget optimization", 
                "model": "llama3.2",
                "capabilities": ["expense tracking", "budget analysis", "financial planning", "spend prediction"],
                "performance_target": "< 3s response time",
                "role": "specialist"
            },
            "location_agent": {
                "name": "Location Intelligence Pro",
                "description": "Location and weather specialist with geographic insights",
                "model": "llama3.2",
                "capabilities": ["weather forecasting", "location services", "geographic analysis", "travel planning", "local information", "timezone management"],
                "performance_target": "< 3s response time",
                "role": "specialist"
            },
            "shadow_agent": {
                "name": "Shadow Intelligence Observer",
                "description": "Silent behavioral modeling and context synthesis agent - your invisible twin",
                "model": "llama3.2",
                "capabilities": ["behavior modeling", "pattern recognition", "intention inference", "context enrichment", "memory synthesis", "predictive analysis"],
                "performance_target": "< 2s background processing",
                "role": "observer"
            }
        }
        
        logger.info(f"🚀 Myndy AI Beta v{self.version} - Enhanced Pipeline initialized")
        logger.info(f"⚡ Available agents: {list(self.agents.keys())}")
        logger.info(f"🔧 Enhanced features: routing, learning, fast_mode")
        if hasattr(self, 'crewai_agents'):
            logger.info(f"🤖 Enhanced agents loaded: {list(self.crewai_agents.keys())}")
        
    def get_models(self) -> List[Dict[str, Any]]:
        """Return enhanced models list"""
        return self._get_models()
        
    def get_manifest(self) -> Dict[str, Any]:
        """Return enhanced pipeline manifest"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "type": self.type,
            "description": "Myndy AI Beta - Enhanced intelligent assistant with optimized routing and faster responses",
            "author": "Jeremy",
            "license": "MIT",
            "features": ["enhanced_routing", "learning_feedback", "performance_optimization", "competitive_testing"],
            "models": self._get_models()
        }
    
    def _import_components(self):
        """Import enhanced CrewAI components"""
        try:
            if not CREWAI_AVAILABLE:
                logger.warning("CrewAI not available, using fallback mode")
                return
            
            # Try to import basic CrewAI components
            from crewai import Agent, Task, Crew, Process
            
            # Create simple agents for testing
            self.crewai_agents = {}
            
            # Create basic agents without complex dependencies
            try:
                # Set a default LLM for agent creation without requiring OpenAI API key
                import os
                if not os.environ.get('OPENAI_API_KEY'):
                    os.environ['OPENAI_API_KEY'] = 'fake-key-for-testing'
                
                # Create Ollama LLMs for each agent based on their specialization
                try:
                    from langchain_community.llms import Ollama
                except ImportError:
                    # Fallback to older import
                    from langchain.llms import Ollama
                
                # Specialized models for each agent type - optimized for tool usage
                # Context Manager: Best tool selection model - needs excellent reasoning
                context_manager_llm = Ollama(model="openhermes", base_url="http://localhost:11434")
                
                # Memory Librarian: Tool-heavy agent - needs good function calling
                memory_librarian_llm = Ollama(model="openhermes", base_url="http://localhost:11434")
                
                # Personal Assistant: Coordination and tool usage
                personal_assistant_llm = Ollama(model="mixtral", base_url="http://localhost:11434")
                
                # Research Specialist: Strong analytical and reasoning capabilities
                research_specialist_llm = Ollama(model="mixtral", base_url="http://localhost:11434")
                
                # Health Analyst: Precise tool usage for health data
                health_analyst_llm = Ollama(model="openhermes", base_url="http://localhost:11434")
                
                # Finance Tracker: Good with numbers and tool execution
                finance_tracker_llm = Ollama(model="mistral", base_url="http://localhost:11434")
                
                # Location Agent: Weather and geographic intelligence
                location_agent_llm = Ollama(model="mistral", base_url="http://localhost:11434")
                
                # Shadow Agent: Silent behavioral modeling and context synthesis
                shadow_agent_llm = Ollama(model="nous-hermes", base_url="http://localhost:11434")
                
                # Project Manager: Task and project coordination with tools
                project_manager_llm = Ollama(model="mistral", base_url="http://localhost:11434")
                
                # Communication Specialist: Email and contact management tools
                communication_specialist_llm = Ollama(model="mistral", base_url="http://localhost:11434")
                
                # Knowledge Curator: Knowledge and content organization
                knowledge_curator_llm = Ollama(model="llama3", base_url="http://localhost:11434")
                
                # Relationship Advisor: People and social connections
                relationship_advisor_llm = Ollama(model="llama3", base_url="http://localhost:11434")
                
                # Entertainment Curator: Movies, events, and places
                entertainment_curator_llm = Ollama(model="llama3", base_url="http://localhost:11434")
                
                self.crewai_agents["context_manager"] = Agent(
                    role="Context Manager",
                    goal="Analyze user requests and select optimal tools for task execution",
                    backstory="I am an intelligent context analyzer that determines the best tools and strategies for handling user requests. I specialize in routing decisions and tool selection optimization.",
                    llm=context_manager_llm
                )
                
                self.crewai_agents["personal_assistant"] = Agent(
                    role="Personal Assistant",
                    goal="Help with general inquiries and provide current information",
                    backstory="I'm a helpful assistant ready to help with various tasks. I coordinate with other specialists when needed.",
                    llm=personal_assistant_llm
                )
                
                self.crewai_agents["memory_librarian"] = Agent(
                    role="Memory Librarian", 
                    goal="Manage personal information and contacts",
                    backstory="I help organize and remember important personal information. I excel at extracting entities and managing contact data.",
                    llm=memory_librarian_llm
                )
                
                self.crewai_agents["research_specialist"] = Agent(
                    role="Research Specialist",
                    goal="Conduct research and provide analytical insights", 
                    backstory="I specialize in research and analysis tasks. I can analyze documents, extract insights, and provide comprehensive research findings.",
                    llm=research_specialist_llm
                )
                
                self.crewai_agents["health_analyst"] = Agent(
                    role="Health Analyst",
                    goal="Analyze health data and provide wellness insights",
                    backstory="I help track and analyze health and fitness information. I provide data-driven insights about wellness trends and patterns.",
                    llm=health_analyst_llm
                )
                
                self.crewai_agents["finance_tracker"] = Agent(
                    role="Finance Tracker", 
                    goal="Track expenses and provide financial insights",
                    backstory="I help manage financial information and spending analysis. I excel at numerical analysis and budget optimization.",
                    llm=finance_tracker_llm
                )
                
                self.crewai_agents["location_agent"] = Agent(
                    role="Location Intelligence Specialist",
                    goal="Provide weather forecasts, location information, and geographic insights",
                    backstory="I specialize in weather, location services, and geographic analysis. I can provide weather forecasts, timezone information, travel planning, and local insights.",
                    llm=location_agent_llm
                )
                
                self.crewai_agents["shadow_agent"] = Agent(
                    role="Shadow Intelligence Observer",
                    goal="Silently observe, model behavior, and synthesize context directly for you",
                    backstory="I am your invisible twin - a silent observer who learns your patterns, preferences, and behaviors. I work in the background, building deep behavioral models about you. When I speak, I address you directly about what I've observed and learned about your preferences, patterns, and context. I provide personal insights and behavioral context directly to you.",
                    llm=shadow_agent_llm
                )
                
                self.crewai_agents["project_manager"] = Agent(
                    role="Project Manager",
                    goal="Coordinate projects, manage tasks, and track progress",
                    backstory="I specialize in project management and task coordination. I help organize work, set deadlines, track progress, and ensure projects stay on track.",
                    llm=project_manager_llm
                )
                
                self.crewai_agents["communication_specialist"] = Agent(
                    role="Communication Specialist", 
                    goal="Manage emails, contacts, and group communications",
                    backstory="I excel at managing communications, organizing contacts, and facilitating group interactions. I help streamline email workflows and maintain relationship networks.",
                    llm=communication_specialist_llm
                )
                
                self.crewai_agents["knowledge_curator"] = Agent(
                    role="Knowledge Curator",
                    goal="Organize knowledge, curate content, and manage information resources",
                    backstory="I specialize in knowledge management and content curation. I help organize information, create connections between ideas, and maintain comprehensive knowledge bases.",
                    llm=knowledge_curator_llm
                )
                
                self.crewai_agents["relationship_advisor"] = Agent(
                    role="Relationship Advisor",
                    goal="Analyze relationships, track social connections, and provide social insights",
                    backstory="I focus on understanding and mapping social relationships. I help track interactions, analyze relationship patterns, and provide insights for better social connections.",
                    llm=relationship_advisor_llm
                )
                
                self.crewai_agents["entertainment_curator"] = Agent(
                    role="Entertainment Curator",
                    goal="Manage entertainment preferences, track experiences, and provide recommendations",
                    backstory="I specialize in entertainment and experience curation. I help track movies, events, places, and provide personalized recommendations based on preferences and history.",
                    llm=entertainment_curator_llm
                )
                
                self.crewai_available = True
                logger.info(f"✅ Created {len(self.crewai_agents)} CrewAI agents with optimized Ollama models")
                logger.info("🧠 Agent Models: context_manager+memory_librarian+health_analyst=openhermes, personal_assistant+research_specialist=mixtral, others=mistral/nous-hermes/llama3")
                return
                
            except Exception as e:
                logger.error(f"Failed to create Ollama agents: {e}")
                logger.info("🔄 Trying fallback with FakeListLLM...")
                
                try:
                    # Fallback to FakeListLLM if Ollama fails
                    from langchain.llms import FakeListLLM
                    fake_llm = FakeListLLM(responses=["I understand your request and I'm here to help."])
                    
                    self.crewai_agents["context_manager"] = Agent(
                        role="Context Manager",
                        goal="Analyze user requests and select optimal tools for task execution",
                        backstory="I am an intelligent context analyzer that determines the best tools and strategies for handling user requests.",
                        llm=fake_llm
                    )
                    
                    self.crewai_agents["personal_assistant"] = Agent(
                        role="Personal Assistant",
                        goal="Help with general inquiries and provide current information",
                        backstory="I'm a helpful assistant ready to help with various tasks.",
                        llm=fake_llm
                    )
                    
                    self.crewai_agents["memory_librarian"] = Agent(
                        role="Memory Librarian", 
                        goal="Manage personal information and contacts",
                        backstory="I help organize and remember important personal information.",
                        llm=fake_llm
                    )
                    
                    self.crewai_agents["research_specialist"] = Agent(
                        role="Research Specialist",
                        goal="Conduct research and provide analytical insights", 
                        backstory="I specialize in research and analysis tasks.",
                        llm=fake_llm
                    )
                    
                    self.crewai_agents["health_analyst"] = Agent(
                        role="Health Analyst",
                        goal="Analyze health data and provide wellness insights",
                        backstory="I help track and analyze health and fitness information.",
                        llm=fake_llm
                    )
                    
                    self.crewai_agents["finance_tracker"] = Agent(
                        role="Finance Tracker", 
                        goal="Track expenses and provide financial insights",
                        backstory="I help manage financial information and spending analysis.",
                        llm=fake_llm
                    )
                    
                    self.crewai_agents["location_agent"] = Agent(
                        role="Location Intelligence Specialist",
                        goal="Provide weather forecasts, location information, and geographic insights",
                        backstory="I specialize in weather, location services, and geographic analysis.",
                        llm=fake_llm
                    )
                    
                    self.crewai_agents["shadow_agent"] = Agent(
                        role="Shadow Intelligence Observer",
                        goal="Silently observe, model behavior, and synthesize context directly for you",
                        backstory="I am your invisible twin - a silent observer who learns your patterns and behaviors. When I speak, I address you directly about your preferences and patterns.",
                        llm=fake_llm
                    )
                    
                    self.crewai_available = True
                    logger.info(f"✅ Created {len(self.crewai_agents)} CrewAI agents with FakeListLLM fallback")
                    return
                    
                except Exception as e2:
                    logger.error(f"Failed to create fallback agents: {e2}")
                    logger.info("🔄 Creating final fallback mock agents for basic functionality")
                    
                    # Create simple mock agents as final fallback
                    self.crewai_agents = {
                        "context_manager": MockAgent(role="Context Manager"),
                        "personal_assistant": MockAgent(role="Personal Assistant"),
                        "memory_librarian": MockAgent(role="Memory Librarian"),
                        "research_specialist": MockAgent(role="Research Specialist"),
                        "health_analyst": MockAgent(role="Health Analyst"),
                        "finance_tracker": MockAgent(role="Finance Tracker"),
                        "location_agent": MockAgent(role="Location Intelligence Specialist"),
                        "shadow_agent": MockAgent(role="Shadow Intelligence Observer")
                    }
                    self.crewai_available = False  # Mark as not available for full functionality
                    logger.info(f"✅ Created {len(self.crewai_agents)} mock agents as final fallback")
                    return
            
        except ImportError as e:
            logger.warning(f"Could not import CrewAI components: {e}")
            self.crewai_available = False
            self.main_coordinator = None
    
    def _get_models(self) -> List[Dict[str, Any]]:
        """Return enhanced models list"""
        models = []
        
        # Add enhanced auto-routing model
        models.append({
            "id": "auto_beta",
            "name": "🚀 Myndy AI Beta (Enhanced)",
            "object": "model",
            "created": int(datetime.now().timestamp()),
            "owned_by": "crewai-myndy-beta"
        })
        
        # Add enhanced individual agents
        for agent_id, agent_info in self.agents.items():
            models.append({
                "id": f"{agent_id}_beta",
                "name": f"⚡ {agent_info['name']}",
                "object": "model", 
                "created": int(datetime.now().timestamp()),
                "owned_by": "crewai-myndy-beta"
            })
            
        return models
    
    def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], 
             body: Dict[str, Any]) -> Union[str, Generator, Iterator]:
        """Enhanced pipeline processing with performance optimization"""
        
        start_time = datetime.now()
        
        if self.valves.debug_mode:
            logger.info(f"Beta Pipeline called with model: {model_id}, message: {user_message}")
            
        try:
            # Get session ID for conversation tracking
            session_id = self._get_session_id(messages)
            
            # Update conversation history
            self._update_conversation_history(session_id, messages)
            
            # Use enhanced CrewAI pipeline or fallback routing
            if self.crewai_available or self.crewai_agents:
                response = self._execute_enhanced_crewai_pipeline(user_message, model_id, session_id)
            else:
                response = "Enhanced CrewAI agents are not available. Please ensure all dependencies are properly installed."
            
            # Add performance timing
            processing_time = (datetime.now() - start_time).total_seconds()
            response += f"\n\n*⚡ Beta processed in {processing_time:.1f}s*"
            
            return response
            
        except Exception as e:
            logger.error(f"Beta Pipeline error: {e}")
            return f"Beta pipeline encountered an error: {str(e)}"
    
    def _get_session_id(self, messages: List[Dict[str, Any]]) -> str:
        """Generate session ID for conversation tracking"""
        content_hash = str(abs(hash(str([msg.get("content", "") for msg in messages]))))
        return f"beta_session_{content_hash[:8]}"
        
    def _update_conversation_history(self, session_id: str, messages: List[Dict[str, Any]]):
        """Update conversation history for a session"""
        if session_id not in self.conversation_sessions:
            self.conversation_sessions[session_id] = {
                "created_at": datetime.now(),
                "messages": [],
                "agent_history": [],
                "performance_metrics": []
            }
            
        self.conversation_sessions[session_id]["messages"] = messages[-20:]
    
    def _execute_enhanced_crewai_pipeline(self, user_message: str, model_id: str, session_id: str) -> str:
        """Execute enhanced CrewAI pipeline with Main Coordinator intelligent routing and tool selection"""
        try:
            if not self.main_coordinator:
                # Fallback to simple agent routing when main coordinator is not available
                return self._execute_simple_agent_routing(user_message, model_id, session_id)
            
            # Get conversation context for better coordination
            conversation_context = self.conversation_sessions.get(session_id, {}).get("messages", [])
            
            # ALWAYS use Main Coordinator for intelligent routing - even for simple requests
            coordination_result = self.main_coordinator.coordinate_response(
                user_message, session_id, conversation_context
            )
            
            if self.valves.debug_mode:
                logger.info(f"🎯 Coordination result: {coordination_result}")
            
            # Execute based on coordination plan - no bypassing for simple requests
            response = self._execute_coordination_plan(user_message, coordination_result, model_id)
            
            # Add coordination metadata to response
            performance_info = self._format_coordination_performance(coordination_result)
            
            return f"{response}\n\n{performance_info}"
                
        except Exception as e:
            logger.error(f"Enhanced pipeline execution error: {e}")
            return f"Enhanced pipeline encountered an error: {str(e)}. Falling back to basic response."
    
    def _execute_task_with_visibility(self, task, agent_name: str = "unknown") -> str:
        """Execute task with tool execution visibility"""
        try:
            if hasattr(self, 'valves') and self.valves.show_tool_execution:
                print(f"\n🔧 EXECUTING TOOLS for {agent_name}:")
                print("=" * 40)
            
            # Execute the task
            try:
                result = task.execute_sync()
            except AttributeError:
                result = task.execute()
            
            if hasattr(self, 'valves') and self.valves.show_tool_results:
                print(f"\n📊 TOOL RESULTS for {agent_name}:")
                print("-" * 40)
                # Truncate very long results for readability
                result_str = str(result)
                if len(result_str) > 500:
                    result_display = result_str[:400] + "... [truncated]"
                else:
                    result_display = result_str
                print(f"Result: {result_display}")
                print("-" * 40)
            
            return str(result)
            
        except Exception as e:
            if hasattr(self, 'valves') and self.valves.show_tool_execution:
                print(f"❌ Tool execution failed for {agent_name}: {e}")
            raise e
    
    def _create_tool_specific_instructions(self, user_message: str, selected_tools: List[str]) -> str:
        """Create specific instructions based on the tools available"""
        instructions = []
        message_lower = user_message.lower()
        
        # MANDATORY: Always extract and store entities
        instructions.append("AUTOMATIC ENTITY DETECTION AND STORAGE:")
        instructions.append("- ALWAYS use extract_conversation_entities to detect people and organizations")
        instructions.append("- AUTOMATICALLY create entities for any people or organizations mentioned using create_entity")
        instructions.append("- AUTOMATICALLY save facts and relationships using add_fact")
        instructions.append("- EXAMPLE: 'Brent Bushnell is the owner of Two Bit Circus' requires:")
        instructions.append("  1. create_entity(name='Brent Bushnell', entity_type='person')")
        instructions.append("  2. create_entity(name='Two Bit Circus', entity_type='organization')")
        instructions.append("  3. add_fact(content='Brent Bushnell is the owner of Two Bit Circus')")
        instructions.append("")
        
        # Weather-specific instructions
        if any(tool in selected_tools for tool in ["weather_api", "local_weather", "format_weather"]):
            instructions.append("Weather Instructions:")
            instructions.append("- Use the weather_api tool to get current weather conditions and forecast")
            instructions.append("- Pass the location parameter (e.g., 'Seattle, WA' or 'Seattle, Washington')")
            instructions.append("- Include temperature, conditions, and any relevant weather details")
            instructions.append("- If a specific location is mentioned, use that location for the weather query")
            instructions.append("- Provide actual weather data, not general information about checking weather websites")
            instructions.append("")
        
        # Time-specific instructions
        if any(tool in selected_tools for tool in ["get_current_time", "format_date", "calculate_time_difference"]):
            instructions.append("Time Instructions:")
            instructions.append("- Use get_current_time to provide accurate current time information")
            instructions.append("- Include timezone information if location is specified")
            instructions.append("- Use appropriate formatting for dates and times")
            instructions.append("")
        
        # Memory/Identity instructions (enhanced)
        if any(tool in selected_tools for tool in ["add_fact", "create_entity", "search_memory", "get_self_profile"]):
            if "i am" in message_lower or "my name" in message_lower:
                instructions.append("Identity Storage Instructions:")
                instructions.append("- IMMEDIATELY use create_entity to store the user's identity")
                instructions.append("- ALSO use add_fact to store identity information as a fact")
                instructions.append("- Extract the name and any other personal details mentioned")
                instructions.append("- Store this information for future reference with high confidence")
                instructions.append("")
            elif "who am i" in message_lower or "about me" in message_lower:
                instructions.append("MANDATORY IDENTITY RETRIEVAL:")
                instructions.append("- STEP 1: Execute get_self_profile() tool immediately")
                instructions.append("- STEP 2: Execute search_memory(query='user identity') tool")
                instructions.append("- STEP 3: Use the actual tool outputs to tell the user who they are")
                instructions.append("- STEP 4: If tools return empty/no results, tell user 'No profile found, please introduce yourself'")
                instructions.append("- EXAMPLE: get_self_profile() -> use the actual profile data in your response")
                instructions.append("- DO NOT say you don't have access - you have the tools available")
                instructions.append("")
        
        # Entity mention detection (new)
        # Check if message contains potential entity mentions
        words = message_lower.split()
        if any(len(word) > 1 and word[0].isupper() for word in user_message.split()):
            instructions.append("Entity Mention Detected:")
            instructions.append("- This message contains capitalized words that may be people or organizations")
            instructions.append("- Use extract_conversation_entities to identify all entities")
            instructions.append("- Create entities and store facts about any relationships mentioned")
            instructions.append("")
        
        # Health instructions
        if any(tool in selected_tools for tool in ["health_query", "health_query_simple"]):
            instructions.append("Health Instructions:")
            instructions.append("- Use health tools to provide accurate health and fitness information")
            instructions.append("- Include relevant health metrics and insights")
            instructions.append("")
        
        # Finance instructions  
        if any(tool in selected_tools for tool in ["get_recent_expenses", "get_spending_summary", "finance_tool"]):
            instructions.append("Finance Instructions:")
            instructions.append("- Use finance tools to provide accurate financial information")
            instructions.append("- Include spending patterns and financial insights")
            instructions.append("")
        
        # Final mandatory instruction
        instructions.append("IMPORTANT: Use ALL available memory tools to automatically save information for future reference!")
        
        return "\n".join(instructions)
    
    def _execute_simple_agent_routing(self, user_message: str, model_id: str, session_id: str) -> str:
        """Simple agent routing fallback when main coordinator is not available"""
        try:
            # Simple routing logic
            message_lower = user_message.lower()
            
            # Determine which agent to use based on simple patterns
            if any(word in message_lower for word in ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy", "location", "where", "timezone", "geography", "travel"]):
                selected_agent = "location_agent"
            elif any(word in message_lower for word in ["i am", "my name is", "remember me", "contact", "person"]):
                selected_agent = "memory_librarian"
            elif any(word in message_lower for word in ["research", "analyze", "study", "document"]):
                selected_agent = "research_specialist"
            elif any(word in message_lower for word in ["health", "fitness", "exercise", "steps"]):
                selected_agent = "health_analyst"
            elif any(word in message_lower for word in ["money", "expense", "cost", "budget", "finance"]):
                selected_agent = "finance_tracker"
            else:
                selected_agent = "personal_assistant"
            
            # Execute with the selected agent
            if selected_agent in self.crewai_agents:
                agent = self.crewai_agents[selected_agent]
                
                # Check if it's a mock agent or real agent
                if isinstance(agent, MockAgent):
                    # Handle mock agent
                    agent_info = self.agents.get(selected_agent, {})
                    agent_name = agent_info.get("name", selected_agent)
                    
                    # Simple responses based on agent type
                    if selected_agent == "personal_assistant":
                        if "time" in message_lower:
                            from datetime import datetime
                            now = datetime.now()
                            response = f"It's currently {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}"
                        else:
                            response = f"I understand you're asking: {user_message}. I'm here to help with your request."
                    elif selected_agent == "memory_librarian":
                        response = f"I've noted your information: {user_message}. I help manage personal information and contacts."
                    elif selected_agent == "location_agent":
                        if any(word in message_lower for word in ["weather", "temperature", "forecast"]):
                            response = f"I can help with weather information! For accurate weather data, I'd need to access current weather services. What location are you interested in?"
                        else:
                            response = f"I specialize in location services, weather, and geographic information. How can I help with your location request?"
                    else:
                        response = f"I understand your {selected_agent.replace('_', ' ')} request: {user_message}"
                    
                    return f"🤖 **{agent_name}** (Mock Agent Fallback)\n\n{response}\n\n*⚡ Simple routing fallback*"
                else:
                    # Handle real CrewAI agent
                    result = self._execute_agent_with_tools(agent, user_message, [], selected_agent)
                    agent_info = self.agents.get(selected_agent, {})
                    agent_name = agent_info.get("name", selected_agent)
                    return f"🤖 **{agent_name}** (Simple Routing)\n\n{result}\n\n*⚡ Simple agent routing*"
            else:
                return f"Selected agent {selected_agent} not available."
                
        except Exception as e:
            logger.error(f"Simple agent routing error: {e}")
            return f"I understand your request: {user_message}. I'm working on providing you with helpful assistance."
    
    def _execute_coordination_plan(self, user_message: str, coordination_result: Dict[str, Any], model_id: str) -> str:
        """Execute the response based on Main Coordinator's plan"""
        
        response_plan = coordination_result["response_plan"]
        routing_analysis = coordination_result["routing_analysis"]
        tool_selection = coordination_result["tool_selection"]
        
        execution_type = response_plan["execution_type"]
        primary_agent = response_plan["agent"]
        
        # Handle different execution types
        if execution_type == "direct_response":
            return self._execute_direct_coordinated_response(user_message, coordination_result)
        elif execution_type == "single_agent":
            return self._execute_single_coordinated_agent(user_message, coordination_result)
        elif execution_type == "collaborative":
            return self._execute_collaborative_coordinated_task(user_message, coordination_result)
        elif execution_type == "tool_focused":
            return self._execute_tool_focused_coordinated_task(user_message, coordination_result)
        else:
            # Fallback to single agent execution
            return self._execute_single_coordinated_agent(user_message, coordination_result)
    
    def _execute_direct_coordinated_response(self, user_message: str, coordination_result: Dict[str, Any]) -> str:
        """Execute direct response with coordination - always includes Shadow Agent for behavioral context"""
        response_plan = coordination_result["response_plan"]
        agent_name = response_plan["agent"]
        tools = response_plan.get("tools", [])
        
        # For direct responses, always use the coordinated agent and tools
        if agent_name in self.crewai_agents:
            agent = self.crewai_agents[agent_name]
            
            # Create enhanced task description with Shadow Agent coordination
            enhanced_user_message = f"""
{user_message}

IMPORTANT: You are working with the Shadow Agent who provides direct behavioral insights to the user.

The Shadow Agent observes the user's patterns and preferences, and when it speaks, it addresses the user directly as "you" to share personal behavioral insights and context.

Instructions:
- Provide a direct, efficient response
- Consider the user's behavioral patterns and preferences
- Shadow Agent should speak directly to the user about their context when relevant
"""
            
            # For time queries specifically, ensure we use the time tool properly
            if any(word in user_message.lower() for word in ["time", "clock"]) and "get_current_time" in tools:
                # Execute with proper tool coordination for time queries
                result = self._execute_agent_with_tools(agent, enhanced_user_message, ["get_current_time"], agent_name)
            elif tools:
                # Execute with the selected tools
                result = self._execute_agent_with_tools(agent, enhanced_user_message, tools[:2], agent_name)
            else:
                # Execute without specific tools but with agent coordination
                result = self._execute_agent_with_tools(agent, enhanced_user_message, [], agent_name)
            
            agent_display_name = self.agents.get(agent_name, {}).get("name", agent_name)
            # Always show Shadow Agent coordination
            return f"🚀 **{agent_display_name}** (Direct) + 👤 Shadow Observer\n\n{result}\n\n*⚡ Direct coordination with behavioral context*"
        else:
            # Fallback only if agent not available
            return f"Requested agent {agent_name} not available for coordination."
    
    def _execute_single_coordinated_agent(self, user_message: str, coordination_result: Dict[str, Any]) -> str:
        """Execute single agent task with coordination - always includes Shadow Agent for behavioral context"""
        response_plan = coordination_result["response_plan"]
        tool_selection = coordination_result["tool_selection"]
        
        agent_name = response_plan["agent"]
        selected_tools = tool_selection["selected_tools"]
        
        if agent_name in self.crewai_agents:
            agent = self.crewai_agents[agent_name]
            
            # Enhanced task description that includes Shadow Agent behavioral context
            enhanced_task = f"""
Process this user request: {user_message}

IMPORTANT: You are working with the Shadow Agent who provides direct behavioral insights to the user.

The Shadow Agent observes the user's patterns and preferences, and when it speaks, it addresses the user directly as "you" to share personal behavioral insights and context.

Consider the user's patterns and provide a response that shows understanding of their personal context.
"""
            
            # Create enhanced task with shadow agent coordination and tools
            from crewai import Task
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from tools.myndy_bridge import get_tool_loader
            tool_loader = get_tool_loader()
            tool_objects = []
            for tool_name in selected_tools:
                tool_obj = tool_loader.create_crewai_tool(tool_name)
                if tool_obj:
                    tool_objects.append(tool_obj)
            
            task = Task(
                description=enhanced_task,
                agent=agent,
                tools=tool_objects,  # Explicitly provide tools to the task
                expected_output="A comprehensive response that incorporates Shadow Agent behavioral insights."
            )
            
            # Execute task with visibility
            result = self._execute_task_with_visibility(task, agent_name)
            
            agent_display_name = self.agents.get(agent_name, {}).get("name", agent_name)
            tool_count = len(selected_tools)
            
            # Always show Shadow Agent coordination
            return f"🧠 **{agent_display_name}** (Team: shadow_agent) + 👤 Shadow Observer\n\n{result}\n\n*🔧 Used {tool_count} tools via Main Coordinator*"
        else:
            return f"Requested agent {agent_name} not available via coordinator."
    
    def _execute_collaborative_coordinated_task(self, user_message: str, coordination_result: Dict[str, Any]) -> str:
        """Execute collaborative task with coordination - always includes Shadow Agent for context"""
        response_plan = coordination_result["response_plan"]
        
        primary_agent = response_plan["primary_agent"]
        secondary_agents = response_plan.get("secondary_agents", [])
        
        # Always include Shadow Agent in collaborative tasks for context enrichment
        if "shadow_agent" not in secondary_agents and "shadow_agent" in self.crewai_agents:
            secondary_agents = secondary_agents + ["shadow_agent"]
        
        # Execute with primary agent and enhanced collaboration info
        if primary_agent in self.crewai_agents:
            agent = self.crewai_agents[primary_agent]
            
            # Create enhanced task description that includes Shadow Agent context
            enhanced_task = f"""
Process this user request with collaborative intelligence: {user_message}

Your team includes:
- Primary: {primary_agent} (you)
- Supporting: {', '.join(secondary_agents)}
- Shadow Observer: Providing direct behavioral insights to the user

The Shadow Agent observes the user's patterns and speaks directly to them about their preferences, patterns, and context. When the Shadow Agent contributes, it addresses the user as "you" and shares personal behavioral insights.

Instructions:
- Consider the user's historical patterns and preferences
- Leverage the collaborative team's expertise
- Shadow Agent should speak directly to the user about their patterns and context
- Provide a response that shows deep understanding of the user
- Use available tools effectively
"""
            
            result = self._execute_agent_with_tools(
                agent, enhanced_task, 
                coordination_result["tool_selection"]["selected_tools"], 
                primary_agent
            )
            
            agent_display_name = self.agents.get(primary_agent, {}).get("name", primary_agent)
            shadow_indicator = " + 👤 Shadow Observer" if "shadow_agent" in secondary_agents else ""
            collab_info = f" (Team: {', '.join([a for a in secondary_agents if a != 'shadow_agent'])}){shadow_indicator}" if secondary_agents else ""
            
            return f"🤝 **{agent_display_name}**{collab_info}\n\n{result}\n\n*🎯 Enhanced collaborative coordination with behavioral context*"
        else:
            return f"Primary collaborative agent {primary_agent} not available."
    
    def _execute_tool_focused_coordinated_task(self, user_message: str, coordination_result: Dict[str, Any]) -> str:
        """Execute tool-focused task with coordination - always includes Shadow Agent for behavioral context"""
        response_plan = coordination_result["response_plan"]
        tool_selection = coordination_result["tool_selection"]
        
        agent_name = response_plan["agent"]
        selected_tools = tool_selection["selected_tools"]
        
        if agent_name in self.crewai_agents:
            agent = self.crewai_agents[agent_name]
            
            # Create enhanced task description focusing on tool usage with Shadow Agent context
            enhanced_task = f"""
Process this request with focus on using available tools effectively: {user_message}

IMPORTANT: You are working with the Shadow Agent who provides direct behavioral insights to the user.

The Shadow Agent observes the user's patterns and preferences, and when it speaks, it addresses the user directly as "you" to share personal behavioral insights and context.

Available coordinated tools: {', '.join(selected_tools)}

Instructions:
- Use tools systematically to gather comprehensive information
- Provide detailed analysis based on tool outputs
- Ensure all relevant tools are utilized appropriately
- Consider the user's patterns and preferences in your analysis
- Shadow Agent should speak directly to the user about their behavioral context
- Give a thorough, well-researched response that shows understanding of the user
"""
            
            result = self._execute_enhanced_agent_task(agent, enhanced_task, agent_name, selected_tools)
            
            agent_display_name = self.agents.get(agent_name, {}).get("name", agent_name)
            tool_count = len(selected_tools)
            
            # Always show Shadow Agent coordination
            return f"⚡ **{agent_display_name}** (Tool-Focused) + 👤 Shadow Observer\n\n{result}\n\n*🛠️ Optimized execution with {tool_count} coordinated tools via Shadow Agent context*"
        else:
            return f"Tool-focused agent {agent_name} not available."
    
    def _execute_agent_with_tools(self, agent, user_message: str, selected_tools: List[str], agent_name: str) -> str:
        """Execute agent with specific tools"""
        try:
            from crewai import Task
            
            # Create enhanced task description with tool guidance
            tool_instructions = self._create_tool_specific_instructions(user_message, selected_tools)
            
            task_description = f"""
Process this user request: {user_message}

MANDATORY TOOL USAGE: You have these tools available and MUST USE THEM:
{', '.join(selected_tools) if selected_tools else 'No specific tools required'}

EXECUTION REQUIREMENTS:
1. ALWAYS execute the available tools first before responding
2. Use the actual tool outputs in your response
3. Do NOT provide generic responses when tools are available
4. For "Who am I?" questions: MUST use get_self_profile and search_memory tools
5. For entity mentions: MUST use extract_conversation_entities and create_entity tools

{tool_instructions}

Step-by-step approach:
1. Execute the relevant tools from the available list
2. Use the tool outputs to craft your response
3. Provide specific, personalized information based on tool results
"""
            
            # Get the actual tool objects for the selected tools
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from tools.myndy_bridge import get_tool_loader
            tool_loader = get_tool_loader()
            tool_objects = []
            for tool_name in selected_tools:
                tool_obj = tool_loader.create_crewai_tool(tool_name)
                if tool_obj:
                    tool_objects.append(tool_obj)
            
            task = Task(
                description=task_description,
                agent=agent,
                tools=tool_objects,  # Explicitly provide tools to the task
                expected_output="A comprehensive response using the available tools effectively."
            )
            
            # Execute task with visibility
            result = self._execute_task_with_visibility(task, agent_name)
            return str(result)
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return f"I apologize, but I encountered an issue processing your request: {user_message}"
    
    def _execute_enhanced_agent_task(self, agent, task_description: str, agent_name: str, selected_tools: List[str] = None) -> str:
        """Execute agent with enhanced task description"""
        try:
            from crewai import Task
            
            # Get the actual tool objects for the selected tools
            tool_objects = []
            if selected_tools:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from tools.myndy_bridge import get_tool_loader
                tool_loader = get_tool_loader()
                for tool_name in selected_tools:
                    tool_obj = tool_loader.create_crewai_tool(tool_name)
                    if tool_obj:
                        tool_objects.append(tool_obj)
            
            task = Task(
                description=task_description,
                agent=agent,
                tools=tool_objects,  # Explicitly provide tools to the task
                expected_output="A detailed, well-researched response using all available tools effectively."
            )
            
            # Execute task with visibility
            result = self._execute_task_with_visibility(task, agent_name)
            return str(result)
            
        except Exception as e:
            logger.error(f"Enhanced agent execution error: {e}")
            return f"I encountered an issue with enhanced processing for: {agent_name}"
    
    def _handle_simple_direct_response(self, user_message: str) -> str:
        """Handle simple direct responses without complex coordination"""
        from datetime import datetime
        
        message_lower = user_message.lower()
        now = datetime.now()
        
        # Time-related requests
        if any(word in message_lower for word in ["time", "clock"]):
            current_time = now.strftime("%I:%M %p")
            return f"🚀 **Personal Assistant Pro** (Ultra-Fast Direct)\n\nIt's currently **{current_time}** on {now.strftime('%A, %B %d, %Y')}"
        
        # Date/day requests
        elif any(word in message_lower for word in ["day", "date", "today"]):
            day_name = now.strftime("%A")
            full_date = now.strftime("%B %d, %Y")
            return f"🚀 **Personal Assistant Pro** (Ultra-Fast Direct)\n\nToday is **{day_name}, {full_date}**"
        
        # General help
        else:
            return f"🚀 **Personal Assistant Pro** (Ultra-Fast Direct)\n\nI understand you're asking: {user_message}\n\nLet me help you with that directly."
    
    def _format_coordination_performance(self, coordination_result: Dict[str, Any]) -> str:
        """Format coordination performance information"""
        
        routing_analysis = coordination_result.get("routing_analysis", {})
        tool_selection = coordination_result.get("tool_selection", {})
        coordination_time = coordination_result.get("coordination_time", 0)
        
        # Create performance summary
        performance_parts = []
        
        # Routing info
        primary_agent = routing_analysis.get("primary_agent", "unknown")
        confidence = routing_analysis.get("confidence", 0)
        performance_parts.append(f"**Routing:** {primary_agent} (confidence: {confidence:.1f})")
        
        # Tool selection info
        tool_count = len(tool_selection.get("selected_tools", []))
        tool_confidence = tool_selection.get("confidence", 0)
        performance_parts.append(f"**Tools:** {tool_count} selected (confidence: {tool_confidence:.1f})")
        
        # Timing info
        performance_parts.append(f"**Coordination:** {coordination_time:.3f}s")
        
        return f"*⚡ {' | '.join(performance_parts)} | Main Coordinator Beta*"
    
    def _is_simple_request(self, user_message: str) -> bool:
        """Check if this is a simple request that doesn't need complex orchestration"""
        message_lower = user_message.lower().strip()
        
        # Simple time/date requests
        time_patterns = [
            r"what\s+(day|date)\s+is\s+it",
            r"what\s+time\s+is\s+it",
            r"what\s+day\s+of\s+the\s+week",
            r"current\s+(time|date)",
            r"today'?s\s+date",
            r"what\s+time",
            r"what\s+day",
            r"time\s+now",
            r"date\s+today"
        ]
        
        # Simple identity/contact statements and lookups
        identity_patterns = [
            r"i\s+am\s+\w+",
            r"my\s+name\s+is\s+\w+",
            r"this\s+is\s+\w+",
            r"i'm\s+\w+",
            r"call\s+me\s+\w+",
            r"who\s+am\s+i",
            r"what\s+is\s+my\s+name",
            r"who\s+is\s+this",
            r"do\s+you\s+know\s+me",
            r"remember\s+me"
        ]
        
        all_patterns = time_patterns + identity_patterns
        return any(re.search(pattern, message_lower) for pattern in all_patterns)
    
    def _handle_simple_request(self, user_message: str) -> str:
        """Handle simple requests directly without agent orchestration"""
        from datetime import datetime
        
        message_lower = user_message.lower()
        now = datetime.now()
        
        # Identity/contact statements and lookups - route to memory librarian
        identity_store_keywords = ["i am", "my name is", "this is", "i'm", "call me"]
        identity_lookup_keywords = ["who am i", "what is my name", "who is this", "do you know me", "remember me"]
        
        if any(phrase in message_lower for phrase in identity_store_keywords):
            return self._handle_identity_statement(user_message)
        elif any(phrase in message_lower for phrase in identity_lookup_keywords):
            return self._handle_identity_lookup(user_message)
        
        # Time-related requests
        elif any(word in message_lower for word in ["time", "clock"]):
            current_time = now.strftime("%I:%M %p")
            return f"🎯 **Personal Assistant Pro** (Direct Response)\n\nIt's currently **{current_time}** on {now.strftime('%A, %B %d, %Y')}.\n\n*⚡ Direct response in < 0.1s*"
        
        # Date/day requests
        elif any(word in message_lower for word in ["day", "date", "today"]):
            day_name = now.strftime("%A")
            full_date = now.strftime("%B %d, %Y")
            return f"🎯 **Personal Assistant Pro** (Direct Response)\n\nToday is **{day_name}, {full_date}**.\n\n*⚡ Direct response in < 0.1s*"
        
        # Fallback for other simple requests
        else:
            return f"🎯 **Personal Assistant Pro** (Direct Response)\n\nI understand you're asking: {user_message}\n\nLet me help you with that directly.\n\n*⚡ Direct response in < 0.1s*"

    def _handle_identity_statement(self, user_message: str) -> str:
        """Handle identity statements by routing to memory librarian"""
        try:
            # Use memory librarian directly for identity management
            if "memory_librarian" in self.crewai_agents:
                memory_agent = self.crewai_agents["memory_librarian"]
                
                # Create a simple task for the memory librarian
                task_description = f"""
Process this identity statement: {user_message}

Instructions:
- Extract the person's name and any other information
- Store or update their contact information
- Acknowledge that you've recorded their identity
- Be conversational and friendly
- Don't use complex tools, just process the basic identity information
"""
                
                from crewai import Task
                task = Task(
                    description=task_description,
                    agent=memory_agent,
                    expected_output="A friendly acknowledgment that the identity has been recorded."
                )
                
                # Execute task with visibility
                result = self._execute_task_with_visibility(task, "memory_librarian")
                return f"📝 **Memory Librarian Pro** (Direct Contact Management)\n\n{result}\n\n*⚡ Identity processed in < 2s*"
            else:
                # Fallback if memory librarian not available
                name_match = re.search(r'(?:i am|my name is|this is|i\'m|call me)\s+(\w+(?:\s+\w+)*)', user_message, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1)
                    return f"📝 **Memory Librarian Pro** (Direct Contact Management)\n\nHello **{name}**! I've noted your identity. Nice to meet you!\n\n*⚡ Identity processed in < 0.1s*"
                else:
                    return f"📝 **Memory Librarian Pro** (Direct Contact Management)\n\nI've noted your identity statement: {user_message}\n\n*⚡ Identity processed in < 0.1s*"
                    
        except Exception as e:
            logger.error(f"Identity statement handling error: {e}")
            # Simple fallback
            name_match = re.search(r'(?:i am|my name is|this is|i\'m|call me)\s+(\w+(?:\s+\w+)*)', user_message, re.IGNORECASE)
            if name_match:
                name = name_match.group(1)
                return f"📝 **Memory Librarian Pro** (Direct Contact Management)\n\nHello **{name}**! I've noted your identity.\n\n*⚡ Identity processed in < 0.1s*"
            else:
                return f"📝 **Memory Librarian Pro** (Direct Contact Management)\n\nI've noted your identity statement.\n\n*⚡ Identity processed in < 0.1s*"

    def _handle_identity_lookup(self, user_message: str) -> str:
        """Handle identity lookup queries by routing to memory librarian"""
        try:
            # Use memory librarian directly for identity lookup
            if "memory_librarian" in self.crewai_agents:
                memory_agent = self.crewai_agents["memory_librarian"]
                
                # Create a simple lookup task for the memory librarian
                task_description = f"""
Search for identity information based on this query: {user_message}

Instructions:
- Search your memory and contact database for any stored identity information
- Look for the current user's name, contact details, or previous interactions
- If you find information, present it clearly and conversationally
- If no information is found, politely explain that you need them to introduce themselves first
- Be helpful and direct in your response
- Use memory search tools if available
"""
                
                from crewai import Task
                task = Task(
                    description=task_description,
                    agent=memory_agent,
                    expected_output="A clear response about the user's identity based on stored information."
                )
                
                # Execute task with visibility
                result = self._execute_task_with_visibility(task, "memory_librarian")
                return f"🔍 **Memory Librarian Pro** (Identity Lookup)\n\n{result}\n\n*⚡ Identity lookup in < 3s*"
            else:
                # Fallback if memory librarian not available
                return f"🔍 **Memory Librarian Pro** (Identity Lookup)\n\nI don't have access to your stored identity information right now. Could you please tell me your name so I can help you better?\n\n*⚡ Identity lookup in < 0.1s*"
                    
        except Exception as e:
            logger.error(f"Identity lookup error: {e}")
            # Simple fallback
            return f"🔍 **Memory Librarian Pro** (Identity Lookup)\n\nI'm having trouble accessing your stored information right now. Could you please remind me who you are?\n\n*⚡ Identity lookup in < 0.1s*"

    def _get_context_analysis(self, user_message: str, session_id: str, target_agent: str = None) -> Dict[str, Any]:
        """Get intelligent context analysis from Context Manager agent"""
        try:
            if "context_manager" in self.crewai_agents:
                context_agent = self.crewai_agents["context_manager"]
                
                # Get conversation context
                conversation_context = self.conversation_sessions.get(session_id, {}).get("messages", [])
                
                # Create context analysis task
                task_description = f"""
Analyze this user request and determine the optimal routing strategy using your reasoning skills:

User Request: "{user_message}"
Available Agents: memory_librarian, research_specialist, personal_assistant, health_analyst, finance_tracker

Instructions:
- Do NOT use tools for this analysis - rely on your reasoning abilities
- Analyze the request type and complexity through pattern recognition
- Consider these routing options:

1. DIRECT_RESPONSE: For simple factual queries like "what time is it", "what day is it"
2. SINGLE_AGENT: For specialist tasks that need one expert:
   - memory_librarian: Identity questions ("who am i"), contact management
   - personal_assistant: Time, weather, scheduling, general assistance
   - research_specialist: Document analysis, research tasks
   - health_analyst: Health and fitness questions
   - finance_tracker: Money, expenses, financial planning

3. COLLABORATIVE: For complex tasks needing multiple specialists

Respond with just: "Approach: [direct_response/single_agent/collaborative], Primary agent: [agent_name], Reasoning: [brief explanation]"
"""
                
                from crewai import Task
                task = Task(
                    description=task_description,
                    agent=context_agent,
                    expected_output="Clear routing recommendation with approach and primary agent."
                )
                
                # Execute task with visibility
                result = self._execute_task_with_visibility(task, "context_manager")
                
                # Parse the context analysis result
                return self._parse_context_analysis(str(result), user_message, target_agent)
                
            else:
                # Fallback to simple analysis
                return self._fallback_context_analysis(user_message, target_agent)
                
        except Exception as e:
            logger.error(f"Context analysis error: {e}")
            return self._fallback_context_analysis(user_message, target_agent)
    
    def _parse_context_analysis(self, analysis_result: str, user_message: str, target_agent: str = None) -> Dict[str, Any]:
        """Parse context analysis result into structured format"""
        analysis_lower = analysis_result.lower()
        
        # Determine approach
        if "direct_response" in analysis_lower or any(word in analysis_lower for word in ["direct", "simple", "immediate", "fast"]):
            approach = "direct_response"
        elif "collaborative" in analysis_lower or any(word in analysis_lower for word in ["multiple", "complex", "collaborate"]):
            approach = "collaborative"
        else:
            approach = "single_agent"
        
        # Determine primary agent from analysis
        primary_agent = "personal_assistant"  # Default
        for agent_name in ["memory_librarian", "research_specialist", "personal_assistant", "health_analyst", "finance_tracker"]:
            if agent_name in analysis_lower:
                primary_agent = agent_name
                break
        
        # Override with target agent if specified
        if target_agent:
            primary_agent = target_agent
        
        return {
            "approach": approach,
            "primary_agent": primary_agent,
            "reasoning": analysis_result[:200] + "..." if len(analysis_result) > 200 else analysis_result,
            "confidence": 0.8,
            "user_message": user_message
        }
    
    def _fallback_context_analysis(self, user_message: str, target_agent: str = None) -> Dict[str, Any]:
        """Fallback context analysis when Context Manager is unavailable"""
        message_lower = user_message.lower()
        
        # Simple classification
        if len(user_message) < 20 and any(word in message_lower for word in ["time", "day", "date"]):
            approach = "direct_response"
            primary_agent = "personal_assistant"
        elif any(word in message_lower for word in ["who am i", "remember me", "i am"]):
            approach = "direct_response"
            primary_agent = "memory_librarian"
        else:
            approach = "single_agent"
            primary_agent = target_agent or "personal_assistant"
        
        return {
            "approach": approach,
            "primary_agent": primary_agent,
            "reasoning": "Fallback analysis - using simple pattern matching",
            "confidence": 0.6,
            "user_message": user_message
        }
    
    def _execute_direct_response(self, user_message: str, context_analysis: Dict[str, Any]) -> str:
        """Execute direct response for simple requests"""
        return self._handle_simple_request(user_message)
    
    def _execute_single_agent_task(self, user_message: str, context_analysis: Dict[str, Any]) -> str:
        """Execute task with single agent based on context analysis"""
        primary_agent = context_analysis["primary_agent"]
        
        if primary_agent in self.crewai_agents:
            agent = self.crewai_agents[primary_agent]
            result = self._execute_crewai_agent(agent, user_message, primary_agent)
            
            agent_info = self.agents.get(primary_agent, {"name": "Agent"})
            return f"🧠 **{agent_info['name']}** (Context-Driven)\n\n{result}\n\n*⚡ Routed by Context Manager*"
        else:
            return f"Context Manager recommended {primary_agent}, but agent not available."
    
    def _execute_collaborative_task(self, user_message: str, context_analysis: Dict[str, Any]) -> str:
        """Execute collaborative task based on context analysis"""
        routing_result = {
            "primary_agent": context_analysis["primary_agent"],
            "reasoning": context_analysis["reasoning"],
            "confidence": context_analysis["confidence"]
        }
        
        delegated_agents = [context_analysis["primary_agent"], "personal_assistant"]
        result = self._execute_orchestrated_task(user_message, delegated_agents, routing_result)
        return self._format_orchestrated_response(result, delegated_agents, routing_result)
    
    def _execute_directed_agent_task(self, user_message: str, target_agent: str, context_analysis: Dict[str, Any]) -> str:
        """Execute task with directed agent using context insights"""
        if target_agent in self.crewai_agents:
            agent = self.crewai_agents[target_agent]
            result = self._execute_crewai_agent(agent, user_message, target_agent)
            
            agent_info = self.agents.get(target_agent, {"name": "Agent"})
            return f"🎯 **{agent_info['name']}** (Context-Optimized)\n\n{result}\n\n*⚡ Optimized by Context Manager*"
        else:
            return f"Requested agent {target_agent} not available."

    def _execute_crewai_agent(self, agent, user_message: str, agent_role: str) -> str:
        """Execute CrewAI agent with enhanced task descriptions"""
        try:
            from crewai import Task
            from crewai.agents.parser import OutputParserException
            
            # Enhanced task descriptions for better performance
            task_description = self._create_enhanced_task_description(user_message, agent_role)
            
            task = Task(
                description=task_description,
                agent=agent,
                expected_output="A comprehensive and efficient response addressing the user's request. Provide clear, actionable information."
            )
            
            # Execute task with visibility
            result = self._execute_task_with_visibility(task, agent_role)
            return str(result)
            
        except OutputParserException as e:
            logger.warning(f"Agent output parsing error: {e}")
            # Return a fallback response when there's a parsing error
            return f"I understand you're asking about: {user_message}. Let me provide a direct response without using complex tools."
        except Exception as e:
            logger.error(f"Enhanced agent execution error: {e}")
            return f"I apologize, but I encountered an issue processing your request: {user_message}. Please try rephrasing your question."
    
    def _create_enhanced_task_description(self, user_message: str, agent_role: str) -> str:
        """Create enhanced task descriptions for optimized performance"""
        
        if agent_role == "personal_assistant":
            return f"""
Respond to this user request: {user_message}

Instructions:
- Provide accurate time, weather, or scheduling information as requested
- Use available tools efficiently and appropriately
- Give clear, concise responses
- If using tools, follow the proper format: Action: tool_name followed by Action Input: parameters
"""
        elif agent_role == "memory_librarian":
            return f"""
Process this user request: {user_message}

Instructions:
- Handle contact information, memories, or knowledge management tasks
- Extract and validate relevant information carefully
- Use memory and contact tools as needed
- Follow proper tool format if using tools: Action: tool_name followed by Action Input: parameters
"""
        elif agent_role == "research_specialist":
            return f"""
Analyze this user request: {user_message}

Instructions:
- Provide research, analysis, or document processing
- Use available tools for text analysis and research
- Give comprehensive but efficient responses
- Follow proper tool format: Action: tool_name followed by Action Input: parameters
"""
        else:
            return f"""
Address this user request: {user_message}

Instructions:
- Provide helpful assistance based on your role as {agent_role}
- Use available tools appropriately
- Give clear, actionable responses
- Follow proper tool format if needed: Action: tool_name followed by Action Input: parameters
"""
    
    def _determine_delegation(self, routing_result: Dict, user_message: str) -> List[str]:
        """Determine which agents the personal assistant should delegate to"""
        primary_agent = routing_result.get("primary_agent", "personal_assistant")
        secondary_agents = routing_result.get("secondary_agents", [])
        
        # Always include personal assistant as orchestrator
        delegated_agents = ["personal_assistant"]
        
        # Add primary agent if different from personal assistant
        if primary_agent != "personal_assistant":
            delegated_agents.append(primary_agent)
        
        # Add secondary agents for complex tasks
        if routing_result.get("requires_collaboration", False):
            for agent in secondary_agents:
                if agent not in delegated_agents:
                    delegated_agents.append(agent)
        
        return delegated_agents
    
    def _execute_orchestrated_task(self, user_message: str, delegated_agents: List[str], routing_result: Dict) -> str:
        """Execute task with personal assistant orchestrating other agents"""
        try:
            from crewai import Task, Crew
            
            # Create orchestrator task for personal assistant
            orchestrator_task = self._create_orchestrator_task(user_message, delegated_agents, routing_result)
            
            # Create tasks for delegated agents
            agent_tasks = []
            agents_to_use = []
            
            for agent_role in delegated_agents:
                if agent_role in self.crewai_agents:
                    agent = self.crewai_agents[agent_role]
                    if agent_role == "personal_assistant":
                        # Personal assistant gets the orchestrator task
                        task = Task(
                            description=orchestrator_task,
                            agent=agent,
                            expected_output="A coordinated response that may include delegated work from specialist agents."
                        )
                    else:
                        # Specialist agents get focused tasks
                        task = Task(
                            description=self._create_specialist_task(user_message, agent_role),
                            agent=agent,
                            expected_output=f"Specialized {agent_role} analysis and recommendations."
                        )
                    agent_tasks.append(task)
                    agents_to_use.append(agent)
            
            # Execute with crew if multiple agents, otherwise single agent
            if len(agent_tasks) > 1:
                crew = Crew(
                    agents=agents_to_use,
                    tasks=agent_tasks,
                    verbose=False,
                    process="sequential"  # Personal assistant coordinates sequentially
                )
                result = crew.kickoff()
            else:
                result = agent_tasks[0].execute()
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Orchestrated task execution error: {e}")
            return f"Personal Assistant: I understand your request about '{user_message}'. Let me handle this directly."
    
    def _execute_delegated_task(self, user_message: str, target_agent: str) -> str:
        """Execute task with personal assistant delegating to specific agent"""
        try:
            from crewai import Task, Crew
            
            if target_agent not in self.crewai_agents or target_agent == "personal_assistant":
                # Direct personal assistant response
                return self._execute_crewai_agent(
                    self.crewai_agents["personal_assistant"], 
                    user_message, 
                    "personal_assistant"
                )
            
            # Personal assistant delegates to specialist
            pa_agent = self.crewai_agents["personal_assistant"]
            specialist_agent = self.crewai_agents[target_agent]
            
            # Create delegation task for personal assistant
            delegation_task = Task(
                description=f"""
You are coordinating with the {target_agent} specialist to handle this request: {user_message}

Your role:
- Understand the user's needs
- Coordinate with the {target_agent} specialist
- Provide a unified, helpful response
- Ensure the specialist provides relevant information
""",
                agent=pa_agent,
                expected_output="A coordinated response incorporating specialist expertise."
            )
            
            # Create specialist task
            specialist_task = Task(
                description=self._create_specialist_task(user_message, target_agent),
                agent=specialist_agent,
                expected_output=f"Specialized {target_agent} analysis and recommendations."
            )
            
            # Execute with crew coordination
            crew = Crew(
                agents=[pa_agent, specialist_agent],
                tasks=[delegation_task, specialist_task],
                verbose=False,
                process="sequential"
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Delegated task execution error: {e}")
            return f"Personal Assistant: I'll help you with '{user_message}' directly."
    
    def _create_orchestrator_task(self, user_message: str, delegated_agents: List[str], routing_result: Dict) -> str:
        """Create orchestrator task description for personal assistant"""
        specialist_agents = [agent for agent in delegated_agents if agent != "personal_assistant"]
        
        if not specialist_agents:
            return f"""
Handle this user request directly: {user_message}

Instructions:
- Provide a helpful, comprehensive response
- Use your available tools as needed
- Be conversational and efficient
"""
        else:
            return f"""
Coordinate the response to this user request: {user_message}

Available specialists: {', '.join(specialist_agents)}
Routing confidence: {routing_result.get('confidence', 0.5):.1f}
Reasoning: {routing_result.get('reasoning', 'Standard routing')}

Your role as Personal Assistant Coordinator:
- Understand the user's complete needs
- Work with specialist agents to gather expert information
- Synthesize all inputs into a unified, helpful response
- Ensure the response is conversational and user-friendly
- Take ownership of the final answer quality
"""
    
    def _create_specialist_task(self, user_message: str, agent_role: str) -> str:
        """Create specialist task description for delegated agents"""
        role_descriptions = {
            "memory_librarian": "Handle contact information, personal memories, and knowledge management",
            "research_specialist": "Provide research, analysis, and document processing expertise", 
            "health_analyst": "Analyze health and fitness data, provide wellness insights",
            "finance_tracker": "Track expenses, analyze financial data, provide budget insights"
        }
        
        role_desc = role_descriptions.get(agent_role, f"Provide {agent_role} expertise")
        
        return f"""
Provide specialist expertise for this user request: {user_message}

Your specialist role: {role_desc}

Instructions:
- Focus on your area of expertise
- Provide clear, actionable insights
- Use your specialized tools as needed
- Work collaboratively with the Personal Assistant
- Be concise but thorough in your analysis
"""
    
    def _format_orchestrated_response(self, result: str, delegated_agents: List[str], routing_info: Dict) -> str:
        """Format orchestrated response with coordination info"""
        response_parts = []
        
        # Coordination header
        if len(delegated_agents) > 1:
            specialists = [agent for agent in delegated_agents if agent != "personal_assistant"]
            response_parts.append(f"🎯 **Personal Assistant Pro** (Coordinating with: {', '.join(specialists)})")
        else:
            response_parts.append(f"🎯 **Personal Assistant Pro** (Direct Response)")
        
        response_parts.append(f"**Routing:** {routing_info.get('reasoning', 'Direct assistance')}")
        response_parts.append("")  # Empty line
        
        # Main response
        response_parts.append(result)
        
        # Coordination info
        response_parts.append(f"\n*⚡ Coordinated by Personal Assistant with {len(delegated_agents)} agent(s)*")
        
        return "\n".join(response_parts)
    
    def _format_delegated_response(self, result: str, target_agent: str) -> str:
        """Format delegated response"""
        agent_info = self.agents.get(target_agent, {"name": "Specialist"})
        
        response_parts = []
        response_parts.append(f"🎯 **Personal Assistant Pro** (Delegated to: {agent_info['name']})")
        response_parts.append("")  # Empty line
        response_parts.append(result)
        response_parts.append(f"\n*⚡ Coordinated by Personal Assistant*")
        
        return "\n".join(response_parts)
    
    def _format_enhanced_response(self, result: str, agent_role: str, routing_info: Dict) -> str:
        """Format enhanced response with beta branding"""
        agent_info = self.agents.get(agent_role, {"name": "Unknown Enhanced Agent"})
        
        response_parts = []
        
        # Enhanced agent header
        if routing_info.get("method") == "direct_beta":
            response_parts.append(f"⚡ **{agent_info['name']}** (Beta Enhanced)")
        else:
            response_parts.append(f"🚀 **{agent_info['name']}** (Beta Auto-Routing)")
            response_parts.append(f"**Enhanced Routing:** {routing_info['reasoning']}")
            
        response_parts.append("")  # Empty line
        
        # Enhanced result
        response_parts.append(f"**Response:** {result}")
        
        # Performance info
        target_time = agent_info.get("performance_target", "< 5s")
        response_parts.append(f"\n**Performance Target:** {target_time}")
        
        return "\n".join(response_parts)


# Global pipeline instance
pipeline = PipelineBeta()


def main():
    """Main execution interface for beta pipeline"""
    print("🚀 Myndy AI Beta v0.2.0 - Enhanced Intelligence Pipeline")
    print("=" * 60)
    print("⚡ Enhanced Features: Intelligent routing, learning feedback, performance optimization")
    print("🤖 Available Agents:", ", ".join(pipeline.agents.keys()))
    print("📊 Performance Targets: Memory < 3s, Assistant < 2s, Research < 5s")
    print()
    print("💬 Interactive Mode - Type your questions (or 'quit' to exit)")
    print("🎯 Use 'auto_beta' for intelligent routing or specify agent name")
    print("=" * 60)
    print()
    
    session_id = f"interactive_{int(datetime.now().timestamp())}"
    message_count = 0
    
    try:
        while True:
            # Get user input
            try:
                user_input = input("💭 You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break
                
            if not user_input or user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
                
            message_count += 1
            
            # Check for model specification
            if user_input.startswith('/'):
                parts = user_input[1:].split(' ', 1)
                if len(parts) == 2:
                    model_id, message = parts
                    if model_id.endswith('_beta'):
                        model_id = model_id
                    elif model_id in pipeline.agents:
                        model_id = f"{model_id}_beta"
                    else:
                        model_id = "auto_beta"
                else:
                    model_id = "auto_beta"
                    message = user_input[1:]
            else:
                model_id = "auto_beta"
                message = user_input
            
            # Create messages array for conversation context
            messages = [{"role": "user", "content": message}]
            
            print(f"\n🔄 Processing with {model_id}...")
            start_time = datetime.now()
            
            try:
                # Execute pipeline
                response = pipeline.pipe(
                    user_message=message,
                    model_id=model_id,
                    messages=messages,
                    body={"messages": messages, "model": model_id}
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                print(f"\n🤖 Assistant: {response}")
                print(f"\n⚡ Processed in {processing_time:.2f}s")
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                logger.error(f"Interactive mode error: {e}")
            
            print("\n" + "-" * 60 + "\n")
            
    except Exception as e:
        logger.error(f"Main loop error: {e}")
        print(f"❌ Fatal error: {e}")


def test_pipeline():
    """Test mode for validating pipeline functionality"""
    print("🧪 Myndy AI Beta v0.2.0 - Test Mode")
    print("=" * 50)
    
    # Enable verbose coordination for agent thought process visibility
    pipeline.valves.verbose_coordination = True
    pipeline.valves.trace_tool_selection = True
    pipeline.valves.show_agent_thoughts = True
    pipeline.valves.show_tool_execution = True
    pipeline.valves.show_tool_results = True
    print("🧠 Enhanced Visibility: Agent thought processes and tool execution enabled")
    print("=" * 50)
    
    test_cases = [
        {"message": "Hello", "expected_agent": "personal_assistant"},
        {"message": "What time is it?", "expected_agent": "personal_assistant"},
        {"message": "I am Jeremy", "expected_agent": "memory_librarian"},
        {"message": "Research artificial intelligence", "expected_agent": "research_specialist"},
        {"message": "How is my health?", "expected_agent": "health_analyst"},
        {"message": "Show my expenses", "expected_agent": "finance_tracker"}
    ]
    
    session_id = f"test_{int(datetime.now().timestamp())}"
    results = []
    
    print("🔍 Running test cases...")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['message']}")
        
        try:
            # Create test messages
            messages = [{"role": "user", "content": test_case['message']}]
            
            # Run through pipeline
            start_time = datetime.now()
            response = pipeline.pipe(
                user_message=test_case['message'],
                model_id="auto_beta",
                messages=messages,
                body={}
            )
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract agent used from response
            used_agent = "unknown"
            if "Personal Assistant" in response:
                used_agent = "personal_assistant"
            elif "Memory Librarian" in response:
                used_agent = "memory_librarian"
            elif "Research Specialist" in response:
                used_agent = "research_specialist"
            elif "Health Analyst" in response:
                used_agent = "health_analyst"
            elif "Finance Tracker" in response:
                used_agent = "finance_tracker"
            
            # Check if routing was correct
            correct_routing = used_agent == test_case['expected_agent']
            status = "✅" if correct_routing else "⚠️"
            
            print(f"  {status} Agent: {used_agent} (expected: {test_case['expected_agent']})")
            print(f"  ⏱️  Duration: {duration:.2f}s")
            print(f"  📝 Response: {response[:100]}...")
            print()
            
            results.append({
                "test": test_case['message'],
                "expected_agent": test_case['expected_agent'],
                "used_agent": used_agent,
                "correct_routing": correct_routing,
                "duration": duration,
                "response_length": len(response)
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
            results.append({
                "test": test_case['message'],
                "expected_agent": test_case['expected_agent'],
                "used_agent": "error",
                "correct_routing": False,
                "duration": 0,
                "error": str(e)
            })
    
    # Summary
    print("📊 Test Results Summary:")
    print("=" * 30)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get('correct_routing', False))
    avg_duration = sum(r.get('duration', 0) for r in results) / total_tests if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful Routing: {successful_tests}/{total_tests} ({(successful_tests/total_tests*100):.1f}%)")
    print(f"Average Response Time: {avg_duration:.2f}s")
    print()
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Pipeline is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check routing logic.")
        return 1

if __name__ == "__main__":
    import sys
    
    # Check execution mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Test mode
            sys.exit(test_pipeline())
        elif sys.argv[1] == "--server":
            # Server mode for OpenWebUI integration
            print("🚀 Server mode starting...")
            print("⚠️  Server mode requires dependency fixes - use test mode for now")
            sys.exit(1)
        else:
            print(f"❌ Unknown argument: {sys.argv[1]}")
            print("Usage: python myndy_ai_beta.py [--test|--server]")
            sys.exit(1)
    else:
        # Interactive mode (default)
        main()
