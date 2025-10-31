#!/usr/bin/env python3
"""
Test script to verify tool execution fixes

This script tests the updated tool execution to ensure the JSON format
and parameter handling issues are resolved.

File: test_tool_fix.py
"""

import sys
from pathlib import Path

# Setup paths
CREWAI_PATH = Path("/Users/jeremy/crewAI")
MYNDY_PATH = Path("/Users/jeremy/myndy")
sys.path.insert(0, str(CREWAI_PATH))
sys.path.insert(0, str(MYNDY_PATH))

def test_tool_execution():
    """Test that tools execute correctly with the fixes"""
    print("🧪 Testing Tool Execution Fixes")
    print("=" * 50)
    
    try:
        # First populate the registry
        print("📋 Step 1: Populating registry...")
        exec(open(str(CREWAI_PATH / "populate_all_tools.py")).read(), {'__name__': '__main__'})
        
        # Import the tool loader
        from tools.myndy_bridge import MyndyToolLoader
        loader = MyndyToolLoader()
        
        # Test creating the get_current_time tool
        print("📋 Step 2: Creating get_current_time tool...")
        time_tool = loader.create_crewai_tool("get_current_time")
        
        if time_tool:
            print(f"✅ Tool created successfully: {time_tool.name}")
            print(f"   Description: {time_tool.description}")
            
            # Test tool execution with valid parameters
            print("📋 Step 3: Testing tool execution...")
            
            # Test 1: With timezone parameter
            try:
                result1 = time_tool._run(timezone="America/Los_Angeles")
                print(f"✅ Test 1 (with timezone): Success")
                print(f"   Result: {result1[:100]}...")
            except Exception as e:
                print(f"❌ Test 1 (with timezone): Failed - {e}")
            
            # Test 2: Without timezone parameter (should use default)
            try:
                result2 = time_tool._run()
                print(f"✅ Test 2 (no timezone): Success")
                print(f"   Result: {result2[:100]}...")
            except Exception as e:
                print(f"❌ Test 2 (no timezone): Failed - {e}")
            
            # Test 3: With invalid parameters (should be cleaned)
            try:
                result3 = time_tool._run(timezone="America/Los_Angeles", invalid_param="None needed")
                print(f"✅ Test 3 (invalid params): Success")
                print(f"   Result: {result3[:100]}...")
            except Exception as e:
                print(f"❌ Test 3 (invalid params): Failed - {e}")
                
        else:
            print("❌ Failed to create get_current_time tool")
            
        # Test format_weather tool
        print("📋 Step 4: Testing format_weather tool...")
        weather_tool = loader.create_crewai_tool("format_weather")
        
        if weather_tool:
            print(f"✅ Weather tool created: {weather_tool.name}")
            print(f"   Description: {weather_tool.description}")
            
            # Test with sample weather data
            try:
                sample_weather = {
                    "temperature": 72,
                    "condition": "sunny",
                    "humidity": 45,
                    "city": "San Francisco"
                }
                result = weather_tool._run(weather_data=sample_weather, format="simple")
                print(f"✅ Weather tool test: Success")
                print(f"   Result: {result[:100]}...")
            except Exception as e:
                print(f"❌ Weather tool test: Failed - {e}")
        else:
            print("❌ Failed to create format_weather tool")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_execution()