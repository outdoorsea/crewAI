#!/usr/bin/env python3
"""
OpenWebUI-compatible Pipeline for Myndy AI
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Union, Generator, Iterator

# Add current directory and parent paths contextually
CURRENT_DIR = Path(__file__).parent
PIPELINE_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(PIPELINE_ROOT))

# Configure simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the pipeline using contextual imports
try:
    from crewai_myndy_pipeline import Pipeline as MyndyPipeline
except ImportError as e:
    logger.error(f"Could not import MyndyPipeline: {e}")
    logger.info("Falling back to simple pipeline mode")
    MyndyPipeline = None

# Initialize pipeline globally
logger.info("🚀 Initializing Myndy AI Pipeline...")
myndy_pipeline = MyndyPipeline()
logger.info(f"✅ Pipeline ready: {myndy_pipeline.name} v{myndy_pipeline.version}")

# OpenWebUI pipeline interface
class Pipeline:
    """OpenWebUI Pipeline Interface"""
    
    def __init__(self):
        self.type = "manifold"
        self.id = "myndy_ai_pipeline"
        self.name = "Myndy AI Pipeline"
        self.version = "0.1.0"
        
    def get_models(self):
        """Return available models"""
        logger.info("📋 Models requested")
        models = myndy_pipeline.get_models()
        logger.info(f"📊 Returning {len(models)} models")
        return models
    
    def pipe(self, body: dict) -> str:
        """Main pipeline execution"""
        logger.info("🎯 Pipeline execution started")
        
        try:
            # Extract request data
            messages = body.get("messages", [])
            model_id = body.get("model", "auto")
            
            # Get user message
            user_message = ""
            for message in reversed(messages):
                if message.get("role") == "user":
                    user_message = message.get("content", "")
                    break
            
            logger.info(f"💬 Processing: {user_message[:50]}...")
            logger.info(f"🤖 Model: {model_id}")
            
            # Execute pipeline
            response = myndy_pipeline.pipe(
                user_message=user_message,
                model_id=model_id,
                messages=messages,
                body=body
            )
            
            logger.info(f"✅ Response generated ({len(response)} chars)")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return f"Error: {str(e)}"

# Create pipeline instance for OpenWebUI
pipeline = Pipeline()

if __name__ == "__main__":
    print("🚀 Myndy AI Pipeline for OpenWebUI")
    print("=" * 60)
    print(f"🎯 Pipeline: {pipeline.name} v{pipeline.version}")
    print(f"🤖 Models: {len(pipeline.get_models())}")
    print("📋 Ready for OpenWebUI integration")
    print("=" * 60)