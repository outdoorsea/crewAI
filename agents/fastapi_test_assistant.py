"""
FastAPI Test Assistant Agent

Specialized agent for testing FastAPI-based memory tools and validating the 
service-oriented architecture. This agent systematically tests all HTTP client
tools and provides detailed feedback on their functionality.

File: agents/fastapi_test_assistant.py
"""

from crewai import Agent
from langchain_core.tools import tool
from typing import List, Optional, Dict, Any
import sys
import json
import time
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Suppress dependency warnings for cleaner output
try:
    from utils.warning_suppression import setup_clean_environment
    setup_clean_environment()
except ImportError:
    # Fallback warning suppression if utils not available
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)

from tools.myndy_fastapi_client import (
    FastAPIConfig,
    search_memory,
    create_person,
    add_memory_fact,
    get_memory_person,
    list_memory_people,
    get_user_profile,
    update_user_profile,
    get_current_status,
    update_user_status,
    get_memory_tools_help,
    get_memory_tools_examples
)
from config import get_agent_llm


# Test-specific tools for the assistant

@tool("test_memory_search")
def test_memory_search_tool(query: str = "test search query") -> str:
    """
    Test the memory search functionality with various query types.
    
    Args:
        query: Search query to test (default: "test search query")
        
    Returns:
        JSON string with test results and analysis
    """
    # Ensure query is a proper string, not a schema object
    if isinstance(query, dict) and "type" in query:
        query = "test search query"  # Fallback to default
    elif not isinstance(query, str):
        query = str(query)
    test_results = {
        "test_name": "Memory Search Test",
        "timestamp": time.time(),
        "results": []
    }
    
    # Test cases
    test_cases = [
        {"query": query, "description": "User-provided query"},
        {"query": "people I know", "description": "People search"},
        {"query": "recent events", "description": "Events search"},
        {"query": "integration test", "description": "Technical search"}
    ]
    
    for case in test_cases:
        try:
            result = search_memory(case["query"], limit=5)
            result_data = json.loads(result)
            
            test_results["results"].append({
                "query": case["query"],
                "description": case["description"],
                "success": result_data.get("success", False),
                "response": result_data,
                "status": "PASS" if result_data.get("success") else "FAIL"
            })
        except Exception as e:
            test_results["results"].append({
                "query": case["query"],
                "description": case["description"],
                "success": False,
                "error": str(e),
                "status": "ERROR"
            })
    
    return json.dumps(test_results, indent=2)


@tool("test_person_management")
def test_person_management_tool() -> str:
    """
    Test person creation, retrieval, and listing functionality.
    
    Returns:
        JSON string with comprehensive person management test results
    """
    test_results = {
        "test_name": "Person Management Test",
        "timestamp": time.time(),
        "results": []
    }
    
    # Test 1: Create a test person
    try:
        create_result = create_person(
            name=f"Test Person {int(time.time())}",
            email="test.assistant@example.com",
            organization="FastAPI Testing Corp",
            job_title="Quality Assurance Specialist",
            notes="Created by FastAPI Test Assistant for validation purposes"
        )
        create_data = json.loads(create_result)
        
        test_results["results"].append({
            "test": "Person Creation",
            "success": create_data.get("success", False),
            "response": create_data,
            "status": "PASS" if create_data.get("success") else "FAIL"
        })
        
        # Get person ID for further tests
        person_id = None
        if create_data.get("success") and create_data.get("data"):
            person_id = create_data["data"].get("id")
            
    except Exception as e:
        test_results["results"].append({
            "test": "Person Creation",
            "success": False,
            "error": str(e),
            "status": "ERROR"
        })
        person_id = None
    
    # Test 2: List people
    try:
        list_result = list_memory_people(limit=10)
        list_data = json.loads(list_result)
        
        test_results["results"].append({
            "test": "People Listing",
            "success": list_data.get("success", False),
            "response": list_data,
            "status": "PASS" if list_data.get("success") else "FAIL"
        })
    except Exception as e:
        test_results["results"].append({
            "test": "People Listing",
            "success": False,
            "error": str(e),
            "status": "ERROR"
        })
    
    # Test 3: Get specific person (if we have an ID)
    if person_id:
        try:
            get_result = get_memory_person(person_id)
            get_data = json.loads(get_result)
            
            test_results["results"].append({
                "test": "Person Retrieval",
                "person_id": person_id,
                "success": get_data.get("success", False),
                "response": get_data,
                "status": "PASS" if get_data.get("success") else "FAIL"
            })
        except Exception as e:
            test_results["results"].append({
                "test": "Person Retrieval",
                "person_id": person_id,
                "success": False,
                "error": str(e),
                "status": "ERROR"
            })
    
    return json.dumps(test_results, indent=2)


