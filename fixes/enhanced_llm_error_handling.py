#!/usr/bin/env python3
"""
fixes/enhanced_llm_error_handling.py

Enhanced error handling for CrewAI LLM module to prevent index out of range errors
and provide better debugging information for Ollama integration issues.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def create_enhanced_llm_method():
    """Create the enhanced _handle_non_streaming_response method"""
    
    return '''    def _handle_non_streaming_response(
        self,
        params: Dict[str, Any],
        callbacks: Optional[List[Any]] = None,
        available_functions: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Handle a non-streaming response from the LLM with enhanced error handling.

        Args:
            params: Parameters for the completion call
            callbacks: Optional list of callback functions
            available_functions: Dict of available functions

        Returns:
            str: The response text
        """
        # --- 1) Make the completion call with enhanced error handling
        try:
            # Log the request for debugging
            logger.debug(f"Making LLM completion call with model: {params.get('model', 'unknown')}")
            logger.debug(f"Message count: {len(params.get('messages', []))}")
            
            # Attempt to make the completion call
            response = litellm.completion(**params)
            
            # Validate response structure immediately
            if not response:
                raise Exception("LLM returned None response")
            
            logger.debug(f"LLM response received: {type(response)}")
            
        except ContextWindowExceededError as e:
            # Convert litellm's context window error to our own exception type
            logger.error(f"Context window exceeded: {e}")
            raise LLMContextLengthExceededException(str(e))
        except Exception as e:
            # Enhanced error logging for Ollama issues
            error_msg = str(e)
            logger.error(f"LLM completion call failed: {error_msg}")
            
            # Provide specific guidance for common Ollama issues
            if "list index out of range" in error_msg:
                logger.error("This appears to be an Ollama empty response issue")
                logger.error("Possible causes:")
                logger.error("  1. Ollama service not running")
                logger.error("  2. Model not available or not loaded")
                logger.error("  3. Malformed request to Ollama API")
                logger.error("  4. Network connectivity issues")
                logger.error("Solutions:")
                logger.error("  • Check Ollama status: ollama list")
                logger.error("  • Restart Ollama: brew services restart ollama")
                logger.error("  • Pull required model: ollama pull llama3.2")
            
            raise

        # --- 2) Extract response message and content with comprehensive validation
        try:
            # Validate response structure
            response_model = cast(ModelResponse, response)
            if not hasattr(response_model, 'choices'):
                logger.error("Response missing 'choices' attribute")
                raise Exception("Invalid response format: missing 'choices' attribute")
            
            response_choices = response_model.choices
            
            # Check if choices exist and are not empty
            if not response_choices:
                logger.error("Response choices is None or empty")
                logger.error(f"Full response: {response}")
                raise Exception("LLM returned empty response - no choices available. This indicates an issue with the Ollama model or connection.")
            
            if len(response_choices) == 0:
                logger.error("Response choices array is empty")
                logger.error(f"Response type: {type(response_choices)}")
                logger.error(f"Full response: {response}")
                raise Exception("LLM returned empty choices array. This may indicate an Ollama model issue or malformed request.")
            
            # Extract first choice safely
            first_choice = response_choices[0]
            if not first_choice:
                logger.error("First choice is None")
                raise Exception("LLM returned None as first choice")
            
            # Extract message safely
            response_message = cast(Choices, first_choice).message
            if not response_message:
                logger.error("Response message is None")
                raise Exception("LLM returned None message")
            
            # Extract content safely
            text_response = response_message.content or ""
            
            # Log successful extraction
            logger.debug(f"Successfully extracted response: {len(text_response)} characters")
            
        except Exception as e:
            logger.error(f"Error extracting response content: {e}")
            logger.error(f"Response structure: {type(response)}")
            if hasattr(response, '__dict__'):
                logger.error(f"Response attributes: {list(response.__dict__.keys())}")
            raise

        # --- 3) Handle callbacks with usage info
        if callbacks and len(callbacks) > 0:
            for callback in callbacks:
                if hasattr(callback, "log_success_event"):
                    usage_info = getattr(response, "usage", None)
                    if usage_info:
                        callback.log_success_event(
                            kwargs=params,
                            response_obj={"usage": usage_info},
                            start_time=0,
                            end_time=0,
                        )

        # --- 4) Check for tool calls
        tool_calls = getattr(response_message, "tool_calls", [])

        # --- 5) If no tool calls or no available functions, return the text response directly
        if not tool_calls or not available_functions:
            self._handle_emit_call_events(text_response, LLMCallType.LLM_CALL)
            return text_response

        # --- 6) Handle tool calls if present
        tool_result = self._handle_tool_call(tool_calls, available_functions)
        if tool_result is not None:
            return tool_result

        # --- 7) If tool call handling didn't return a result, emit completion event and return text response
        self._handle_emit_call_events(text_response, LLMCallType.LLM_CALL)
        return text_response'''


def apply_enhanced_error_handling():
    """Apply enhanced error handling to the CrewAI LLM module"""
    
    # Path to the LLM file
    llm_file = Path(__file__).parent.parent / "src" / "crewai" / "llm.py"
    
    if not llm_file.exists():
        logger.error(f"LLM file not found: {llm_file}")
        return False
    
    # Create backup
    backup_file = llm_file.with_suffix(".py.enhanced_backup")
    if not backup_file.exists():
        shutil.copy2(llm_file, backup_file)
        logger.info(f"Created enhanced backup: {backup_file}")
    
    # Read the current file
    with open(llm_file, 'r') as f:
        content = f.read()
    
    # Find the method to replace
    method_start = content.find("def _handle_non_streaming_response(")
    if method_start == -1:
        logger.error("Could not find _handle_non_streaming_response method")
        return False
    
    # Find the end of the method (next method definition or class end)
    next_method_start = content.find("\n    def ", method_start + 1)
    if next_method_start == -1:
        # Look for class end or end of file
        next_method_start = len(content)
    
    # Extract the method
    original_method = content[method_start:next_method_start]
    
    # Create the enhanced method
    enhanced_method = create_enhanced_llm_method()
    
    # Replace the method
    new_content = content[:method_start] + enhanced_method + content[next_method_start:]
    
    # Add necessary imports if not present
    if "import logging" not in new_content:
        import_section = new_content.find("from typing import")
        if import_section != -1:
            new_content = new_content[:import_section] + "import logging\n" + new_content[import_section:]
    
    # Add logger if not present
    if "logger = logging.getLogger(__name__)" not in new_content:
        class_def = new_content.find("class LLM:")
        if class_def != -1:
            new_content = new_content[:class_def] + "logger = logging.getLogger(__name__)\n\n" + new_content[class_def:]
    
    # Write the enhanced content
    with open(llm_file, 'w') as f:
        f.write(new_content)
    
    logger.info("✅ Applied enhanced error handling to CrewAI LLM module")
    return True


def create_ollama_diagnostics():
    """Create a diagnostic script for Ollama issues"""
    
    diagnostics_script = '''#!/usr/bin/env python3
