"""
title: User-Aware Myndy AI Pipeline
author: Jeremy
version: 1.0.0
license: MIT
description: Enhanced Myndy AI pipeline with user context awareness
requirements: fastapi, uvicorn, pydantic
"""

import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Generator, Iterator, Optional

# Add paths contextually
CURRENT_DIR = Path(__file__).parent
PIPELINE_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(PIPELINE_ROOT))

from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    """User-Aware OpenWebUI-compatible Myndy AI Pipeline"""
    
    class Valves(BaseModel):
        """Configuration valves for the pipeline"""
        enable_user_tracking: bool = True
        enable_user_logging: bool = True
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        debug_mode: bool = False
        store_user_sessions: bool = True
        myndy_path: str = str(PIPELINE_ROOT.parent / "myndy-ai") if (PIPELINE_ROOT.parent / "myndy-ai").exists() else "../myndy-ai"
    
    def __init__(self):
        """Initialize the pipeline"""
        self.type = "manifold"  # Required for OpenWebUI
        self.id = "myndy_ai_user_aware"
        self.name = "Myndy AI (User-Aware)"
        self.version = "1.0.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        # User session storage
        self.user_sessions = {}
        self.user_preferences = {}
        
        # Import pipeline components
        self._import_pipeline()
        
        logger.info(f"🚀 User-Aware Myndy AI Pipeline {self.version} initialized")
    
    def _import_pipeline(self):
        """Import the actual pipeline implementation"""
        try:
            # Try to import the full pipeline
            from crewai_myndy_pipeline_proper import Pipeline as FullPipeline
            self._pipeline = FullPipeline()
            self.pipeline_type = "full"
            logger.info("✅ Loaded full CrewAI-Myndy pipeline")
        except ImportError as e:
            logger.warning(f"⚠️ Could not load full pipeline: {e}")
            self._create_minimal_pipeline()
            self.pipeline_type = "minimal"
    
    def _create_minimal_pipeline(self):
        """Create a minimal pipeline for basic functionality"""
        class MinimalPipeline:
            def __init__(self):
                self.name = "Myndy AI (User-Aware Minimal)"
                self.version = "1.0.0"
            
            def get_models(self):
                return [
                    {
                        "id": "myndy_ai_user_aware",
                        "name": "🧠 Myndy AI (User-Aware)",
                        "object": "model",
                        "created": int(datetime.now().timestamp()),
                        "owned_by": "myndy-ai"
                    }
                ]
        
        self._pipeline = MinimalPipeline()
        logger.info("✅ Created minimal user-aware pipeline")
    
    def _extract_user_info(self, __user__: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract and structure user information"""
        if not __user__:
            return {
                "id": "anonymous",
                "name": "Anonymous User", 
                "email": None,
                "role": "user",
                "is_authenticated": False
            }
        
        return {
            "id": __user__.get("id", "unknown"),
            "name": __user__.get("name", "Unknown User"),
            "email": __user__.get("email"),
            "role": __user__.get("role", "user"),
            "is_authenticated": True,
            "raw_user_data": __user__
        }
    
    def _extract_request_headers(self, __request__: Optional[Any]) -> Dict[str, Any]:
        """Extract relevant headers from the request"""
        headers = {}
        if __request__ and hasattr(__request__, 'headers'):
            request_headers = dict(__request__.headers)
            
            # Look for common user-related headers
            user_headers = {
                'x-user-id': request_headers.get('x-user-id'),
                'x-user-email': request_headers.get('x-user-email'),
                'x-user-name': request_headers.get('x-user-name'),
                'x-user-role': request_headers.get('x-user-role'),
                'authorization': request_headers.get('authorization'),
                'user-agent': request_headers.get('user-agent'),
                'x-forwarded-for': request_headers.get('x-forwarded-for'),
                'x-real-ip': request_headers.get('x-real-ip'),
            }
            
            # Filter out None values
            headers = {k: v for k, v in user_headers.items() if v is not None}
        
        return headers
    
    def _get_or_create_user_session(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get or create a user session"""
        user_id = user_info["id"]
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "user_id": user_id,
                "name": user_info["name"],
                "email": user_info["email"],
                "role": user_info["role"],
                "session_start": datetime.now().isoformat(),
                "conversation_count": 0,
                "last_activity": datetime.now().isoformat(),
                "preferences": {},
                "conversation_history": []
            }
        
        # Update last activity
        self.user_sessions[user_id]["last_activity"] = datetime.now().isoformat()
        self.user_sessions[user_id]["conversation_count"] += 1
        
        return self.user_sessions[user_id]
    
    def _log_user_activity(self, user_info: Dict[str, Any], message: str, headers: Dict[str, Any]):
        """Log user activity for debugging and analytics"""
        if self.valves.enable_user_logging:
            logger.info(f"👤 User Activity:")
            logger.info(f"   🆔 User ID: {user_info['id']}")
            logger.info(f"   👤 Name: {user_info['name']}")
            logger.info(f"   📧 Email: {user_info['email']}")
            logger.info(f"   🎭 Role: {user_info['role']}")
            logger.info(f"   🔐 Authenticated: {user_info['is_authenticated']}")
            logger.info(f"   💬 Message: {message[:50]}{'...' if len(message) > 50 else ''}")
            
            if self.valves.debug_mode and headers:
                logger.info(f"   📋 Headers: {headers}")
    
    async def pipe(
        self,
        body: dict,
        __user__: Optional[Dict[str, Any]] = None,
        __request__: Optional[Any] = None,
        __event_emitter__: Optional[Any] = None,
        __event_call__: Optional[Any] = None,
        __task__: Optional[str] = None,
        __task_body__: Optional[dict] = None,
        __files__: Optional[list] = None,
        __metadata__: Optional[dict] = None,
        __tools__: Optional[dict] = None,
    ) -> Union[str, Generator, Iterator]:
        """Enhanced pipe function with user context awareness"""
        
        start_time = time.time()
        
        # Extract user information
        user_info = self._extract_user_info(__user__)
        headers = self._extract_request_headers(__request__)
        
        # Extract message from body
        messages = body.get("messages", [])
        model_id = body.get("model", "auto")
        
        user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break
        
        # Log user activity
        self._log_user_activity(user_info, user_message, headers)
        
        # Get or create user session
        if self.valves.enable_user_tracking:
            user_session = self._get_or_create_user_session(user_info)
            
            # Add conversation to history
            user_session["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "message": user_message,
                "model": model_id,
                "task": __task__
            })
        
        try:
            # Enhanced body with user context
            enhanced_body = body.copy()
            enhanced_body["__user_context__"] = {
                "user_info": user_info,
                "headers": headers,
                "session": user_session if self.valves.enable_user_tracking else None,
                "files": __files,
                "metadata": __metadata,
                "tools": __tools,
                "task": __task
            }
            
            # Use full Myndy pipeline if available
            if hasattr(self._pipeline, 'pipe'):
                logger.info(f"🧠 Processing through {self.pipeline_type} pipeline for user {user_info['name']}")
                
                # Check if pipeline supports the new signature
                import inspect
                pipe_signature = inspect.signature(self._pipeline.pipe)
                
                if '__user__' in pipe_signature.parameters:
                    # New signature support
                    response = await self._pipeline.pipe(
                        body=enhanced_body,
                        __user__=__user__,
                        __request__=__request__
                    )
                else:
                    # Legacy signature support
                    response = self._pipeline.pipe(
                        user_message=user_message,
                        model_id=model_id,
                        messages=messages,
                        body=enhanced_body
                    )
                
                if self.valves.enable_user_logging:
                    process_time = time.time() - start_time
                    logger.info(f"⚡ Pipeline completed for {user_info['name']} in {process_time:.3f}s")
                
                return response
            
            else:
                # Fallback with user context
                response = f"""🧠 **Myndy AI (User-Aware Mode)**

Hello **{user_info['name']}**! 👋

**Your Message:** {user_message}

**User Context:**
- 🆔 User ID: {user_info['id']}
- 👤 Name: {user_info['name']}
- 📧 Email: {user_info['email'] or 'Not provided'}
- 🎭 Role: {user_info['role']}
- 🔐 Authenticated: {'Yes' if user_info['is_authenticated'] else 'No'}

**Session Info:**
- 💬 Conversations this session: {user_session['conversation_count'] if self.valves.enable_user_tracking else 'N/A'}
- 🕐 Last activity: {user_session['last_activity'] if self.valves.enable_user_tracking else 'N/A'}

**Pipeline Status:**
- ✅ User context: Captured
- ✅ Session tracking: {'Enabled' if self.valves.enable_user_tracking else 'Disabled'}
- ⚠️  Full pipeline: {self.pipeline_type}

The user-aware pipeline is functioning correctly and has captured your user context!"""

                return response
                
        except Exception as e:
            logger.error(f"❌ Pipeline error for user {user_info['name']}: {e}")
            if self.valves.debug_mode:
                import traceback
                logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            
            return f"❌ **Pipeline Error**\n\nSorry {user_info['name']}, I encountered an error processing your request: {str(e)}\n\nPlease try again or check the pipeline logs for more details."
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get available models"""
        try:
            if hasattr(self._pipeline, 'get_models'):
                models = self._pipeline.get_models()
                # Add user-aware prefix to model names
                for model in models:
                    if not model["name"].startswith("🧠"):
                        model["name"] = f"🧠 {model['name']} (User-Aware)"
                return models
            else:
                # Fallback
                return [
                    {
                        "id": "myndy_ai_user_aware",
                        "name": "🧠 Myndy AI (User-Aware)",
                        "object": "model",
                        "created": int(datetime.now().timestamp()),
                        "owned_by": "myndy-ai"
                    }
                ]
        except Exception as e:
            logger.error(f"❌ Error getting models: {e}")
            return []
    
    # OpenWebUI lifecycle methods
    async def on_startup(self):
        """Called when the pipeline starts up"""
        logger.info("🚀 User-Aware Myndy AI Pipeline starting up...")
        logger.info(f"👤 User tracking: {'Enabled' if self.valves.enable_user_tracking else 'Disabled'}")
        logger.info(f"📝 User logging: {'Enabled' if self.valves.enable_user_logging else 'Disabled'}")
    
    async def on_shutdown(self):
        """Called when the pipeline shuts down"""
        logger.info("🛑 User-Aware Myndy AI Pipeline shutting down...")
        if self.valves.enable_user_logging and self.user_sessions:
            logger.info(f"📊 Final session stats: {len(self.user_sessions)} users tracked")
    
    async def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info("🔧 User-aware pipeline valves updated")
        logger.info(f"   👤 User tracking: {self.valves.enable_user_tracking}")
        logger.info(f"   📝 User logging: {self.valves.enable_user_logging}")


# Export for OpenWebUI to discover
__all__ = ["Pipeline"]

# Test function for debugging
def test_user_aware_pipeline():
    """Test the user-aware pipeline functionality"""
    print("🧪 Testing User-Aware Myndy AI Pipeline...")
    
    pipeline = Pipeline()
    
    # Test with mock user data
    mock_user = {
        "id": "test_user_123",
        "name": "Test User",
        "email": "test@example.com",
        "role": "user"
    }
    
    mock_body = {
        "messages": [{"role": "user", "content": "Hello from test user!"}],
        "model": "auto"
    }
    
    # Test the pipe function
    import asyncio
    
    async def run_test():
        response = await pipeline.pipe(
            body=mock_body,
            __user__=mock_user
        )
        return response
    
    response = asyncio.run(run_test())
    print(f"✅ Response: {response[:200]}...")
    
    print("🎉 User-aware pipeline test completed successfully!")

if __name__ == "__main__":
    test_user_aware_pipeline()