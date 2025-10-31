#!/usr/bin/env python3
"""
Test script to see if we can make a simple CrewAI tool that works
"""

import sys
from pathlib import Path

# Add the crewAI directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_simple_langchain_tool():
    """Test simple LangChain tool creation"""
    print("🧪 Testing Simple LangChain Tool Creation")
    print("=" * 50)
    
    try:
        from langchain.tools import BaseTool
        
        # Create a simple tool by defining a class with minimal overhead
        class GetProfileTool(BaseTool):
            name = "get_self_profile"
            description = "Get user profile information"
            
            def _run(self, **kwargs):
                """Execute the tool"""
                return """{
  "success": true,
  "message": "No user profile found in memory",
  "retrieved_at": "2025-05-30T17:49:20.594855"
}"""
        
        # Test tool creation
        print("📋 Test 1: Creating simple LangChain tool...")
        profile_tool = GetProfileTool()
        print(f"✅ Created tool: {profile_tool.name}")
        
        # Test execution
        print("\n📋 Test 2: Testing tool execution...")
        result = profile_tool._run()
        print(f"✅ Tool result: {result}")
        
        # Test with CrewAI
        print("\n📋 Test 3: Testing with CrewAI...")
        try:
            from crewai import Agent, Task
            from langchain_community.llms import Ollama
            
            llm = Ollama(model="openhermes", base_url="http://localhost:11434")
            
            agent = Agent(
                role="Test Agent",
                goal="Test tool usage",
                backstory="I test tools.",
                llm=llm,
                tools=[profile_tool]
            )
            
            task = Task(
                description="Use the get_self_profile tool to answer: Who am I? You MUST use the get_self_profile tool.",
                agent=agent,
                expected_output="Response using tool results"
            )
            
            print("🔧 Executing task with simple tool...")
            try:
                result = task.execute()
                print(f"✅ Task result: {result}")
            except AttributeError:
                # Try older CrewAI version method
                result = task.run()
                print(f"✅ Task result: {result}")
            
        except Exception as e:
            print(f"❌ CrewAI test failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🎉 Simple LangChain tool testing completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_langchain_tool()