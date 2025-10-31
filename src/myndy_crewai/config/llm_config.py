"""
LLM Configuration for CrewAI-Myndy Integration

This module configures the LLM backends for CrewAI agents, primarily using
Ollama for local inference with OpenAI as fallback.

File: config/llm_config.py
"""

import os
import subprocess
import requests
from typing import Dict, Any, Optional, List
try:
    # Try to import from the new langchain-ollama package
    from langchain_ollama import Ollama, ChatOllama
    OLLAMA_PACKAGE = "langchain_ollama"
except ImportError:
    # Fallback to the deprecated langchain_community package
    from langchain_community.llms import Ollama
    from langchain_community.chat_models import ChatOllama
    OLLAMA_PACKAGE = "langchain_community"
import logging

logger = logging.getLogger(__name__)


class LLMConfig:
    """Configuration manager for LLM backends."""
    
    def __init__(self):
        """Initialize LLM configuration."""
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("MEMEX_DEFAULT_MODEL", "llama3.2")
        
        # Log which Ollama package is being used
        logger.info(f"Using Ollama from package: {OLLAMA_PACKAGE}")
        
        # Available Ollama models based on myndy setup
        self.available_models = [
            "llama3.2",
            "llama3.1",
            "qwen2.5",
            "gemma2", 
            "mistral",
            "phi3",
            "mixtral",
            "codellama",
            "deepseek-coder"
        ]
        
        # Model assignments per agent role
        self.agent_models = {
            "context_manager": "mixtral",        # Strong reasoning for routing decisions
            "memory_librarian": "llama3.2",      # Good for structured data  
            "research_specialist": "mixtral",    # Strong reasoning (using available model)
            "personal_assistant": "llama3.2",    # Fast responses (using available model)
            "health_analyst": "phi3",            # Efficient for analysis
            "finance_tracker": "mixtral",        # Good with numbers
            "test_assistant": "llama3.2"         # Fast testing and validation
        }
    
    def get_ollama_llm(self, model: str = None, **kwargs) -> Ollama:
        """
        Get an Ollama LLM instance.
        
        Args:
            model: Model name to use (defaults to default_model)
            **kwargs: Additional parameters for Ollama
            
        Returns:
            Configured Ollama LLM instance
        """
        model = model or self.default_model
        
        default_params = {
            "base_url": self.ollama_base_url,
            "model": model,
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "num_predict": kwargs.get("num_predict", 2048),
        }
        
        # Override with any provided kwargs
        default_params.update(kwargs)
        
        try:
            llm = Ollama(**default_params)
            logger.info(f"Created Ollama LLM with model: {model} (using {OLLAMA_PACKAGE})")
            return llm
        except Exception as e:
            logger.error(f"Failed to create Ollama LLM: {e}")
            raise
    
    def get_chat_ollama_llm(self, model: str = None, **kwargs) -> ChatOllama:
        """
        Get a ChatOllama LLM instance for conversational use.
        
        Args:
            model: Model name to use (defaults to default_model)
            **kwargs: Additional parameters for ChatOllama
            
        Returns:
            Configured ChatOllama LLM instance
        """
        model = model or self.default_model
        
        # Ensure model is available, pull if necessary
        if not self.ensure_model_available(model):
            logger.warning(f"Could not ensure model {model} is available, proceeding anyway...")
        
        # Ensure model has :latest tag if no tag specified
        if ":" not in model:
            model = f"{model}:latest"
        
        # For CrewAI compatibility, use model directly (no ollama/ prefix for ChatOllama)
        ollama_model = model
        
        default_params = {
            "base_url": self.ollama_base_url,
            "model": ollama_model,
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "num_predict": kwargs.get("num_predict", 2048),
        }
        
        # Override with any provided kwargs
        default_params.update(kwargs)
        
        try:
            llm = ChatOllama(**default_params)
            logger.info(f"Created ChatOllama LLM with model: {model} (using {OLLAMA_PACKAGE})")
            return llm
        except Exception as e:
            logger.error(f"Failed to create ChatOllama LLM: {e}")
            if OLLAMA_PACKAGE == "langchain_community":
                logger.warning("Consider upgrading to langchain-ollama package to resolve deprecation warnings")
            raise
    
    def get_agent_llm(self, agent_role: str, **kwargs) -> ChatOllama:
        """
        Get the appropriate LLM for a specific agent role.
        
        Args:
            agent_role: The role of the agent
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Configured LLM instance for the agent
        """
        model = self.agent_models.get(agent_role, self.default_model)
        return self.get_chat_ollama_llm(model, **kwargs)
    
    def check_model_exists(self, model: str) -> bool:
        """
        Check if a model exists in Ollama.
        
        Args:
            model: Model name to check
            
        Returns:
            True if model exists, False otherwise
        """
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                model_names = [m['name'].split(':')[0] for m in models_data.get('models', [])]
                return model in model_names
            return False
        except Exception as e:
            logger.warning(f"Could not check if model {model} exists: {e}")
            return False
    
    def pull_model(self, model: str) -> bool:
        """
        Pull a model using Ollama CLI.
        
        Args:
            model: Model name to pull
            
        Returns:
            True if pull was successful, False otherwise
        """
        try:
            logger.info(f"Pulling Ollama model: {model}")
            result = subprocess.run(
                ["ollama", "pull", model], 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully pulled model: {model}")
                return True
            else:
                logger.error(f"Failed to pull model {model}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while pulling model: {model}")
            return False
        except Exception as e:
            logger.error(f"Error pulling model {model}: {e}")
            return False
    
    def ensure_model_available(self, model: str) -> bool:
        """
        Ensure a model is available, pulling it if necessary.
        
        Args:
            model: Model name to ensure is available
            
        Returns:
            True if model is available, False otherwise
        """
        if self.check_model_exists(model):
            logger.debug(f"Model {model} already available")
            return True
        
        logger.info(f"Model {model} not found, attempting to pull...")
        return self.pull_model(model)

    def test_ollama_connection(self, model: str = None) -> bool:
        """
        Test connection to Ollama server.
        
        Args:
            model: Model to test (defaults to default_model)
            
        Returns:
            True if connection successful, False otherwise
        """
        model = model or self.default_model
        
        try:
            llm = self.get_ollama_llm(model)
            # Try a simple completion
            response = llm("Hello")
            logger.info(f"Ollama connection test successful with model: {model}")
            return True
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False
    
    def list_available_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of available model names
        """
        return self.available_models.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive model configuration information.
        
        Returns:
            Dictionary with model configuration details
        """
        return {
            "ollama_base_url": self.ollama_base_url,
            "default_model": self.default_model,
            "available_models": self.available_models,
            "agent_models": self.agent_models,
            "ollama_only": True
        }


# Global configuration instance
_llm_config = None

def get_llm_config() -> LLMConfig:
    """
    Get the global LLM configuration instance.
    
    Returns:
        LLMConfig instance
    """
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfig()
    return _llm_config


def get_agent_llm(agent_role: str, **kwargs) -> ChatOllama:
    """
    Convenience function to get LLM for an agent role.
    
    Args:
        agent_role: The role of the agent
        **kwargs: Additional LLM parameters
        
    Returns:
        Configured LLM instance
    """
    config = get_llm_config()
    return config.get_agent_llm(agent_role, **kwargs)


if __name__ == "__main__":
    # Test the LLM configuration
    config = LLMConfig()
    
    print("LLM Configuration Test")
    print("=" * 40)
    
    info = config.get_model_info()
    print(f"Ollama URL: {info['ollama_base_url']}")
    print(f"Default model: {info['default_model']}")
    print(f"Available models: {', '.join(info['available_models'])}")
    print(f"Ollama only: {info['ollama_only']}")
    
    print("\nAgent model assignments:")
    for role, model in info['agent_models'].items():
        print(f"  {role}: {model}")
    
    # Test connection
    print(f"\nTesting Ollama connection...")
    if config.test_ollama_connection():
        print("✅ Ollama connection successful")
    else:
        print("❌ Ollama connection failed")