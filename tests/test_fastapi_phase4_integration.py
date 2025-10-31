#!/usr/bin/env python3
"""
Integration Tests for FastAPI Phase 4 Utility Agents

Tests the integration between Weather and Time agents in Phase 4 of the 
FastAPI architecture implementation.

File: tests/test_fastapi_phase4_integration.py
"""

import sys
import json
import logging
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.fastapi_weather_agent import create_fastapi_weather_agent
from agents.fastapi_time_agent import create_fastapi_time_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFastAPIPhase4Integration(unittest.TestCase):
    """Test Phase 4 utility agents integration"""
    
    def setUp(self):
        """Set up test environment"""
        logger.info("Setting up Phase 4 integration tests")
        self.weather_agent = create_fastapi_weather_agent()
        self.time_agent = create_fastapi_time_agent()
        
    def test_both_agents_creation(self):
        """Test that both utility agents can be created successfully"""
        
        # Verify both agents exist
        self.assertIsNotNone(self.weather_agent)
        self.assertIsNotNone(self.time_agent)
        
        # Verify agents have different specializations
        self.assertEqual(self.weather_agent.agent.role, "Weather Specialist")
        self.assertEqual(self.time_agent.agent.role, "Time Specialist")
        
        # Verify both have tools
        self.assertGreater(len(self.weather_agent.tools), 0)
        self.assertGreater(len(self.time_agent.tools), 0)
        
        logger.info("✅ Both utility agents created successfully")
        
    def test_complementary_tool_coverage(self):
        """Test that agents have complementary but non-overlapping tool coverage"""
        
        # Get tool names for both agents
        weather_tools = [getattr(tool, 'name', getattr(tool, '__name__', 'unknown')) 
                        for tool in self.weather_agent.tools]
        time_tools = [getattr(tool, 'name', getattr(tool, '__name__', 'unknown')) 
                     for tool in self.time_agent.tools]
        
        logger.info(f"Weather tools: {weather_tools}")
        logger.info(f"Time tools: {time_tools}")
        
        # Verify no tool overlap (each agent has distinct tools)
        tool_overlap = set(weather_tools) & set(time_tools)
        self.assertEqual(len(tool_overlap), 0, f"Unexpected tool overlap: {tool_overlap}")
        
        # Verify weather agent has weather-specific tools
        weather_specific = [tool for tool in weather_tools if 'weather' in tool.lower()]
        self.assertGreater(len(weather_specific), 0, "Weather agent should have weather-specific tools")
        
        # Verify time agent has time-specific tools
        time_specific = [tool for tool in time_tools if any(keyword in tool.lower() 
                        for keyword in ['time', 'date', 'format', 'convert', 'business'])]
        self.assertGreater(len(time_specific), 0, "Time agent should have time-specific tools")
        
        logger.info("✅ Complementary tool coverage verified")
        
    def test_travel_planning_scenario(self):
        """Test integration scenario: Travel planning with weather and time coordination"""
        
        # Scenario: Planning a trip requiring both weather and time information
        
        # Get current time for trip planning
        time_tool = None
        for tool in self.time_agent.tools:
            if getattr(tool, 'name', '') == 'get_current_time':
                time_tool = tool
                break
        
        time_result = time_tool("US/Pacific", "human")
        time_data = json.loads(time_result)
        
        # Get weather for destination
        weather_tool = None
        for tool in self.weather_agent.tools:
            if getattr(tool, 'name', '') == 'get_current_weather':
                weather_tool = tool
                break
        
        weather_result = weather_tool("Miami, FL")
        weather_data = json.loads(weather_result)
        
        # Verify both operations succeeded
        self.assertEqual(time_data["status"], "success")
        self.assertEqual(weather_data["status"], "success")
        
        # Verify we got useful travel planning data
        self.assertIn("current_time", time_data)
        self.assertIn("day_of_week", time_data)
        self.assertIn("location", weather_data)
        self.assertIn("current", weather_data)
        self.assertIn("temperature", weather_data["current"])
        
        logger.info("✅ Travel planning scenario integration verified")
        
    def test_meeting_scheduling_scenario(self):
        """Test integration scenario: Meeting scheduling across timezones with weather"""
        
        # Scenario: Scheduling outdoor meeting considering time zones and weather
        
        # Check business hours in target timezone
        business_tool = None
        for tool in self.time_agent.tools:
            if getattr(tool, 'name', '') == 'check_business_hours':
                business_tool = tool
                break
        
        business_result = business_tool("US/Eastern", "14:00")
        business_data = json.loads(business_result)
        
        # Get weather for meeting location
        multi_weather_tool = None
        for tool in self.weather_agent.tools:
            if getattr(tool, 'name', '') == 'get_multi_location_weather':
                multi_weather_tool = tool
                break
        
        weather_result = multi_weather_tool("New York, Boston, Philadelphia")
        weather_data = json.loads(weather_result)
        
        # Verify both operations succeeded
        self.assertEqual(business_data["status"], "success")
        self.assertEqual(weather_data["status"], "success")
        
        # Verify meeting planning data is available
        self.assertIn("analysis", business_data)
        self.assertIn("is_business_hours", business_data["analysis"])
        self.assertIn("locations", weather_data)
        self.assertEqual(weather_data["location_count"], 3)
        
        logger.info("✅ Meeting scheduling scenario integration verified")
        
    def test_event_planning_scenario(self):
        """Test integration scenario: Event planning with weather forecasts and time calculations"""
        
        # Scenario: Planning outdoor event with weather forecast and time management
        
        # Calculate time until event (future date)
        calc_tool = None
        for tool in self.time_agent.tools:
            if getattr(tool, 'name', '') == 'calculate_time':
                calc_tool = tool
                break
        
        time_result = calc_tool("add", "2025-06-10 10:00:00", "", "7", "days")
        time_data = json.loads(time_result)
        
        # Get weather forecast for event period
        forecast_tool = None
        for tool in self.weather_agent.tools:
            if getattr(tool, 'name', '') == 'get_weather_forecast':
                forecast_tool = tool
                break
        
        forecast_result = forecast_tool("San Francisco, CA", 5)
        forecast_data = json.loads(forecast_result)
        
        # Verify both operations succeeded
        self.assertEqual(time_data["status"], "success")
        self.assertEqual(forecast_data["status"], "success")
        
        # Verify event planning data
        self.assertIn("result", time_data)
        self.assertIn("result_time", time_data["result"])
        self.assertIn("forecast", forecast_data)
        self.assertEqual(len(forecast_data["forecast"]), 5)
        
        logger.info("✅ Event planning scenario integration verified")
        
    def test_international_coordination_scenario(self):
        """Test integration scenario: International business coordination"""
        
        # Scenario: Coordinating with international teams across timezones and weather
        
        # Convert meeting time to different timezone
        tz_tool = None
        for tool in self.time_agent.tools:
            if getattr(tool, 'name', '') == 'convert_timezone':
                tz_tool = tool
                break
        
        tz_result = tz_tool("09:00", "US/Pacific", "Europe/London")
        tz_data = json.loads(tz_result)
        
        # Compare weather between locations
        compare_tool = None
        for tool in self.weather_agent.tools:
            if getattr(tool, 'name', '') == 'compare_weather_locations':
                compare_tool = tool
                break
        
        compare_result = compare_tool("San Francisco, CA", "London, UK")
        compare_data = json.loads(compare_result)
        
        # Verify both operations succeeded
        self.assertEqual(tz_data["status"], "success")
        self.assertEqual(compare_data["status"], "success")
        
        # Verify international coordination data
        self.assertIn("conversion", tz_data)
        self.assertIn("time_difference", tz_data["conversion"])
        self.assertIn("comparison", compare_data)
        self.assertIn("temperature_diff", compare_data["comparison"])
        
        logger.info("✅ International coordination scenario integration verified")
        
    def test_error_handling_coordination(self):
        """Test that both agents handle errors gracefully in coordinated scenarios"""
        
        # Test time agent with invalid input
        format_tool = None
        for tool in self.time_agent.tools:
            if getattr(tool, 'name', '') == 'format_date':
                format_tool = tool
                break
        
        invalid_time_result = format_tool("invalid-date", "auto", "human")
        invalid_time_data = json.loads(invalid_time_result)
        
        # Test weather agent with invalid input
        multi_weather_tool = None
        for tool in self.weather_agent.tools:
            if getattr(tool, 'name', '') == 'get_multi_location_weather':
                multi_weather_tool = tool
                break
        
        invalid_weather_result = multi_weather_tool("")  # Empty locations
        invalid_weather_data = json.loads(invalid_weather_result)
        
        # Verify both handle errors gracefully
        self.assertEqual(invalid_time_data["status"], "error")
        self.assertEqual(invalid_weather_data["status"], "error")
        self.assertIn("error", invalid_time_data)
        self.assertIn("error", invalid_weather_data)
        
        logger.info("✅ Error handling coordination verified")
        
    def test_architecture_consistency(self):
        """Test that both agents follow consistent architecture patterns"""
        
        # Verify both agents use HTTP-only communication pattern
        weather_goal = self.weather_agent.agent.goal
        time_goal = self.time_agent.agent.goal
        
        self.assertIn("HTTP API calls", weather_goal)
        self.assertIn("HTTP API calls", time_goal)
        self.assertIn("backend", self.weather_agent.agent.backstory.lower())
        self.assertIn("backend", self.time_agent.agent.backstory.lower())
        
        # Verify consistent agent configuration
        self.assertFalse(self.weather_agent.agent.allow_delegation)
        self.assertFalse(self.time_agent.agent.allow_delegation)
        self.assertTrue(self.weather_agent.agent.verbose)
        self.assertTrue(self.time_agent.agent.verbose)
        
        # Verify both have quick response configuration
        self.assertEqual(self.weather_agent.agent.max_execution_time, 60)
        self.assertEqual(self.time_agent.agent.max_execution_time, 60)
        
        logger.info("✅ Architecture consistency verified")
        
    def test_tool_naming_conventions(self):
        """Test that both agents follow consistent tool naming conventions"""
        
        # Get all tool names
        weather_tools = [getattr(tool, 'name', '') for tool in self.weather_agent.tools]
        time_tools = [getattr(tool, 'name', '') for tool in self.time_agent.tools]
        
        # Verify weather tools follow naming convention
        weather_prefixes = ['get_', 'compare_']
        for tool_name in weather_tools:
            if tool_name:  # Skip empty names
                has_valid_prefix = any(tool_name.startswith(prefix) for prefix in weather_prefixes)
                self.assertTrue(has_valid_prefix, f"Weather tool '{tool_name}' doesn't follow naming convention")
        
        # Verify time tools follow naming convention
        time_prefixes = ['get_', 'format_', 'calculate_', 'convert_', 'check_']
        for tool_name in time_tools:
            if tool_name:  # Skip empty names
                has_valid_prefix = any(tool_name.startswith(prefix) for prefix in time_prefixes)
                self.assertTrue(has_valid_prefix, f"Time tool '{tool_name}' doesn't follow naming convention")
        
        logger.info("✅ Tool naming conventions verified")
        
    def test_phase4_completion_status(self):
        """Test that Phase 4 implementation meets completion criteria"""
        
        # Verify both agents exist and are functional
        self.assertIsNotNone(self.weather_agent)
        self.assertIsNotNone(self.time_agent)
        
        # Verify minimum tool count for utility agents
        weather_tool_count = len(self.weather_agent.tools)
        time_tool_count = len(self.time_agent.tools)
        
        self.assertGreaterEqual(weather_tool_count, 4, "Weather agent should have at least 4 tools")
        self.assertGreaterEqual(time_tool_count, 4, "Time agent should have at least 4 tools")
        
        # Verify agents follow FastAPI HTTP-only architecture
        for agent in [self.weather_agent, self.time_agent]:
            self.assertIn("HTTP", agent.agent.goal.upper())
            self.assertIn("service separation", agent.agent.goal.lower())
        
        # Verify utility agent specializations are distinct
        weather_role = self.weather_agent.agent.role
        time_role = self.time_agent.agent.role
        self.assertNotEqual(weather_role, time_role)
        
        logger.info("✅ Phase 4 completion criteria verified")

def run_fastapi_phase4_integration_tests():
    """Run all Phase 4 integration tests"""
    
    print("🧪 Testing FastAPI Phase 4 Utility Agents Integration")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFastAPIPhase4Integration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ All Phase 4 integration tests passed!")
        print("✅ Weather and Time agents work together effectively")
        print("✅ Travel planning, meeting scheduling scenarios verified")
        print("✅ International coordination and event planning operational")
        print("✅ Error handling and architecture consistency confirmed")
        print("✅ Phase 4 utility agents integration complete")
        print("")
        print("🎯 Phase 4 COMPLETED - Weather and Time agents fully integrated")
        print("📋 Ready for Phase 5: Unit Testing Framework")
    else:
        print("❌ Some integration tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_fastapi_phase4_integration_tests()
    sys.exit(0 if success else 1)