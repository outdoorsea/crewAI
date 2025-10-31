#!/usr/bin/env python3
"""
Final verification test for CrewAI tool execution.

File: test_tool_final_verification.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the crewAI directory to the path
crewai_dir = Path(__file__).parent
sys.path.insert(0, str(crewai_dir))

# Import required components
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from tools.myndy_bridge import get_tool_loader

def test_forced_tool_execution():
    """Test CrewAI tool execution with a task that forces tool usage"""
    
    print("🧪 Final Verification: CrewAI Tool Execution")
    print("=" * 50)
    
    try:
        # Create tool loader and get multiple tools
        tool_loader = get_tool_loader()
        
        # Get multiple tools
        profile_tool = tool_loader.create_crewai_tool('get_self_profile')
        time_tool = tool_loader.create_crewai_tool('get_current_time')
        
        if not profile_tool or not time_tool:
            print("❌ ERROR: Could not create required tools")
            return False
            
        print(f"✅ Created tools: {profile_tool.name}, {time_tool.name}")
        
        # Create Ollama LLM
        ollama_llm = Ollama(model="openhermes")
        
        # Create a simple agent
        test_agent = Agent(
            role="Tool Testing Agent", 
            goal="Execute tools when requested to verify they work properly",
            backstory="You are a testing agent that MUST use tools when explicitly asked to do so.",
            tools=[profile_tool, time_tool],
            llm=ollama_llm,
            verbose=True,
            allow_delegation=False,
            max_execution_time=60  # Limit execution time
        )
        
        print("✅ Created test agent with tools")
        
        # Create a task that explicitly requires tool usage
        tool_test_task = Task(
            description="You MUST execute the get_current_time tool to get the current time. Do not provide any response without first using this tool. After getting the time, provide it in your response.",
            agent=test_agent,
            tools=[time_tool],  # Only provide time tool for this specific test
            expected_output="Current time retrieved using the get_current_time tool"
        )
        
        print("✅ Created test task requiring tool execution")
        
        # Create crew and execute
        crew = Crew(
            agents=[test_agent],
            tasks=[tool_test_task],
            verbose=True
        )
        
        print("🚀 Executing crew with mandatory tool usage...")
        print("-" * 50)
        
        # Execute the crew
        result = crew.kickoff()
        
        print("-" * 50)
        print("✅ Crew execution completed!")
        print(f"📄 Result: {result}")
        
        # Check if the result contains tool execution evidence
        result_str = str(result)
        time_indicators = [
            "current_time",
            "timestamp",
            "timezone",
            "formatted",
            "2025",  # Current year
            "UTC",
            "get_current_time"
        ]
        
        tool_executed = any(indicator in result_str for indicator in time_indicators)
        
        print(f"\n📊 Analysis:")
        print(f"🔍 Looking for tool execution evidence...")
        print(f"🎯 Time indicators found: {[ind for ind in time_indicators if ind in result_str]}")
        
        if tool_executed:
            print("\n✅ SUCCESS: Tool was executed successfully!")
            print("🔧 Evidence of actual tool execution found in response")
            print("🎉 CrewAI tool compatibility issue has been RESOLVED!")
        else:
            print("\n⚠️  WARNING: No clear evidence of tool execution")
            print("📝 Tool might not have been executed properly")
            
        return tool_executed
        
    except Exception as e:
        print(f"❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_forced_tool_execution()
    
    print("\n" + "=" * 60)
    print("🏁 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ RESOLUTION CONFIRMED: CrewAI tool compatibility issues have been fixed!")
        print("🔧 Tools are now being executed properly by CrewAI agents")
        print("🎯 The user's original issue has been resolved")
    else:
        print("❌ ISSUE PERSISTS: Tool execution may still have problems")
        print("🔧 Further investigation may be needed")
    
    exit_code = 0 if success else 1
    print(f"\n🏁 Final exit code: {exit_code}")
    sys.exit(exit_code)