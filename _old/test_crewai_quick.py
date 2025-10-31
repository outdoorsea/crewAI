#!/usr/bin/env python3
"""
Quick CrewAI Test

A minimal test to verify CrewAI + Ollama is working.
Run this first before the more comprehensive tests.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def quick_test():
    """Quick test of CrewAI with Ollama."""
    print("⚡ Quick CrewAI + Ollama Test")
    print("=" * 35)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from crewai import Agent, Task, Crew
        print("✅ CrewAI imports successful")
        
        # Test agent creation
        print("🤖 Creating agent...")
        agent = Agent(
            role="Test Assistant",
            goal="Verify CrewAI + Ollama integration",
            backstory="A simple test agent",
            llm="ollama/llama3.2",
            verbose=False
        )
        print("✅ Agent created successfully")
        
        # Test task creation
        print("📋 Creating task...")
        task = Task(
            description="Say 'Hello from CrewAI with Ollama!' and nothing else.",
            expected_output="A simple greeting message",
            agent=agent
        )
        print("✅ Task created successfully")
        
        # Test crew creation
        print("👥 Creating crew...")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False
        )
        print("✅ Crew created successfully")
        
        # Test execution
        print("🚀 Executing crew...")
        result = crew.kickoff()
        
        print("\n" + "="*35)
        print("📝 RESULT:")
        print(result)
        print("="*35)
        
        print("\n🎉 Quick test PASSED!")
        print("💡 You can now run the full test suite")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Install missing dependencies: pip install crewai")
        return False
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        print("💡 Check if Ollama is running: ollama serve")
        print("💡 Check if model is available: ollama pull llama3.2")
        return False

def check_prerequisites():
    """Check if prerequisites are met."""
    print("🔍 Checking Prerequisites")
    print("=" * 30)
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            if any("llama3.2" in name for name in model_names):
                print("✅ llama3.2 model available")
                return True
            else:
                print("⚠️  llama3.2 model not found")
                print("💡 Run: ollama pull llama3.2")
                return False
        else:
            print("❌ Ollama server not responding correctly")
            return False
            
    except Exception as e:
        print("❌ Cannot connect to Ollama")
        print("💡 Start Ollama: ollama serve")
        return False

if __name__ == "__main__":
    print("⚡ CrewAI Quick Test")
    print("=" * 25)
    
    if check_prerequisites():
        success = quick_test()
        exit(0 if success else 1)
    else:
        print("\n❌ Prerequisites not met")
        print("\n🔧 Setup steps:")
        print("1. Install Ollama: brew install ollama")
        print("2. Start Ollama: ollama serve")
        print("3. Pull model: ollama pull llama3.2")
        exit(1)