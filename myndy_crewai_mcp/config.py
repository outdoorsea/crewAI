"""
MCP Server Configuration

Configuration management for the MCP server including environment variables,
server settings, and transport configuration.

File: mcp/config.py
"""

import os
import logging
from typing import Optional, Literal
from pydantic import BaseModel, Field
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPConfig(BaseModel):
    """Configuration for MCP server"""

    # Server Identity
    server_name: str = Field(
        default="myndy-crewai-mcp",
        description="MCP server name"
    )
    server_version: str = Field(
        default="0.1.0",
        description="MCP server version"
    )

    # Myndy-AI Backend Configuration
    myndy_api_url: str = Field(
        default_factory=lambda: os.getenv("MYNDY_API_URL", "http://localhost:8000"),
        description="Myndy-AI backend API URL"
    )
    myndy_api_timeout: int = Field(
        default=30,
        description="Timeout for myndy-ai API calls in seconds"
    )

    # Transport Configuration
    transport_type: Literal["stdio", "sse", "http"] = Field(
        default="sse",
        description="Transport layer type (sse for web-based LibreChat)"
    )

    # HTTP Transport Settings (if using HTTP)
    http_host: str = Field(
        default="0.0.0.0",
        description="HTTP server host"
    )
    http_port: int = Field(
        default=9092,
        description="HTTP server port"
    )

    # Logging Configuration
    log_level: str = Field(
        default_factory=lambda: os.getenv("MCP_LOG_LEVEL", "INFO"),
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    log_file: Optional[Path] = Field(
        default=None,
        description="Optional log file path"
    )

    # Feature Flags
    enable_tools: bool = Field(
        default=True,
        description="Enable tool execution"
    )
    enable_resources: bool = Field(
        default=True,
        description="Enable resource access"
    )
    enable_prompts: bool = Field(
        default=True,
        description="Enable prompt templates"
    )

    # Performance Settings
    max_concurrent_requests: int = Field(
        default=50,
        description="Maximum concurrent MCP requests"
    )
    request_timeout: int = Field(
        default=120,
        description="Maximum time for a single request in seconds"
    )

    # Cache Settings
    enable_cache: bool = Field(
        default=True,
        description="Enable tool result caching"
    )
    cache_ttl: int = Field(
        default=300,
        description="Cache TTL in seconds"
    )

    # Security Settings
    require_authentication: bool = Field(
        default=False,
        description="Require authentication for MCP requests"
    )
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("MCP_API_KEY"),
        description="Optional API key for authentication"
    )

    # Development Settings
    debug_mode: bool = Field(
        default_factory=lambda: os.getenv("MCP_DEBUG", "false").lower() == "true",
        description="Enable debug mode"
    )
    verbose: bool = Field(
        default_factory=lambda: os.getenv("MCP_VERBOSE", "false").lower() == "true",
        description="Enable verbose logging"
    )

    class Config:
        """Pydantic config"""
        env_prefix = "MCP_"
        case_sensitive = False

    def configure_logging(self):
        """Configure logging based on settings"""
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)

        handlers = []

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

        # File handler (if specified)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)

        # Configure root logger
        logging.basicConfig(
            level=log_level,
            handlers=handlers,
            force=True
        )

        # Set debug mode for MCP components
        if self.debug_mode:
            logging.getLogger("mcp").setLevel(logging.DEBUG)
            logging.getLogger("myndy_mcp").setLevel(logging.DEBUG)

        logger.info(f"=' MCP Server logging configured: {self.log_level}")
        if self.debug_mode:
            logger.debug("= Debug mode enabled")
        if self.verbose:
            logger.debug("=� Verbose mode enabled")

    def validate_config(self) -> bool:
        """Validate configuration settings"""
        issues = []

        # Validate myndy-ai URL
        if not self.myndy_api_url.startswith("http"):
            issues.append(f"Invalid myndy_api_url: {self.myndy_api_url}")

        # Validate port range
        if not (1024 <= self.http_port <= 65535):
            issues.append(f"Invalid http_port: {self.http_port}")

        # Validate timeouts
        if self.myndy_api_timeout <= 0:
            issues.append(f"Invalid myndy_api_timeout: {self.myndy_api_timeout}")

        if self.request_timeout <= 0:
            issues.append(f"Invalid request_timeout: {self.request_timeout}")

        # Log issues
        if issues:
            for issue in issues:
                logger.error(f"L Configuration error: {issue}")
            return False

        logger.info(" Configuration validated successfully")
        return True

    def get_server_info(self) -> dict:
        """Get server information for capability negotiation"""
        return {
            "name": self.server_name,
            "version": self.server_version,
            "capabilities": {
                "tools": self.enable_tools,
                "resources": self.enable_resources,
                "prompts": self.enable_prompts,
            }
        }


# Global configuration instance
_config: Optional[MCPConfig] = None


def get_config() -> MCPConfig:
    """Get the global MCP configuration instance"""
    global _config
    if _config is None:
        _config = MCPConfig()
        _config.configure_logging()
        _config.validate_config()
    return _config


def set_config(config: MCPConfig):
    """Set the global MCP configuration instance"""
    global _config
    _config = config
    _config.configure_logging()
    _config.validate_config()


def reset_config():
    """Reset configuration to defaults (useful for testing)"""
    global _config
    _config = None


# Convenience function to get config values
def get_myndy_api_url() -> str:
    """Get Myndy-AI backend URL"""
    return get_config().myndy_api_url


def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return get_config().debug_mode


def is_verbose_mode() -> bool:
    """Check if verbose mode is enabled"""
    return get_config().verbose
