#!/usr/bin/env python3
"""
Basic CrewAI Test with Ollama

This script tests CrewAI functionality with Ollama integration.
Run this after setting up Ollama and pulling the required models.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_crew():
    """Test basic CrewAI functionality with Ollama."""
    print("🤖 Testing Basic CrewAI with Ollama")
    print("=" * 50)
    
    try:
        from crewai import Agent, Task, Crew
        
        # Create a simple agent
        researcher = Agent(
            role="Research Analyst",
            goal="Provide accurate and helpful information",
            backstory="You are an expert research analyst with years of experience in data analysis and research.",
            llm="ollama/llama3.2",
            verbose=True,
            allow_delegation=False
        )
        
        # Create a simple task
        research_task = Task(
            description="Write a brief summary about the benefits of local AI models like Ollama. Keep it under 200 words.",
            expected_output="A clear, informative summary about local AI benefits in under 200 words.",
            agent=researcher
        )
        
        # Create crew
        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True
        )
        
        print("✅ CrewAI objects created successfully!")
        print(f"📊 Agent: {researcher.role}")
        print(f"📋 Task: {research_task.description[:50]}...")
        print(f"🔧 LLM: {researcher.llm}")
        
        # Execute the crew
        print("\n🚀 Starting crew execution...")
        result = crew.kickoff()
        
        print("\n" + "="*50)
        print("📝 RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Basic crew test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_agent_crew():
    """Test multi-agent CrewAI functionality."""
    print("\n🤖 Testing Multi-Agent CrewAI")
    print("=" * 50)
    
    try:
        from crewai import Agent, Task, Crew
        
        # Create multiple agents with different models
        researcher = Agent(
            role="Researcher",
            goal="Gather comprehensive information",
            backstory="Expert at finding and analyzing information",
            llm="ollama/llama3.2",
            verbose=True
        )
        
        writer = Agent(
            role="Writer", 
            goal="Create clear and engaging content",
            backstory="Professional writer with excellent communication skills",
            llm="ollama/qwen2.5",  # Different model for variety
            verbose=True
        )
        
        # Create tasks
        research_task = Task(
            description="Research the key advantages of using local AI models",
            expected_output="A list of 3-5 key advantages with brief explanations",
            agent=researcher
        )
        
        writing_task = Task(
            description="Take the research findings and write a professional summary",
            expected_output="A well-structured 150-word summary",
            agent=writer
        )
        
        # Create crew with multiple agents
        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, writing_task],
            verbose=True
        )
        
        print("✅ Multi-agent crew created successfully!")
        print(f"👥 Agents: {len(crew.agents)}")
        print(f"📋 Tasks: {len(crew.tasks)}")
        
        # Execute
        print("\n🚀 Starting multi-agent execution...")
        result = crew.kickoff()
        
        print("\n" + "="*50)
        print("📝 MULTI-AGENT RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_custom_config_agents():
    """Test agents using custom configuration."""
    print("\n🤖 Testing Custom Config Agents")
    print("=" * 50)
    
    try:
        from crewai import Agent, Task, Crew
        from config.llm_config import get_agent_llm
        
        # Use custom configuration for different agent roles
        memory_agent = Agent(
            role="Memory Librarian",
            goal="Organize and categorize information effectively",
            backstory="Specialist in information organization and retrieval",
            llm=get_agent_llm("memory_librarian"),  # Uses llama3.2
            verbose=True
        )
        
        # Create a simple memory task
        memory_task = Task(
            description="Categorize the following information: 'Local AI models provide privacy, cost savings, and offline capability'",
            expected_output="A structured categorization with main topics and subtopics",
            agent=memory_agent
        )
        
        # Create crew
        crew = Crew(
            agents=[memory_agent],
            tasks=[memory_task],
            verbose=True
        )
        
        print("✅ Custom config crew created!")
        print(f"🧠 Agent role: {memory_agent.role}")
        
        # Execute
        print("\n🚀 Starting custom config execution...")
        result = crew.kickoff()
        
        print("\n" + "="*50)
        print("📝 CUSTOM CONFIG RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Custom config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_ollama_status():
    """Check if Ollama is running and models are available."""
    print("🔍 Checking Ollama Status")
    print("=" * 30)
    
    import requests
    
    try:
        # Check if Ollama server is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama server is running")
            print(f"📦 Available models: {len(models)}")
            
            # Check for required models
            model_names = [model.get("name", "") for model in models]
            required_models = ["llama3.2", "qwen2.5", "nomic-embed-text"]
            
            for model in required_models:
                if any(model in name for name in model_names):
                    print(f"✅ {model} - Available")
                else:
                    print(f"⚠️  {model} - Not found (run: ollama pull {model})")
            
            return True
        else:
            print(f"❌ Ollama server responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama server")
        print("💡 Start Ollama with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def main():
    """Run all CrewAI tests."""
    print("🚀 CrewAI Testing Suite")
    print("=" * 60)
    
    # Check Ollama first
    if not check_ollama_status():
        print("\n❌ Ollama is not properly set up. Please:")
        print("1. Install Ollama: brew install ollama")
        print("2. Start Ollama: ollama serve")
        print("3. Pull models: ollama pull llama3.2")
        print("4. Pull embeddings: ollama pull nomic-embed-text")
        return 1
    
    # Run tests
    tests = [
        test_basic_crew,
        test_multi_agent_crew,
        test_custom_config_agents
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} passed")
            else:
                print(f"❌ {test.__name__} failed")
        except KeyboardInterrupt:
            print(f"\n⏹️  Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CrewAI is working with Ollama!")
    elif passed > 0:
        print("⚠️  Some tests passed. Check the errors above.")
    else:
        print("❌ All tests failed. Check your configuration.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())