"""
Ollama Diagnostics Script for CrewAI Integration
"""

import requests
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            logger.info(f"✅ Ollama is running with {len(models)} models")
            for model in models[:3]:  # Show first 3 models
                logger.info(f"   📦 {model.get('name', 'unknown')}")
            return True
        else:
            logger.error(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Cannot connect to Ollama: {e}")
        return False

def test_ollama_completion():
    """Test a simple completion with Ollama"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": "Hello",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Ollama completion test successful")
            logger.info(f"   Response: {data.get('response', 'No response')[:100]}...")
            return True
        else:
            logger.error(f"❌ Ollama completion failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Ollama completion test failed: {e}")
        return False

def test_litellm_integration():
    """Test LiteLLM with Ollama"""
    try:
        import litellm
        
        response = litellm.completion(
            model="ollama/llama3.2",
            messages=[{"role": "user", "content": "Say hello"}],
            api_base="http://localhost:11434"
        )
        
        if response and response.choices:
            logger.info("✅ LiteLLM integration working")
            return True
        else:
            logger.error("❌ LiteLLM returned empty response")
            return False
    except Exception as e:
        logger.error(f"❌ LiteLLM integration failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Ollama Diagnostics for CrewAI")
    print("=" * 40)
    
    print("\\n1. Checking Ollama service...")
    service_ok = check_ollama_service()
    
    print("\\n2. Testing Ollama completion...")
    completion_ok = test_ollama_completion()
    
    print("\\n3. Testing LiteLLM integration...")
    litellm_ok = test_litellm_integration()
    
    print("\\n📊 Summary:")
    print(f"   Service: {'✅' if service_ok else '❌'}")
    print(f"   Completion: {'✅' if completion_ok else '❌'}")
    print(f"   LiteLLM: {'✅' if litellm_ok else '❌'}")
    
    if all([service_ok, completion_ok, litellm_ok]):
        print("\\n🎉 All systems working!")
    else:
        print("\\n⚠️ Issues detected. Try:")
        print("   • brew services restart ollama")
        print("   • ollama pull llama3.2")
        print("   • Check firewall settings")
'''
    
    diagnostics_file = Path(__file__).parent / "ollama_diagnostics.py"
    with open(diagnostics_file, 'w') as f:
        f.write(diagnostics_script)
    
    # Make it executable
    os.chmod(diagnostics_file, 0o755)
    
    logger.info(f"✅ Created diagnostics script: {diagnostics_file}")
    return diagnostics_file


def main():
    """Main function to apply enhanced error handling"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔧 CrewAI Enhanced Error Handling")
    print("=" * 40)
    
    # Apply enhanced error handling
    print("\\n1. Applying enhanced error handling...")
    if apply_enhanced_error_handling():
        print("   ✅ Enhanced error handling applied")
    else:
        print("   ❌ Failed to apply enhanced error handling")
        return False
    
    # Create diagnostics script
    print("\\n2. Creating diagnostics script...")
    diagnostics_file = create_ollama_diagnostics()
    if diagnostics_file:
        print(f"   ✅ Diagnostics script created: {diagnostics_file}")
    else:
        print("   ❌ Failed to create diagnostics script")
    
    print("\\n✅ Enhanced error handling setup complete!")
    print("\\n💡 Benefits:")
    print("   • Better error messages for Ollama issues")
    print("   • Detailed logging for debugging")
    print("   • Specific guidance for common problems")
    print("   • Validation of response structure")
    
    print("\\n🔍 To diagnose Ollama issues, run:")
    print(f"   python {diagnostics_file}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)