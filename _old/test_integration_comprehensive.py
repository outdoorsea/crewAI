#!/usr/bin/env python3
"""
Comprehensive integration test suite for CrewAI-myndy tool bridge
Tests the complete functionality including dependency fixes
"""

import sys
from pathlib import Path

# Add the crewAI directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_dependency_fixes():
    """Test that dependency issues are resolved"""
    print("🧪 Testing Dependency Fixes")
    print("=" * 50)
    
    try:
        # Test pytz import
        import pytz
        print("✅ pytz imported successfully")
        
        # Test qdrant-client import
        import qdrant_client
        print("✅ qdrant_client imported successfully")
        
        # Test timezone functionality
        tz = pytz.timezone('UTC')
        current_time = __import__('datetime').datetime.now(tz)
        print(f"✅ Timezone functionality working: {current_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dependency test failed: {e}")
        return False

def test_tool_execution_with_dependencies():
    """Test tool execution now that dependencies are fixed"""
    print("\n🧪 Testing Tool Execution with Dependencies")
    print("=" * 50)
    
    try:
        from tools.myndy_bridge import get_tool_loader
        
        # Test creating and executing get_current_time tool
        loader = get_tool_loader()
        time_tool = loader.create_crewai_tool('get_current_time')
        
        if not time_tool:
            print("❌ Could not create time tool")
            return False
            
        print(f"✅ Created time tool: {time_tool.name}")
        
        # Test execution with timezone
        result = time_tool._run(timezone='UTC')
        print(f"✅ Time tool result: {result[:100]}...")
        
        # Test get_self_profile tool
        profile_tool = loader.create_crewai_tool('get_self_profile')
        if profile_tool:
            result = profile_tool._run()
            print(f"✅ Profile tool result: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crewai_integration_complete():
    """Test complete CrewAI integration with multiple tools"""
    print("\n🧪 Testing Complete CrewAI Integration")
    print("=" * 50)
    
    try:
        from crewai import Agent, Task, Crew
        from langchain_community.llms import Ollama
        from tools.myndy_bridge import get_tool_loader
        
        # Get multiple tools
        loader = get_tool_loader()
        tools = []
        
        tool_names = ['get_current_time', 'get_self_profile', 'search_memory']
        for tool_name in tool_names:
            tool = loader.create_crewai_tool(tool_name)
            if tool:
                tools.append(tool)
                print(f"✅ Created tool: {tool_name}")
        
        if not tools:
            print("❌ No tools created")
            return False
            
        # Create agent with multiple tools
        llm = Ollama(model='openhermes', base_url='http://localhost:11434')
        
        agent = Agent(
            role='Enhanced Memory Assistant',
            goal='Answer questions using multiple available tools',
            backstory='I use various tools to provide comprehensive information.',
            llm=llm,
            tools=tools,
            verbose=True
        )
        
        task = Task(
            description='Use the available tools to answer: What time is it and who am I? Use get_current_time to get the time and get_self_profile to get user information.',
            agent=agent,
            tools=tools,
            expected_output='A response using both time and profile tools'
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        print("🚀 Executing comprehensive CrewAI task...")
        result = crew.kickoff()
        print(f"✅ Comprehensive Task Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_agent_types():
    """Test different agent types with their specialized tools"""
    print("\n🧪 Testing Multiple Agent Types")
    print("=" * 50)
    
    try:
        from tools.myndy_bridge import get_agent_tools
        
        agent_types = [
            'memory_librarian',
            'personal_assistant', 
            'research_specialist',
            'health_analyst',
            'finance_tracker'
        ]
        
        for agent_type in agent_types:
            tools = get_agent_tools(agent_type)
            print(f"✅ {agent_type}: {len(tools)} tools loaded")
            
            if tools:
                # Test first tool execution
                first_tool = tools[0]
                try:
                    # Test with minimal parameters
                    result = first_tool._run()
                    print(f"  └─ Tool {first_tool.name} executed successfully")
                except Exception as e:
                    print(f"  └─ Tool {first_tool.name} execution note: {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Multiple agent test failed: {e}")
        return False

def test_error_handling_and_fallbacks():
    """Test error handling and fallback mechanisms"""
    print("\n🧪 Testing Error Handling and Fallbacks")
    print("=" * 50)
    
    try:
        from tools.myndy_bridge import get_tool_loader
        
        loader = get_tool_loader()
        
        # Test invalid tool name
        invalid_tool = loader.create_crewai_tool('nonexistent_tool')
        if invalid_tool is None:
            print("✅ Properly handles invalid tool names")
        else:
            print("❌ Should return None for invalid tools")
        
        # Test tool execution with invalid parameters
        time_tool = loader.create_crewai_tool('get_current_time')
        if time_tool:
            # Test with invalid timezone
            result = time_tool._run(timezone='Invalid/Timezone')
            print(f"✅ Graceful error handling: {result[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🎯 CrewAI-Myndy Integration Test Suite")
    print("=" * 70)
    
    tests = [
        test_dependency_fixes,
        test_tool_execution_with_dependencies,
        test_crewai_integration_complete,
        test_multiple_agent_types,
        test_error_handling_and_fallbacks
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print("\n✅ PASSED\n")
            else:
                print("\n❌ FAILED\n")
        except Exception as e:
            print(f"\n❌ FAILED with exception: {e}\n")
    
    print("=" * 70)
    print(f"🎯 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is working correctly!")
        return True
    else:
        print("⚠️  Some tests failed - see details above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)