"""
Environment Configuration for CrewAI-Myndy Integration

This module handles loading environment variables and managing paths
for the CrewAI-Myndy integration system.

File: config/env_config.py
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
def load_env_file(env_path: Optional[Path] = None) -> None:
    """Load environment variables from .env file."""
    if env_path is None:
        env_path = Path(__file__).parent.parent.parent / ".env"
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value

# Load the .env file
load_env_file()

class EnvConfig:
    """Environment configuration manager."""
    
    @property
    def myndy_path(self) -> Path:
        """Get the Myndy-AI path from environment."""
        path_str = os.getenv('MYNDY_PATH', '/Users/jeremy/myndy-core/myndy-ai')
        return Path(path_str)
    
    @property
    def qdrant_host(self) -> str:
        """Get Qdrant host from environment."""
        return os.getenv('QDRANT_HOST', 'localhost')
    
    @property
    def qdrant_port(self) -> int:
        """Get Qdrant port from environment."""
        return int(os.getenv('QDRANT_PORT', '6333'))
    
    @property
    def qdrant_grpc_port(self) -> int:
        """Get Qdrant gRPC port from environment."""
        return int(os.getenv('QDRANT_GRPC_PORT', '6334'))
    
    @property
    def default_model(self) -> str:
        """Get default model from environment."""
        return os.getenv('MEMEX_DEFAULT_MODEL', 'llama3.2')
    
    @property
    def verbose_logging(self) -> bool:
        """Get verbose logging setting from environment."""
        return os.getenv('MYNDY_VERBOSE', 'false').lower() == 'true'
    
    @property
    def colored_logs(self) -> bool:
        """Get colored logs setting from environment."""
        return os.getenv('MYNDY_COLORED_LOGS', 'true').lower() == 'true'
    
    @property
    def myndy_api_base_url(self) -> str:
        """Get Myndy-AI FastAPI base URL from environment."""
        return os.getenv('MYNDY_API_BASE_URL', 'http://localhost:8081')
    
    @property
    def myndy_api_key(self) -> str:
        """Get Myndy-AI FastAPI key from environment."""
        return os.getenv('MYNDY_API_KEY', 'development-key-crewai-integration')
    
    @property
    def use_http_client(self) -> bool:
        """Whether to use HTTP client instead of direct imports."""
        return os.getenv('MYNDY_USE_HTTP_CLIENT', 'true').lower() == 'true'
    
    def setup_myndy_path(self) -> bool:
        """Add Myndy-AI path to sys.path if it exists."""
        myndy_path = self.myndy_path
        if myndy_path.exists():
            myndy_path_str = str(myndy_path)
            if myndy_path_str not in sys.path:
                sys.path.insert(0, myndy_path_str)
            return True
        else:
            return False
    
    def get_pipeline_host(self) -> str:
        """Get CrewAI pipeline host from environment."""
        return os.getenv('CREWAI_PIPELINE_HOST', '0.0.0.0')
    
    def get_pipeline_port(self) -> int:
        """Get CrewAI pipeline port from environment."""
        return int(os.getenv('CREWAI_PIPELINE_PORT', '9091'))
    
    def get_api_timeout(self) -> int:
        """Get API timeout from environment."""
        return int(os.getenv('CREWAI_API_TIMEOUT', '10'))

# Global instance
env_config = EnvConfig()