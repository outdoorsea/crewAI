#!/usr/bin/env python3
"""
Test script to verify that hardcoded OpenAI settings don't interfere with Ollama usage.
This tests the fixes for:
1. Added Ollama models to LLM_CONTEXT_WINDOW_SIZES
2. Proper Ollama model detection and configuration
3. Removal of Ollama-incompatible parameters
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crewai.llm import LLM, LLM_CONTEXT_WINDOW_SIZES
import logging

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_ollama_context_window_sizes():
    """Test that Ollama models are included in context window sizes"""
    print("=== Testing Ollama Context Window Sizes ===")
    
    ollama_models = [
        "ollama/llama3.2",
        "ollama/llama3.1", 
        "ollama/mixtral",
        "ollama/mistral",
        "ollama/gemma2"
    ]
    
    for model in ollama_models:
        if model in LLM_CONTEXT_WINDOW_SIZES:
            context_size = LLM_CONTEXT_WINDOW_SIZES[model]
            print(f"✅ {model}: {context_size} tokens")
        else:
            print(f"❌ {model}: NOT FOUND in context window sizes")
            return False
    
    return True

def test_ollama_model_detection():
    """Test that Ollama models are properly detected"""
    print("\n=== Testing Ollama Model Detection ===")
    
    try:
        llm = LLM(model="ollama/llama3.2")
        
        if hasattr(llm, 'is_ollama') and llm.is_ollama:
            print("✅ Ollama model properly detected")
        else:
            print("❌ Ollama model not detected")
            return False
            
        # Check provider detection
        provider = llm._get_custom_llm_provider()
        if provider == "ollama":
            print(f"✅ Provider correctly identified as: {provider}")
        else:
            print(f"❌ Wrong provider identified: {provider}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating Ollama LLM: {e}")
        return False
    
    return True

def test_ollama_parameter_filtering():
    """Test that Ollama-incompatible parameters are filtered"""
    print("\n=== Testing Ollama Parameter Filtering ===")
    
    try:
        llm = LLM(
            model="ollama/llama3.2",
            reasoning_effort="high",  # Should be filtered
            logprobs=True,           # Should be filtered
            top_logprobs=5,          # Should be filtered
            logit_bias={100: 0.5}    # Should be filtered
        )
        
        # Test parameter preparation
        messages = [{"role": "user", "content": "Hello"}]
        params = llm._prepare_completion_params(messages)
        
        # Check that incompatible parameters were filtered
        filtered_params = ["reasoning_effort", "logprobs", "top_logprobs", "logit_bias"]
        for param in filtered_params:
            if param in params and params[param] is not None:
                print(f"❌ Parameter {param} should have been filtered but wasn't")
                return False
            else:
                print(f"✅ Parameter {param} properly filtered")
        
        # Check that base_url was set
        if params.get("base_url") == "http://localhost:11434":
            print("✅ base_url properly set for Ollama")
        else:
            print(f"❌ base_url not set correctly: {params.get('base_url')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing parameter filtering: {e}")
        return False
    
    return True

def test_non_ollama_model_unchanged():
    """Test that non-Ollama models aren't affected by Ollama-specific logic"""
    print("\n=== Testing Non-Ollama Models Unchanged ===")
    
    try:
        llm = LLM(
            model="gpt-4",
            reasoning_effort="high",  # Should NOT be filtered for non-Ollama
            logprobs=True,           # Should NOT be filtered for non-Ollama
        )
        
        if hasattr(llm, 'is_ollama') and not llm.is_ollama:
            print("✅ Non-Ollama model properly detected")
        else:
            print("❌ Non-Ollama model incorrectly detected as Ollama")
            return False
            
        # Test parameter preparation
        messages = [{"role": "user", "content": "Hello"}]
        params = llm._prepare_completion_params(messages)
        
        # Check that parameters were NOT filtered for non-Ollama models
        if params.get("reasoning_effort") == "high":
            print("✅ reasoning_effort preserved for non-Ollama model")
        else:
            print(f"❌ reasoning_effort incorrectly filtered: {params.get('reasoning_effort')}")
            return False
            
        if params.get("logprobs") is True:
            print("✅ logprobs preserved for non-Ollama model")
        else:
            print(f"❌ logprobs incorrectly filtered: {params.get('logprobs')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing non-Ollama model: {e}")
        return False
    
    return True

def test_context_window_retrieval():
    """Test that context window sizes are properly retrieved for Ollama models"""
    print("\n=== Testing Context Window Retrieval ===")
    
    try:
        llm = LLM(model="ollama/llama3.2")
        context_size = llm.get_context_window_size()
        
        expected_size = int(131072 * 0.75)  # 75% of max context
        if context_size == expected_size:
            print(f"✅ Context window size correctly calculated: {context_size}")
        else:
            print(f"❌ Wrong context window size: {context_size}, expected: {expected_size}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing context window retrieval: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Testing Ollama Hardcoded Settings Fixes")
    print("=" * 50)
    
    tests = [
        test_ollama_context_window_sizes,
        test_ollama_model_detection,
        test_ollama_parameter_filtering,
        test_non_ollama_model_unchanged,
        test_context_window_retrieval
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Ollama hardcoded settings fixes are working correctly.")
        print("\nKey fixes applied:")
        print("✅ Added Ollama models to LLM_CONTEXT_WINDOW_SIZES")
        print("✅ Added Ollama model detection (_is_ollama_model)")
        print("✅ Added Ollama-specific parameter filtering")
        print("✅ Ensured proper base_url configuration for Ollama")
        print("✅ Preserved non-Ollama model functionality")
        return 0
    else:
        print("❌ Some tests failed. Please check the Ollama configuration logic.")
        return 1

if __name__ == "__main__":
    sys.exit(main())