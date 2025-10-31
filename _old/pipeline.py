"""
title: Myndy AI Pipeline
author: Jeremy  
version: 1.0.0
license: MIT
description: Myndy AI - Your personal intelligent assistant with conversation-driven learning and 5 specialized agents
requirements: fastapi, uvicorn, pydantic
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Generator, Iterator

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "/Users/jeremy/myndy")

from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    """Myndy AI Pipeline for OpenWebUI"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        enable_contact_management: bool = True
        enable_memory_search: bool = True
        debug_mode: bool = False
        myndy_path: str = "/Users/jeremy/myndy"
        api_key: str = "0p3n-w3bu!"  # Standard OpenWebUI pipeline key
    
    def __init__(self):
        """Initialize the pipeline"""
        self.type = "manifold"
        self.id = "myndy_ai"
        self.name = "Myndy AI"
        self.version = "1.0.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # Load pipeline implementation
        self._load_pipeline()
        
        logger.info(f"🚀 Myndy AI Pipeline {self.version} ready for OpenWebUI")
    
    def _load_pipeline(self):
        """Load the actual pipeline implementation"""
        try:
            # Import the pipeline from the pipeline directory
            from pipeline.crewai_myndy_pipeline import Pipeline as MyndyPipeline
            self._pipeline = MyndyPipeline()
            self.pipeline_type = "full"
            logger.info("✅ Loaded full Myndy pipeline")
        except ImportError as e:
            logger.warning(f"⚠️ Full pipeline not available: {e}")
            try:
                from pipeline.simple_server import SimplePipeline
                self._pipeline = SimplePipeline()
                self.pipeline_type = "simple"
                logger.info("✅ Loaded simple pipeline")
            except ImportError as e2:
                logger.warning(f"⚠️ Simple pipeline not available: {e2}")
                self._create_fallback_pipeline()
                self.pipeline_type = "fallback"
    
    def _create_fallback_pipeline(self):
        """Create a basic fallback pipeline"""
        class FallbackPipeline:
            def __init__(self):
                self.name = "Myndy AI (Fallback)"
                self.version = "1.0.0"
                
                # Basic agent definitions
                self.agents = {
                    "memory_librarian": {"name": "Memory Librarian", "description": "Manages contacts and knowledge"},
                    "research_specialist": {"name": "Research Specialist", "description": "Conducts research and analysis"},
                    "personal_assistant": {"name": "Personal Assistant", "description": "Handles scheduling and productivity"},
                    "health_analyst": {"name": "Health Analyst", "description": "Analyzes health and fitness data"},
                    "finance_tracker": {"name": "Finance Tracker", "description": "Tracks expenses and budgets"}
                }
            
            def get_models(self):
                models = []
                
                # Add auto-routing model
                models.append({
                    "id": "auto",
                    "name": "🧠 Myndy AI v1.0",
                    "object": "model",
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "myndy-ai"
                })
                
                # Add individual agents
                for agent_id, agent_info in self.agents.items():
                    models.append({
                        "id": agent_id,
                        "name": f"🎯 {agent_info['name']}",
                        "object": "model",
                        "created": int(datetime.now().timestamp()),
                        "owned_by": "myndy-ai"
                    })
                
                return models
            
            def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], body: Dict[str, Any]) -> str:
                # Simple routing logic
                message_lower = user_message.lower()
                
                if model_id == "auto":
                    if any(word in message_lower for word in ["contact", "person", "remember", "know"]):
                        selected_agent = "memory_librarian"
                    elif any(word in message_lower for word in ["weather", "time", "schedule"]):
                        selected_agent = "personal_assistant"
                    elif any(word in message_lower for word in ["research", "analyze", "find"]):
                        selected_agent = "research_specialist"
                    elif any(word in message_lower for word in ["health", "fitness", "exercise"]):
                        selected_agent = "health_analyst"
                    elif any(word in message_lower for word in ["money", "expense", "budget"]):
                        selected_agent = "finance_tracker"
                    else:
                        selected_agent = "personal_assistant"
                else:
                    selected_agent = model_id
                
                agent_info = self.agents.get(selected_agent, {"name": "Assistant"})
                
                response_parts = []
                response_parts.append(f"🤖 **{agent_info['name']}** (Fallback Mode)")
                
                if model_id == "auto":
                    response_parts.append(f"**Routing:** Auto-selected {agent_info['name']} based on message analysis")
                
                response_parts.append("")
                response_parts.append(f"**Your message:** {user_message}")
                response_parts.append("")
                response_parts.append("**Response:** I'm running in fallback mode. For full functionality:")
                response_parts.append("1. Ensure all dependencies are installed")
                response_parts.append("2. Verify Myndy is available at `/Users/jeremy/myndy`")
                response_parts.append("3. Check pipeline logs for any import errors")
                response_parts.append("")
                response_parts.append("**🚀 This confirms the pipeline is working and OpenWebUI can communicate with it!**")
                
                return "\n".join(response_parts)
        
        self._pipeline = FallbackPipeline()
        logger.info("✅ Created fallback pipeline")
    
    def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], 
             body: Dict[str, Any]) -> Union[str, Generator, Iterator]:
        """Process messages through the pipeline"""
        
        if self.valves.debug_mode:
            logger.info(f"🔍 Processing message: {user_message[:50]}...")
            logger.info(f"🎯 Model: {model_id}")
            logger.info(f"📊 Pipeline type: {self.pipeline_type}")
        
        try:
            return self._pipeline.pipe(user_message, model_id, messages, body)
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            return f"I encountered an error: {str(e)}\n\nPipeline type: {self.pipeline_type}\nThis confirms OpenWebUI can reach the pipeline."
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get available models"""
        try:
            models = self._pipeline.get_models()
            logger.info(f"📊 Returning {len(models)} models")
            return models
        except Exception as e:
            logger.error(f"❌ Error getting models: {e}")
            # Return at least one model so OpenWebUI can detect the pipeline
            return [{
                "id": "myndy_ai",
                "name": "🧠 Myndy AI (Error Mode)",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "myndy-ai"
            }]
    
    def on_startup(self):
        """Called when pipeline starts"""
        logger.info("🚀 Myndy AI Pipeline starting...")
    
    def on_shutdown(self):
        """Called when pipeline shuts down"""
        logger.info("🛑 Myndy AI Pipeline shutting down...")
    
    def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info("⚙️ Pipeline valves updated")


# Test the pipeline
if __name__ == "__main__":
    print("🧪 Testing Myndy AI Pipeline...")
    
    pipeline = Pipeline()
    
    # Test models
    models = pipeline.get_models()
    print(f"✅ Found {len(models)} models:")
    for model in models:
        print(f"   - {model['name']}")
    
    # Test pipeline
    response = pipeline.pipe(
        user_message="Hello Myndy!",
        model_id="auto", 
        messages=[{"role": "user", "content": "Hello Myndy!"}],
        body={}
    )
    print(f"✅ Pipeline response: {response[:100]}...")
    
    print("🎉 Pipeline test completed!")