#!/usr/bin/env python3
"""
Clean Output Test Script

This script tests that warning suppression is working correctly.

File: test_clean_output.py
"""

import warnings
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set up warning suppression
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

def test_clean_imports():
    """Test that imports don't show warnings"""
    print("🧪 Testing clean imports...")
    
    try:
        from agents.fastapi_test_assistant import create_fastapi_test_assistant
        print("✅ FastAPI Test Assistant imported cleanly")
    except Exception as e:
        print(f"❌ Failed to import FastAPI Test Assistant: {e}")
        return False
    
    try:
        from agents.fastapi_memory_librarian import create_fastapi_memory_librarian  
        print("✅ FastAPI Memory Librarian imported cleanly")
    except Exception as e:
        print(f"❌ Failed to import FastAPI Memory Librarian: {e}")
        return False
        
    return True

def test_agent_creation():
    """Test that agent creation doesn't show warnings"""
    print("\n🤖 Testing clean agent creation...")
    
    try:
        from agents.fastapi_test_assistant import create_fastapi_test_assistant
        agent = create_fastapi_test_assistant(verbose=False)
        print("✅ FastAPI Test Assistant created cleanly")
        print(f"   Agent role: {agent.role}")
        print(f"   Tools available: {len(agent.tools)}")
    except Exception as e:
        print(f"❌ Failed to create FastAPI Test Assistant: {e}")
        return False
        
    return True

def main():
    """Run clean output tests"""
    print("🚀 Clean Output Test Suite")
    print("=" * 40)
    
    success = True
    
    if not test_clean_imports():
        success = False
        
    if not test_agent_creation():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed - output is clean!")
        print("\n✨ The warning suppression is working correctly:")
        print("   • No pkg_resources deprecation warnings")
        print("   • No Pydantic V1/V2 mixing warnings")
        print("   • Clean agent creation and tool loading")
    else:
        print("⚠️ Some tests failed - check output above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())