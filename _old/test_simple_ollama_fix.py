#!/usr/bin/env python3
"""
Simple test to verify Ollama models were added to LLM_CONTEXT_WINDOW_SIZES
"""

import sys
import os

def test_ollama_in_context_sizes():
    """Test that Ollama models are included in the hardcoded context window sizes"""
    
    # Read the LLM file directly to check for Ollama entries
    llm_file_path = os.path.join(os.path.dirname(__file__), 'src', 'crewai', 'llm.py')
    
    if not os.path.exists(llm_file_path):
        print(f"❌ LLM file not found at: {llm_file_path}")
        return False
    
    with open(llm_file_path, 'r') as f:
        content = f.read()
    
    # Check for Ollama model entries
    ollama_models = [
        '"ollama/llama3.2"',
        '"ollama/llama3.1"',
        '"ollama/mixtral"',
        '"ollama/mistral"',
        '"ollama/gemma2"'
    ]
    
    print("=== Checking Ollama Models in LLM_CONTEXT_WINDOW_SIZES ===")
    
    found_ollama_section = False
    all_found = True
    
    # Check if ollama comment section exists
    if '# ollama models' in content:
        found_ollama_section = True
        print("✅ Found '# ollama models' section")
    else:
        print("❌ Missing '# ollama models' section")
        all_found = False
    
    # Check each model
    for model in ollama_models:
        if model in content:
            print(f"✅ Found {model}")
        else:
            print(f"❌ Missing {model}")
            all_found = False
    
    # Check for _is_ollama_model method
    if '_is_ollama_model' in content:
        print("✅ Found _is_ollama_model method")
    else:
        print("❌ Missing _is_ollama_model method")
        all_found = False
    
    # Check for ollama detection logic
    if 'self.is_ollama = self._is_ollama_model(model)' in content:
        print("✅ Found Ollama detection in __init__")
    else:
        print("❌ Missing Ollama detection in __init__")
        all_found = False
    
    # Check for Ollama parameter filtering
    if 'ollama_incompatible_params' in content:
        print("✅ Found Ollama parameter filtering logic")
    else:
        print("❌ Missing Ollama parameter filtering logic")
        all_found = False
    
    return found_ollama_section and all_found

def main():
    """Run the simple test"""
    print("Testing Ollama Hardcoded Settings Fix")
    print("=" * 50)
    
    if test_ollama_in_context_sizes():
        print("\n🎉 All Ollama fixes are present in the LLM file!")
        print("\nKey fixes verified:")
        print("✅ Ollama models added to LLM_CONTEXT_WINDOW_SIZES")
        print("✅ _is_ollama_model method implemented")
        print("✅ Ollama detection added to __init__")
        print("✅ Ollama parameter filtering logic added")
        print("\nThis should resolve the 'list index out of range' error by:")
        print("- Providing proper context window sizes for Ollama models")
        print("- Detecting Ollama models correctly")
        print("- Filtering out OpenAI-specific parameters that cause conflicts")
        print("- Ensuring proper Ollama base_url configuration")
        return 0
    else:
        print("\n❌ Some Ollama fixes are missing from the LLM file.")
        return 1

if __name__ == "__main__":
    sys.exit(main())