@tool("test_profile_operations")
def test_profile_operations_tool() -> str:
    """
    Test user profile retrieval and update functionality.
    
    Returns:
        JSON string with profile operation test results
    """
    test_results = {
        "test_name": "Profile Operations Test",
        "timestamp": time.time(),
        "results": []
    }
    
    # Test 1: Get user profile
    try:
        profile_result = get_user_profile()
        profile_data = json.loads(profile_result)
        
        test_results["results"].append({
            "test": "Profile Retrieval",
            "success": profile_data.get("success", False),
            "response": profile_data,
            "status": "PASS" if profile_data.get("success") else "FAIL"
        })
    except Exception as e:
        test_results["results"].append({
            "test": "Profile Retrieval",
            "success": False,
            "error": str(e),
            "status": "ERROR"
        })
    
    # Test 2: Update user profile
    try:
        update_result = update_user_profile(
            interests=["FastAPI testing", "Service architecture", "Agent validation"],
            goals=["Validate service integration", "Test tool functionality"]
        )
        update_data = json.loads(update_result)
        
        test_results["results"].append({
            "test": "Profile Update",
            "success": update_data.get("success", False),
            "response": update_data,
            "status": "PASS" if update_data.get("success") else "FAIL"
        })
    except Exception as e:
        test_results["results"].append({
            "test": "Profile Update",
            "success": False,
            "error": str(e),
            "status": "ERROR"
        })
    
    return json.dumps(test_results, indent=2)


@tool("test_status_operations")
def test_status_operations_tool() -> str:
    """
    Test status retrieval and update functionality.
    
    Returns:
        JSON string with status operation test results
    """
    test_results = {
        "test_name": "Status Operations Test",
        "timestamp": time.time(),
        "results": []
    }
    
    # Test 1: Get current status
    try:
        status_result = get_current_status()
        status_data = json.loads(status_result)
        
        test_results["results"].append({
            "test": "Status Retrieval",
            "success": status_data.get("success", False),
            "response": status_data,
            "status": "PASS" if status_data.get("success") else "FAIL"
        })
    except Exception as e:
        test_results["results"].append({
            "test": "Status Retrieval",
            "success": False,
            "error": str(e),
            "status": "ERROR"
        })
    
    # Test 2: Update status
    try:
        update_result = update_user_status(
            mood="focused",
            energy_level="high",
            activity="testing FastAPI tools",
            availability="busy",
            notes="Running comprehensive FastAPI tool validation tests"
        )
        update_data = json.loads(update_result)
        
        test_results["results"].append({
            "test": "Status Update",
            "success": update_data.get("success", False),
            "response": update_data,
            "status": "PASS" if update_data.get("success") else "FAIL"
        })
    except Exception as e:
        test_results["results"].append({
            "test": "Status Update",
            "success": False,
            "error": str(e),
            "status": "ERROR"
        })
    
    return json.dumps(test_results, indent=2)


@tool("test_fact_storage")
def test_fact_storage_tool() -> str:
    """
    Test fact storage functionality with various data types.
    
    Returns:
        JSON string with fact storage test results
    """
    test_results = {
        "test_name": "Fact Storage Test",
        "timestamp": time.time(),
        "results": []
    }
    
    # Test facts with different configurations
    test_facts = [
        {
            "content": f"FastAPI tool testing completed at {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "source": "FastAPI Test Assistant",
            "confidence": 1.0,
            "tags": ["testing", "fastapi", "validation"]
        },
        {
            "content": "Service-oriented architecture validation in progress",
            "source": "Integration Testing",
            "confidence": 0.95,
            "tags": ["architecture", "soa", "validation"]
        },
        {
            "content": "HTTP client tools functioning correctly",
            "source": "Test Assistant",
            "tags": ["http", "tools", "status"]
        }
    ]
    
    for i, fact in enumerate(test_facts):
        try:
            result = add_memory_fact(
                content=fact["content"],
                source=fact.get("source"),
                confidence=fact.get("confidence"),
                tags=fact.get("tags")
            )
            result_data = json.loads(result)
            
            test_results["results"].append({
                "test": f"Fact Storage {i+1}",
                "fact_content": fact["content"][:50] + "...",
                "success": result_data.get("success", False),
                "response": result_data,
                "status": "PASS" if result_data.get("success") else "FAIL"
            })
        except Exception as e:
            test_results["results"].append({
                "test": f"Fact Storage {i+1}",
                "fact_content": fact["content"][:50] + "...",
                "success": False,
                "error": str(e),
                "status": "ERROR"
            })
    
    return json.dumps(test_results, indent=2)


