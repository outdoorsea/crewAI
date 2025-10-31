#!/usr/bin/env python3
"""
FastAPI Test Assistant Demo

This script demonstrates the FastAPI Test Assistant agent by running
comprehensive tests of all FastAPI-based memory tools and providing
detailed analysis of the service-oriented architecture.

File: test_fastapi_assistant_demo.py
"""

import json
import sys
import time
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Suppress dependency warnings for cleaner output
try:
    from utils.warning_suppression import setup_clean_environment
    setup_clean_environment()
except ImportError:
    # Fallback warning suppression if utils not available
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)

def run_test_assistant_demo():
    """Run a comprehensive demo of the FastAPI Test Assistant"""
    print("🤖 FastAPI Test Assistant Demo")
    print("=" * 50)
    
    try:
        from agents.fastapi_test_assistant import create_fastapi_test_assistant
        from crewai import Task, Crew
        
        # Create the test assistant
        print("🏗️ Creating FastAPI Test Assistant...")
        assistant = create_fastapi_test_assistant(verbose=False)
        print(f"✅ Assistant created: {assistant.role}")
        print(f"   Tools available: {len(assistant.tools)}")
        
        # Create comprehensive testing task
        print("\n📋 Creating comprehensive testing task...")
        test_task = Task(
            description=(
                "Run a comprehensive test suite of all FastAPI-based memory tools. "
                "Test each tool category systematically: memory search, person management, "
                "profile operations, status operations, fact storage, and help system. "
                "Provide detailed analysis of results, identify any issues, and validate "
                "that the service-oriented architecture is working correctly. "
                "Use the comprehensive test suite tool to get a complete overview."
            ),
            agent=assistant,
            expected_output=(
                "Comprehensive test report including individual test results, "
                "success rates, identified issues, and overall assessment of "
                "FastAPI tool functionality and service architecture compliance."
            )
        )
        
        # Create crew and execute
        print("🎬 Executing comprehensive test suite...")
        crew = Crew(
            agents=[assistant],
            tasks=[test_task],
            verbose=True
        )
        
        start_time = time.time()
        result = crew.kickoff()
        end_time = time.time()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUITE COMPLETED")
        print("=" * 60)
        print(f"⏱️ Execution time: {end_time - start_time:.2f} seconds")
        print(f"📋 Result length: {len(str(result))} characters")
        
        # Try to parse and display key metrics if result contains JSON
        try:
            # Look for JSON in the result
            result_str = str(result)
            if "{" in result_str and "}" in result_str:
                # Extract JSON portion
                json_start = result_str.find("{")
                json_end = result_str.rfind("}") + 1
                json_portion = result_str[json_start:json_end]
                
                parsed_result = json.loads(json_portion)
                summary = parsed_result.get("summary", {})
                
                if summary:
                    print("\n📈 TEST METRICS:")
                    print(f"   Total Tests: {summary.get('total_tests', 'N/A')}")
                    print(f"   Passed: {summary.get('passed', 'N/A')}")
                    print(f"   Failed: {summary.get('failed', 'N/A')}")
                    print(f"   Errors: {summary.get('errors', 'N/A')}")
                    print(f"   Success Rate: {summary.get('success_rate', 'N/A'):.1f}%")
                    print(f"   Overall Status: {summary.get('overall_status', 'N/A')}")
        except:
            # If we can't parse JSON, just show the raw result
            pass
        
        print(f"\n📄 DETAILED RESULTS:")
        print("-" * 40)
        print(str(result))
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_individual_tool_demo():
    """Demonstrate individual tool testing capabilities"""
    print("\n🔧 Individual Tool Testing Demo")
    print("=" * 40)
    
    try:
        from agents.fastapi_test_assistant import create_fastapi_test_assistant
        from crewai import Task, Crew
        
        # Create the test assistant
        assistant = create_fastapi_test_assistant(verbose=False)
        
        # Test individual tool categories
        individual_tests = [
            {
                "name": "Memory Search Test",
                "description": "Test memory search functionality with a specific query about 'FastAPI integration testing'.",
                "expected": "Search results and analysis of memory search tool performance."
            },
            {
                "name": "Person Management Test", 
                "description": "Test person creation, retrieval, and listing capabilities.",
                "expected": "Results of person management operations including creation and retrieval."
            },
            {
                "name": "Profile Operations Test",
                "description": "Test user profile retrieval and update functionality.", 
                "expected": "Profile operation results and validation of profile management."
            }
        ]
        
        for test in individual_tests:
            print(f"\n🧪 Running {test['name']}...")
            
            task = Task(
                description=test["description"],
                agent=assistant,
                expected_output=test["expected"]
            )
            
            crew = Crew(agents=[assistant], tasks=[task], verbose=False)
            result = crew.kickoff()
            
            print(f"✅ {test['name']} completed")
            print(f"📋 Result summary: {str(result)[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual tool demo failed: {e}")
        return False


def main():
    """Run the complete FastAPI Test Assistant demonstration"""
    print("🚀 FastAPI Test Assistant Demonstration")
    print("=" * 60)
    print("This demo shows the specialized testing agent validating FastAPI tools")
    print()
    
    # Check if we can import required modules
    try:
        from agents.fastapi_test_assistant import create_fastapi_test_assistant
        print("✅ FastAPI Test Assistant module loaded successfully")
    except ImportError as e:
        print(f"❌ Failed to import FastAPI Test Assistant: {e}")
        print("   Make sure you're in the crewAI directory and all dependencies are installed")
        return 1
    
    success = True
    
    # Run comprehensive demo
    print("\n" + "🎯" * 20)
    print("COMPREHENSIVE TEST SUITE DEMO")
    print("🎯" * 20)
    if not run_test_assistant_demo():
        success = False
    
    # Run individual tool demo
    print("\n" + "🔍" * 20) 
    print("INDIVIDUAL TOOL TESTING DEMO")
    print("🔍" * 20)
    if not run_individual_tool_demo():
        success = False
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 FastAPI Test Assistant demonstration completed successfully!")
        print("\n✨ The Test Assistant demonstrates:")
        print("   • Systematic testing of all FastAPI-based memory tools")
        print("   • Comprehensive validation of service-oriented architecture")
        print("   • Detailed error analysis and performance reporting")
        print("   • Individual and suite-based testing capabilities")
        print("   • Real-time validation of HTTP communication")
        print("\n📋 Next Steps:")
        print("   1. Use the Test Assistant to validate your FastAPI server setup")
        print("   2. Run regular validation tests during development")
        print("   3. Integrate testing into your CI/CD pipeline")
        print("   4. Extend the Test Assistant for additional tool categories")
    else:
        print("⚠️ Some parts of the demonstration encountered issues.")
        print("   Please check the error messages above and ensure:")
        print("   1. FastAPI server is running (if testing live tools)")
        print("   2. All dependencies are properly installed")
        print("   3. Python path and imports are configured correctly")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())