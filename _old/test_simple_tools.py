#!/usr/bin/env python3
"""
Test script to verify tools work with CrewAI using a simpler tool format
"""

import sys
from pathlib import Path

# Add the crewAI directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_crewai_tools():
    """Test simple CrewAI tools without complex wrappers"""
    print("🧪 Testing Simple CrewAI Tools")
    print("=" * 50)
    
    try:
        # Test 1: Create simple tools using CrewAI's basic format
        from crewai.tools import BaseTool
        from pydantic import BaseModel, Field
        import json
        
        class GetProfileTool(BaseTool):
            name: str = "get_profile"
            description: str = "Get user profile information"
            
            def _run(self, **kwargs):
                """Execute the tool"""
                return {
                    "success": True,
                    "message": "No user profile found in memory",
                    "profile": {}
                }
        
        class SearchMemoryTool(BaseTool):
            name: str = "search_memory"
            description: str = "Search memory for user information"
            
            def _run(self, query: str = "", **kwargs):
                """Execute the tool"""
                return {
                    "success": True,
                    "query": query,
                    "results": [],
                    "message": f"No results found for query: {query}"
                }
        
        # Test 2: Test with CrewAI agent
        print("📋 Test 1: Creating simple tools...")
        
        profile_tool = GetProfileTool()
        memory_tool = SearchMemoryTool()
        
        print(f"✅ Created tools: {profile_tool.name}, {memory_tool.name}")
        
        # Test 3: Test direct execution
        print("\n📋 Test 2: Testing direct tool execution...")
        
        profile_result = profile_tool._run()
        print(f"✅ Profile tool result: {profile_result}")
        
        memory_result = memory_tool._run(query="user identity")
        print(f"✅ Memory tool result: {memory_result}")
        
        # Test 4: Test with CrewAI agent
        print("\n📋 Test 3: Testing with CrewAI agent...")
        
        try:
            from crewai import Agent, Task
            from langchain_community.llms import Ollama
            
            # Create simple agent
            llm = Ollama(model="openhermes", base_url="http://localhost:11434")
            
            agent = Agent(
                role="Test Agent",
                goal="Test tool usage",
                backstory="I am testing tools.",
                llm=llm,
                tools=[profile_tool, memory_tool]
            )
            
            task = Task(
                description="Use the get_profile and search_memory tools to answer: Who am I?",
                agent=agent,
                expected_output="Response using tool results"
            )
            
            print("🔧 Executing task with tools...")
            result = task.execute_sync()
            print(f"✅ Task result: {result}")
            
        except Exception as e:
            print(f"❌ CrewAI agent test failed: {e}")
        
        print("\n🎉 Simple tool testing completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crewai_tools()