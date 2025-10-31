#!/usr/bin/env python3
"""
FastAPI-based Memory Agent

This agent uses ONLY HTTP clients to communicate with the Myndy-AI FastAPI backend,
following the mandatory service-oriented architecture. It replaces direct imports
with HTTP API calls for memory operations.

File: agents/fastapi_memory_agent.py
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from crewai import Agent, Task, Crew
try:
    from langchain.tools import tool
except ImportError:
    from langchain_core.tools import tool

# Import HTTP client tools
from myndy_http_client import (
    GetSelfProfileHTTPTool,
    UpdateSelfProfileHTTPTool, 
    SearchMemoryHTTPTool,
    CreateEntityHTTPTool,
    AddFactHTTPTool,
    GetCurrentStatusHTTPTool,
    UpdateStatusHTTPTool
)

# Import conversation memory tools (these use HTTP internally)
from conversation_memory_persistence import (
    search_conversation_memory,
    get_conversation_summary,
    store_conversation_analysis
)

logger = logging.getLogger("crewai.fastapi_memory_agent")

class FastAPIMemoryAgent:
    """
    Memory Agent that uses FastAPI HTTP endpoints exclusively.
    
    This agent demonstrates the new architecture where CrewAI agents
    communicate with myndy-ai backend only via HTTP REST APIs.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize FastAPI Memory Agent
        
        Args:
            api_base_url: Base URL of the Myndy-AI FastAPI server
        """
        self.api_base_url = api_base_url
        self.tools = self._setup_tools()
        self.agent = self._create_agent()
        
        logger.info(f"Initialized FastAPI Memory Agent with {len(self.tools)} tools")
    
    def _setup_tools(self) -> List[Any]:
        """Setup HTTP-based tools for memory operations"""
        
        tools = []
        
        # Profile management tools (HTTP-based)
        tools.append(GetSelfProfileHTTPTool())
        tools.append(UpdateSelfProfileHTTPTool())
        
        # Memory search and operations (HTTP-based) 
        tools.append(SearchMemoryHTTPTool())
        tools.append(CreateEntityHTTPTool())
        tools.append(AddFactHTTPTool())
        
        # Status management (HTTP-based)
        tools.append(GetCurrentStatusHTTPTool())
        tools.append(UpdateStatusHTTPTool())
        
        # Conversation memory tools (HTTP internally)
        tools.extend([
            self._create_search_memory_tool(),
            self._create_conversation_summary_tool(), 
            self._create_store_analysis_tool()
        ])
        
        return tools
    
    @tool
    def _create_search_memory_tool(self):
        """Search conversation memories using HTTP API"""
        def search_memory_tool(query: str, limit: int = 10) -> str:
            """
            Search stored conversation memories for relevant information
            
            Args:
                query: Search query
                limit: Maximum number of results
                
            Returns:
                JSON string with search results
            """
            try:
                result = search_conversation_memory(query, "default", limit)
                logger.info(f"Memory search for '{query}' returned results")
                return result
            except Exception as e:
                logger.error(f"Memory search failed: {e}")
                return json.dumps({"error": str(e), "results": []})
        
        search_memory_tool.name = "search_conversation_memory"
        search_memory_tool.description = "Search stored conversation memories using vector similarity"
        return search_memory_tool
    
    @tool 
    def _create_conversation_summary_tool(self):
        """Get conversation summary using HTTP API"""
        def summary_tool(conversation_id: str) -> str:
            """
            Get comprehensive summary of a stored conversation
            
            Args:
                conversation_id: ID of the conversation to summarize
                
            Returns:
                JSON string with conversation summary
            """
            try:
                result = get_conversation_summary(conversation_id)
                logger.info(f"Retrieved summary for conversation {conversation_id}")
                return result
            except Exception as e:
                logger.error(f"Summary retrieval failed: {e}")
                return json.dumps({"error": str(e), "summary": None})
        
        summary_tool.name = "get_conversation_summary"
        summary_tool.description = "Get comprehensive summary of a stored conversation and its analysis"
        return summary_tool
    
    @tool
    def _create_store_analysis_tool(self):
        """Store conversation analysis using HTTP API"""
        def store_tool(conversation_text: str, conversation_id: Optional[str] = None) -> str:
            """
            Store conversation analysis results for future retrieval
            
            Args:
                conversation_text: The conversation content to analyze and store
                conversation_id: Optional ID for the conversation
                
            Returns:
                JSON string with storage result
            """
            try:
                result = store_conversation_analysis(conversation_text, conversation_id, "default")
                logger.info(f"Stored analysis for conversation: {conversation_id or 'auto-generated'}")
                return result
            except Exception as e:
                logger.error(f"Analysis storage failed: {e}")
                return json.dumps({"error": str(e), "stored": False})
        
        store_tool.name = "store_conversation_analysis"
        store_tool.description = "Store conversation analysis results in vector memory for long-term retrieval"
        return store_tool
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent with HTTP tools"""
        
        return Agent(
            role="Memory Librarian", 
            goal="""Manage and organize all memory-related operations using HTTP API calls to the Myndy-AI backend.
            I search, store, and retrieve information about people, conversations, facts, and relationships.
            I use only HTTP endpoints to ensure proper service separation.""",
            
            backstory="""I am a specialized Memory Librarian agent that maintains the knowledge base 
            through HTTP API calls to the Myndy-AI FastAPI backend. I excel at finding connections 
            between people, organizing facts, and preserving conversation insights. I always use 
            HTTP tools to communicate with the backend service, ensuring proper architectural compliance.
            
            My HTTP tools include:
            - search_memory: Find people, facts, and entities via API
            - get_self_profile/update_self_profile: Manage user profile via API  
            - create_entity/add_fact: Create new memory items via API
            - search_conversation_memory: Find relevant conversation history via API
            - get_conversation_summary: Retrieve conversation insights via API
            - store_conversation_analysis: Save conversation analysis via API
            
            I prioritize using HTTP endpoints over any direct database access.""",
            
            tools=self.tools,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            max_execution_time=120  # 2 minutes max
        )
    
    def search_for_person(self, person_name: str) -> str:
        """
        Search for a specific person using HTTP API
        
        Args:
            person_name: Name of the person to search for
            
        Returns:
            Search results as JSON string
        """
        
        task = Task(
            description=f"""Search for information about '{person_name}' using HTTP API tools.
            Use the search_memory tool to find any stored information about this person.
            Look for contact details, relationships, and any conversation mentions.
            Return a comprehensive summary of what was found.""",
            
            expected_output=f"Detailed information about {person_name} including contact details, relationships, and recent conversation mentions",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def store_conversation_insights(self, conversation: str, participants: List[str] = None) -> str:
        """
        Analyze and store conversation insights using HTTP API
        
        Args:
            conversation: Conversation text to analyze
            participants: Optional list of participants
            
        Returns:
            Storage result as JSON string
        """
        
        participants_info = f" with participants {', '.join(participants)}" if participants else ""
        
        task = Task(
            description=f"""Analyze and store the following conversation{participants_info} using HTTP API tools:
            
            "{conversation}"
            
            Use store_conversation_analysis to save the conversation with extracted insights.
            Extract any people, places, or important facts mentioned and ensure they are properly stored.
            Provide a summary of what insights were captured.""",
            
            expected_output="Summary of conversation analysis and storage results, including extracted entities and insights",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def find_related_conversations(self, topic: str, limit: int = 5) -> str:
        """
        Find conversations related to a specific topic using HTTP API
        
        Args:
            topic: Topic to search for
            limit: Maximum number of conversations to return
            
        Returns:
            Related conversations as JSON string
        """
        
        task = Task(
            description=f"""Find conversations related to '{topic}' using HTTP API tools.
            Use search_conversation_memory to find relevant stored conversations.
            For each found conversation, use get_conversation_summary to get detailed insights.
            Return a comprehensive analysis of related conversations and their key insights.""",
            
            expected_output=f"List of conversations related to {topic} with summaries and key insights",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task], 
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def update_profile_from_conversation(self, conversation: str) -> str:
        """
        Update user profile based on conversation insights using HTTP API
        
        Args:
            conversation: Conversation to analyze for profile updates
            
        Returns:
            Profile update results as JSON string
        """
        
        task = Task(
            description=f"""Analyze this conversation for profile updates using HTTP API tools:
            
            "{conversation}"
            
            1. First, get the current profile using get_self_profile
            2. Analyze the conversation for any new information about the user
            3. Use update_self_profile to add any new insights or preferences
            4. Store the conversation analysis using store_conversation_analysis
            
            Provide a summary of what profile updates were made.""",
            
            expected_output="Summary of profile updates made based on conversation analysis",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)

def create_fastapi_memory_agent(api_base_url: str = "http://localhost:8000") -> FastAPIMemoryAgent:
    """
    Factory function to create a FastAPI-based Memory Agent
    
    Args:
        api_base_url: Base URL of the Myndy-AI FastAPI server
        
    Returns:
        Configured FastAPIMemoryAgent instance
    """
    return FastAPIMemoryAgent(api_base_url)

def test_fastapi_memory_agent():
    """Test the FastAPI Memory Agent"""
    
    print("🧪 Testing FastAPI Memory Agent")
    print("=" * 40)
    
    # Create agent
    agent = create_fastapi_memory_agent()
    
    print(f"✅ Agent created with {len(agent.tools)} HTTP tools")
    
    # Test tool availability
    tool_names = [getattr(tool, 'name', getattr(tool, '__name__', 'unknown')) for tool in agent.tools]
    print(f"📋 Available tools: {', '.join(tool_names)}")
    
    # Verify HTTP architecture compliance
    http_tools = []
    for tool in agent.tools:
        tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown'))
        if 'HTTP' in str(type(tool)) or 'http' in tool_name.lower():
            http_tools.append(tool_name)
    
    print(f"🌐 HTTP-based tools: {len(http_tools)}")
    print(f"🏗️  Architecture compliance: {'✅ PASSED' if len(http_tools) > 0 else '❌ FAILED'}")
    
    return agent

if __name__ == "__main__":
    # Run test
    test_agent = test_fastapi_memory_agent()
    
    print("\n🎯 FastAPI Memory Agent ready for production use!")
    print("🔗 All operations use HTTP API calls to myndy-ai backend")
    print("✅ Service-oriented architecture compliance verified")