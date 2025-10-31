#!/usr/bin/env python3
"""
Test script for FastAPI HTTP client tools

This script tests the HTTP client tools to ensure they can communicate
with the myndy-ai FastAPI service.

File: test_fastapi_client.py
"""

import json
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_fastapi_client_imports():
    """Test that all FastAPI client tools can be imported"""
    try:
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
        print("✅ All FastAPI client tools imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import FastAPI client tools: {e}")
        return False


def test_tool_functions():
    """Test that tool functions can be called (without running server)"""
    try:
        from tools.myndy_fastapi_client import (
            search_memory,
            create_person,
            get_memory_tools_help
        )
        
        print("🔧 Testing tool function signatures...")
        
        # Test that functions can be called (they will fail since server isn't running)
        # But this tests the function signatures and basic error handling
        
        # Test search_memory
        result = search_memory("test query")
        result_data = json.loads(result)
        assert "success" in result_data
        assert result_data["success"] == False  # Expected since server isn't running
        print("✅ search_memory function signature works")
        
        # Test create_person  
        result = create_person("Test Person", email="test@example.com")
        result_data = json.loads(result)
        assert "success" in result_data
        assert result_data["success"] == False  # Expected since server isn't running
        print("✅ create_person function signature works")
        
        # Test help function
        result = get_memory_tools_help()
        result_data = json.loads(result)
        assert "success" in result_data
        assert result_data["success"] == False  # Expected since server isn't running
        print("✅ get_memory_tools_help function signature works")
        
        print("✅ All tool function signatures are working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Tool function test failed: {e}")
        return False


def test_config():
    """Test FastAPI configuration"""
    try:
        from tools.myndy_fastapi_client import FastAPIConfig
        
        # Test default config
        config = FastAPIConfig()
        assert config.base_url == "http://localhost:8000"
        assert config.api_version == "api/v1"
        assert config.full_base_url == "http://localhost:8000/api/v1"
        print("✅ Default FastAPI configuration works")
        
        # Test custom config
        config = FastAPIConfig(
            base_url="http://example.com:8080",
            api_version="v2",
            api_key="test-key"
        )
        assert config.base_url == "http://example.com:8080"
        assert config.api_version == "v2"
        assert config.api_key == "test-key"
        assert config.full_base_url == "http://example.com:8080/v2"
        print("✅ Custom FastAPI configuration works")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Testing FastAPI HTTP Client Tools")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_fastapi_client_imports),
        ("Configuration Tests", test_config),
        ("Function Signature Tests", test_tool_functions)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All FastAPI client tests passed!")
        print("\n📝 Next Steps:")
        print("1. Start the FastAPI server: python start_api_server.py")
        print("2. Test actual API calls with the server running")
        print("3. Integrate tools with CrewAI agents")
    else:
        print(f"\n⚠️ {failed} tests failed. Please fix the issues before proceeding.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())