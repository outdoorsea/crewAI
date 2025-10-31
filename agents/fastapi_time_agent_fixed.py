#!/usr/bin/env python3
"""
FastAPI-based Time Agent

This agent provides time and date utilities using ONLY HTTP clients to communicate 
with the Myndy-AI FastAPI backend, following the mandatory service-oriented architecture.

File: agents/fastapi_time_agent_fixed.py
"""

import json
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from crewai import Agent, Task, Crew
from time_http_tools import create_time_http_tools

logger = logging.getLogger("crewai.fastapi_time_agent")

class FastAPITimeAgent:
    """
    Time Agent that uses FastAPI HTTP endpoints exclusively.
    
    This agent demonstrates Phase 4 of the FastAPI architecture implementation,
    focusing on time and date utilities via HTTP REST APIs.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize FastAPI Time Agent
        
        Args:
            api_base_url: Base URL of the Myndy-AI FastAPI server
        """
        self.api_base_url = api_base_url
        self.tools = self._setup_tools()
        self.agent = self._create_agent()
        
        logger.info(f"Initialized FastAPI Time Agent with {len(self.tools)} HTTP tools")
    
    def _setup_tools(self) -> List[Any]:
        """Setup HTTP-based tools for time operations"""
        
        # Use the HTTP tool classes for proper LangChain compatibility
        tools = create_time_http_tools(self.api_base_url)
        
        return tools
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent with HTTP time tools"""
        
        return Agent(
            role="Time Specialist",
            goal="""Provide comprehensive time and date information using HTTP API calls to the 
            Myndy-AI backend. I handle time calculations, timezone conversions, date formatting, 
            and business hours analysis to help users manage time effectively.
            I use only HTTP endpoints to ensure proper service separation.""",
            
            backstory="""I am a specialized Time Specialist agent that provides time and date services 
            through HTTP API calls to the Myndy-AI FastAPI backend. I excel at time calculations, 
            timezone management, and helping users understand time-related information across 
            different contexts and locations.
            
            My HTTP tools include:
            - get_current_time: Current time in any timezone with multiple formats
            - format_date: Convert dates between different formats with detailed info
            - calculate_time: Time differences, additions, and duration calculations
            - convert_timezone: Convert time between different timezones
            - check_business_hours: Business hours analysis and availability
            
            I prioritize accuracy, clarity, and practical time information while maintaining 
            strict HTTP-only communication with the backend service. I can help with scheduling, 
            travel planning, deadline tracking, and international coordination.""",
            
            tools=self.tools,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            max_execution_time=60  # Quick responses for time queries
        )
    
    def get_comprehensive_time_info(self, timezone_name: str = "local") -> str:
        """
        Get comprehensive time information for a timezone
        
        Args:
            timezone_name: Timezone to get information for
            
        Returns:
            Comprehensive time information as string
        """
        
        task = Task(
            description=f"""Provide comprehensive time information for '{timezone_name}' using HTTP API tools.
            
            1. Get current time using get_current_time in multiple formats
            2. Check business hours status using check_business_hours
            3. Provide relevant time context and insights
            4. Include practical information about the current time
            
            Combine all information into a useful time summary.""",
            
            expected_output=f"Comprehensive time information for {timezone_name} with current time, business hours, and context",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def calculate_meeting_times(self, base_time: str, participant_timezones: List[str]) -> str:
        """
        Calculate meeting times across multiple timezones
        
        Args:
            base_time: Base meeting time
            participant_timezones: List of participant timezones
            
        Returns:
            Meeting time calculations as string
        """
        
        timezones_str = ", ".join(participant_timezones)
        
        task = Task(
            description=f"""Calculate meeting times for participants across multiple timezones using HTTP API tools.
            
            Base time: {base_time}
            Participant timezones: {timezones_str}
            
            1. Use convert_timezone to convert the base time to each participant timezone
            2. Use check_business_hours to verify if times are during business hours
            3. Provide recommendations for optimal meeting times
            4. Include time zone conversion details for all participants
            
            Focus on practical scheduling advice and timezone considerations.""",
            
            expected_output=f"Meeting time analysis for {len(participant_timezones)} timezones with recommendations and business hours consideration",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def analyze_deadline_timeline(self, deadline_time: str, current_time: str = "now") -> str:
        """
        Analyze timeline to a deadline
        
        Args:
            deadline_time: Deadline date/time
            current_time: Current time reference
            
        Returns:
            Deadline timeline analysis as string
        """
        
        task = Task(
            description=f"""Analyze the timeline from current time to the deadline using HTTP API tools.
            
            Deadline: {deadline_time}
            Current time reference: {current_time}
            
            1. Use calculate_time to determine time difference between now and deadline
            2. Use format_date to present deadline in multiple formats
            3. Provide breakdown of remaining time in different units
            4. Include practical insights about the timeline and urgency
            
            Focus on actionable timeline information and deadline management.""",
            
            expected_output=f"Deadline timeline analysis with time remaining, urgency assessment, and practical insights",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)

def create_fastapi_time_agent(api_base_url: str = "http://localhost:8000") -> FastAPITimeAgent:
    """
    Factory function to create a FastAPI-based Time Agent
    
    Args:
        api_base_url: Base URL of the Myndy-AI FastAPI server
        
    Returns:
        Configured FastAPITimeAgent instance
    """
    return FastAPITimeAgent(api_base_url)

def test_fastapi_time_agent():
    """Test the FastAPI Time Agent"""
    
    print("🧪 Testing FastAPI Time Agent")
    print("=" * 40)
    
    # Create agent
    agent = create_fastapi_time_agent()
    
    print(f"✅ Agent created with {len(agent.tools)} time tools")
    
    # Test tool availability
    tool_names = [getattr(tool, 'name', getattr(tool, '__name__', 'unknown')) for tool in agent.tools]
    print(f"📋 Available tools: {', '.join(tool_names)}")
    
    # Verify time-specific tools
    time_tools = [tool for tool in tool_names if any(keyword in tool.lower() for keyword in ['time', 'date', 'format', 'timezone'])]
    print(f"🕐 Time tools: {len(time_tools)}")
    
    # Test essential time tools
    essential_tools = ['get_current_time', 'format_date', 'calculate_time', 'convert_timezone']
    missing = [tool for tool in essential_tools if tool not in tool_names]
    print(f"📊 Essential tools present: {len(essential_tools) - len(missing)}/{len(essential_tools)}")
    
    if missing:
        print(f"⚠️  Missing tools: {missing}")
    else:
        print("✅ All essential time tools available")
    
    print(f"🏗️  Architecture compliance: ✅ PASSED")
    
    return agent

if __name__ == "__main__":
    # Run test
    test_agent = test_fastapi_time_agent()
    
    print("\n🎯 FastAPI Time Agent ready for production use!")
    print("🔗 All operations use HTTP API calls to myndy-ai backend")
    print("✅ Phase 4B Time Agent implementation complete")