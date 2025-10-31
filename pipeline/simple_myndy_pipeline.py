"""
title: Myndy AI Simple Pipeline
author: Jeremy
version: 1.0.0
license: MIT
description: Simple Myndy AI pipeline for testing valve functionality
requirements: pydantic
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Union, Generator, Iterator
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    """Simple Myndy AI Pipeline for OpenWebUI"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        debug_mode: bool = False
        api_key: str = "test-key"
    
    def __init__(self):
        """Initialize the pipeline"""
        self.type = "manifold"
        self.name = "Myndy AI Simple"
        self.version = "1.0.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        logger.info("🚀 Simple Myndy AI Pipeline initialized")
    
    async def on_startup(self):
        """Called when the pipeline starts up"""
        logger.info("🚀 Pipeline startup initiated")
        
    async def on_shutdown(self):
        """Called when the pipeline shuts down"""
        logger.info("🛑 Pipeline shutdown initiated")
        
    async def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info("⚙️ Pipeline valves updated")
        logger.info(f"🔧 Current valve settings: {self.valves.dict()}")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models for OpenWebUI"""
        return [
            {
                "id": "myndy_simple",
                "name": "🧠 Myndy AI (Simple)",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "myndy-ai"
            }
        ]
    
    def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], body: Dict[str, Any]) -> str:
        """Main processing function"""
        logger.info(f"💬 Processing message: {user_message}")
        logger.info(f"🔧 Debug mode: {self.valves.debug_mode}")
        logger.info(f"🛠️ Tool execution: {self.valves.enable_tool_execution}")
        
        response = f"Hello! This is Myndy AI Simple responding to: {user_message}\n\n"
        response += f"Current settings:\n"
        response += f"- Debug mode: {self.valves.debug_mode}\n"
        response += f"- Tool execution: {self.valves.enable_tool_execution}\n"
        response += f"- Intelligent routing: {self.valves.enable_intelligent_routing}\n"
        
        return response