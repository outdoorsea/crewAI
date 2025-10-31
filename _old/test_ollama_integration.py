#!/usr/bin/env python3
"""
Test Ollama Integration with CrewAI

This script tests the Ollama configuration changes to ensure CrewAI
can work with Ollama instead of OpenAI.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_constants_configuration():
    """Test that constants are configured for Ollama."""
    print("🔧 Testing constants configuration...")
    
    from crewai.cli.constants import DEFAULT_LLM_MODEL, PROVIDERS, MODELS
    
    # Check default model
    assert DEFAULT_LLM_MODEL == "ollama/llama3.2", f"Expected ollama/llama3.2, got {DEFAULT_LLM_MODEL}"
    print(f"✅ Default model: {DEFAULT_LLM_MODEL}")
    
    # Check Ollama is first provider
    assert PROVIDERS[0] == "ollama", f"Expected ollama first, got {PROVIDERS[0]}"
    print(f"✅ Primary provider: {PROVIDERS[0]}")
    
    # Check Ollama models are available
    ollama_models = MODELS.get("ollama", [])
    assert len(ollama_models) > 2, f"Expected multiple Ollama models, got {len(ollama_models)}"
    print(f"✅ Ollama models available: {len(ollama_models)}")
    
    return True

def test_embedding_configuration():
    """Test that embedding functions default to Ollama."""
    print("\n🔧 Testing embedding configuration...")
    
    from crewai.utilities.embedding_configurator import EmbeddingConfigurator
    
    configurator = EmbeddingConfigurator()
    
    # Check Ollama is first in embedding functions
    embedding_providers = list(configurator.embedding_functions.keys())
    assert embedding_providers[0] == "ollama", f"Expected ollama first, got {embedding_providers[0]}"
    print(f"✅ Primary embedding provider: {embedding_providers[0]}")
    
    # Test default embedding function
    try:
        default_embedding = configurator._create_default_embedding_function()
        print(f"✅ Default embedding function created successfully")
        return True
    except Exception as e:
        print(f"⚠️  Default embedding function creation failed: {e}")
        return False

def test_custom_config():
    """Test custom LLM configuration."""
    print("\n🔧 Testing custom LLM configuration...")
    
    try:
        from config.llm_config import get_llm_config
        
        config = get_llm_config()
        info = config.get_model_info()
        
        # Check default model
        assert info['default_model'] == "llama3.2", f"Expected llama3.2, got {info['default_model']}"
        print(f"✅ Default model: {info['default_model']}")
        
        # Check Ollama URL
        assert "localhost:11434" in info['ollama_base_url'], f"Expected localhost:11434 in URL"
        print(f"✅ Ollama URL: {info['ollama_base_url']}")
        
        # Check models
        assert len(info['available_models']) >= 5, f"Expected at least 5 models"
        print(f"✅ Available models: {len(info['available_models'])}")
        
        return True
    except Exception as e:
        print(f"⚠️  Custom config test failed: {e}")
        return False

def test_basic_crew_creation():
    """Test basic CrewAI functionality with Ollama."""
    print("\n🔧 Testing basic CrewAI functionality...")
    
    try:
        from crewai import Agent, Task, Crew
        
        # Create a simple agent with Ollama
        agent = Agent(
            role="Test Agent",
            goal="Test Ollama integration",
            backstory="A simple test agent",
            llm="ollama/llama3.2",
            verbose=True
        )
        
        # Create a simple task
        task = Task(
            description="Say hello and confirm you're working with Ollama",
            expected_output="A greeting confirming Ollama integration",
            agent=agent
        )
        
        # Create crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        print("✅ CrewAI objects created successfully with Ollama configuration")
        print("⚠️  Note: Actual execution requires Ollama server to be running")
        
        return True
        
    except Exception as e:
        print(f"⚠️  CrewAI creation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Ollama Integration with CrewAI")
    print("=" * 50)
    
    tests = [
        test_constants_configuration,
        test_embedding_configuration, 
        test_custom_config,
        test_basic_crew_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ollama integration is configured correctly.")
        print("\n📝 Next steps:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Pull required models: ollama pull llama3.2")
        print("3. Pull embedding model: ollama pull nomic-embed-text")
        print("4. Test with a real CrewAI execution")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())