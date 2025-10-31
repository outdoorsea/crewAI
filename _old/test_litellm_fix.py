#!/usr/bin/env python3
"""
Test script to verify the LiteLLM fix is working with Ollama
"""

import sys
import os
import logging
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_crewai_llm():
    """Test CrewAI LLM with Ollama"""
    try:
        # Import CrewAI LLM
        from src.crewai.llm import LLM
        
        # Create LLM instance with Ollama model
        llm = LLM(
            model="ollama/llama3.2",
            base_url="http://localhost:11434"
        )
        
        # Test with a simple message
        logger.info("Testing CrewAI LLM with Ollama...")
        response = llm.call("Hello! Please respond with 'Test successful' if you can hear me.")
        
        logger.info(f"✅ CrewAI LLM test successful!")
        logger.info(f"Response: {response}")
        return True
        
    except Exception as e:
        logger.error(f"❌ CrewAI LLM test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_litellm_direct():
    """Test LiteLLM directly with Ollama"""
    try:
        import litellm
        
        logger.info("Testing LiteLLM directly with Ollama...")
        response = litellm.completion(
            model="ollama/llama3.2",
            messages=[{"role": "user", "content": "Say hello"}],
            api_base="http://localhost:11434"
        )
        
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            logger.info(f"✅ LiteLLM direct test successful!")
            logger.info(f"Response: {content}")
            return True
        else:
            logger.error("❌ LiteLLM returned empty response")
            return False
            
    except Exception as e:
        logger.error(f"❌ LiteLLM direct test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all tests"""
    print("🔧 Testing LiteLLM Ollama Fix")
    print("=" * 40)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: LiteLLM direct
    print("\n1. Testing LiteLLM directly...")
    if test_litellm_direct():
        success_count += 1
        print("   ✅ LiteLLM direct test passed")
    else:
        print("   ❌ LiteLLM direct test failed")
    
    # Test 2: CrewAI LLM
    print("\n2. Testing CrewAI LLM...")
    if test_crewai_llm():
        success_count += 1
        print("   ✅ CrewAI LLM test passed")
    else:
        print("   ❌ CrewAI LLM test failed")
    
    # Summary
    print(f"\n📊 Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("\n🎉 All tests passed! The fix is working correctly.")
        return True
    else:
        print("\n⚠️ Some tests failed. The issue may not be fully resolved.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)