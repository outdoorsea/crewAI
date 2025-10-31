#!/usr/bin/env python3
"""
Script to upgrade from deprecated langchain_community.ChatOllama 
to the new langchain-ollama package.

This script will:
1. Install the new langchain-ollama package
2. Test the import
3. Update requirements.txt if needed
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_langchain_ollama():
    """Install the new langchain-ollama package"""
    try:
        logger.info("Installing langchain-ollama package...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "langchain-ollama"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✅ langchain-ollama package installed successfully")
        logger.info(f"Installation output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install langchain-ollama: {e.stderr}")
        return False

def test_import():
    """Test if the new package can be imported"""
    try:
        from langchain_ollama import Ollama, ChatOllama
        logger.info("✅ Successfully imported Ollama and ChatOllama from langchain-ollama")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import from langchain-ollama: {e}")
        return False

def update_requirements():
    """Add langchain-ollama to requirements.txt if it exists"""
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        logger.info(f"No {requirements_file} found, skipping update")
        return
    
    # Read current requirements
    with open(requirements_file, 'r') as f:
        requirements = f.read()
    
    # Check if langchain-ollama is already listed
    if "langchain-ollama" in requirements:
        logger.info("langchain-ollama already in requirements.txt")
        return
    
    # Add langchain-ollama to requirements
    with open(requirements_file, 'a') as f:
        f.write("\nlangchain-ollama>=0.1.0\n")
    
    logger.info("✅ Added langchain-ollama to requirements.txt")

def test_llm_config():
    """Test the updated LLM configuration"""
    try:
        # Add current directory to path for imports
        sys.path.insert(0, os.path.dirname(__file__))
        
        from config.llm_config import LLMConfig
        
        # Test creating LLM config
        config = LLMConfig()
        logger.info("✅ LLMConfig created successfully")
        
        # Test getting an LLM
        llm = config.get_ollama_llm("llama3.2")
        logger.info("✅ Ollama LLM created successfully")
        
        # Test getting a ChatOllama LLM
        chat_llm = config.get_chat_ollama_llm("llama3.2")
        logger.info("✅ ChatOllama LLM created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to test LLM config: {e}")
        return False

def main():
    """Main upgrade process"""
    logger.info("🔄 Upgrading from langchain_community.ChatOllama to langchain-ollama")
    logger.info("=" * 70)
    
    success = True
    
    # Step 1: Install new package
    if not install_langchain_ollama():
        success = False
    
    # Step 2: Test import
    if success and not test_import():
        success = False
    
    # Step 3: Update requirements
    if success:
        update_requirements()
    
    # Step 4: Test LLM configuration
    if success and not test_llm_config():
        success = False
    
    logger.info("=" * 70)
    if success:
        logger.info("🎉 Successfully upgraded to langchain-ollama!")
        logger.info("The deprecation warning should no longer appear.")
        logger.info("\nBenefits:")
        logger.info("✅ No more deprecation warnings")
        logger.info("✅ Better performance and reliability")
        logger.info("✅ Latest Ollama integration features")
        logger.info("✅ Future-proof with LangChain 1.0")
        return 0
    else:
        logger.error("❌ Upgrade failed. The system will continue to use langchain_community as fallback.")
        return 1

if __name__ == "__main__":
    sys.exit(main())