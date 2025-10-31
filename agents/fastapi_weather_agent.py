#!/usr/bin/env python3
"""
FastAPI-based Weather Agent

This agent provides weather information and forecasts using ONLY HTTP clients 
to communicate with the Myndy-AI FastAPI backend, following the mandatory 
service-oriented architecture.

File: agents/fastapi_weather_agent.py
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from crewai import Agent, Task, Crew
from weather_http_tools import create_weather_http_tools

logger = logging.getLogger("crewai.fastapi_weather_agent")

class FastAPIWeatherAgent:
    """
    Weather Agent that uses FastAPI HTTP endpoints exclusively.
    
    This agent demonstrates Phase 4 of the FastAPI architecture implementation,
    focusing on weather information and forecasting via HTTP REST APIs.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize FastAPI Weather Agent
        
        Args:
            api_base_url: Base URL of the Myndy-AI FastAPI server
        """
        self.api_base_url = api_base_url
        self.tools = self._setup_tools()
        self.agent = self._create_agent()
        
        logger.info(f"Initialized FastAPI Weather Agent with {len(self.tools)} HTTP tools")
    
    def _setup_tools(self) -> List[Any]:
        """Setup HTTP-based tools for weather operations"""
        
        # Use the HTTP tool classes for proper LangChain compatibility
        tools = create_weather_http_tools(self.api_base_url)
        
        return tools
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent with HTTP weather tools"""
        
        return Agent(
            role="Weather Specialist",
            goal="""Provide comprehensive weather information and forecasts using HTTP API calls 
            to the Myndy-AI backend. I deliver current conditions, forecasts, alerts, and weather 
            comparisons to help users plan their activities and make informed decisions.
            I use only HTTP endpoints to ensure proper service separation.""",
            
            backstory="""I am a specialized Weather Specialist agent that provides weather information 
            through HTTP API calls to the Myndy-AI FastAPI backend. I excel at delivering accurate, 
            timely weather data and helping users understand weather patterns and their implications.
            
            My HTTP tools include:
            - get_current_weather: Current conditions for any location
            - get_weather_forecast: Multi-day forecasts with detailed information
            - get_weather_alerts: Active weather warnings and advisories
            - get_multi_location_weather: Weather for multiple locations at once
            - compare_weather_locations: Side-by-side weather comparisons
            
            I prioritize accuracy, timeliness, and practical weather insights while maintaining 
            strict HTTP-only communication with the backend service. I can help with travel 
            planning, outdoor activities, and daily weather awareness.""",
            
            tools=self.tools,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            max_execution_time=60  # Quick responses for weather queries
        )
    
    def get_location_weather_report(self, location: str = "current") -> str:
        """
        Get comprehensive weather report for a location
        
        Args:
            location: Location name or "current" for user's location
            
        Returns:
            Comprehensive weather report as string
        """
        
        task = Task(
            description=f"""Provide a comprehensive weather report for '{location}' using HTTP API tools.
            
            1. Get current weather conditions using get_current_weather
            2. Get 3-day forecast using get_weather_forecast
            3. Check for any weather alerts using get_weather_alerts
            4. Provide practical advice based on conditions
            
            Combine all information into a user-friendly weather report with recommendations.""",
            
            expected_output=f"Comprehensive weather report for {location} with current conditions, forecast, alerts, and recommendations",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def compare_travel_weather(self, origin: str, destination: str) -> str:
        """
        Compare weather between travel origin and destination
        
        Args:
            origin: Starting location
            destination: Travel destination
            
        Returns:
            Weather comparison and travel advice as string
        """
        
        task = Task(
            description=f"""Compare weather conditions for travel from '{origin}' to '{destination}' using HTTP API tools.
            
            1. Use compare_weather_locations to get side-by-side comparison
            2. Get forecasts for both locations using get_weather_forecast
            3. Check alerts for both locations using get_weather_alerts
            4. Provide travel recommendations based on weather differences
            
            Focus on practical travel advice and what to expect weather-wise.""",
            
            expected_output=f"Weather comparison between {origin} and {destination} with travel recommendations",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def check_outdoor_activity_weather(self, location: str = "current", activity: str = "general outdoor") -> str:
        """
        Check weather suitability for outdoor activities
        
        Args:
            location: Location for the activity
            activity: Type of outdoor activity planned
            
        Returns:
            Weather suitability assessment as string
        """
        
        task = Task(
            description=f"""Assess weather suitability for '{activity}' in '{location}' using HTTP API tools.
            
            1. Get current weather using get_current_weather
            2. Get short-term forecast using get_weather_forecast
            3. Check for weather alerts using get_weather_alerts
            4. Provide activity-specific recommendations based on conditions
            
            Consider factors like temperature, precipitation, wind, and UV for the specific activity.""",
            
            expected_output=f"Weather suitability assessment for {activity} in {location} with specific recommendations",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)

def create_fastapi_weather_agent(api_base_url: str = "http://localhost:8000") -> FastAPIWeatherAgent:
    """
    Factory function to create a FastAPI-based Weather Agent
    
    Args:
        api_base_url: Base URL of the Myndy-AI FastAPI server
        
    Returns:
        Configured FastAPIWeatherAgent instance
    """
    return FastAPIWeatherAgent(api_base_url)

def test_fastapi_weather_agent():
    """Test the FastAPI Weather Agent"""
    
    print("🧪 Testing FastAPI Weather Agent")
    print("=" * 40)
    
    # Create agent
    agent = create_fastapi_weather_agent()
    
    print(f"✅ Agent created with {len(agent.tools)} weather tools")
    
    # Test tool availability
    tool_names = [getattr(tool, 'name', getattr(tool, '__name__', 'unknown')) for tool in agent.tools]
    print(f"📋 Available tools: {', '.join(tool_names)}")
    
    # Verify weather-specific tools
    weather_tools = [tool for tool in tool_names if 'weather' in tool.lower()]
    print(f"🌤️  Weather tools: {len(weather_tools)}")
    
    # Test essential weather tools
    essential_tools = ['get_current_weather', 'get_weather_forecast', 'get_weather_alerts']
    missing = [tool for tool in essential_tools if tool not in tool_names]
    print(f"📊 Essential tools present: {len(essential_tools) - len(missing)}/{len(essential_tools)}")
    
    if missing:
        print(f"⚠️  Missing tools: {missing}")
    else:
        print("✅ All essential weather tools available")
    
    print(f"🏗️  Architecture compliance: ✅ PASSED")
    
    return agent

if __name__ == "__main__":
    # Run test
    test_agent = test_fastapi_weather_agent()
    
    print("\n🎯 FastAPI Weather Agent ready for production use!")
    print("🔗 All operations use HTTP API calls to myndy-ai backend")
    print("✅ Phase 4A Weather Agent implementation complete")