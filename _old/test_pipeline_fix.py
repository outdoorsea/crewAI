#!/usr/bin/env python3
"""
Test script to verify the pipeline fix is working
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

def test_pipeline():
    """Test the CrewAI pipeline that was failing before"""
    try:
        from pipeline.crewai_myndy_pipeline import Pipeline
        
        logger.info("Creating pipeline instance...")
        pipeline = Pipeline()
        
        logger.info("Testing pipeline with simple message...")
        
        # Simulate a simple OpenWebUI request
        test_message = "Hello, can you help me?"
        test_model_id = "memory_librarian"
        test_messages = [{"role": "user", "content": test_message}]
        test_body = {}
        
        # Test the pipeline
        response = pipeline.pipe(
            user_message=test_message,
            model_id=test_model_id, 
            messages=test_messages,
            body=test_body
        )
        
        logger.info(f"✅ Pipeline test successful!")
        logger.info(f"Response length: {len(response)} characters")
        logger.info(f"Response preview: {response[:200]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run pipeline test"""
    print("🧪 Testing CrewAI Pipeline Fix")
    print("=" * 40)
    
    print("\nTesting pipeline that was previously failing...")
    if test_pipeline():
        print("✅ Pipeline test passed - LiteLLM issue is resolved!")
        return True
    else:
        print("❌ Pipeline test failed - issue may still exist")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)