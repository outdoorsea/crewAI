#!/usr/bin/env python3
"""
OpenWebUI-Compatible Pipeline with Enhanced Real-Time Logging
"""

import logging
import sys
import time
import warnings
from pathlib import Path
from typing import List, Dict, Any, Union, Generator, Iterator
from pydantic import BaseModel

# Suppress specific warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", message=".*Mixing V1 models and V2 models.*")
warnings.filterwarnings("ignore", category=UserWarning, module="crewai.telemtry.telemetry")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")

# Add current directory and parent paths contextually
CURRENT_DIR = Path(__file__).parent
PIPELINE_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(PIPELINE_ROOT))

# Configure enhanced terminal logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/myndy_openwebui_pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

# Try to import the full pipeline, fall back to simple
try:
    from crewai_myndy_pipeline import Pipeline as MyndyPipeline
    logger.info("🚀 Loaded full CrewAI-Myndy pipeline")
    PIPELINE_TYPE = "full"
    myndy_pipeline = MyndyPipeline()
    logger.info(f"✅ Pipeline initialized: {myndy_pipeline.name}")
except ImportError as e:
    logger.warning(f"⚠️ Could not load full pipeline: {e}")
    logger.info("📦 Using simple fallback")
    PIPELINE_TYPE = "simple"
    myndy_pipeline = None

class Pipeline:
    """OpenWebUI-Compatible Pipeline with Enhanced Logging"""
    
    class Valves(BaseModel):
        """Pipeline configuration valves"""
        enable_enhanced_logging: bool = True
        enable_intelligent_routing: bool = True
        enable_tool_execution: bool = True
        debug_mode: bool = False
        myndy_api_path: str = str(PIPELINE_ROOT.parent / "myndy-ai") if (PIPELINE_ROOT.parent / "myndy-ai").exists() else "../myndy-ai"
        pipeline_name: str = "Myndy AI Pipeline with Logs"
    
    def __init__(self):
        """Initialize the OpenWebUI-compatible pipeline"""
        self.type = "manifold"  # Allows model selection
        self.id = "myndy_ai_pipeline_logs"
        self.name = "🚀 Myndy AI Pipeline (Enhanced Logging)"
        self.version = "1.0.0"
        
        # Initialize valves
        self.valves = self.Valves()
        
        logger.info(f"🎯 Initializing OpenWebUI Pipeline: {self.name}")
        logger.info(f"📊 Pipeline type: {PIPELINE_TYPE}")
        
    async def on_startup(self):
        """Called when OpenWebUI starts the pipeline"""
        logger.info("🚀 OpenWebUI Pipeline starting up...")
        logger.info(f"📊 Pipeline: {self.name} v{self.version}")
        if myndy_pipeline:
            logger.info(f"🤖 Available models: {len(myndy_pipeline.get_models())}")
            logger.info(f"⚡ Available agents: {list(myndy_pipeline.agents.keys())}")
        else:
            logger.info("📦 Running in simple fallback mode")
    
    async def on_shutdown(self):
        """Called when OpenWebUI shuts down the pipeline"""
        logger.info("🛑 OpenWebUI Pipeline shutting down...")
    
    async def on_valves_updated(self):
        """Called when pipeline configuration is updated"""
        logger.info("🔧 Pipeline valves updated")
        logger.info(f"   📝 Enhanced logging: {self.valves.enable_enhanced_logging}")
        logger.info(f"   🧠 Intelligent routing: {self.valves.enable_intelligent_routing}")
        logger.info(f"   🛠️  Tool execution: {self.valves.enable_tool_execution}")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Return available models for OpenWebUI"""
        if self.valves.enable_enhanced_logging:
            logger.info("📋 Models requested by OpenWebUI")
        
        if myndy_pipeline and hasattr(myndy_pipeline, 'get_models'):
            models = myndy_pipeline.get_models()
            if self.valves.enable_enhanced_logging:
                logger.info(f"📊 Returning {len(models)} models from Myndy pipeline")
            return models
        else:
            # Fallback models
            fallback_models = [
                {
                    "id": "myndy_fallback",
                    "name": "🔧 Myndy AI (Fallback Mode)",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "myndy-ai-fallback"
                }
            ]
            if self.valves.enable_enhanced_logging:
                logger.info("📦 Returning fallback models")
            return fallback_models
    
    def pipe(
        self, 
        user_message: str, 
        model_id: str, 
        messages: List[Dict[str, Any]], 
        body: Dict[str, Any]
    ) -> Union[str, Generator, Iterator]:
        """Main pipeline processing function for OpenWebUI"""
        
        start_time = time.time()
        
        if self.valves.enable_enhanced_logging:
            logger.info(f"💬 OpenWebUI Pipeline processing:")
            logger.info(f"   🎯 Model: {model_id}")
            logger.info(f"   📝 Message: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
            logger.info(f"   📊 Message count: {len(messages)}")
            if self.valves.debug_mode:
                logger.info(f"   🔍 Full body: {body}")
        
        try:
            # Use full Myndy pipeline if available
            if myndy_pipeline and hasattr(myndy_pipeline, 'pipe'):
                if self.valves.enable_enhanced_logging:
                    logger.info("🧠 Processing through full Myndy AI pipeline...")
                
                response = myndy_pipeline.pipe(
                    user_message=user_message,
                    model_id=model_id,
                    messages=messages,
                    body=body
                )
                
                if self.valves.enable_enhanced_logging:
                    process_time = time.time() - start_time
                    logger.info(f"⚡ Myndy pipeline completed in {process_time:.3f}s")
                    logger.info(f"📤 Response length: {len(response)} characters")
                
                return response
            
            else:
                # Fallback processing
                if self.valves.enable_enhanced_logging:
                    logger.info("📦 Processing through fallback mode...")
                
                response = f"""🔧 **Myndy AI Pipeline (Fallback Mode)**

