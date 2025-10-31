"""
Async HTTP Client for CrewAI Performance Optimization

This module provides high-performance async HTTP client with connection pooling
for communication with myndy-ai API backend.

File: tools/async_http_client.py
"""

import aiohttp
import asyncio
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HTTPMetrics:
    """HTTP performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_errors: int = 0
    connection_errors: int = 0
    total_response_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def average_response_time(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests

class AsyncHTTPClient:
    """High-performance async HTTP client with connection pooling"""
    
    _instance = None
    _session = None
    _metrics = HTTPMetrics()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, base_url: str = None):
        # Use environment configuration for base URL
        if base_url is None:
            try:
                from ..config.env_config import env_config
                base_url = env_config.myndy_api_base_url
            except ImportError:
                import os
                base_url = os.getenv("CREWAI_MYNDY_API_URL", "http://localhost:8081")
        if self._session is None:
            self.base_url = base_url
            # Don't initialize session immediately - use lazy initialization
            self._initialized = False
    
    def _initialize_session(self):
        """Initialize aiohttp session with optimized connection pooling"""
        # Connection pooling configuration
        connector = aiohttp.TCPConnector(
            limit=100,              # Total connection pool size
            limit_per_host=30,      # Per-host connection limit
            ttl_dns_cache=300,      # DNS cache TTL (5 minutes)
            use_dns_cache=True,
            keepalive_timeout=300,  # Keep connections alive for 5 minutes
            enable_cleanup_closed=True,
            force_close=False,      # Reuse connections
            ssl=False               # No SSL for localhost
        )
        
        # Timeout configuration - much more aggressive than before
        timeout = aiohttp.ClientTimeout(
            total=10,       # Total timeout reduced from 30s
            connect=3,      # Connection timeout
            sock_read=5,    # Socket read timeout
            sock_connect=3  # Socket connect timeout
        )
        
        # Session configuration
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "CrewAI-ToolBridge/2.0-Optimized",
                "Connection": "keep-alive"
            },
            # Enable response compression
            auto_decompress=True,
            # Configure connection limits
            connector_owner=True
        )
        
        logger.info("✅ Async HTTP client initialized with connection pooling")
        logger.info(f"📊 Pool config: {connector.limit} total, {connector.limit_per_host} per host")
    
    async def _ensure_initialized(self):
        """Ensure session is initialized (lazy initialization)"""
        if not hasattr(self, '_initialized') or not self._initialized:
            self._initialize_session()
            self._initialized = True

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """High-performance async POST request with metrics"""
        await self._ensure_initialized()
        
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        # Update metrics
        self._metrics.total_requests += 1
        
        try:
            async with self._session.post(url, json=data) as response:
                response_time = time.time() - start_time
                self._metrics.total_response_time += response_time
                
                if response.status == 200:
                    self._metrics.successful_requests += 1
                    result = await response.json()
                    
                    logger.debug(f"✅ HTTP POST {endpoint} - {response.status} in {response_time:.3f}s")
                    return result
                else:
                    self._metrics.failed_requests += 1
                    error_text = await response.text()
                    
                    logger.warning(f"❌ HTTP POST {endpoint} - {response.status}: {error_text}")
                    return {
                        "error": f"HTTP {response.status}: {response.reason}",
                        "details": error_text,
                        "fallback_used": True
                    }
                    
        except asyncio.TimeoutError:
            self._metrics.timeout_errors += 1
            self._metrics.failed_requests += 1
            response_time = time.time() - start_time
            
            logger.warning(f"⏰ HTTP POST {endpoint} - Timeout after {response_time:.3f}s")
            return {
                "error": "Request timeout", 
                "timeout": response_time,
                "fallback_used": True
            }
            
        except aiohttp.ClientConnectionError as e:
            self._metrics.connection_errors += 1
            self._metrics.failed_requests += 1
            response_time = time.time() - start_time
            
            logger.error(f"🔌 HTTP POST {endpoint} - Connection error: {e}")
            return {
                "error": f"Connection error: {str(e)}", 
                "fallback_used": True
            }
            
        except Exception as e:
            self._metrics.failed_requests += 1
            response_time = time.time() - start_time
            
            logger.error(f"💥 HTTP POST {endpoint} - Unexpected error: {e}")
            return {
                "error": f"Request failed: {str(e)}", 
                "fallback_used": True
            }
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """High-performance async GET request"""
        await self._ensure_initialized()
        
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        self._metrics.total_requests += 1
        
        try:
            async with self._session.get(url, params=params) as response:
                response_time = time.time() - start_time
                self._metrics.total_response_time += response_time
                
                if response.status == 200:
                    self._metrics.successful_requests += 1
                    result = await response.json()
                    
                    logger.debug(f"✅ HTTP GET {endpoint} - {response.status} in {response_time:.3f}s")
                    return result
                else:
                    self._metrics.failed_requests += 1
                    error_text = await response.text()
                    
                    logger.warning(f"❌ HTTP GET {endpoint} - {response.status}: {error_text}")
                    return {
                        "error": f"HTTP {response.status}: {response.reason}",
                        "details": error_text,
                        "fallback_used": True
                    }
                    
        except Exception as e:
            self._metrics.failed_requests += 1
            logger.error(f"💥 HTTP GET {endpoint} - Error: {e}")
            return {"error": f"Request failed: {str(e)}", "fallback_used": True}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get HTTP client performance metrics"""
        return {
            "total_requests": self._metrics.total_requests,
            "successful_requests": self._metrics.successful_requests,
            "failed_requests": self._metrics.failed_requests,
            "success_rate": round(self._metrics.success_rate, 2),
            "timeout_errors": self._metrics.timeout_errors,
            "connection_errors": self._metrics.connection_errors,
            "average_response_time": round(self._metrics.average_response_time, 3),
            "total_response_time": round(self._metrics.total_response_time, 3)
        }
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self._metrics = HTTPMetrics()
        logger.info("📊 HTTP metrics reset")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check HTTP client and connection health"""
        try:
            await self._ensure_initialized()
            start_time = time.time()
            result = await self.get("/api/v1/status/")
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": round(response_time, 3),
                "connection_pool": {
                    "total_connections": self._session.connector.limit,
                    "per_host_limit": self._session.connector.limit_per_host,
                    "keepalive_timeout": self._session.connector.keepalive_timeout
                },
                "metrics": self.get_metrics()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "metrics": self.get_metrics()
            }
    
    async def close(self):
        """Close the HTTP session and connections"""
        if self._session:
            await self._session.close()
            logger.info("🔌 HTTP client connections closed")

# Global client instance - singleton pattern (lazy initialization)
http_client = None

def get_http_client() -> AsyncHTTPClient:
    """Get or create the global HTTP client instance"""
    global http_client
    if http_client is None:
        http_client = AsyncHTTPClient()
    return http_client

# Convenience functions for backward compatibility
async def async_post(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for async POST requests"""
    client = get_http_client()
    return await client.post(endpoint, data)

async def async_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function for async GET requests"""
    client = get_http_client()
    return await client.get(endpoint, params)

def get_http_metrics() -> Dict[str, Any]:
    """Get global HTTP client metrics"""
    client = get_http_client()
    return client.get_metrics()

# Graceful shutdown support
import atexit

def cleanup_http_client():
    """Cleanup function for graceful shutdown"""
    global http_client
    if http_client is not None:
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.run_until_complete(http_client.close())
        except:
            pass

atexit.register(cleanup_http_client)