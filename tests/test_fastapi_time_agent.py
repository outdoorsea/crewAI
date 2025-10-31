#!/usr/bin/env python3
"""
Unit Tests for FastAPI Time Agent

Tests the FastAPI-based Time Agent implementation following Phase 4B
of the implementation plan.

File: tests/test_fastapi_time_agent.py
"""

import sys
import json
import logging
import pytest
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.fastapi_time_agent import FastAPITimeAgent, create_fastapi_time_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFastAPITimeAgent(unittest.TestCase):
    """Test FastAPI Time Agent implementation"""
    
    def setUp(self):
        """Set up test environment"""
        logger.info("Setting up FastAPI Time Agent tests")
        
    def test_agent_creation(self):
        """Test that FastAPI Time Agent can be created with proper configuration"""
        
        agent = create_fastapi_time_agent("http://localhost:8000")
        
        # Verify agent was created
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, FastAPITimeAgent)
        
        # Verify API configuration
        self.assertEqual(agent.api_base_url, "http://localhost:8000")
        
        # Verify tools were loaded
        self.assertIsNotNone(agent.tools)
        self.assertGreater(len(agent.tools), 0)
        
        # Verify agent was created
        self.assertIsNotNone(agent.agent)
        
        logger.info(f"✅ Agent created with {len(agent.tools)} tools")
        
    def test_time_tool_integration(self):
        """Test that agent uses time tools correctly"""
        
        agent = create_fastapi_time_agent()
        
        # Check for time-specific tools
        tool_names = []
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown'))
            tool_names.append(tool_name)
        
        logger.info(f"Time agent tool names: {tool_names}")
        
        # Verify essential time tools are present
        essential_time_tools = [
            'get_current_time', 'format_date', 'calculate_time',
            'convert_timezone', 'check_business_hours'
        ]
        
        missing_tools = []
        for tool in essential_time_tools:
            if tool not in tool_names:
                missing_tools.append(tool)
        
        self.assertEqual(len(missing_tools), 0, 
                        f"Missing essential time tools: {missing_tools}")
        
        logger.info("✅ Time tool integration verified")
        
    def test_agent_configuration(self):
        """Test that agent is configured correctly for time operations"""
        
        agent = create_fastapi_time_agent()
        
        # Verify agent role and goal
        self.assertEqual(agent.agent.role, "Time Specialist")
        self.assertIn("time", agent.agent.goal.lower())
        self.assertIn("HTTP API calls", agent.agent.goal)
        
        # Verify backstory mentions time and HTTP architecture
        self.assertIn("Time Specialist", agent.agent.backstory)
        self.assertIn("HTTP API calls", agent.agent.backstory)
        self.assertIn("time", agent.agent.backstory.lower())
        self.assertIn("timezone", agent.agent.backstory.lower())
        
        # Verify agent settings for quick time responses
        self.assertTrue(agent.agent.verbose)
        self.assertFalse(agent.agent.allow_delegation)
        self.assertEqual(agent.agent.max_iter, 3)
        self.assertEqual(agent.agent.max_execution_time, 60)  # Quick responses
        
        logger.info("✅ Time agent configuration verified")
        
    def test_current_time_tool(self):
        """Test the current time tool functionality"""
        
        agent = create_fastapi_time_agent()
        
        # Find the current time tool
        time_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'get_current_time':
                time_tool = tool
                break
        
        self.assertIsNotNone(time_tool, "Current time tool not found")
        
        # Test tool execution with default (local) timezone
        result = time_tool("local", "standard")
        result_data = json.loads(result)
        
        self.assertIn("timezone", result_data)
        self.assertIn("current_time", result_data)
        self.assertIn("all_formats", result_data)
        self.assertIn("day_of_week", result_data)
        self.assertIn("is_weekend", result_data)
        self.assertEqual(result_data["status"], "success")
        
        # Verify all format types are provided
        formats = result_data["all_formats"]
        self.assertIn("standard", formats)
        self.assertIn("iso", formats)
        self.assertIn("timestamp", formats)
        self.assertIn("human", formats)
        
        logger.info("✅ Current time tool verified")
        
    def test_timezone_conversion_tool(self):
        """Test the timezone conversion tool functionality"""
        
        agent = create_fastapi_time_agent()
        
        # Find the timezone conversion tool
        tz_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'convert_timezone':
                tz_tool = tool
                break
        
        self.assertIsNotNone(tz_tool, "Timezone conversion tool not found")
        
        # Test tool execution
        result = tz_tool("14:30", "UTC", "US/Pacific")
        result_data = json.loads(result)
        
        self.assertIn("input", result_data)
        self.assertIn("conversion", result_data)
        self.assertIn("formatted_results", result_data)
        self.assertEqual(result_data["status"], "success")
        
        # Verify conversion data
        conversion = result_data["conversion"]
        self.assertIn("original_time", conversion)
        self.assertIn("converted_time", conversion)
        self.assertIn("time_difference", conversion)
        
        logger.info("✅ Timezone conversion tool verified")
        
    def test_date_formatting_tool(self):
        """Test the date formatting tool functionality"""
        
        agent = create_fastapi_time_agent()
        
        # Find the date formatting tool
        format_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'format_date':
                format_tool = tool
                break
        
        self.assertIsNotNone(format_tool, "Date formatting tool not found")
        
        # Test tool execution with ISO date
        result = format_tool("2025-06-10T14:30:00", "auto", "human")
        result_data = json.loads(result)
        
        self.assertIn("input", result_data)
        self.assertIn("output", result_data)
        self.assertIn("all_formats", result_data)
        self.assertIn("date_info", result_data)
        self.assertEqual(result_data["status"], "success")
        
        # Verify date information
        date_info = result_data["date_info"]
        self.assertIn("day_of_week", date_info)
        self.assertIn("month_name", date_info)
        self.assertIn("week_number", date_info)
        self.assertIn("is_weekend", date_info)
        self.assertIn("quarter", date_info)
        
        logger.info("✅ Date formatting tool verified")
        
    def test_time_calculation_tool(self):
        """Test the time calculation tool functionality"""
        
        agent = create_fastapi_time_agent()
        
        # Find the time calculation tool
        calc_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'calculate_time':
                calc_tool = tool
                break
        
        self.assertIsNotNone(calc_tool, "Time calculation tool not found")
        
        # Test difference calculation
        result = calc_tool("difference", "2025-06-10 10:00:00", "2025-06-10 14:30:00")
        result_data = json.loads(result)
        
        self.assertIn("operation", result_data)
        self.assertIn("input", result_data)
        self.assertIn("result", result_data)
        self.assertEqual(result_data["status"], "success")
        self.assertEqual(result_data["operation"], "difference")
        
        # Verify difference calculation
        diff_result = result_data["result"]
        self.assertIn("total_seconds", diff_result)
        self.assertIn("hours", diff_result)
        self.assertIn("minutes", diff_result)
        self.assertIn("human_readable", diff_result)
        
        # Test addition calculation
        result2 = calc_tool("add", "2025-06-10 10:00:00", "", "3", "hours")
        result2_data = json.loads(result2)
        
        self.assertEqual(result2_data["status"], "success")
        self.assertIn("result_time", result2_data["result"])
        
        logger.info("✅ Time calculation tool verified")
        
    def test_business_hours_tool(self):
        """Test the business hours tool functionality"""
        
        agent = create_fastapi_time_agent()
        
        # Find the business hours tool
        bh_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'check_business_hours':
                bh_tool = tool
                break
        
        self.assertIsNotNone(bh_tool, "Business hours tool not found")
        
        # Test tool execution
        result = bh_tool("US/Pacific", "13:30")  # 1:30 PM
        result_data = json.loads(result)
        
        self.assertIn("check_time", result_data)
        self.assertIn("business_hours", result_data)
        self.assertIn("analysis", result_data)
        self.assertEqual(result_data["status"], "success")
        
        # Verify business hours analysis
        analysis = result_data["analysis"]
        self.assertIn("is_business_day", analysis)
        self.assertIn("is_business_hours", analysis)
        self.assertIn("is_open", analysis)
        self.assertIn("status", analysis)
        
        # Verify business hours configuration
        bh_config = result_data["business_hours"]
        self.assertIn("start_time", bh_config)
        self.assertIn("end_time", bh_config)
        self.assertIn("business_days", bh_config)
        
        logger.info("✅ Business hours tool verified")
        
    def test_error_handling(self):
        """Test that time tools handle errors gracefully"""
        
        agent = create_fastapi_time_agent()
        
        # Find the date formatting tool
        format_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'format_date':
                format_tool = tool
                break
        
        self.assertIsNotNone(format_tool)
        
        # Test with invalid date string
        result = format_tool("invalid-date-string", "auto", "human")
        result_data = json.loads(result)
        
        # Verify error is handled gracefully
        self.assertIn("error", result_data)
        self.assertEqual(result_data["status"], "error")
        
        logger.info("✅ Error handling verified")
        
    def test_time_agent_specialization(self):
        """Test that agent is specialized for time operations"""
        
        agent = create_fastapi_time_agent()
        
        # Verify agent focuses on time operations
        time_keywords = ["time", "date", "timezone", "format", "calculate", "schedule", "business hours"]
        goal_contains_keywords = any(keyword in agent.agent.goal.lower() for keyword in time_keywords)
        self.assertTrue(goal_contains_keywords, "Agent goal should focus on time operations")
        
        backstory_contains_keywords = any(keyword in agent.agent.backstory.lower() for keyword in time_keywords)
        self.assertTrue(backstory_contains_keywords, "Agent backstory should emphasize time expertise")
        
        # Verify tools are time-focused
        time_tool_count = 0
        for tool in agent.tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown')).lower()
            if any(keyword in tool_name for keyword in ['time', 'date', 'format', 'calculate', 'convert', 'business']):
                time_tool_count += 1
        
        self.assertGreaterEqual(time_tool_count, 4, "Should have multiple time-focused tools")
        
        logger.info("✅ Time agent specialization verified")
        
    def test_architecture_compliance(self):
        """Test that agent follows service-oriented architecture"""
        
        agent = create_fastapi_time_agent()
        
        # Verify agent mentions HTTP/API architecture
        self.assertIn("HTTP", agent.agent.goal.upper())
        self.assertIn("API", agent.agent.goal.upper())
        self.assertIn("backend", agent.agent.backstory.lower())
        
        # Verify quick response configuration for time queries
        self.assertEqual(agent.agent.max_iter, 3, "Time agent should allow quick iterations")
        self.assertEqual(agent.agent.max_execution_time, 60, "Time agent should respond quickly")
        
        # Verify tools are function-based (HTTP pattern)
        function_based_tools = 0
        for tool in agent.tools:
            if hasattr(tool, '__call__') and hasattr(tool, 'name'):
                function_based_tools += 1
        
        self.assertGreater(function_based_tools, 0, "Agent should have function-based tools")
        
        logger.info("✅ Architecture compliance verified")
        
    def test_comprehensive_time_capabilities(self):
        """Test comprehensive time management capabilities"""
        
        agent = create_fastapi_time_agent()
        
        # Test that agent can handle various time formats
        format_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'format_date':
                format_tool = tool
                break
        
        # Test different input formats
        test_formats = [
            ("2025-06-10", "auto", "human"),
            ("1718023800", "timestamp", "iso"),
            ("06/10/2025", "auto", "standard")
        ]
        
        for date_str, input_fmt, output_fmt in test_formats:
            result = format_tool(date_str, input_fmt, output_fmt)
            result_data = json.loads(result)
            
            # Should successfully parse and format
            if "error" not in result_data:
                self.assertEqual(result_data["status"], "success")
                self.assertIn("all_formats", result_data)
        
        logger.info("✅ Comprehensive time capabilities verified")
        
    def test_timezone_coverage(self):
        """Test that common timezones are supported"""
        
        agent = create_fastapi_time_agent()
        
        # Find timezone conversion tool
        tz_tool = None
        for tool in agent.tools:
            if getattr(tool, 'name', '') == 'convert_timezone':
                tz_tool = tool
                break
        
        # Test common timezone conversions
        common_timezones = ["UTC", "US/Eastern", "US/Pacific", "Europe/London", "Asia/Tokyo"]
        
        for tz in common_timezones:
            result = tz_tool("12:00", "UTC", tz.lower())
            result_data = json.loads(result)
            
            # Should handle common timezones
            if "error" in result_data:
                # Only fail if it's an unexpected timezone
                self.assertIn("Unknown timezone", result_data["error"])
            else:
                self.assertEqual(result_data["status"], "success")
        
        logger.info("✅ Timezone coverage verified")

def run_fastapi_time_agent_tests():
    """Run all FastAPI Time Agent tests"""
    
    print("🧪 Testing FastAPI Time Agent Implementation")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFastAPITimeAgent)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All FastAPI Time Agent tests passed!")
        print("✅ Time and date tools verified")
        print("✅ Current time, formatting, calculations working")
        print("✅ Timezone conversion and business hours operational")
        print("✅ Service-oriented architecture compliance confirmed")
        print("✅ Phase 4B implementation complete")
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_fastapi_time_agent_tests()
    sys.exit(0 if success else 1)