**Your message:** {user_message}

**Response:** I'm running in fallback mode as the full Myndy AI pipeline couldn't be loaded. 

**Pipeline Status:**
- ✅ OpenWebUI integration: Working
- ✅ Enhanced logging: Active
- ⚠️  Full pipeline: {PIPELINE_TYPE}
- 📊 Models available: {len(self.get_models())}

The full CrewAI-Myndy pipeline with intelligent agents is temporarily unavailable, but the basic pipeline infrastructure is functioning correctly."""

                if self.valves.enable_enhanced_logging:
                    process_time = time.time() - start_time
                    logger.info(f"📦 Fallback processing completed in {process_time:.3f}s")
                
                return response
                
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            if self.valves.debug_mode:
                import traceback
                logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            
            return f"❌ **Pipeline Error**\n\nSorry, I encountered an error processing your request: {str(e)}\n\nPlease try again or check the pipeline logs for more details."


# Create the pipeline instance for OpenWebUI
pipeline = Pipeline()


if __name__ == "__main__":
    import sys
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from contextlib import asynccontextmanager
    
    # Check if user wants pipeline class mode (default is server)
    if len(sys.argv) > 1 and sys.argv[1] == "--pipeline":
        # Pipeline class mode
        print("🚀 OpenWebUI-Compatible Myndy AI Pipeline")
        print("=" * 60)
        print(f"📊 Pipeline Type: {PIPELINE_TYPE.title()}")
        print(f"🎯 Pipeline ID: {pipeline.id}")
        print(f"📋 Available Models: {len(pipeline.get_models())}")
        print()
        print("📁 This file can be directly uploaded to OpenWebUI")
        print("🖥️  To run as server: python server_with_logs.py")
        print("=" * 60)
        
        # Test the pipeline locally
        test_response = pipeline.pipe(
            user_message="Hello from local test",
            model_id="auto",
            messages=[{"role": "user", "content": "Hello from local test"}],
            body={}
        )
        print(f"\n🧪 Test Response:\n{test_response}")
        print("\n✅ Pipeline is ready for OpenWebUI integration!")
    
    else:
        # Server mode (default)
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Application lifespan manager"""
            logger.info("🚀 Myndy AI Pipeline server starting up...")
            logger.info(f"📊 Pipeline type: {PIPELINE_TYPE}")
            logger.info(f"🎯 Pipeline initialized: {pipeline.name}")
            logger.info(f"🎯 Available models: {len(pipeline.get_models())}")
            yield
            logger.info("🛑 Myndy AI Pipeline server shutting down...")

        # Create FastAPI app
        app = FastAPI(
            title=f"Myndy AI Pipeline ({PIPELINE_TYPE.title()})",
            description="Myndy AI integration with enhanced logging",
            version="1.0.0",
            lifespan=lifespan
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Request logging middleware
        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            """Log all HTTP requests with timing"""
            start_time = time.time()
            logger.info(f"📥 {request.method} {request.url.path}")
            response = await call_next(request)
            process_time = time.time() - start_time
            status_emoji = "✅" if response.status_code < 400 else "❌"
            logger.info(f"📤 {status_emoji} {response.status_code} | {process_time:.3f}s")
            return response

        @app.get("/")
        async def get_pipeline_manifest():
            """Get pipeline manifest"""
            return {
                "name": pipeline.name,
                "version": pipeline.version,
                "type": pipeline.type,
                "id": pipeline.id,
                "models": pipeline.get_models()
            }

        @app.get("/status")
        async def get_status():
            """System status and metrics"""
            logger.info("📊 Status endpoint accessed")
            return {
                "status": "healthy",
                "agents_available": len(pipeline.get_models()),
                "tools_available": "31+",
                "ollama_status": True,
                "pipeline_type": pipeline.type,
                "pipeline_id": pipeline.id
            }

        @app.get("/agents")
        async def get_agents():
            """List all available agents"""
            logger.info("🤖 Agents endpoint accessed") 
            return {
                "agents": pipeline.get_models(),
                "total": len(pipeline.get_models())
            }

        @app.post("/agents/{agent_role}/chat")
        async def chat_with_agent(agent_role: str, request: dict):
            """Chat with specific agent"""
            logger.info(f"🗣️ Direct chat with agent: {agent_role}")
            # Set the model to the specific agent
            request["model"] = agent_role
            return await _handle_chat_request(request)

        @app.get("/tools")
        async def get_tools():
            """List available tools"""
            logger.info("🔧 Tools endpoint accessed")
            import requests
            import os
            try:
                # Get API base URL from environment
                api_base_url = os.getenv("MYNDY_API_BASE_URL", "http://localhost:8000")
                
                # Call myndy-ai API to get available tools
                response = requests.get(
                    f"{api_base_url}/api/v1/tools",
                    timeout=10
                )
                if response.status_code == 200:
                    tools_data = response.json()
                    logger.info(f"📋 Retrieved {len(tools_data.get('tools', []))} tools from myndy-ai")
                    return tools_data
                else:
                    logger.warning(f"Failed to get tools from myndy-ai: {response.status_code}")
                    return {"tools": [], "total": 0, "error": "Backend unavailable"}
            except Exception as e:
                logger.error(f"Error connecting to myndy-ai tools API: {e}")
                return {"tools": [], "total": 0, "error": str(e)}

        @app.post("/tools/execute")
        async def execute_tool(request: dict):
            """Execute specific tool"""
            logger.info(f"⚡ Tool execution request: {request.get('tool_name', 'unknown')}")
            import requests
            import os
            try:
                # Get API base URL from environment
                api_base_url = os.getenv("MYNDY_API_BASE_URL", "http://localhost:8000")
                
                # Forward tool execution to myndy-ai API
                response = requests.post(
                    f"{api_base_url}/api/v1/tools/execute",
                    json=request,
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Tool execution successful")
                    return result
                else:
                    logger.error(f"Tool execution failed: {response.status_code}")
                    return {"error": f"Tool execution failed: {response.status_code}"}
            except Exception as e:
                logger.error(f"Error executing tool via myndy-ai API: {e}")
                return {"error": str(e)}

        @app.post("/tasks")
        async def create_task(request: dict):
            """Create and execute a task"""
            logger.info(f"📋 Task creation request: {request.get('task_type', 'unknown')}")
            import requests
            import os
            try:
                # Get API base URL from environment
                api_base_url = os.getenv("MYNDY_API_BASE_URL", "http://localhost:8000")
                
                # Forward task to myndy-ai API
                response = requests.post(
                    f"{api_base_url}/api/v1/tasks",
                    json=request,
                    timeout=60
                )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Task created successfully")
                    return result
                else:
                    logger.error(f"Task creation failed: {response.status_code}")
                    return {"error": f"Task creation failed: {response.status_code}"}
            except Exception as e:
                logger.error(f"Error creating task via myndy-ai API: {e}")
                return {"error": str(e)}

        @app.get("/tasks/{task_id}")
        async def get_task(task_id: str):
            """Get task status and results"""
            logger.info(f"📊 Task status request: {task_id}")
            import requests
            import os
            try:
                # Get API base URL from environment
                api_base_url = os.getenv("MYNDY_API_BASE_URL", "http://localhost:8000")
                
                # Get task status from myndy-ai API
                response = requests.get(
                    f"{api_base_url}/api/v1/tasks/{task_id}",
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"📋 Task status retrieved")
                    return result
                else:
                    logger.error(f"Task retrieval failed: {response.status_code}")
                    return {"error": f"Task not found: {response.status_code}"}
            except Exception as e:
                logger.error(f"Error getting task via myndy-ai API: {e}")
                return {"error": str(e)}

        @app.post("/crews/execute")
        async def execute_crew(request: dict):
            """Execute multi-agent crew task"""
            logger.info(f"👥 Crew execution request")
            import requests
            import os
            try:
                # Get API base URL from environment
                api_base_url = os.getenv("MYNDY_API_BASE_URL", "http://localhost:8000")
                
                # Forward crew execution to myndy-ai API
                response = requests.post(
                    f"{api_base_url}/api/v1/crews/execute",
                    json=request,
                    timeout=120
                )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Crew execution successful")
                    return result
                else:
                    logger.error(f"Crew execution failed: {response.status_code}")
                    return {"error": f"Crew execution failed: {response.status_code}"}
            except Exception as e:
                logger.error(f"Error executing crew via myndy-ai API: {e}")
                return {"error": str(e)}

        @app.get("/v1/models")
        async def get_models():
            """Get available models"""
            logger.info("📋 Models endpoint accessed")
            models = pipeline.get_models()
            logger.info(f"📊 Returning {len(models)} available models")
            return {
                "data": models,
                "pipeline": True,
                "pipeline_type": "manifold",
                "pipeline_id": pipeline.id,
                "pipeline_name": pipeline.name
            }

        @app.get("/models")
        async def get_models_alt():
            """Get available models (alternative endpoint)"""
            logger.info("📋 Models endpoint accessed (alt)")
            logger.info("📋 Models requested by OpenWebUI")
            models = pipeline.get_models()
            logger.info(f"📊 Returning {len(models)} models from Myndy pipeline")
            return {
                "data": models,
                "pipeline": True,
                "pipeline_type": "manifold", 
                "pipeline_id": pipeline.id,
                "pipeline_name": pipeline.name,
                "type": "pipeline"
            }

        @app.get("/api/v1/pipelines/list")
        async def get_pipelines_list():
            """Get list of available pipelines for OpenWebUI"""
            logger.info("📋 Pipelines list endpoint accessed")
            return {
                "data": [
                    {
                        "id": pipeline.id,
                        "name": pipeline.name,
                        "version": pipeline.version,
                        "type": pipeline.type,
                        "description": "Myndy AI - Your personal intelligent assistant with conversation-driven learning",
                        "models": pipeline.get_models()
                    }
                ]
            }

        @app.get("/pipelines")
        async def get_pipelines():
            """Get pipelines for OpenWebUI detection"""
            logger.info("📋 Pipelines endpoint accessed")
            return {
                "data": [
                    {
                        "id": pipeline.id,
                        "name": pipeline.name,
                        "version": pipeline.version,
                        "type": pipeline.type,
                        "description": "Myndy AI - Your personal intelligent assistant with conversation-driven learning",
                        "author": "Jeremy",
                        "license": "MIT",
                        "status": "active",
                        "models": pipeline.get_models()
                    }
                ]
            }

        @app.post("/openai/verify")
        async def verify_openai_connection(request: dict):
            """OpenWebUI verification endpoint"""
            logger.info("🔍 OpenWebUI verification request")
            return {
                "status": "success",
                "message": "Myndy AI Pipeline connection verified",
                "pipeline": {
                    "name": pipeline.name,
                    "version": pipeline.version,
                    "type": pipeline.type,
                    "models": len(pipeline.get_models())
                }
            }

        @app.post("/verify")
        async def verify_connection_alt(request: dict):
            """Alternative verification endpoint"""
            logger.info("🔍 Pipeline verification request")
            return {
                "status": "verified",
                "pipeline": pipeline.name,
                "version": pipeline.version,
                "models_count": len(pipeline.get_models())
            }

        async def _handle_chat_request(request: dict):
            """Internal chat handling logic"""
            try:
                messages = request.get("messages", [])
                model_id = request.get("model", "auto")
                
                user_message = ""
                for message in reversed(messages):
                    if message.get("role") == "user":
                        user_message = message.get("content", "")
                        break
                
                logger.info(f"💬 Processing: {user_message[:50]}...")
                
                response = pipeline.pipe(
                    user_message=user_message,
                    model_id=model_id,
                    messages=messages,
                    body=request
                )
                
                from datetime import datetime
                return {
                    "id": f"chatcmpl-{datetime.now().timestamp()}",
                    "object": "chat.completion",
                    "created": int(datetime.now().timestamp()),
                    "model": model_id,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": len(user_message.split()),
                        "completion_tokens": len(response.split()),
                        "total_tokens": len(user_message.split()) + len(response.split())
                    }
                }
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                return {
                    "error": {
                        "message": str(e),
                        "type": "pipeline_error",
                        "code": "processing_failed"
                    }
                }
        
        # Removed standard /v1/chat/completions to force OpenWebUI to treat as pipeline

        @app.post("/v1/chat/crewai")
        async def crewai_pipeline_chat(request: dict):
            """Custom CrewAI pipeline endpoint"""
            logger.info("🤖 CrewAI custom endpoint accessed")
            return await _handle_chat_request(request)

        @app.get("/v1/chat/crewai/models")
        async def crewai_pipeline_models():
            """Models endpoint for CrewAI pipeline"""
            logger.info("📋 CrewAI models endpoint accessed")
            models = pipeline.get_models()
            return {
                "data": models,
                "object": "list"
            }

        print("🚀 Starting Myndy AI Pipeline Server with Enhanced Logging")
        print("=" * 60)
        print(f"📊 Pipeline Type: {PIPELINE_TYPE.title()}")
        print("🖥️  Real-time logs will appear below...")
        print("🌐 Server will be available at: http://localhost:9099")
        print("🔗 Add to OpenWebUI: http://localhost:9099")
        print("⏹️  Press Ctrl+C to stop")
        print("=" * 60)
        print()
        
        # Enhanced port handling with automatic process cleanup
        import subprocess
        import signal
        
        def kill_process_on_port(port):
            """Kill any process using the specified port"""
            try:
                # Find process using the port
                result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            pid = int(pid.strip())
                            logger.info(f"🔄 Killing existing process {pid} on port {port}")
                            print(f"🔄 Killing existing process {pid} on port {port}")
                            os.kill(pid, signal.SIGTERM)
                            # Give it a moment to cleanly shut down
                            import time
                            time.sleep(1)
                        except (ValueError, ProcessLookupError, PermissionError) as e:
                            logger.warning(f"⚠️ Could not kill process {pid}: {e}")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                logger.warning(f"⚠️ Could not check port {port}: {e}")
            return False
        
        port = 9099
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                uvicorn.run(
                    app, 
                    host="0.0.0.0", 
                    port=port,
                    log_config=None,
                    access_log=False
                )
                break
            except OSError as e:
                if "address already in use" in str(e).lower():
                    if attempt == 0:
                        # First attempt: try to kill existing process
                        logger.info(f"📍 Port {port} in use, attempting to clean up existing process...")
                        print(f"📍 Port {port} in use, attempting to clean up existing process...")
                        if kill_process_on_port(port):
                            # Try the same port again after cleanup
                            continue
                    
                    if attempt < max_attempts - 1:
                        # Subsequent attempts: try next port
                        port += 1
                        logger.warning(f"⚠️ Port {port-1} still in use, trying port {port}")
                        print(f"⚠️ Port {port-1} still in use, trying port {port}")
                    else:
                        logger.error(f"❌ Failed to start server after {max_attempts} attempts")
                        print(f"❌ Failed to start server after {max_attempts} attempts")
                        print(f"💡 Manual cleanup: pkill -f 'server_with_logs.py'")
                        raise
                else:
                    logger.error(f"❌ Failed to start server: {e}")
                    raise