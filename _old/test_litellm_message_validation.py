#!/usr/bin/env python3
"""
Test script to verify LiteLLM message validation fixes.
This tests the additional validation we added to prevent the 
"list index out of range" error in LiteLLM's prompt template processing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crewai.llm import LLM
import logging

# Set up logging to see error messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_empty_messages_validation():
    """Test that empty messages array is properly validated"""
    print("=== Testing Empty Messages Array Validation ===")
    
    try:
        llm = LLM(model="ollama/llama3.2:latest")
        
        # Test 1: Empty list
        try:
            result = llm.call(messages=[])
            print("❌ FAILED: Empty list should have raised ValueError")
            return False
        except ValueError as e:
            if "Messages array cannot be empty" in str(e):
                print("✅ PASSED: Empty list properly rejected")
            else:
                print(f"❌ FAILED: Wrong error for empty list: {e}")
                return False
        except Exception as e:
            print(f"❌ FAILED: Unexpected error for empty list: {e}")
            return False
        
        # Test 2: None messages (this should be caught in _format_messages_for_provider)
        try:
            result = llm._format_messages_for_provider(None)
            print("❌ FAILED: None messages should have raised TypeError")
            return False
        except TypeError as e:
            if "Messages cannot be None" in str(e):
                print("✅ PASSED: None messages properly rejected")
            else:
                print(f"❌ FAILED: Wrong error for None messages: {e}")
                return False
        except Exception as e:
            print(f"❌ FAILED: Unexpected error for None messages: {e}")
            return False
            
        # Test 3: Empty array in _format_messages_for_provider
        try:
            result = llm._format_messages_for_provider([])
            print("❌ FAILED: Empty array should have raised ValueError")
            return False
        except ValueError as e:
            if "Messages array cannot be empty" in str(e):
                print("✅ PASSED: Empty array properly rejected in _format_messages_for_provider")
            else:
                print(f"❌ FAILED: Wrong error for empty array: {e}")
                return False
        except Exception as e:
            print(f"❌ FAILED: Unexpected error for empty array: {e}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error creating LLM instance: {e}")
        return False
    
    return True

def test_invalid_message_format():
    """Test that invalid message formats are properly validated"""
    print("\n=== Testing Invalid Message Format Validation ===")
    
    try:
        llm = LLM(model="ollama/llama3.2:latest")
        
        # Test 1: Non-dict message
        try:
            result = llm._format_messages_for_provider(["not a dict"])
            print("❌ FAILED: Non-dict message should have raised TypeError")
            return False
        except TypeError as e:
            if "Invalid message format at index 0" in str(e):
                print("✅ PASSED: Non-dict message properly rejected")
            else:
                print(f"❌ FAILED: Wrong error for non-dict message: {e}")
                return False
        except Exception as e:
            print(f"❌ FAILED: Unexpected error for non-dict message: {e}")
            return False
        
        # Test 2: Missing role key
        try:
            result = llm._format_messages_for_provider([{"content": "hello"}])
            print("❌ FAILED: Missing role key should have raised TypeError")
            return False
        except TypeError as e:
            if "Invalid message format at index 0" in str(e):
                print("✅ PASSED: Missing role key properly rejected")
            else:
                print(f"❌ FAILED: Wrong error for missing role: {e}")
                return False
        except Exception as e:
            print(f"❌ FAILED: Unexpected error for missing role: {e}")
            return False
            
        # Test 3: Missing content key
        try:
            result = llm._format_messages_for_provider([{"role": "user"}])
            print("❌ FAILED: Missing content key should have raised TypeError")
            return False
        except TypeError as e:
            if "Invalid message format at index 0" in str(e):
                print("✅ PASSED: Missing content key properly rejected")
            else:
                print(f"❌ FAILED: Wrong error for missing content: {e}")
                return False
        except Exception as e:
            print(f"❌ FAILED: Unexpected error for missing content: {e}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error creating LLM instance: {e}")
        return False
    
    return True

def test_valid_messages():
    """Test that valid messages are processed correctly"""
    print("\n=== Testing Valid Messages Processing ===")
    
    try:
        llm = LLM(model="ollama/llama3.2:latest")
        
        # Test valid message format
        valid_messages = [{"role": "user", "content": "Hello, world!"}]
        
        try:
            result = llm._format_messages_for_provider(valid_messages)
            print("✅ PASSED: Valid messages processed successfully")
            print(f"   Formatted messages: {result}")
            return True
        except Exception as e:
            print(f"❌ FAILED: Valid messages should not raise error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error creating LLM instance: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing LiteLLM Message Validation Fixes")
    print("=" * 50)
    
    tests = [
        test_empty_messages_validation,
        test_invalid_message_format,
        test_valid_messages
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The message validation fixes are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the validation logic.")
        return 1

if __name__ == "__main__":
    sys.exit(main())