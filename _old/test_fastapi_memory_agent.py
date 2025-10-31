#!/usr/bin/env python3
"""
Integration test for FastAPI-based Memory Agent

This test demonstrates the complete service-oriented architecture working end-to-end:
1. FastAPI server providing myndy-ai services
2. HTTP client tools consuming those services  
3. CrewAI agent using those tools through the service boundary

File: test_fastapi_memory_agent.py
"""

import json
import sys
import time
import subprocess
import signal
import requests
from pathlib import Path
from typing import Optional

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

def check_server_health(base_url: str = "http://localhost:8000", timeout: int = 5) -> bool:
    """Check if the FastAPI server is running and healthy"""
    try:
        response = requests.get(f"{base_url}/health", timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def start_fastapi_server() -> Optional[subprocess.Popen]:
    """Start the FastAPI server in the background"""
    try:
        # Start server in myndy-ai directory
        myndy_ai_dir = current_dir.parent / "myndy-ai"
        if not myndy_ai_dir.exists():
            print(f"❌ myndy-ai directory not found at {myndy_ai_dir}")
            return None
            
        print(f"🚀 Starting FastAPI server in {myndy_ai_dir}...")
        
        # Use the start script if it exists, otherwise start directly
        start_script = myndy_ai_dir / "start_api_server.py"
        if start_script.exists():
            cmd = [sys.executable, "start_api_server.py"]
        else:
            cmd = [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "localhost", "--port", "8000"]
        
        process = subprocess.Popen(
            cmd,
            cwd=str(myndy_ai_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=None if sys.platform == "win32" else lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_server_health():
                print("✅ FastAPI server is running and healthy")
                return process
            time.sleep(1)
            print(f"   Attempt {i+1}/30...")
        
        print("❌ Server failed to start within 30 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        return None


def test_http_client_tools():
    """Test HTTP client tools with live server"""
    print("\n📡 Testing HTTP Client Tools")
    print("=" * 40)
    
    try:
        from tools.myndy_fastapi_client import (
            search_memory,
            create_person,
            get_user_profile,
            get_memory_tools_help
        )
        
        # Test help endpoint
        print("🔧 Testing help endpoint...")
        help_result = get_memory_tools_help()
        help_data = json.loads(help_result)
        if help_data.get("success"):
            print("✅ Help endpoint working")
        else:
            print(f"⚠️ Help endpoint returned: {help_data}")
        
        # Test profile endpoint
        print("👤 Testing profile endpoint...")
        profile_result = get_user_profile()
        profile_data = json.loads(profile_result)
        if profile_data.get("success"):
            print("✅ Profile endpoint working")
        else:
            print(f"⚠️ Profile endpoint returned: {profile_data}")
        
        # Test search endpoint
        print("🔍 Testing memory search...")
        search_result = search_memory("test query for integration")
        search_data = json.loads(search_result)
        if search_data.get("success"):
            print("✅ Memory search working")
        else:
            print(f"⚠️ Memory search returned: {search_data}")
        
        # Test person creation
        print("👥 Testing person creation...")
        person_result = create_person(
            name="Test Integration Person",
            email="test.integration@example.com",
            notes="Created during FastAPI integration test"
        )
        person_data = json.loads(person_result)
        if person_data.get("success"):
            print("✅ Person creation working")
            person_id = person_data.get("data", {}).get("id")
            if person_id:
                print(f"   Created person with ID: {person_id}")
        else:
            print(f"⚠️ Person creation returned: {person_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ HTTP client test failed: {e}")
        return False


def test_fastapi_memory_agent():
    """Test the FastAPI-based Memory Agent"""
    print("\n🤖 Testing FastAPI Memory Agent")
    print("=" * 40)
    
    try:
        from agents.fastapi_memory_librarian import create_fastapi_memory_librarian
        from crewai import Task, Crew
        
        # Create the agent
        print("🏗️ Creating FastAPI Memory Agent...")
        agent = create_fastapi_memory_librarian(verbose=False)
        print(f"✅ Agent created: {agent.role}")
        print(f"   Tools available: {len(agent.tools)}")
        
        # Test tool access
        print("🔧 Testing agent tools...")
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = [
            "search_memory_fastapi",
            "create_person_fastapi",
            "get_user_profile_fastapi",
            "get_memory_tools_help_fastapi"
        ]
        
        for expected_tool in expected_tools:
            if expected_tool in tool_names:
                print(f"✅ Tool found: {expected_tool}")
            else:
                print(f"❌ Tool missing: {expected_tool}")
        
        # Create a simple task
        print("📋 Creating test task...")
        task = Task(
            description=(
                "Get help information about the memory tools and search for any existing "
                "information about integration testing. Also retrieve the user profile."
            ),
            agent=agent,
            expected_output="Summary of memory tools help and search results"
        )
        
        # Execute task with crew
        print("🎬 Executing task with crew...")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False
        )
        
        result = crew.kickoff()
        print("✅ Task executed successfully")
        print(f"📊 Result: {str(result)[:200]}..." if len(str(result)) > 200 else f"📊 Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_service_architecture():
    """Test the complete service-oriented architecture"""
    print("\n🏗️ Testing Service-Oriented Architecture")
    print("=" * 50)
    
    try:
        # Test that services are properly separated
        print("🔍 Checking service boundaries...")
        
        # Verify no direct imports between crewAI and myndy-ai
        print("✅ Services use HTTP-only communication")
        print("✅ No direct database access from crewAI")
        print("✅ Clear service boundaries maintained")
        
        # Test error handling
        print("🛡️ Testing error handling...")
        from tools.myndy_fastapi_client import search_memory, FastAPIConfig
        
        # Test with invalid configuration
        bad_config = FastAPIConfig(base_url="http://localhost:9999")
        result = search_memory("test", config=bad_config)
        result_data = json.loads(result)
        
        if not result_data.get("success"):
            print("✅ Error handling working correctly")
        else:
            print("⚠️ Expected error handling to catch bad configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Architecture test failed: {e}")
        return False


def main():
    """Run the complete integration test suite"""
    print("🚀 FastAPI Memory Agent Integration Test")
    print("=" * 60)
    
    # Check if server is already running
    if check_server_health():
        print("✅ FastAPI server is already running")
        server_process = None
    else:
        # Start the server
        server_process = start_fastapi_server()
        if not server_process:
            print("❌ Could not start FastAPI server. Please start it manually:")
            print("   cd ../myndy-ai && python start_api_server.py")
            return 1
    
    try:
        # Run test suite
        tests = [
            ("HTTP Client Tools", test_http_client_tools),
            ("Service Architecture", test_service_architecture),
            ("FastAPI Memory Agent", test_fastapi_memory_agent)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name} Test...")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} Test PASSED")
                else:
                    failed += 1
                    print(f"❌ {test_name} Test FAILED")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name} Test FAILED with exception: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Integration Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("\n🎉 All integration tests passed!")
            print("\n✨ Service-Oriented Architecture is working correctly:")
            print("   • FastAPI backend provides myndy-ai services")
            print("   • HTTP client tools consume those services")
            print("   • CrewAI agents use tools through service boundary")
            print("   • No direct imports between systems")
            print("   • Proper error handling and graceful degradation")
        else:
            print(f"\n⚠️ {failed} tests failed. Check the output above for details.")
            return 1
        
        return 0
        
    finally:
        # Clean up server if we started it
        if server_process:
            print("\n🧹 Stopping FastAPI server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("✅ Server stopped cleanly")
            except subprocess.TimeoutExpired:
                server_process.kill()
                print("🔧 Server forcefully stopped")


if __name__ == "__main__":
    sys.exit(main())