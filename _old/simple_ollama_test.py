#!/usr/bin/env python3
"""
Simple Ollama Configuration Test

This script tests just the basic configuration changes without 
running full CrewAI functionality.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_constants():
    """Test constants configuration."""
    print("🔧 Testing constants configuration...")
    
    try:
        from crewai.cli.constants import DEFAULT_LLM_MODEL, PROVIDERS, MODELS
        
        print(f"✅ Default model: {DEFAULT_LLM_MODEL}")
        print(f"✅ Primary provider: {PROVIDERS[0]}")
        print(f"✅ Ollama models: {len(MODELS.get('ollama', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Constants test failed: {e}")
        return False

def test_custom_config():
    """Test custom config."""
    print("\n🔧 Testing custom config...")
    
    try:
        from config.llm_config import LLMConfig
        
        config = LLMConfig()
        info = config.get_model_info()
        
        print(f"✅ Default model: {info['default_model']}")
        print(f"✅ Ollama URL: {info['ollama_base_url']}")
        print(f"✅ Available models: {len(info['available_models'])}")
        
        return True
    except Exception as e:
        print(f"❌ Custom config test failed: {e}")
        return False

def main():
    """Run simple tests."""
    print("🚀 Simple Ollama Configuration Test")
    print("=" * 40)
    
    tests = [test_constants, test_custom_config]
    passed = sum(test() for test in tests)
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Configuration looks good!")
        print("\n📝 To complete setup:")
        print("1. Install Ollama: brew install ollama")
        print("2. Start Ollama: ollama serve")
        print("3. Pull models: ollama pull llama3.2")
        print("4. Pull embedding model: ollama pull nomic-embed-text")
    
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    exit(main())