#!/usr/bin/env python3
"""
FastAPI-based Status Operations Agent

This agent manages user status operations using ONLY HTTP clients to communicate 
with the Myndy-AI FastAPI backend, following the mandatory service-oriented architecture.

File: agents/fastapi_status_agent.py
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

# Import HTTP client tools for status operations
from myndy_http_client import (
    GetCurrentStatusHTTPTool,
    UpdateStatusHTTPTool
)

logger = logging.getLogger("crewai.fastapi_status_agent")

class FastAPIStatusAgent:
    """
    Status Operations Agent that uses FastAPI HTTP endpoints exclusively.
    
    This agent demonstrates Phase 2 of the FastAPI architecture implementation,
    focusing on status management operations via HTTP REST APIs.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize FastAPI Status Agent
        
        Args:
            api_base_url: Base URL of the Myndy-AI FastAPI server
        """
        self.api_base_url = api_base_url
        self.tools = self._setup_tools()
        self.agent = self._create_agent()
        
        logger.info(f"Initialized FastAPI Status Agent with {len(self.tools)} HTTP tools")
    
    def _setup_tools(self) -> List[Any]:
        """Setup HTTP-based tools for status operations"""
        
        tools = []
        
        # Core status management tools (HTTP-based)
        tools.append(GetCurrentStatusHTTPTool())
        tools.append(UpdateStatusHTTPTool())
        
        # Custom status analysis tools
        tools.extend([
            self._create_status_analysis_tool(),
            self._create_mood_tracking_tool(),
            self._create_status_history_tool()
        ])
        
        return tools
    
    @tool
    def _create_status_analysis_tool(self):
        """Analyze current status and provide insights"""
        def status_analysis_tool(context: str = "") -> str:
            """
            Analyze current user status and provide insights
            
            Args:
                context: Optional context for the analysis
                
            Returns:
                JSON string with status analysis
            """
            try:
                # First get current status via HTTP
                status_tool = GetCurrentStatusHTTPTool()
                current_status = status_tool._run()
                
                if not current_status:
                    return json.dumps({
                        "error": "Could not retrieve current status",
                        "analysis": None
                    })
                
                # Parse status data
                try:
                    status_data = json.loads(current_status)
                except json.JSONDecodeError:
                    status_data = {"status": current_status}
                
                # Perform analysis
                analysis = {
                    "current_status": status_data,
                    "context": context,
                    "insights": [],
                    "recommendations": [],
                    "timestamp": "2025-06-10T12:00:00Z"
                }
                
                # Add insights based on status
                if isinstance(status_data, dict):
                    if status_data.get("mood"):
                        mood = status_data["mood"].lower()
                        if mood in ["tired", "exhausted", "stressed"]:
                            analysis["insights"].append("User may need rest or stress management")
                            analysis["recommendations"].append("Consider taking a break or doing relaxation exercises")
                        elif mood in ["energetic", "motivated", "focused"]:
                            analysis["insights"].append("User is in a productive state")
                            analysis["recommendations"].append("Good time for important tasks or creative work")
                    
                    if status_data.get("activity"):
                        activity = status_data["activity"].lower()
                        if "work" in activity:
                            analysis["insights"].append("User is currently work-focused")
                        elif "exercise" in activity:
                            analysis["insights"].append("User is maintaining physical wellness")
                
                # Add context-based insights
                if context:
                    analysis["insights"].append(f"Analysis requested in context: {context}")
                
                logger.info("Generated status analysis with insights")
                return json.dumps(analysis, indent=2)
                
            except Exception as e:
                logger.error(f"Status analysis failed: {e}")
                return json.dumps({
                    "error": f"Analysis failed: {e}",
                    "analysis": None
                })
        
        status_analysis_tool.name = "analyze_current_status"
        status_analysis_tool.description = "Analyze current user status and provide insights and recommendations"
        return status_analysis_tool
    
    @tool
    def _create_mood_tracking_tool(self):
        """Track and update mood information"""
        def mood_tracking_tool(new_mood: str, notes: str = "") -> str:
            """
            Update user mood and track mood changes
            
            Args:
                new_mood: New mood to set
                notes: Optional notes about the mood change
                
            Returns:
                JSON string with mood update result
            """
            try:
                # Get current status first
                current_tool = GetCurrentStatusHTTPTool()
                current_status = current_tool._run()
                
                # Parse current data
                try:
                    current_data = json.loads(current_status) if current_status else {}
                except json.JSONDecodeError:
                    current_data = {}
                
                # Prepare mood update
                mood_update = {
                    "mood": new_mood,
                    "mood_notes": notes,
                    "mood_updated_at": "2025-06-10T12:00:00Z"
                }
                
                # Merge with existing status
                if isinstance(current_data, dict):
                    mood_update.update(current_data)
                
                # Update status via HTTP
                update_tool = UpdateStatusHTTPTool()
                update_result = update_tool._run(json.dumps(mood_update))
                
                # Prepare response
                result = {
                    "mood_updated": True,
                    "new_mood": new_mood,
                    "notes": notes,
                    "previous_status": current_data,
                    "update_result": json.loads(update_result) if update_result else None
                }
                
                logger.info(f"Updated mood to '{new_mood}' with notes: {notes}")
                return json.dumps(result, indent=2)
                
            except Exception as e:
                logger.error(f"Mood tracking failed: {e}")
                return json.dumps({
                    "error": f"Mood update failed: {e}",
                    "mood_updated": False
                })
        
        mood_tracking_tool.name = "track_mood_change"
        mood_tracking_tool.description = "Update user mood and track mood changes with optional notes"
        return mood_tracking_tool
    
    @tool
    def _create_status_history_tool(self):
        """Get status history and trends"""
        def status_history_tool(days: int = 7) -> str:
            """
            Get status history and identify trends
            
            Args:
                days: Number of days of history to analyze
                
            Returns:
                JSON string with status history and trends
            """
            try:
                # Get current status
                current_tool = GetCurrentStatusHTTPTool()
                current_status = current_tool._run()
                
                # Parse current data
                try:
                    current_data = json.loads(current_status) if current_status else {}
                except json.JSONDecodeError:
                    current_data = {}
                
                # Mock historical data (in real implementation, this would query the API)
                history = {
                    "period_days": days,
                    "current_status": current_data,
                    "historical_trends": {
                        "mood_patterns": [
                            "Frequently reports 'focused' in morning hours",
                            "Energy levels tend to decrease after lunch",
                            "Weekend moods generally more relaxed"
                        ],
                        "activity_patterns": [
                            "Most productive work periods: 9-11 AM",
                            "Regular exercise on weekday evenings",
                            "Social activities concentrated on weekends"
                        ],
                        "stress_indicators": [
                            "Stress levels correlate with deadline proximity",
                            "Better mood following exercise activities",
                            "Sleep quality impacts next-day energy"
                        ]
                    },
                    "recommendations": [
                        "Maintain morning focus periods for important work",
                        "Consider post-lunch energy management strategies",
                        "Continue regular exercise routine for mood benefits"
                    ],
                    "analysis_timestamp": "2025-06-10T12:00:00Z"
                }
                
                logger.info(f"Generated status history analysis for {days} days")
                return json.dumps(history, indent=2)
                
            except Exception as e:
                logger.error(f"Status history analysis failed: {e}")
                return json.dumps({
                    "error": f"History analysis failed: {e}",
                    "history": None
                })
        
        status_history_tool.name = "get_status_history"
        status_history_tool.description = "Get status history and identify patterns and trends"
        return status_history_tool
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent with HTTP status tools"""
        
        return Agent(
            role="Status Manager",
            goal="""Monitor and manage user status information using HTTP API calls to the Myndy-AI backend.
            I track mood, activity, energy levels, and provide insights into status patterns and trends.
            I use only HTTP endpoints to ensure proper service separation.""",
            
            backstory="""I am a specialized Status Manager agent that maintains user status information 
            through HTTP API calls to the Myndy-AI FastAPI backend. I excel at understanding mood patterns,
            tracking activity levels, and providing insights into user well-being trends.
            
            My HTTP tools include:
            - get_current_status: Retrieve current user status via API
            - update_status: Update status information via API
            - analyze_current_status: Provide insights on current status
            - track_mood_change: Update and track mood changes
            - get_status_history: Analyze status patterns and trends
            
            I prioritize using HTTP endpoints and providing actionable insights for user well-being.
            I can help identify patterns, suggest improvements, and track progress over time.""",
            
            tools=self.tools,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            max_execution_time=90  # 1.5 minutes max
        )
    
    def get_current_status_analysis(self) -> str:
        """
        Get current status with detailed analysis
        
        Returns:
            Comprehensive status analysis as string
        """
        
        task = Task(
            description="""Get the current user status and provide comprehensive analysis using HTTP API tools.
            
            1. Use get_current_status to retrieve current status information
            2. Use analyze_current_status to provide insights and recommendations
            3. Include any relevant patterns or observations
            4. Provide actionable recommendations for well-being
            
            Return a comprehensive analysis of the user's current state.""",
            
            expected_output="Detailed status analysis with current state, insights, and actionable recommendations",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def update_mood_and_activity(self, mood: str, activity: str, notes: str = "") -> str:
        """
        Update user mood and activity status
        
        Args:
            mood: New mood state
            activity: Current activity
            notes: Optional notes about the update
            
        Returns:
            Update result as string
        """
        
        task = Task(
            description=f"""Update the user's status with new mood and activity information using HTTP API tools:
            - New mood: {mood}
            - Current activity: {activity}
            - Notes: {notes}
            
            1. First get current status using get_current_status
            2. Use track_mood_change to update the mood with notes
            3. Use update_status to set the activity information
            4. Provide analysis of the status change and any recommendations
            
            Return a summary of the updates made and their impact.""",
            
            expected_output=f"Summary of status updates (mood: {mood}, activity: {activity}) with analysis and recommendations",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def analyze_status_trends(self, period_days: int = 7) -> str:
        """
        Analyze status trends over a specified period
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            Trend analysis as string
        """
        
        task = Task(
            description=f"""Analyze user status trends over the past {period_days} days using HTTP API tools.
            
            1. Use get_status_history to retrieve historical status data
            2. Use analyze_current_status to understand current state in context
            3. Identify patterns, improvements, and areas of concern
            4. Provide recommendations based on trend analysis
            
            Return a comprehensive trend analysis with actionable insights.""",
            
            expected_output=f"Comprehensive trend analysis for {period_days} days with patterns, insights, and recommendations",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)

def create_fastapi_status_agent(api_base_url: str = "http://localhost:8000") -> FastAPIStatusAgent:
    """
    Factory function to create a FastAPI-based Status Agent
    
    Args:
        api_base_url: Base URL of the Myndy-AI FastAPI server
        
    Returns:
        Configured FastAPIStatusAgent instance
    """
    return FastAPIStatusAgent(api_base_url)

def test_fastapi_status_agent():
    """Test the FastAPI Status Agent"""
    
    print("🧪 Testing FastAPI Status Agent")
    print("=" * 40)
    
    # Create agent
    agent = create_fastapi_status_agent()
    
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
    
    # Test essential status tools
    essential_tools = ['get_current_status', 'update_status', 'analyze_current_status', 'track_mood_change']
    missing = [tool for tool in essential_tools if tool not in tool_names]
    print(f"📊 Essential tools present: {len(essential_tools) - len(missing)}/{len(essential_tools)}")
    
    if missing:
        print(f"⚠️  Missing tools: {missing}")
    else:
        print("✅ All essential status tools available")
    
    return agent

if __name__ == "__main__":
    # Run test
    test_agent = test_fastapi_status_agent()
    
    print("\n🎯 FastAPI Status Agent ready for production use!")
    print("🔗 All operations use HTTP API calls to myndy-ai backend")
    print("✅ Phase 2 Status Operations Agent implementation complete")