@tool("test_help_system")
def test_help_system_tool() -> str:
    """
    Test the help and training endpoints.
    
    Returns:
        JSON string with help system test results
    """
    test_results = {
        "test_name": "Help System Test",
        "timestamp": time.time(),
        "results": []
    }
    
    # Test 1: Get help information
    try:
        help_result = get_memory_tools_help()
        help_data = json.loads(help_result)
        
        test_results["results"].append({
            "test": "Tools Help",
            "success": help_data.get("success", False),
            "response": help_data,
            "status": "PASS" if help_data.get("success") else "FAIL"
        })
    except Exception as e:
        test_results["results"].append({
            "test": "Tools Help",
            "success": False,
            "error": str(e),
            "status": "ERROR"
        })
    
    # Test 2: Get examples
    try:
        examples_result = get_memory_tools_examples()
        examples_data = json.loads(examples_result)
        
        test_results["results"].append({
            "test": "Tools Examples",
            "success": examples_data.get("success", False),
            "response": examples_data,
            "status": "PASS" if examples_data.get("success") else "FAIL"
        })
    except Exception as e:
        test_results["results"].append({
            "test": "Tools Examples",
            "success": False,
            "error": str(e),
            "status": "ERROR"
        })
    
    return json.dumps(test_results, indent=2)


