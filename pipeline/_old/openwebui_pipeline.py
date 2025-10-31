"""
title: Myndy AI Pipeline
author: Jeremy
version: 1.0.0
license: MIT
description: Myndy AI pipeline with intelligent agent routing and real-time logging
requirements: fastapi, uvicorn, pydantic
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Generator, Iterator

# Add paths contextually
CURRENT_DIR = Path(__file__).parent
PIPELINE_ROOT = CURRENT_DIR.parent
MYNDY_AI_ROOT = PIPELINE_ROOT.parent / "myndy-ai"

sys.path.insert(0, str(PIPELINE_ROOT))
if MYNDY_AI_ROOT.exists():
    sys.path.insert(0, str(MYNDY_AI_ROOT))
else:
    # Try alternative paths
    for alt_path in ["../../myndy-ai", "../myndy-ai", "../../../myndy-ai"]:
        abs_alt = (CURRENT_DIR / alt_path).resolve()
        if abs_alt.exists():
            sys.path.insert(0, str(abs_alt))
            break

from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    """OpenWebUI-compatible Myndy AI Pipeline"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        enable_contact_management: bool = True
        enable_memory_search: bool = True
        debug_mode: bool = False
        myndy_path: str = str(MYNDY_AI_ROOT) if 'MYNDY_AI_ROOT' in globals() and MYNDY_AI_ROOT.exists() else "../myndy-ai"
    
    def __init__(self):
        """Initialize the pipeline"""
        self.type = "manifold"  # Required for OpenWebUI
        self.id = "myndy_ai"
        self.name = "Myndy AI"
        self.version = "1.0.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # Import pipeline components
        self._import_pipeline()
        
        logger.info(f"🚀 Myndy AI Pipeline {self.version} initialized for OpenWebUI")
    
    def _import_pipeline(self):
        """Import the actual pipeline implementation"""
        try:
            # Try to import the full pipeline
            from crewai_myndy_pipeline import Pipeline as FullPipeline
            self._pipeline = FullPipeline()
            self.pipeline_type = "full"
            logger.info("✅ Loaded full CrewAI-Myndy pipeline")
        except ImportError as e:
            logger.warning(f"⚠️ Could not load full pipeline: {e}")
            try:
                # Fallback to simple pipeline
                from simple_server import SimplePipeline
                self._pipeline = SimplePipeline()
                self.pipeline_type = "simple"
                logger.info("✅ Loaded simple Myndy pipeline")
            except ImportError as e2:
                logger.error(f"❌ Could not load any pipeline: {e2}")
                # Create minimal pipeline
                self._create_minimal_pipeline()
                self.pipeline_type = "minimal"
    
    def _create_minimal_pipeline(self):
        """Create a minimal pipeline for basic functionality"""
        class MinimalPipeline:
            def __init__(self):
                self.name = "Myndy AI (Minimal)"
                self.version = "1.0.0"
            
            def get_models(self):
                return [
                    {
                        "id": "myndy_ai",
                        "name": "🧠 Myndy AI",
                        "object": "model",
                        "created": int(datetime.now().timestamp()),
                        "owned_by": "myndy-ai"
                    }
                ]
            
            def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], body: Dict[str, Any]) -> str:
                return f"Myndy AI (Minimal Mode): {user_message}\n\nNote: Install full dependencies for complete functionality."
        
        self._pipeline = MinimalPipeline()
        logger.info("✅ Created minimal pipeline")
    
    def on_startup(self):
        """Called when the pipeline starts up"""
        logger.info("🚀 Myndy AI Pipeline starting up...")
        if hasattr(self._pipeline, 'on_startup'):
            self._pipeline.on_startup()
    
    def on_shutdown(self):
        """Called when the pipeline shuts down"""
        logger.info("🛑 Myndy AI Pipeline shutting down...")
        if hasattr(self._pipeline, 'on_shutdown'):
            self._pipeline.on_shutdown()
    
    def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info("⚙️ Pipeline valves updated")
        if hasattr(self._pipeline, 'valves'):
            # Update the underlying pipeline valves
            for key, value in self.valves.dict().items():
                if hasattr(self._pipeline.valves, key):
                    setattr(self._pipeline.valves, key, value)
    
    def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], 
             body: Dict[str, Any]) -> Union[str, Generator, Iterator]:
        """Process messages through the pipeline"""
        
        if self.valves.debug_mode:
            logger.info(f"🔍 Processing: {user_message[:50]}...")
            logger.info(f"🎯 Model: {model_id}")
            logger.info(f"📊 Pipeline type: {self.pipeline_type}")
        
        try:
            # Delegate to the underlying pipeline
            if hasattr(self._pipeline, 'pipe'):
                return self._pipeline.pipe(user_message, model_id, messages, body)
            else:
                # Fallback for minimal pipeline
                return self._pipeline.pipe(user_message, model_id, messages, body)
                
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get available models"""
        try:
            if hasattr(self._pipeline, 'get_models'):
                models = self._pipeline.get_models()
                logger.info(f"📊 Returning {len(models)} models")
                return models
            else:
                # Fallback
                return [
                    {
                        "id": "myndy_ai",
                        "name": "🧠 Myndy AI",
                        "object": "model",
                        "created": int(datetime.now().timestamp()),
                        "owned_by": "myndy-ai"
                    }
                ]
        except Exception as e:
            logger.error(f"❌ Error getting models: {e}")
            return []
    
    def get_manifest(self) -> Dict[str, Any]:
        """Return pipeline manifest for OpenWebUI"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "type": self.type,
            "description": "Myndy AI - Your personal intelligent assistant with conversation-driven learning",
            "author": "Jeremy",
            "license": "MIT",
            "models": self.get_models()
        }


# Export for OpenWebUI to discover
__all__ = ["Pipeline"]

# Test function for debugging
def test_pipeline():
    """Test the pipeline functionality"""
    print("🧪 Testing Myndy AI Pipeline...")
    
    pipeline = Pipeline()
    
    # Test models
    models = pipeline.get_models()
    print(f"✅ Models: {len(models)} available")
    
    # Test pipe function
    test_message = "Hello Myndy!"
    response = pipeline.pipe(
        user_message=test_message,
        model_id="auto",
        messages=[{"role": "user", "content": test_message}],
        body={}
    )
    print(f"✅ Response: {response[:100]}...")
    
    print("🎉 Pipeline test completed successfully!")

if __name__ == "__main__":
    test_pipeline()