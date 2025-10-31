"""
Shared Resource Manager for CrewAI Performance Optimization

This module provides centralized resource management for LLMs, tools, and agents
to optimize memory usage, reduce initialization overhead, and improve performance
across the entire CrewAI system.

File: core/shared_resource_manager.py
"""

import asyncio
import logging
import time
import threading
import weakref
from typing import Dict, Any, Optional, List, Set, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import json

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class ResourceMetrics:
    """Resource usage and performance metrics"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    creation_time: float = 0.0
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    memory_usage_mb: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0

@dataclass
class CachedResource(Generic[T]):
    """Wrapper for cached resources with metadata"""
    resource: T
    metrics: ResourceMetrics
    created_at: float = field(default_factory=time.time)
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if resource has expired based on TTL"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def update_access(self):
        """Update access metrics"""
        self.metrics.access_count += 1
        self.metrics.last_access = time.time()

class SharedResourceManager:
    """
    Centralized resource manager for LLMs, tools, and agents
    
    Features:
    - Singleton pattern for global access
    - Thread-safe resource caching
    - Memory usage tracking
    - Resource lifecycle management
    - Performance metrics collection
    - Automatic cleanup and garbage collection
    """
    
    _instance = None
    _lock = threading.RLock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not SharedResourceManager._initialized:
            # Resource caches
            self.llm_cache: Dict[str, CachedResource] = {}
            self.agent_cache: Dict[str, CachedResource] = {}
            self.tool_cache: Dict[str, CachedResource] = {}
            self.response_cache: Dict[str, CachedResource] = {}
            
            # Configuration
            self.max_cache_size = 1000
            self.default_ttl = 3600  # 1 hour
            self.cleanup_interval = 300  # 5 minutes
            
            # Concurrency control
            self.agent_semaphore = asyncio.Semaphore(10)
            self.llm_semaphore = asyncio.Semaphore(5)
            self.tool_semaphore = asyncio.Semaphore(20)
            
            # Performance tracking
            self.global_metrics = {
                "llm": ResourceMetrics(),
                "agent": ResourceMetrics(),
                "tool": ResourceMetrics(),
                "response": ResourceMetrics()
            }
            
            # Cleanup task
            self.cleanup_task = None
            self.running = True
            
            # Resource factories
            self.resource_factories: Dict[str, Callable] = {}
            
            SharedResourceManager._initialized = True
            logger.info("🔧 SharedResourceManager initialized")
            self._start_cleanup_task()
    
    def register_factory(self, resource_type: str, factory_func: Callable) -> None:
        """Register a factory function for creating resources"""
        self.resource_factories[resource_type] = factory_func
        logger.debug(f"Registered factory for {resource_type}")
    
    def _create_cache_key(self, *args, **kwargs) -> str:
        """Create deterministic cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _evict_lru(self, cache: Dict[str, CachedResource], max_size: int):
        """Evict least recently used items from cache"""
        if len(cache) <= max_size:
            return
            
        # Sort by last access time and remove oldest
        sorted_items = sorted(
            cache.items(), 
            key=lambda x: x[1].metrics.last_access
        )
        
        items_to_remove = len(cache) - max_size
        for i in range(items_to_remove):
            key, resource = sorted_items[i]
            del cache[key]
            logger.debug(f"Evicted LRU resource: {key[:8]}...")
    
    def _cleanup_expired(self, cache: Dict[str, CachedResource]) -> int:
        """Remove expired resources from cache"""
        expired_keys = [
            key for key, resource in cache.items()
            if resource.is_expired()
        ]
        
        for key in expired_keys:
            del cache[key]
        
        return len(expired_keys)
    
    async def get_llm(self, model_name: str, **config) -> Any:
        """Get or create LLM instance with caching"""
        cache_key = self._create_cache_key("llm", model_name, **config)
        
        async with self.llm_semaphore:
            # Check cache first
            if cache_key in self.llm_cache:
                cached = self.llm_cache[cache_key]
                if not cached.is_expired():
                    cached.update_access()
                    self.global_metrics["llm"].cache_hits += 1
                    logger.debug(f"LLM cache hit: {model_name}")
                    return cached.resource
                else:
                    del self.llm_cache[cache_key]
            
            # Create new LLM instance
            self.global_metrics["llm"].cache_misses += 1
            start_time = time.time()
            
            try:
                # Use factory if registered
                if "llm" in self.resource_factories:
                    llm = await self._call_factory("llm", model_name, **config)
                else:
                    # Fallback to default LLM creation
                    llm = await self._create_default_llm(model_name, **config)
                
                creation_time = time.time() - start_time
                
                # Cache the LLM
                metrics = ResourceMetrics(creation_time=creation_time)
                cached_llm = CachedResource(
                    resource=llm,
                    metrics=metrics,
                    ttl=self.default_ttl
                )
                
                self.llm_cache[cache_key] = cached_llm
                self._evict_lru(self.llm_cache, self.max_cache_size)
                
                logger.info(f"✅ Created and cached LLM: {model_name} in {creation_time:.3f}s")
                return llm
                
            except Exception as e:
                logger.error(f"❌ Failed to create LLM {model_name}: {e}")
                raise
    
    async def get_agent(self, agent_role: str, **config) -> Any:
        """Get or create agent instance with caching"""
        cache_key = self._create_cache_key("agent", agent_role, **config)
        
        async with self.agent_semaphore:
            # Check cache first
            if cache_key in self.agent_cache:
                cached = self.agent_cache[cache_key]
                if not cached.is_expired():
                    cached.update_access()
                    self.global_metrics["agent"].cache_hits += 1
                    logger.debug(f"Agent cache hit: {agent_role}")
                    return cached.resource
                else:
                    del self.agent_cache[cache_key]
            
            # Create new agent instance
            self.global_metrics["agent"].cache_misses += 1
            start_time = time.time()
            
            try:
                # Use factory if registered
                if "agent" in self.resource_factories:
                    agent = await self._call_factory("agent", agent_role, **config)
                else:
                    # Fallback to default agent creation
                    agent = await self._create_default_agent(agent_role, **config)
                
                creation_time = time.time() - start_time
                
                # Cache the agent
                metrics = ResourceMetrics(creation_time=creation_time)
                cached_agent = CachedResource(
                    resource=agent,
                    metrics=metrics,
                    ttl=self.default_ttl
                )
                
                self.agent_cache[cache_key] = cached_agent
                self._evict_lru(self.agent_cache, self.max_cache_size)
                
                logger.info(f"✅ Created and cached agent: {agent_role} in {creation_time:.3f}s")
                return agent
                
            except Exception as e:
                logger.error(f"❌ Failed to create agent {agent_role}: {e}")
                raise
    
    async def get_tool(self, tool_name: str, **config) -> Any:
        """Get or create tool instance with caching"""
        cache_key = self._create_cache_key("tool", tool_name, **config)
        
        async with self.tool_semaphore:
            # Check cache first
            if cache_key in self.tool_cache:
                cached = self.tool_cache[cache_key]
                if not cached.is_expired():
                    cached.update_access()
                    self.global_metrics["tool"].cache_hits += 1
                    logger.debug(f"Tool cache hit: {tool_name}")
                    return cached.resource
                else:
                    del self.tool_cache[cache_key]
            
            # Create new tool instance
            self.global_metrics["tool"].cache_misses += 1
            start_time = time.time()
            
            try:
                # Use factory if registered
                if "tool" in self.resource_factories:
                    tool = await self._call_factory("tool", tool_name, **config)
                else:
                    # Fallback to default tool creation
                    tool = await self._create_default_tool(tool_name, **config)
                
                creation_time = time.time() - start_time
                
                # Cache the tool
                metrics = ResourceMetrics(creation_time=creation_time)
                cached_tool = CachedResource(
                    resource=tool,
                    metrics=metrics,
                    ttl=self.default_ttl
                )
                
                self.tool_cache[cache_key] = cached_tool
                self._evict_lru(self.tool_cache, self.max_cache_size)
                
                logger.debug(f"✅ Created and cached tool: {tool_name} in {creation_time:.3f}s")
                return tool
                
            except Exception as e:
                logger.error(f"❌ Failed to create tool {tool_name}: {e}")
                raise
    
    def cache_response(self, key: str, response: Any, ttl: Optional[float] = None) -> None:
        """Cache response with optional TTL"""
        with self._lock:
            metrics = ResourceMetrics()
            cached_response = CachedResource(
                resource=response,
                metrics=metrics,
                ttl=ttl or self.default_ttl
            )
            
            self.response_cache[key] = cached_response
            self._evict_lru(self.response_cache, self.max_cache_size)
    
    def get_cached_response(self, key: str) -> Optional[Any]:
        """Get cached response if valid"""
        with self._lock:
            if key in self.response_cache:
                cached = self.response_cache[key]
                if not cached.is_expired():
                    cached.update_access()
                    self.global_metrics["response"].cache_hits += 1
                    return cached.resource
                else:
                    del self.response_cache[key]
            
            self.global_metrics["response"].cache_misses += 1
            return None
    
    async def _call_factory(self, resource_type: str, *args, **kwargs) -> Any:
        """Call registered factory function"""
        factory = self.resource_factories[resource_type]
        if asyncio.iscoroutinefunction(factory):
            return await factory(*args, **kwargs)
        else:
            # Run in thread pool for sync factories
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, factory, *args)
    
    async def _create_default_llm(self, model_name: str, **config) -> Any:
        """Default LLM creation fallback"""
        # This is a placeholder - implement based on your LLM framework
        logger.warning(f"Using default LLM creation for {model_name}")
        
        # Import here to avoid circular imports
        try:
            from config.llm_config import get_agent_llm
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, get_agent_llm, model_name)
        except ImportError:
            logger.error("No LLM factory registered and default creation failed")
            return None
    
    async def _create_default_agent(self, agent_role: str, **config) -> Any:
        """Default agent creation fallback"""
        # This is a placeholder - implement based on your agent framework
        logger.warning(f"Using default agent creation for {agent_role}")
        
        try:
            from agents.simple_agents import create_simple_agents
            loop = asyncio.get_event_loop()
            agents = await loop.run_in_executor(None, create_simple_agents)
            return agents.get(agent_role) if agents else None
        except ImportError:
            logger.error("No agent factory registered and default creation failed")
            return None
    
    async def _create_default_tool(self, tool_name: str, **config) -> Any:
        """Default tool creation fallback"""
        # This is a placeholder - implement based on your tool framework
        logger.warning(f"Using default tool creation for {tool_name}")
        
        try:
            from tools.myndy_bridge import get_agent_tools
            tools = get_agent_tools("general")
            for tool in tools:
                if hasattr(tool, 'name') and tool.name == tool_name:
                    return tool
            return None
        except ImportError:
            logger.error("No tool factory registered and default creation failed")
            return None
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        try:
            loop = asyncio.get_event_loop()
            self.cleanup_task = loop.create_task(self._cleanup_loop())
        except RuntimeError:
            # No event loop running, cleanup will be manual
            logger.warning("No event loop for cleanup task, manual cleanup required")
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while self.running:
            try:
                # Cleanup expired resources
                expired_llms = self._cleanup_expired(self.llm_cache)
                expired_agents = self._cleanup_expired(self.agent_cache)
                expired_tools = self._cleanup_expired(self.tool_cache)
                expired_responses = self._cleanup_expired(self.response_cache)
                
                total_expired = expired_llms + expired_agents + expired_tools + expired_responses
                if total_expired > 0:
                    logger.debug(f"🧹 Cleaned up {total_expired} expired resources")
                
                # Wait before next cleanup
                await asyncio.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(self.cleanup_interval)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        with self._lock:
            cache_sizes = {
                "llm_cache": len(self.llm_cache),
                "agent_cache": len(self.agent_cache),
                "tool_cache": len(self.tool_cache),
                "response_cache": len(self.response_cache)
            }
            
            cache_hit_rates = {
                f"{name}_hit_rate": metrics.hit_rate
                for name, metrics in self.global_metrics.items()
            }
            
            total_memory_mb = sum(
                sum(res.metrics.memory_usage_mb for res in cache.values())
                for cache in [self.llm_cache, self.agent_cache, self.tool_cache, self.response_cache]
            )
            
            return {
                "cache_sizes": cache_sizes,
                "cache_hit_rates": cache_hit_rates,
                "global_metrics": {
                    name: {
                        "total_requests": metrics.total_requests,
                        "cache_hits": metrics.cache_hits,
                        "cache_misses": metrics.cache_misses,
                        "hit_rate": round(metrics.hit_rate, 2)
                    }
                    for name, metrics in self.global_metrics.items()
                },
                "resource_utilization": {
                    "total_memory_mb": round(total_memory_mb, 2),
                    "max_cache_size": self.max_cache_size,
                    "cache_utilization": round(sum(cache_sizes.values()) / (self.max_cache_size * 4) * 100, 2)
                },
                "configuration": {
                    "default_ttl": self.default_ttl,
                    "cleanup_interval": self.cleanup_interval,
                    "max_concurrent_agents": self.agent_semaphore._value,
                    "max_concurrent_llms": self.llm_semaphore._value,
                    "max_concurrent_tools": self.tool_semaphore._value
                }
            }
    
    def clear_cache(self, cache_type: Optional[str] = None):
        """Clear specific cache or all caches"""
        with self._lock:
            if cache_type == "llm" or cache_type is None:
                cleared_llms = len(self.llm_cache)
                self.llm_cache.clear()
                if cleared_llms > 0:
                    logger.info(f"🗑️ Cleared {cleared_llms} LLM cache entries")
            
            if cache_type == "agent" or cache_type is None:
                cleared_agents = len(self.agent_cache)
                self.agent_cache.clear()
                if cleared_agents > 0:
                    logger.info(f"🗑️ Cleared {cleared_agents} agent cache entries")
            
            if cache_type == "tool" or cache_type is None:
                cleared_tools = len(self.tool_cache)
                self.tool_cache.clear()
                if cleared_tools > 0:
                    logger.info(f"🗑️ Cleared {cleared_tools} tool cache entries")
            
            if cache_type == "response" or cache_type is None:
                cleared_responses = len(self.response_cache)
                self.response_cache.clear()
                if cleared_responses > 0:
                    logger.info(f"🗑️ Cleared {cleared_responses} response cache entries")
    
    def shutdown(self):
        """Shutdown resource manager and cleanup"""
        self.running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Clear all caches
        self.clear_cache()
        
        logger.info("🔌 SharedResourceManager shutdown complete")

