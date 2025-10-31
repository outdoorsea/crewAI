#!/usr/bin/env python3
"""
Weather Tool Debug Test
Test specifically the weather tool selection and execution

File: test_weather_debug.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_weather_tool_selection_debug():
    """Debug weather tool selection step by step"""
    print("🔧 Weather Tool Selection Debug")
    print("=" * 50)
    
    try:
        from pipeline.myndy_ai_beta import PipelineBeta
        
        # Create pipeline instance
        pipeline = PipelineBeta()
        
        # Enable ALL visibility modes for maximum debugging
        pipeline.valves.verbose_coordination = True
        pipeline.valves.trace_tool_selection = True  
        pipeline.valves.show_agent_thoughts = True
        pipeline.valves.show_tool_execution = True
        pipeline.valves.show_tool_results = True
        pipeline.valves.debug_mode = True
        
        print("🌦️ Testing weather query with maximum visibility...")
        print("Query: 'What is the weather in Seattle?'")
        print("-" * 50)
        
        # Test weather query with full visibility
        response = pipeline.pipe(
            user_message="What is the weather in Seattle?",
            model_id="auto_beta",
            messages=[{"role": "user", "content": "What is the weather in Seattle?"}],
            body={"messages": [{"role": "user", "content": "What is the weather in Seattle?"}], "model": "auto_beta"}
        )
        
        print("\n" + "=" * 50)
        print("📊 FINAL RESPONSE:")
        print("=" * 50)
        print(response)
        
        # Check if response contains actual API data vs generic response
        contains_api_data = any(indicator in response.lower() for indicator in [
            "°f", "°c", "degrees", "humidity", "wind speed", "pressure", 
            "visibility", "feels like", "current conditions"
        ])
        
        contains_generic = any(phrase in response.lower() for phrase in [
            "check websites", "weather.com", "accuweather", "recommend checking", 
            "my last update", "up-to-date information"
        ])
        
        print(f"\n🔍 Analysis:")
        print(f"Contains API data indicators: {'✅' if contains_api_data else '❌'}")
        print(f"Contains generic phrases: {'⚠️' if contains_generic else '✅'}")
        
        if contains_api_data and not contains_generic:
            print("🎉 SUCCESS: Real weather API data detected!")
            return True
        elif contains_generic:
            print("❌ ISSUE: Still using generic responses instead of API")
            return False
        else:
            print("❓ UNCLEAR: Response doesn't clearly indicate API usage")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_availability():
    """Test if weather_api tool is actually available"""
    print("\n🔧 Testing Tool Availability")
    print("=" * 50)
    
    try:
        from tools.myndy_bridge import MyndyToolLoader
        
        loader = MyndyToolLoader()
        
        # Test weather_api tool creation
        weather_tool = loader.create_crewai_tool("weather_api")
        
        if weather_tool:
            print("✅ weather_api tool created successfully")
            print(f"Tool name: {weather_tool.name if hasattr(weather_tool, 'name') else 'Unknown'}")
            print(f"Tool description: {weather_tool.description if hasattr(weather_tool, 'description') else 'No description'}")
            
            # Try to get tool metadata if available
            if hasattr(weather_tool, '_run'):
                print("✅ Tool has _run method (executable)")
            else:
                print("❌ Tool missing _run method")
                
            return True
        else:
            print("❌ weather_api tool creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Tool availability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 WEATHER TOOL DEBUG SUITE")
    print("=" * 60)
    
    # Test 1: Tool availability
    tool_available = test_tool_availability()
    
    # Test 2: Full weather tool execution with debug
    if tool_available:
        execution_success = test_weather_tool_selection_debug()
        
        if execution_success:
            print("\n🎉 Weather tool is working correctly!")
        else:
            print("\n⚠️ Weather tool needs further debugging")
    else:
        print("\n❌ Cannot test execution - tool not available")