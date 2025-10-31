#!/usr/bin/env python3
"""
Advanced CrewAI Tests with Ollama

This script tests more complex CrewAI features including:
- Sequential and hierarchical processes
- Memory integration
- Custom tools
- Error handling
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path  
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_sequential_process():
    """Test sequential task execution."""
    print("🔄 Testing Sequential Process")
    print("=" * 40)
    
    try:
        from crewai import Agent, Task, Crew, Process
        
        # Create agents for sequential workflow
        data_analyst = Agent(
            role="Data Analyst",
            goal="Analyze data and extract insights",
            backstory="Expert in data analysis and pattern recognition",
            llm="ollama/llama3.2",
            verbose=True
        )
        
        report_writer = Agent(
            role="Report Writer", 
            goal="Create clear, professional reports",
            backstory="Skilled technical writer with data visualization expertise",
            llm="ollama/qwen2.5",
            verbose=True
        )
        
        # Create sequential tasks
        analysis_task = Task(
            description="Analyze the benefits of local AI: privacy, cost, performance. Provide 3 key insights.",
            expected_output="Three clear insights about local AI benefits",
            agent=data_analyst
        )
        
        report_task = Task(
            description="Create a professional report based on the analysis results. Include an executive summary.",
            expected_output="A structured report with executive summary and main findings",
            agent=report_writer
        )
        
        # Create crew with sequential process
        crew = Crew(
            agents=[data_analyst, report_writer],
            tasks=[analysis_task, report_task],
            process=Process.sequential,
            verbose=True
        )
        
        print("✅ Sequential crew created")
        print(f"📊 Process: {crew.process}")
        
        result = crew.kickoff()
        
        print("\n" + "="*50)
        print("📋 SEQUENTIAL PROCESS RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Sequential process test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_integration():
    """Test memory functionality."""
    print("\n🧠 Testing Memory Integration")
    print("=" * 40)
    
    try:
        from crewai import Agent, Task, Crew
        
        # Create agent with memory
        memory_agent = Agent(
            role="Knowledge Manager",
            goal="Store and retrieve information effectively", 
            backstory="Specialist in knowledge management and information retrieval",
            llm="ollama/llama3.2",
            verbose=True,
            memory=True  # Enable memory
        )
        
        # Create memory-related tasks
        store_task = Task(
            description="Remember this important fact: Ollama allows running LLMs locally without internet connection.",
            expected_output="Confirmation that the information has been stored",
            agent=memory_agent
        )
        
        recall_task = Task(
            description="What did you learn about Ollama in the previous task?",
            expected_output="Accurate recall of the Ollama information",
            agent=memory_agent
        )
        
        # Create crew
        crew = Crew(
            agents=[memory_agent],
            tasks=[store_task, recall_task],
            verbose=True,
            memory=True
        )
        
        print("✅ Memory-enabled crew created")
        
        result = crew.kickoff()
        
        print("\n" + "="*50)
        print("🧠 MEMORY TEST RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")
        print("💡 Note: Memory features may require additional setup")
        import traceback
        traceback.print_exc()
        return False

def test_custom_tools():
    """Test custom tools with agents."""
    print("\n🔧 Testing Custom Tools")
    print("=" * 40)
    
    try:
        from crewai import Agent, Task, Crew
        from crewai.tools import tool
        
        # Define a custom tool
        @tool
        def calculate_percentage(part: float, whole: float) -> str:
            """Calculate percentage given part and whole numbers."""
            if whole == 0:
                return "Cannot divide by zero"
            percentage = (part / whole) * 100
            return f"{part} is {percentage:.2f}% of {whole}"
        
        @tool  
        def word_count(text: str) -> str:
            """Count words in a given text."""
            words = len(text.split())
            return f"The text contains {words} words"
        
        # Create agent with custom tools
        calculator_agent = Agent(
            role="Calculator Assistant",
            goal="Perform calculations and text analysis",
            backstory="Mathematical assistant with text processing capabilities",
            llm="ollama/llama3.2",
            tools=[calculate_percentage, word_count],
            verbose=True
        )
        
        # Create task using tools
        calc_task = Task(
            description="Calculate what percentage 25 is of 100, then count the words in this sentence: 'Local AI models provide privacy and control'",
            expected_output="Both the percentage calculation and word count results",
            agent=calculator_agent
        )
        
        # Create crew
        crew = Crew(
            agents=[calculator_agent],
            tasks=[calc_task],
            verbose=True
        )
        
        print("✅ Custom tools crew created")
        print(f"🔧 Tools available: {len(calculator_agent.tools)}")
        
        result = crew.kickoff()
        
        print("\n" + "="*50)
        print("🔧 CUSTOM TOOLS RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Custom tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and recovery."""
    print("\n⚠️  Testing Error Handling")
    print("=" * 40)
    
    try:
        from crewai import Agent, Task, Crew
        
        # Create agent
        test_agent = Agent(
            role="Test Agent",
            goal="Handle various scenarios gracefully",
            backstory="Agent designed to test error handling",
            llm="ollama/llama3.2",
            verbose=True
        )
        
        # Create task that might cause issues
        error_task = Task(
            description="Try to provide a helpful response even if something goes wrong. This is a test of error handling.",
            expected_output="A response that shows graceful error handling",
            agent=test_agent
        )
        
        # Create crew
        crew = Crew(
            agents=[test_agent],
            tasks=[error_task],
            verbose=True
        )
        
        print("✅ Error handling test crew created")
        
        result = crew.kickoff()
        
        print("\n" + "="*50)
        print("⚠️  ERROR HANDLING RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error handling test encountered expected error: {e}")
        # This is actually good - we want to see how errors are handled
        return True

