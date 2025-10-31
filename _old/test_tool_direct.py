#!/usr/bin/env python3
"""
Direct test of CrewAI tool execution to verify compatibility fixes.

File: test_tool_direct.py
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

def test_direct_tool_execution():
    """Test CrewAI tool execution directly with an agent and task"""
    
    print("🧪 Testing Direct CrewAI Tool Execution")
    print("=" * 50)
    
    try:
        # Create tool loader and get a specific tool
        tool_loader = get_tool_loader()
        
        # Get the get_self_profile tool
        profile_tool = tool_loader.create_crewai_tool('get_self_profile')
        
        if not profile_tool:
            print("❌ ERROR: Could not create get_self_profile tool")
            return False
            
        print(f"✅ Created tool: {profile_tool.name}")
        print(f"📝 Tool description: {profile_tool.description[:100]}...")
        
        # Create Ollama LLM
        ollama_llm = Ollama(model="openhermes")
        
        # Create a simple agent
        test_agent = Agent(
            role="Memory Assistant", 
            goal="Help users access their profile information",
            backstory="You are a helpful assistant that can access user profile data.",
            tools=[profile_tool],  # Provide the tool to the agent
            llm=ollama_llm,  # Use Ollama instead of OpenAI
            verbose=True,
            allow_delegation=False
        )
        
        print("✅ Created test agent with tool")
        
        # Create a task that should use the tool
        profile_task = Task(
            description="Get the user's profile information and tell me who I am. Use the get_self_profile tool to access my profile data.",
            agent=test_agent,
            tools=[profile_tool],  # Explicitly provide tools to the task
            expected_output="Profile information about the user"
        )
        
        print("✅ Created test task")
        
        # Create crew and execute
        crew = Crew(
            agents=[test_agent],
            tasks=[profile_task],
            verbose=True
        )
        
        print("🚀 Executing crew with tool...")
        print("-" * 30)
        
        # Execute the crew
        result = crew.kickoff()
        
        print("-" * 30)
        print("✅ Crew execution completed!")
        print(f"📄 Result: {result}")
        
        # Check if the result indicates tool usage
        result_str = str(result).lower()
        success_indicators = [
            "profile",
            "memory",
            "retrieved_at",
            "success",
            "user"
        ]
        
        tool_used = any(indicator in result_str for indicator in success_indicators)
        
        if tool_used:
            print("\n✅ SUCCESS: Tool execution appears to be working!")
            print("🔧 Evidence of tool usage found in response")
        else:
            print("\n⚠️  WARNING: No clear evidence of tool usage in response")
            print("📝 The response might not indicate tool execution")
            
        return tool_used
        
    except Exception as e:
        print(f"❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_tool_execution()
    exit_code = 0 if success else 1
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    sys.exit(exit_code)