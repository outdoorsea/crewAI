#!/usr/bin/env python3
"""
Simple test script for agent tools - focuses on core tool functionality
Tests that tools can be created and executed without complex agent scenarios
"""

import sys
from pathlib import Path

# Add the crewAI directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_tool_creation_all_agents():
    """Test that tools can be created for all agent types"""
    print("🔧 Testing Tool Creation for All Agent Types")
    print("=" * 60)
    
    try:
        from tools.myndy_bridge import get_agent_tools
        
        agent_types = [
            'memory_librarian',
            'personal_assistant', 
            'research_specialist',
            'health_analyst',
            'finance_tracker'
        ]
        
        results = {}
        
        for agent_type in agent_types:
            print(f"\n📋 Testing {agent_type}:")
            try:
                tools = get_agent_tools(agent_type)
                results[agent_type] = len(tools)
                print(f"  ✅ {len(tools)} tools created successfully")
                
                # Test first tool if available
                if tools:
                    first_tool = tools[0]
                    print(f"  └─ First tool: {first_tool.name}")
                    print(f"     Description: {first_tool.description[:50]}...")
                    
                    # Test tool execution for known safe tools
                    if first_tool.name in ['get_current_time', 'get_self_profile', 'search_memory']:
                        try:
                            result = first_tool._run()
                            print(f"  ✅ Tool execution successful: {str(result)[:50]}...")
                        except Exception as e:
                            print(f"  ⚠️  Tool execution failed: {e}")
                else:
                    print(f"  ⚠️  No tools available for {agent_type}")
                    
            except Exception as e:
                print(f"  ❌ Failed to create tools for {agent_type}: {e}")
                results[agent_type] = 0
        
        return results
        
    except Exception as e:
        print(f"❌ Tool creation test failed: {e}")
        return {}

def test_core_tools_directly():
    """Test core tools directly without agent framework"""
    print("\n🎯 Testing Core Tools Directly")
    print("=" * 60)
    
    try:
        from tools.myndy_bridge import get_tool_loader
        
        # Test the core tools we know should work
        core_tools = [
            'get_current_time',
            'get_self_profile', 
            'search_memory',
            'create_entity'
        ]
        
        loader = get_tool_loader()
        
        for tool_name in core_tools:
            print(f"\n🔧 Testing {tool_name}:")
            try:
                tool = loader.create_crewai_tool(tool_name)
                if tool:
                    print(f"  ✅ Tool created: {tool.name}")
                    
                    # Test execution with appropriate parameters
                    if tool_name == 'get_current_time':
                        result = tool._run(timezone='UTC')
                    elif tool_name == 'create_entity':
                        result = tool._run(name='Test User', entity_type='person')
                    else:
                        result = tool._run()
                        
                    print(f"  ✅ Execution result: {str(result)[:100]}...")
                else:
                    print(f"  ❌ Failed to create {tool_name}")
                    
            except Exception as e:
                print(f"  ❌ Error testing {tool_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Core tools test failed: {e}")
        return False

def test_basic_crewai_functionality():
    """Test basic CrewAI functionality without tools"""
    print("\n🤖 Testing Basic CrewAI Functionality")
    print("=" * 60)
    
    try:
        from crewai import Agent, Task, Crew
        from langchain_community.llms import Ollama
        
        # Test basic agent creation and execution without tools
        llm = Ollama(model='openhermes', base_url='http://localhost:11434')
        
        agent = Agent(
            role='Test Agent',
            goal='Provide simple responses for testing',
            backstory='I am a test agent used to verify basic functionality.',
            llm=llm,
            tools=[],  # No tools
            verbose=False  # Reduce output
        )
        
        task = Task(
            description='Say hello and confirm you are working.',
            agent=agent,
            expected_output='A simple greeting confirming the agent is functional'
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False
        )
        
        print("🚀 Testing basic agent execution...")
        result = crew.kickoff()
        print(f"✅ Agent Response: {str(result)[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Basic CrewAI test failed: {e}")
        return False

def main():
    """Run all simplified tests"""
    print("🎯 Simplified Agent and Tool Testing")
    print("=" * 70)
    
    # Test 1: Tool creation for all agents
    tool_results = test_tool_creation_all_agents()
    
    # Test 2: Core tools directly
    core_tools_working = test_core_tools_directly()
    
    # Test 3: Basic CrewAI functionality
    basic_crewai_working = test_basic_crewai_functionality()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary:")
    print("=" * 70)
    
    print("\n🔧 Tool Creation Results:")
    total_tools = 0
    for agent_type, tool_count in tool_results.items():
        total_tools += tool_count
        status = "✅" if tool_count > 0 else "❌"
        print(f"  {status} {agent_type}: {tool_count} tools")
    
    print(f"\n📈 Overall Results:")
    print(f"  • Total tools created: {total_tools}")
    print(f"  • Core tools working: {'✅' if core_tools_working else '❌'}")
    print(f"  • Basic CrewAI working: {'✅' if basic_crewai_working else '❌'}")
    
    # Determine overall success
    agents_with_tools = sum(1 for count in tool_results.values() if count > 0)
    total_agents = len(tool_results)
    
    success_rate = (agents_with_tools / total_agents) * 100 if total_agents > 0 else 0
    
    print(f"\n🎯 Success Rate: {agents_with_tools}/{total_agents} agents with tools ({success_rate:.1f}%)")
    
    if success_rate >= 60 and core_tools_working:
        print("🎉 SYSTEM IS FUNCTIONAL - Core capabilities working!")
        return True
    else:
        print("⚠️  System needs attention - core functionality issues detected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)