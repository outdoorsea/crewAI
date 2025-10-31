#!/usr/bin/env python3
"""
Unit Tests for FastAPI Weather Agent

Tests the FastAPI-based Weather Agent implementation following Phase 4A
of the implementation plan.

File: tests/test_fastapi_weather_agent.py
"""

import sys
import json
import logging
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.fastapi_weather_agent import FastAPIWeatherAgent, create_fastapi_weather_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFastAPIWeatherAgent(unittest.TestCase):
    """Test FastAPI Weather Agent implementation"""
    
    def setUp(self):
        """Set up test environment"""
        logger.info("Setting up FastAPI Weather Agent tests")
        
    def test_agent_creation(self):
        """Test that FastAPI Weather Agent can be created with proper configuration"""
        
        agent = create_fastapi_weather_agent("http://localhost:8000")
        
        # Verify agent was created
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, FastAPIWeatherAgent)
        
        # Verify API configuration
        self.assertEqual(agent.api_base_url, "http://localhost:8000")
        
        # Verify tools were loaded
        self.assertIsNotNone(agent.tools)
        self.assertGreater(len(agent.tools), 0)
        
        # Verify agent was created
        self.assertIsNotNone(agent.agent)
        
        logger.info(f"✅ Agent created with {len(agent.tools)} tools")
        
    def test_weather_tool_integration(self):
        """Test that agent uses weather tools correctly"""
        
        agent = create_fastapi_weather_agent()
        
        # Check for weather-specific tools
        tool_names = []
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown'))
            tool_names.append(tool_name)
        
        logger.info(f"Weather agent tool names: {tool_names}")
        
        # Verify essential weather tools are present
        essential_weather_tools = [
            'get_current_weather', 'get_weather_forecast', 'get_weather_alerts',
            'get_multi_location_weather', 'compare_weather_locations'
        ]
        
        missing_tools = []
        for tool in essential_weather_tools:
            if tool not in tool_names:
                missing_tools.append(tool)
        
        self.assertEqual(len(missing_tools), 0, 
                        f"Missing essential weather tools: {missing_tools}")
        
        logger.info("✅ Weather tool integration verified")
        
    def test_agent_configuration(self):
        """Test that agent is configured correctly for weather operations"""
        
        agent = create_fastapi_weather_agent()
        
        # Verify agent role and goal
        self.assertEqual(agent.agent.role, "Weather Specialist")
        self.assertIn("weather", agent.agent.goal.lower())
        self.assertIn("HTTP API calls", agent.agent.goal)
        
        # Verify backstory mentions weather and HTTP architecture
        self.assertIn("Weather Specialist", agent.agent.backstory)
        self.assertIn("HTTP API calls", agent.agent.backstory)
        self.assertIn("weather", agent.agent.backstory.lower())
        self.assertIn("forecasts", agent.agent.backstory.lower())
        
        # Verify agent settings for quick weather responses
        self.assertTrue(agent.agent.verbose)
        self.assertFalse(agent.agent.allow_delegation)
        self.assertEqual(agent.agent.max_iter, 3)
        self.assertEqual(agent.agent.max_execution_time, 60)  # Quick responses
        
        logger.info("✅ Weather agent configuration verified")
        
    def test_current_weather_tool(self):
        """Test the current weather tool functionality"""
        
        agent = create_fastapi_weather_agent()
        
        # Find the current weather tool
        weather_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'get_current_weather':
                weather_tool = tool
                break
        
        self.assertIsNotNone(weather_tool, "Current weather tool not found")
        
        # Test tool execution with default location
        result = weather_tool("San Francisco, CA")
        result_data = json.loads(result)
        
        self.assertIn("location", result_data)
        self.assertIn("current", result_data)
        self.assertIn("temperature", result_data["current"])
        self.assertIn("condition", result_data["current"])
        self.assertEqual(result_data["status"], "success")
        
        logger.info("✅ Current weather tool verified")
        
    def test_weather_forecast_tool(self):
        """Test the weather forecast tool functionality"""
        
        agent = create_fastapi_weather_agent()
        
        # Find the forecast tool
        forecast_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'get_weather_forecast':
                forecast_tool = tool
                break
        
        self.assertIsNotNone(forecast_tool, "Weather forecast tool not found")
        
        # Test tool execution with 3-day forecast
        result = forecast_tool("Seattle, WA", 3)
        result_data = json.loads(result)
        
        self.assertIn("location", result_data)
        self.assertIn("forecast", result_data)
        self.assertIn("forecast_days", result_data)
        self.assertEqual(result_data["forecast_days"], 3)
        self.assertEqual(len(result_data["forecast"]), 3)
        self.assertEqual(result_data["status"], "success")
        
        # Verify forecast structure
        for day_forecast in result_data["forecast"]:
            self.assertIn("date", day_forecast)
            self.assertIn("high_temp", day_forecast)
            self.assertIn("low_temp", day_forecast)
            self.assertIn("condition", day_forecast)
        
        logger.info("✅ Weather forecast tool verified")
        
    def test_weather_alerts_tool(self):
        """Test the weather alerts tool functionality"""
        
        agent = create_fastapi_weather_agent()
        
        # Find the alerts tool
        alerts_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'get_weather_alerts':
                alerts_tool = tool
                break
        
        self.assertIsNotNone(alerts_tool, "Weather alerts tool not found")
        
        # Test tool execution
        result = alerts_tool("Miami, FL")
        result_data = json.loads(result)
        
        self.assertIn("location", result_data)
        self.assertIn("active_alerts", result_data)
        self.assertIn("alert_count", result_data)
        self.assertEqual(result_data["status"], "success")
        self.assertIsInstance(result_data["active_alerts"], list)
        
        logger.info("✅ Weather alerts tool verified")
        
    def test_multi_location_weather_tool(self):
        """Test the multi-location weather tool functionality"""
        
        agent = create_fastapi_weather_agent()
        
        # Find the multi-location tool
        multi_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'get_multi_location_weather':
                multi_tool = tool
                break
        
        self.assertIsNotNone(multi_tool, "Multi-location weather tool not found")
        
        # Test tool execution with multiple cities
        locations = "New York, Los Angeles, Chicago"
        result = multi_tool(locations)
        result_data = json.loads(result)
        
        self.assertIn("locations", result_data)
        self.assertIn("location_count", result_data)
        self.assertEqual(result_data["location_count"], 3)
        self.assertEqual(len(result_data["locations"]), 3)
        self.assertEqual(result_data["status"], "success")
        
        # Verify each location has weather data
        for location_weather in result_data["locations"]:
            self.assertIn("location", location_weather)
            self.assertIn("temperature", location_weather)
            self.assertIn("condition", location_weather)
        
        logger.info("✅ Multi-location weather tool verified")
        
    def test_weather_comparison_tool(self):
        """Test the weather comparison tool functionality"""
        
        agent = create_fastapi_weather_agent()
        
        # Find the comparison tool
        comparison_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'compare_weather_locations':
                comparison_tool = tool
                break
        
        self.assertIsNotNone(comparison_tool, "Weather comparison tool not found")
        
        # Test tool execution with two locations
        result = comparison_tool("Boston, MA", "Phoenix, AZ")
        result_data = json.loads(result)
        
        self.assertIn("location1", result_data)
        self.assertIn("location2", result_data)
        self.assertIn("comparison", result_data)
        self.assertIn("summary", result_data)
        self.assertEqual(result_data["status"], "success")
        
        # Verify comparison data
        self.assertIn("temperature_diff", result_data["comparison"])
        self.assertIn("warmer_location", result_data["comparison"])
        
        logger.info("✅ Weather comparison tool verified")
        
    def test_error_handling(self):
        """Test that weather tools handle errors gracefully"""
        
        agent = create_fastapi_weather_agent()
        
        # Find the multi-location tool
        multi_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'get_multi_location_weather':
                multi_tool = tool
                break
        
        self.assertIsNotNone(multi_tool)
        
        # Test with empty location string
        result = multi_tool("")
        result_data = json.loads(result)
        
        # Verify error is handled gracefully
        self.assertIn("error", result_data)
        self.assertEqual(result_data["status"], "error")
        
        logger.info("✅ Error handling verified")
        
    def test_weather_agent_specialization(self):
        """Test that agent is specialized for weather operations"""
        
        agent = create_fastapi_weather_agent()
        
        # Verify agent focuses on weather information
        weather_keywords = ["weather", "forecast", "conditions", "alerts", "temperature", "climate"]
        goal_contains_keywords = any(keyword in agent.agent.goal.lower() for keyword in weather_keywords)
        self.assertTrue(goal_contains_keywords, "Agent goal should focus on weather information")
        
        backstory_contains_keywords = any(keyword in agent.agent.backstory.lower() for keyword in weather_keywords)
        self.assertTrue(backstory_contains_keywords, "Agent backstory should emphasize weather expertise")
        
        # Verify tools are weather-focused
        weather_tool_count = 0
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown')).lower()
            if any(keyword in tool_name for keyword in ['weather', 'forecast', 'alert', 'location', 'compare']):
                weather_tool_count += 1
        
        self.assertGreaterEqual(weather_tool_count, 4, "Should have multiple weather-focused tools")
        
        logger.info("✅ Weather agent specialization verified")
        
    def test_architecture_compliance(self):
        """Test that agent follows service-oriented architecture"""
        
        agent = create_fastapi_weather_agent()
        
        # Verify agent mentions HTTP/API architecture
        self.assertIn("HTTP", agent.agent.goal.upper())
        self.assertIn("API", agent.agent.goal.upper())
        self.assertIn("backend", agent.agent.backstory.lower())
        
        # Verify quick response configuration for weather queries
        self.assertEqual(agent.agent.max_iter, 3, "Weather agent should allow quick iterations")
        self.assertEqual(agent.agent.max_execution_time, 60, "Weather agent should respond quickly")
        
        # Verify tools are function-based (HTTP pattern)
        function_based_tools = 0
        for tool in agent.tools:
            if hasattr(tool, '__call__') and hasattr(tool, 'name'):
                function_based_tools += 1
        
        self.assertGreater(function_based_tools, 0, "Agent should have function-based tools")
        
        logger.info("✅ Architecture compliance verified")
        
    def test_weather_data_structure(self):
        """Test that weather data follows expected structure"""
        
        agent = create_fastapi_weather_agent()
        
        # Find current weather tool
        weather_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'get_current_weather':
                weather_tool = tool
                break
        
        result = weather_tool("Denver, CO")
        result_data = json.loads(result)
        
        # Verify comprehensive weather data structure
        current_data = result_data["current"]
        self.assertIn("temperature", current_data)
        self.assertIn("humidity", current_data)
        self.assertIn("wind_speed", current_data)
        self.assertIn("pressure", current_data)
        self.assertIn("visibility", current_data)
        self.assertIn("uv_index", current_data)
        
        # Verify data types
        self.assertIsInstance(current_data["temperature"], (int, float))
        self.assertIsInstance(current_data["humidity"], (int, float))
        self.assertIsInstance(current_data["wind_speed"], (int, float))
        
        logger.info("✅ Weather data structure verified")

def run_fastapi_weather_agent_tests():
    """Run all FastAPI Weather Agent tests"""
    
    print("🧪 Testing FastAPI Weather Agent Implementation")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFastAPIWeatherAgent)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All FastAPI Weather Agent tests passed!")
        print("✅ Weather information tools verified")
        print("✅ Current weather, forecasts, alerts working")
        print("✅ Multi-location and comparison functionality operational")
        print("✅ Service-oriented architecture compliance confirmed")
        print("✅ Phase 4A implementation complete")
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_fastapi_weather_agent_tests()
    sys.exit(0 if success else 1)