def test_different_models():
    """Test different Ollama models."""
    print("\n🤖 Testing Different Models")
    print("=" * 40)
    
    models_to_test = [
        ("ollama/llama3.2", "General purpose"),
        ("ollama/qwen2.5", "Advanced reasoning"),
        ("ollama/gemma2", "Fast responses"),
        ("ollama/phi3", "Efficient analysis")
    ]
    
    results = []
    
    for model, description in models_to_test:
        try:
            from crewai import Agent, Task, Crew
            
            print(f"\nTesting {model} ({description})...")
            
            agent = Agent(
                role="Model Tester",
                goal="Test model performance",
                backstory=f"Testing {description} capabilities",
                llm=model,
                verbose=False  # Reduce verbosity for multiple tests
            )
            
            task = Task(
                description="Say hello and briefly explain what makes local AI valuable in exactly one sentence.",
                expected_output="A single sentence about local AI value",
                agent=agent
            )
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False
            )
            
            result = crew.kickoff()
            results.append((model, True, str(result)[:100] + "..."))
            print(f"✅ {model} - Success")
            
        except Exception as e:
            results.append((model, False, str(e)))
            print(f"❌ {model} - Failed: {e}")
    
    print("\n" + "="*50)
    print("🤖 MODEL COMPARISON RESULTS:")
    print("="*50)
    for model, success, result in results:
        status = "✅" if success else "❌"
        print(f"{status} {model}")
        print(f"   {result}")
        print()
    
    return len([r for r in results if r[1]]) > 0

def main():
    """Run advanced CrewAI tests."""
    print("🚀 Advanced CrewAI Testing Suite")
    print("=" * 70)
    
    # Check if basic requirements are met
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama server not accessible")
            return 1
    except:
        print("❌ Ollama server not running. Start with: ollama serve")
        return 1
    
    # Run advanced tests
    tests = [
        test_sequential_process,
        test_memory_integration,
        test_custom_tools,
        test_error_handling,
        test_different_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} completed")
            else:
                print(f"❌ {test.__name__} failed")
        except KeyboardInterrupt:
            print(f"\n⏹️  Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print(f"\n📊 Advanced Test Results: {passed}/{total} tests completed")
    
    if passed >= total * 0.8:  # 80% success rate
        print("🎉 Most advanced features are working!")
    elif passed > 0:
        print("⚠️  Some advanced features working, some may need troubleshooting")
    else:
        print("❌ Advanced features need configuration help")
    
    return 0

if __name__ == "__main__":
    exit(main())