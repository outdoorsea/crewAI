#!/usr/bin/env python3
"""
OpenWebUI Pipeline Server for Myndy AI
Run with: python pipeline_server.py
Then add http://localhost:9099 to OpenWebUI pipelines
"""

import logging
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

# Import the pipeline
from pipeline import Pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Myndy AI Pipeline Server",
    description="OpenWebUI-compatible server for Myndy AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = Pipeline()

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Myndy AI Pipeline Server starting...")
    pipeline.on_startup()

@app.on_event("shutdown") 
async def shutdown_event():
    """Shutdown event"""
    logger.info("🛑 Myndy AI Pipeline Server shutting down...")
    pipeline.on_shutdown()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Myndy AI Pipeline Server",
        "version": pipeline.version,
        "status": "running",
        "pipeline_type": getattr(pipeline, 'pipeline_type', 'unknown')
    }

@app.get("/models")
async def get_models():
    """Get available models (OpenWebUI format)"""
    models = pipeline.get_models()
    return {"data": models}

@app.get("/v1/models")
async def get_models_v1():
    """Get available models (OpenAI format)"""
    models = pipeline.get_models()
    return {"data": models}

@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """Handle chat completion requests"""
    try:
        # Extract information from request
        messages = request.get("messages", [])
        model_id = request.get("model", "auto")
        
        # Get the last user message
        user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break
        
        logger.info(f"💬 Chat request: model={model_id}, message='{user_message[:50]}...'")
        
        # Process through pipeline
        response = pipeline.pipe(
            user_message=user_message,
            model_id=model_id,
            messages=messages,
            body=request
        )
        
        # Return OpenAI-compatible response
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
                "completion_tokens": len(str(response).split()),
                "total_tokens": len(user_message.split()) + len(str(response).split())
            }
        }
    except Exception as e:
        logger.error(f"❌ Chat completion error: {e}")
        return {
            "error": {
                "message": str(e),
                "type": "pipeline_error",
                "code": "processing_failed"
            }
        }

if __name__ == "__main__":
    print("🚀 Starting Myndy AI Pipeline Server")
    print("=" * 50)
    print("🌐 Server will be available at: http://localhost:9099")
    print("🔗 Add this URL to OpenWebUI pipelines")
    print("📊 Available models: 6 AI agents + auto-routing")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    # Test pipeline before starting server
    print("🧪 Testing pipeline...")
    models = pipeline.get_models()
    print(f"✅ Pipeline ready with {len(models)} models")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9099,
        log_level="info"
    )