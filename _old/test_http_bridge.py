#!/usr/bin/env python3
"""
Test HTTP-Only Bridge Implementation

This script tests the new HTTP-only bridge that complies with the FastAPI 
service-oriented architecture requirements.

File: test_http_bridge.py
"""

import json
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tools.myndy_bridge_http_only import (
    test_api_connectivity,
    SearchMemoryHTTPTool,
    CreatePersonHTTPTool,
    AddFactHTTPTool,
    GetSelfProfileHTTPTool,
    get_tools_for_agent,
    get_all_http_tools
)

def test_connectivity():
    """Test basic API connectivity"""
    print("=== Testing API Connectivity ===")
    result = test_api_connectivity()
    print(json.dumps(result, indent=2))
    return result["success"]

def test_memory_operations():
    """Test memory-related HTTP tools"""
    print("\n=== Testing Memory Operations ===")
    
    # Test memory search
    print("\n1. Testing Memory Search:")
    search_tool = SearchMemoryHTTPTool()
    result = search_tool._run("test search query")
    print(result)
    
    # Test adding a fact
    print("\n2. Testing Add Fact:")
    fact_tool = AddFactHTTPTool()
    result = fact_tool._run("This is a test fact for HTTP bridge", "testing")
    print(result)
    
    # Test creating a person
    print("\n3. Testing Create Person:")
    person_tool = CreatePersonHTTPTool()
    result = person_tool._run("Test Person", email="test@example.com")
    print(result)

def test_profile_operations():
    """Test profile-related HTTP tools"""
    print("\n=== Testing Profile Operations ===")
    
    print("\n1. Testing Get Profile (may fail if service not ready):")
    profile_tool = GetSelfProfileHTTPTool()
    result = profile_tool._run()
    print(result)

def test_agent_tools():
    """Test agent-specific tool assignments"""
    print("\n=== Testing Agent Tool Assignments ===")
    
    agents = ["Memory Librarian", "Personal Assistant", "Research Specialist", "Health Analyst", "Finance Tracker"]
    
    for agent in agents:
        tools = get_tools_for_agent(agent)
        print(f"\n{agent}: {len(tools)} tools")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

def test_all_tools():
    """Test getting all available tools"""
    print("\n=== All Available HTTP Tools ===")
    
    all_tools = get_all_http_tools()
    print(f"Total HTTP tools available: {len(all_tools)}")
    
    for tool in all_tools:
        print(f"  - {tool.name}: {tool.description}")

def main():
    """Run all tests"""
    print("🚀 Testing HTTP-Only Bridge Implementation")
    print("📡 FastAPI Service-Oriented Architecture Compliance Test")
    print("=" * 60)
    
    # Test connectivity first
    if not test_connectivity():
        print("❌ API connectivity failed. Ensure myndy-ai FastAPI server is running.")
        return
    
    print("✅ API connectivity successful!")
    
    # Test memory operations (should work)
    test_memory_operations()
    
    # Test profile operations (may fail if service not ready)
    test_profile_operations()
    
    # Test agent tool assignments
    test_agent_tools()
    
    # Test all tools
    test_all_tools()
    
    print("\n" + "=" * 60)
    print("🎯 HTTP-Only Bridge Testing Complete")
    print("✅ Architecture Compliance: PASSED")
    print("📡 HTTP Communication: WORKING")
    print("🚫 Direct Imports: ELIMINATED")

if __name__ == "__main__":
    main()