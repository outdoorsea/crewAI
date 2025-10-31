#!/usr/bin/env python3
"""
Test tool execution with direct implementation

File: test_tool_execution.py
"""

import sys
from pathlib import Path

# Setup paths
CREWAI_PATH = Path("/Users/jeremy/crewAI")
sys.path.insert(0, str(CREWAI_PATH))

def test_direct_tool_execution():
    """Test that tools execute correctly with direct implementation"""
    print("🧪 Testing Direct Tool Execution")
    print("=" * 50)
    
    from tools.myndy_bridge import MyndyToolLoader
    loader = MyndyToolLoader()
    
    # Test get_current_time tool
    print("📋 Step 1: Testing get_current_time...")
    time_tool = loader.create_crewai_tool("get_current_time")
    
    if time_tool:
        try:
            result = time_tool._run()  # No timezone, should use default
            print(f"✅ get_current_time: Success")
            print(f"   Result: {result}")
        except Exception as e:
            print(f"❌ get_current_time: Failed - {e}")
    else:
        print("❌ Failed to create get_current_time tool")
    
    # Test local_weather tool
    print("\n📋 Step 2: Testing local_weather...")
    weather_tool = loader.create_crewai_tool("local_weather")
    
    if weather_tool:
        try:
            result = weather_tool._run(location="Seattle")
            print(f"✅ local_weather: Success")
            print(f"   Result: {result}")
        except Exception as e:
            print(f"❌ local_weather: Failed - {e}")
    else:
        print("❌ Failed to create local_weather tool")
    
    # Test format_weather tool
    print("\n📋 Step 3: Testing format_weather...")
    format_tool = loader.create_crewai_tool("format_weather")
    
    if format_tool:
        try:
            sample_data = {"temperature": 72, "condition": "sunny", "city": "Seattle"}
            result = format_tool._run(weather_data=sample_data, format="simple")
            print(f"✅ format_weather: Success")
            print(f"   Result: {result}")
        except Exception as e:
            print(f"❌ format_weather: Failed - {e}")
    else:
        print("❌ Failed to create format_weather tool")

if __name__ == "__main__":
    test_direct_tool_execution()