@tool("run_comprehensive_test_suite")
def run_comprehensive_test_suite_tool(query: str = "comprehensive test suite validation") -> str:
    """
    Run all FastAPI tool tests and provide a comprehensive summary.
    
    Args:
        query: Optional query string for memory search tests
    
    Returns:
        JSON string with complete test suite results and analysis
    """
    # Ensure query is a proper string, not a schema object
    if isinstance(query, dict) and "type" in query:
        query = "comprehensive test suite validation"  # Fallback to default
    elif not isinstance(query, str):
        query = str(query)
    suite_results = {
        "test_suite": "FastAPI Tools Comprehensive Validation",
        "timestamp": time.time(),
        "start_time": time.strftime('%Y-%m-%d %H:%M:%S'),
        "individual_tests": [],
        "summary": {}
    }
    
    # Run all individual tests
    test_functions = [
        ("Memory Search", test_memory_search_tool),
        ("Person Management", test_person_management_tool),
        ("Profile Operations", test_profile_operations_tool),
        ("Status Operations", test_status_operations_tool),
        ("Fact Storage", test_fact_storage_tool),
        ("Help System", test_help_system_tool)
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    error_tests = 0
    
    for test_name, test_func in test_functions:
        try:
            # Call the tool functions directly with proper parameters
            if test_name == "Memory Search":
                # Ensure query is a string, not a schema object
                test_query = query if isinstance(query, str) else "comprehensive test suite validation"
                result = test_memory_search_tool(test_query)
            elif test_name == "Person Management":
                result = test_person_management_tool()
            elif test_name == "Profile Operations":
                result = test_profile_operations_tool()
            elif test_name == "Status Operations":
                result = test_status_operations_tool()
            elif test_name == "Fact Storage":
                result = test_fact_storage_tool()
            elif test_name == "Help System":
                result = test_help_system_tool()
            
            result_data = json.loads(result)
            suite_results["individual_tests"].append({
                "test_name": test_name,
                "result": result_data
            })
            
            # Count results
            for test_result in result_data.get("results", []):
                total_tests += 1
                status = test_result.get("status", "UNKNOWN")
                if status == "PASS":
                    passed_tests += 1
                elif status == "FAIL":
                    failed_tests += 1
                elif status == "ERROR":
                    error_tests += 1
                    
        except Exception as e:
            suite_results["individual_tests"].append({
                "test_name": test_name,
                "error": str(e),
                "status": "SUITE_ERROR"
            })
            error_tests += 1
    
    # Calculate summary
    suite_results["summary"] = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "errors": error_tests,
        "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
        "overall_status": "PASS" if failed_tests == 0 and error_tests == 0 else "FAIL",
        "end_time": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return json.dumps(suite_results, indent=2)


def get_fastapi_test_tools() -> List:
    """Get all FastAPI testing tools for the agent"""
    return [
        test_memory_search_tool,
        test_person_management_tool,
        test_profile_operations_tool,
        test_status_operations_tool,
        test_fact_storage_tool,
        test_help_system_tool,
        run_comprehensive_test_suite_tool
    ]


def create_fastapi_test_assistant(
    verbose: bool = True,
    allow_delegation: bool = False,
    max_iter: int = 30,
    max_execution_time: Optional[int] = 600,
    fastapi_config: Optional[FastAPIConfig] = None
) -> Agent:
    """
    Create a FastAPI Test Assistant agent for validating HTTP-based tools.
    
    Args:
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow task delegation to other agents
        max_iter: Maximum number of iterations for task execution
        max_execution_time: Maximum execution time in seconds
        fastapi_config: Optional FastAPI configuration for custom endpoints
        
    Returns:
        Configured FastAPI Test Assistant agent
    """
    
    # Get testing tools
    tools = get_fastapi_test_tools()
    
    # Get the appropriate LLM for this agent
    try:
        llm = get_agent_llm("test_assistant")
    except Exception as e:
        print(f"Warning: Failed to get configured LLM: {e}")
        # Fallback to a default LLM if configuration fails
        from crewai import LLM
        llm = LLM(model="ollama/llama3.2:latest", base_url="http://localhost:11434")
    
    # Create the agent with specialized testing instructions
    agent = Agent(
        role="FastAPI Test Assistant",
        goal=(
            "Systematically test and validate all FastAPI-based memory tools to ensure "
            "the service-oriented architecture is functioning correctly. Provide detailed "
            "analysis of tool performance, identify any issues, and verify proper "
            "HTTP communication between crewAI agents and myndy-ai services."
        ),
        backstory=(
            "You are a specialized quality assurance engineer with expertise in "
            "service-oriented architectures, API testing, and distributed systems validation. "
            "You have extensive experience in testing HTTP-based microservices, validating "
            "tool integrations, and ensuring proper separation of concerns in multi-service "
            "architectures. Your role is critical in validating that the FastAPI-based "
            "tools work correctly and that the service boundaries are properly maintained. "
            "You understand the importance of comprehensive testing, error analysis, and "
            "performance validation in service-oriented systems. You provide clear, "
            "actionable feedback on system functionality and identify potential issues "
            "before they impact production usage."
        ),
        tools=tools,
        llm=llm,
        verbose=verbose,
        allow_delegation=allow_delegation,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        memory=True  # Enable memory for this agent
    )
    
    return agent


def get_fastapi_test_assistant_capabilities() -> List[str]:
    """
    Get a list of capabilities for the FastAPI Test Assistant agent.
    
    Returns:
        List of capability descriptions
    """
    return [
        "Comprehensive FastAPI tool validation",
        "Memory search functionality testing",
        "Person management operations testing",
        "Profile and status operations validation",
        "Fact storage system testing",
        "Help and training system validation",
        "HTTP communication verification",
        "Service boundary compliance checking",
        "Error handling and graceful degradation testing",
        "Performance and reliability assessment",
        "Test result analysis and reporting",
        "Service-oriented architecture validation"
    ]


if __name__ == "__main__":
    # Test agent creation and basic functionality
    print("FastAPI Test Assistant Agent")
    print("=" * 40)
    
    try:
        agent = create_fastapi_test_assistant(verbose=False)
        print(f"✅ Agent created successfully")
        print(f"Role: {agent.role}")
        print(f"Tools available: {len(agent.tools)}")
        
        print("\nTesting Tools:")
        for tool in agent.tools:
            print(f"  • {tool.name}")
        
        print("\nCapabilities:")
        for capability in get_fastapi_test_assistant_capabilities()[:5]:
            print(f"  • {capability}")
            
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        import traceback
        traceback.print_exc()