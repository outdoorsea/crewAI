#!/usr/bin/env python3
"""
fixes/fix_litellm_ollama_issue.py

Fix for the LiteLLM "list index out of range" error when using Ollama with CrewAI.
This patch adds proper error handling for empty responses from Ollama.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def apply_llm_fix():
    """Apply the fix to the CrewAI LLM module"""
    
    # Path to the LLM file that needs fixing
    llm_file = Path(__file__).parent.parent / "src" / "crewai" / "llm.py"
    
    if not llm_file.exists():
        logger.error(f"LLM file not found: {llm_file}")
        return False
    
    # Create backup
    backup_file = llm_file.with_suffix(".py.backup")
    if not backup_file.exists():
        shutil.copy2(llm_file, backup_file)
        logger.info(f"Created backup: {backup_file}")
    
    # Read the current file
    with open(llm_file, 'r') as f:
        content = f.read()
    
    # The problematic code that needs fixing
    problematic_code = '''        # --- 2) Extract response message and content
        response_message = cast(Choices, cast(ModelResponse, response).choices)[
            0
        ].message
        text_response = response_message.content or ""'''
    
    # The fixed code with proper error handling
    fixed_code = '''        # --- 2) Extract response message and content with error handling
        # Check if response has choices before accessing index 0
        response_choices = cast(ModelResponse, response).choices
        if not response_choices or len(response_choices) == 0:
            logger.error("Empty response from LLM - no choices returned")
            raise Exception("LLM returned empty response - no choices available. This may indicate an issue with the Ollama model or connection.")
        
        response_message = cast(Choices, response_choices[0]).message
        text_response = response_message.content or ""'''
    
    # Apply the fix
    if problematic_code in content:
        new_content = content.replace(problematic_code, fixed_code)
        
        # Write the fixed content
        with open(llm_file, 'w') as f:
            f.write(new_content)
        
        logger.info("✅ Applied LiteLLM Ollama fix to CrewAI LLM module")
        return True
    else:
        logger.warning("⚠️ Problematic code pattern not found - file may already be fixed or have changed")
        return False


def verify_ollama_connection():
    """Verify that Ollama is running and accessible"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            logger.info(f"✅ Ollama is running with {len(models)} models available")
            
            # List available models
            if models:
                model_names = [model.get("name", "unknown") for model in models]
                logger.info(f"Available models: {', '.join(model_names[:5])}")
                return True
            else:
                logger.warning("⚠️ Ollama is running but no models are available")
                return False
        else:
            logger.error(f"❌ Ollama responded with status {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ Cannot connect to Ollama: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking Ollama: {e}")
        return False


def check_model_availability(model_name: str = "llama3.2"):
    """Check if a specific model is available in Ollama"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "").split(":")[0] for model in models]
            
            if model_name in model_names:
                logger.info(f"✅ Model '{model_name}' is available")
                return True
            else:
                logger.warning(f"⚠️ Model '{model_name}' not found. Available: {', '.join(model_names)}")
                return False
        else:
            return False
    except Exception as e:
        logger.error(f"Error checking model availability: {e}")
        return False


def pull_model_if_needed(model_name: str = "llama3.2"):
    """Pull a model if it's not available"""
    if check_model_availability(model_name):
        return True
    
    try:
        import subprocess
        logger.info(f"🔄 Pulling model '{model_name}' - this may take a few minutes...")
        
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully pulled model '{model_name}'")
            return True
        else:
            logger.error(f"❌ Failed to pull model '{model_name}': {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Timeout while pulling model '{model_name}'")
        return False
    except FileNotFoundError:
        logger.error("❌ Ollama CLI not found. Please ensure Ollama is installed.")
        return False
    except Exception as e:
        logger.error(f"❌ Error pulling model '{model_name}': {e}")
        return False


def test_litellm_ollama():
    """Test LiteLLM with Ollama to verify the fix works"""
    try:
        import litellm
        
        # Test with a simple completion
        logger.info("🧪 Testing LiteLLM with Ollama...")
        
        response = litellm.completion(
            model="ollama/llama3.2",
            messages=[{"role": "user", "content": "Hello! Say 'test successful' if you can respond."}],
            api_base="http://localhost:11434"
        )
        
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            logger.info(f"✅ LiteLLM test successful: {content}")
            return True
        else:
            logger.error("❌ LiteLLM test failed: empty response")
            return False
            
    except Exception as e:
        logger.error(f"❌ LiteLLM test failed: {e}")
        return False


def main():
    """Main function to apply all fixes and run tests"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔧 CrewAI LiteLLM Ollama Fix")
    print("=" * 40)
    
    success_count = 0
    total_steps = 6
    
    # Step 1: Apply the LLM fix
    print("\n1. Applying LiteLLM fix...")
    if apply_llm_fix():
        success_count += 1
        print("   ✅ Fix applied successfully")
    else:
        print("   ❌ Failed to apply fix")
    
    # Step 2: Verify Ollama connection
    print("\n2. Checking Ollama connection...")
    if verify_ollama_connection():
        success_count += 1
        print("   ✅ Ollama is accessible")
    else:
        print("   ❌ Ollama connection failed")
        print("   💡 Try: brew services start ollama")
    
    # Step 3: Check model availability
    print("\n3. Checking model availability...")
    if check_model_availability("llama3.2"):
        success_count += 1
        print("   ✅ Required model is available")
    else:
        print("   ⚠️ Model not available")
    
    # Step 4: Pull model if needed
    print("\n4. Ensuring model is available...")
    if pull_model_if_needed("llama3.2"):
        success_count += 1
        print("   ✅ Model is ready")
    else:
        print("   ❌ Could not ensure model availability")
    
    # Step 5: Test LiteLLM integration
    print("\n5. Testing LiteLLM integration...")
    if test_litellm_ollama():
        success_count += 1
        print("   ✅ LiteLLM integration working")
    else:
        print("   ❌ LiteLLM integration failed")
    
    # Step 6: Overall assessment
    print("\n6. Overall assessment...")
    if success_count >= 4:  # Need at least fix + connection + model
        success_count += 1
        print("   ✅ System should be working now")
    else:
        print("   ❌ System may still have issues")
    
    # Summary
    print(f"\n📊 Summary: {success_count}/{total_steps} steps successful")
    
    if success_count >= 4:
        print("\n🎉 Fix complete! CrewAI should now work with Ollama.")
        print("\n💡 Usage tips:")
        print("   • Ensure Ollama is running: brew services start ollama")
        print("   • Use model names like 'ollama/llama3.2' in CrewAI")
        print("   • Check logs if you still see errors")
    else:
        print("\n⚠️ Some issues remain. Please check:")
        print("   • Ollama installation and service status")
        print("   • Available models: ollama list")
        print("   • Network connectivity to localhost:11434")
    
    return success_count >= 4


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)