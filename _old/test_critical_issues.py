#!/usr/bin/env python3
"""
Critical Issues Test Suite
Test identity memory persistence and weather tool execution

File: test_critical_issues.py
"""

import sys
import os
from pathlib import Path
import asyncio
import json
import time

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_identity_memory_persistence():
    """Test that Shadow Agent remembers user identity between sessions"""
    print("🧪 Testing Identity Memory Persistence")
    print("=" * 50)
    
    try:
        from pipeline.myndy_ai_beta import PipelineBeta
        
        # Create pipeline instance
        pipeline = PipelineBeta()
        
        # Enable verbose modes for debugging
        pipeline.valves.verbose_coordination = True
        pipeline.valves.show_tool_execution = True
        pipeline.valves.show_tool_results = True
        
        print("📝 Step 1: Setting identity - 'I am Jeremy Irish'")
        
        # Test 1: Set identity
        identity_response = pipeline.pipe(
            user_message="I am Jeremy Irish",
            model_id="auto_beta",
            messages=[{"role": "user", "content": "I am Jeremy Irish"}],
            body={"messages": [{"role": "user", "content": "I am Jeremy Irish"}], "model": "auto_beta"}
        )
        
        print(f"Identity Response: {identity_response[:200]}...")
        
        # Wait a moment for processing
        time.sleep(2)
        
        print("\n🔍 Step 2: Querying identity - 'Who am I?'")
        
        # Test 2: Query identity
        identity_query_response = pipeline.pipe(
            user_message="Who am I?",
            model_id="auto_beta", 
            messages=[{"role": "user", "content": "Who am I?"}],
            body={"messages": [{"role": "user", "content": "Who am I?"}], "model": "auto_beta"}
        )
        
        print(f"Identity Query Response: {identity_query_response[:200]}...")
        
        # Check if response contains the name
        success = "jeremy" in identity_query_response.lower() and "irish" in identity_query_response.lower()
        
        print(f"\n✅ Identity Memory Test: {'PASSED' if success else 'FAILED'}")
        print(f"Expected: Response should contain 'Jeremy Irish'")
        print(f"Actual: {'Found Jeremy Irish' if success else 'Jeremy Irish not found'}")
        
        return success
        
    except Exception as e:
        print(f"❌ Identity Memory Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_weather_tool_execution():
    """Test that weather queries actually execute weather tools"""
    print("\n🌤️ Testing Weather Tool Execution")
    print("=" * 50)
    
    try:
        from pipeline.myndy_ai_beta import PipelineBeta
        
        # Create pipeline instance  
        pipeline = PipelineBeta()
        
        # Enable verbose modes for debugging
        pipeline.valves.verbose_coordination = True
        pipeline.valves.show_tool_execution = True
        pipeline.valves.show_tool_results = True
        
        print("🌦️ Testing: 'What is the weather in Seattle?'")
        
        # Test weather query
        weather_response = pipeline.pipe(
            user_message="What is the weather in Seattle?",
            model_id="auto_beta",
            messages=[{"role": "user", "content": "What is the weather in Seattle?"}],
            body={"messages": [{"role": "user", "content": "What is the weather in Seattle?"}], "model": "auto_beta"}
        )
        
        print(f"Weather Response: {weather_response[:300]}...")
        
        # Check if response contains actual weather data (not generic response)
        generic_phrases = [
            "check websites", "accuweather", "weather.com", "ask siri", 
            "google assistant", "alexa", "local news", "online sources"
        ]
        
        has_generic_response = any(phrase in weather_response.lower() for phrase in generic_phrases)
        
        # Look for actual weather data indicators
        weather_data_indicators = [
            "temperature", "°f", "°c", "degrees", "humidity", "wind", 
            "cloudy", "sunny", "rainy", "forecast", "high", "low"
        ]
        
        has_weather_data = any(indicator in weather_response.lower() for indicator in weather_data_indicators)
        
        success = has_weather_data and not has_generic_response
        
        print(f"\n✅ Weather Tool Test: {'PASSED' if success else 'FAILED'}")
        print(f"Expected: Actual weather data, not generic website recommendations")
        print(f"Actual: {'Real weather data found' if has_weather_data else 'No weather data'}")
        if has_generic_response:
            print(f"Issue: Response contains generic website recommendations")
        
        return success
        
    except Exception as e:
        print(f"❌ Weather Tool Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_bridge_availability():
    """Test if required tools are available in the tool bridge"""
    print("\n🔧 Testing Tool Bridge Availability")
    print("=" * 50)
    
    try:
        from tools.myndy_bridge import get_agent_tools, MyndyToolLoader
        
        # Test Shadow Agent tools
        print("🕵️ Testing Shadow Agent tools...")
        shadow_tools = get_agent_tools("shadow_agent")
        shadow_tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in shadow_tools]
        
        required_shadow_tools = ["add_fact", "create_entity", "search_memory", "get_self_profile"]
        shadow_has_memory_tools = any(tool in str(shadow_tool_names) for tool in required_shadow_tools)
        
        print(f"Shadow Agent Tools ({len(shadow_tools)}): {shadow_tool_names[:5]}...")
        print(f"Has Memory Tools: {'✅' if shadow_has_memory_tools else '❌'}")
        
        # Test Personal Assistant tools
        print("\n👤 Testing Personal Assistant tools...")
        pa_tools = get_agent_tools("personal_assistant")
        pa_tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in pa_tools]
        
        has_weather_tools = any("weather" in str(tool).lower() for tool in pa_tool_names)
        
        print(f"Personal Assistant Tools ({len(pa_tools)}): {pa_tool_names[:5]}...")
        print(f"Has Weather Tools: {'✅' if has_weather_tools else '❌'}")
        
        # Test tool loader
        print("\n🔧 Testing MyndyToolLoader...")
        loader = MyndyToolLoader()
        
        # Test specific tool creation
        weather_tool = loader.create_crewai_tool("weather_api")
        local_weather_tool = loader.create_crewai_tool("local_weather")
        memory_tool = loader.create_crewai_tool("add_fact")
        
        print(f"Can create weather_api tool: {'✅' if weather_tool else '❌'}")
        print(f"Can create local_weather tool: {'✅' if local_weather_tool else '❌'}")
        print(f"Can create add_fact tool: {'✅' if memory_tool else '❌'}")
        
        success = shadow_has_memory_tools and has_weather_tools and weather_tool and memory_tool
        
        print(f"\n✅ Tool Bridge Test: {'PASSED' if success else 'FAILED'}")
        return success
        
    except Exception as e:
        print(f"❌ Tool Bridge Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_myndy_registry_tools():
    """Test if required tools exist in myndy registry"""
    print("\n📋 Testing Myndy Registry Tools")
    print("=" * 50)
    
    try:
        # Test myndy-ai tool availability
        sys.path.insert(0, "/Users/jeremy/myndy-core/myndy-ai")
        
        from agents.tools.registry import registry
        
        required_tools = [
            "add_fact", "add_preference", "create_entity", "update_status",
            "search_memory", "get_current_status", "get_self_profile",
            "weather_api", "local_weather"
        ]
        
        available_tools = []
        missing_tools = []
        
        for tool_name in required_tools:
            tool_metadata = registry.get_tool(tool_name)
            if tool_metadata:
                available_tools.append(tool_name)
                print(f"✅ {tool_name}: Available")
            else:
                missing_tools.append(tool_name)
                print(f"❌ {tool_name}: Missing")
        
        success = len(missing_tools) == 0
        
        print(f"\n✅ Registry Test: {'PASSED' if success else 'FAILED'}")
        print(f"Available: {len(available_tools)}/{len(required_tools)} tools")
        if missing_tools:
            print(f"Missing: {missing_tools}")
        
        return success
        
    except Exception as e:
        print(f"❌ Registry Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all critical issue tests"""
    print("🧪 CRITICAL ISSUES TEST SUITE")
    print("=" * 60)
    print("Testing identity memory persistence and weather tool execution")
    print("=" * 60)
    
    results = []
    
    # Test 1: Tool availability
    results.append(("Tool Bridge Availability", test_tool_bridge_availability()))
    
    # Test 2: Myndy registry tools
    results.append(("Myndy Registry Tools", test_myndy_registry_tools()))
    
    # Test 3: Weather tool execution  
    results.append(("Weather Tool Execution", test_weather_tool_execution()))
    
    # Test 4: Identity memory persistence
    results.append(("Identity Memory Persistence", test_identity_memory_persistence()))
    
    # Summary
    print("\n" + "=" * 60)
    print("🧪 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed < total:
        print("\n⚠️  CRITICAL ISSUES DETECTED - FIXES NEEDED")
        return False
    else:
        print("\n🎉 ALL TESTS PASSED - SYSTEM WORKING CORRECTLY")
        return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)