# Global instance
_resource_manager = None

def get_resource_manager() -> SharedResourceManager:
    """Get the global shared resource manager instance"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = SharedResourceManager()
    return _resource_manager

# Convenience functions
async def get_shared_llm(model_name: str, **config) -> Any:
    """Get shared LLM instance"""
    return await get_resource_manager().get_llm(model_name, **config)

async def get_shared_agent(agent_role: str, **config) -> Any:
    """Get shared agent instance"""
    return await get_resource_manager().get_agent(agent_role, **config)

async def get_shared_tool(tool_name: str, **config) -> Any:
    """Get shared tool instance"""
    return await get_resource_manager().get_tool(tool_name, **config)

def cache_shared_response(key: str, response: Any, ttl: Optional[float] = None):
    """Cache response in shared cache"""
    get_resource_manager().cache_response(key, response, ttl)

def get_shared_response(key: str) -> Optional[Any]:
    """Get cached response from shared cache"""
    return get_resource_manager().get_cached_response(key)

def get_shared_metrics() -> Dict[str, Any]:
    """Get shared resource manager metrics"""
    return get_resource_manager().get_performance_metrics()

def register_shared_factory(resource_type: str, factory_func: Callable):
    """Register factory function for resource creation"""
    get_resource_manager().register_factory(resource_type, factory_func)

# Cleanup function for graceful shutdown
import atexit

def cleanup_shared_resources():
    """Cleanup function for graceful shutdown"""
    global _resource_manager
    if _resource_manager:
        _resource_manager.shutdown()
        _resource_manager = None

atexit.register(cleanup_shared_resources)

if __name__ == "__main__":
    # Test the shared resource manager
    import asyncio
    
    async def test_resource_manager():
        rm = get_resource_manager()
        
        # Test metrics
        metrics = rm.get_performance_metrics()
        print("📊 Resource Manager Test")
        print("=" * 25)
        print(f"Cache sizes: {metrics['cache_sizes']}")
        print(f"Configuration: {metrics['configuration']}")
        
        # Test caching
        cache_shared_response("test_key", {"test": "data"}, 60)
        cached = get_shared_response("test_key")
        print(f"Cache test: {cached}")
        
        print("✅ Shared Resource Manager test complete")
    
    asyncio.run(test_resource_manager())