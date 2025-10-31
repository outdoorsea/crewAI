"""
Production Server for CrewAI-Myndy OpenAPI

Enhanced server with Open WebUI compatibility and production features.

File: api/server.py
"""

import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Add myndy to path
MYNDY_PATH = Path("/Users/jeremy/myndy")
sys.path.insert(0, str(MYNDY_PATH))

from api.main import app
from api.openapi_extensions import add_openai_compatibility

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_production_app() -> FastAPI:
    """Create the production FastAPI application."""
    
    # Add OpenAI compatibility for Open WebUI
    app_with_extensions = add_openai_compatibility(app)
    
    # Update CORS for production
    app_with_extensions.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Open WebUI default
            "http://localhost:8080",  # Alternative Open WebUI port
            "http://localhost:8000",  # API server
            "*"  # Allow all for development - restrict in production
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    return app_with_extensions

def main():
    """Run the production server."""
    production_app = create_production_app()
    
    logger.info("Starting CrewAI-Myndy OpenAPI Server")
    logger.info("Compatible with Open WebUI and other front-ends")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("OpenAPI Spec: http://localhost:8000/openapi.json")
    
    uvicorn.run(
        production_app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        reload=False  # Set to True for development
    )

if __name__ == "__main__":
    main()