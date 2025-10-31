"""
Tool Result Caching System for CrewAI Performance Optimization

This module provides high-performance caching for tool execution results
with TTL (Time To Live) and LRU (Least Recently Used) eviction policies.

File: tools/tool_cache.py
"""

import hashlib
import json
import time
import asyncio
import logging
from typing import Dict, Any, Optional, Set, Tuple, List
from dataclasses import dataclass, field
from functools import wraps
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    size_bytes: int = 0
    
    def __post_init__(self):
        # Estimate size in bytes
        try:
            self.size_bytes = len(json.dumps(self.value, default=str).encode('utf-8'))
        except:
            self.size_bytes = 1024  # Default estimate

@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    average_access_time: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100
    
    @property
    def miss_rate(self) -> float:
        return 100.0 - self.hit_rate

class ToolResultCache:
    """High-performance tool result cache with TTL and LRU eviction"""
    
    def __init__(self, 
                 max_size: int = 1000,
                 ttl_seconds: int = 300,
                 max_memory_mb: int = 100,
                 cleanup_interval: int = 60):
        """
        Initialize cache with configuration
        
        Args:
            max_size: Maximum number of cache entries
            ttl_seconds: Time to live for cache entries (seconds)
            max_memory_mb: Maximum memory usage in MB
            cleanup_interval: Cleanup interval in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cleanup_interval = cleanup_interval
        
        # LRU cache implementation
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()
        self._lock = threading.RLock()
        
        # Cache key tracking
        self._tool_keys: Dict[str, Set[str]] = {}  # tool_name -> set of cache keys
        
        # Background cleanup
        self._cleanup_task = None
        self._running = True
        
        logger.info(f"🔧 Tool cache initialized: max_size={max_size}, ttl={ttl_seconds}s, max_memory={max_memory_mb}MB")
    
    def _create_cache_key(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Create deterministic cache key from tool name and parameters"""
        # Sort parameters to ensure consistent key generation
        sorted_params = json.dumps(parameters, sort_keys=True, default=str)
        key_data = f"{tool_name}:{sorted_params}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        return (time.time() - entry.timestamp) > self.ttl_seconds
    
    def _evict_lru(self):
        """Evict least recently used entries"""
        with self._lock:
            while len(self._cache) >= self.max_size:
                # Remove oldest entry (LRU)
                key, entry = self._cache.popitem(last=False)
                self._stats.evictions += 1
                self._stats.total_size_bytes -= entry.size_bytes
                
                # Update tool key tracking
                for tool_name, keys in self._tool_keys.items():
                    if key in keys:
                        keys.discard(key)
                        break
                
                logger.debug(f"🗑️ LRU evicted cache entry: {key[:8]}...")
    
    def _evict_by_memory(self):
        """Evict entries if memory limit exceeded"""
        with self._lock:
            while self._stats.total_size_bytes > self.max_memory_bytes and self._cache:
                # Remove oldest entry
                key, entry = self._cache.popitem(last=False)
                self._stats.evictions += 1
                self._stats.total_size_bytes -= entry.size_bytes
                
                # Update tool key tracking
                for tool_name, keys in self._tool_keys.items():
                    if key in keys:
                        keys.discard(key)
                        break
                
                logger.debug(f"💾 Memory evicted cache entry: {key[:8]}...")
    
    def get(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Any]:
        """Get cached result if valid"""
        cache_key = self._create_cache_key(tool_name, parameters)
        start_time = time.time()
        
        with self._lock:
            self._stats.total_requests += 1
            
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                
                # Check if expired
                if self._is_expired(entry):
                    del self._cache[cache_key]
                    self._stats.cache_misses += 1
                    self._stats.total_size_bytes -= entry.size_bytes
                    logger.debug(f"⏰ Cache entry expired: {tool_name}")
                    return None
                
                # Move to end (most recently used)
                self._cache.move_to_end(cache_key)
                
                # Update access metadata
                entry.access_count += 1
                entry.last_access = time.time()
                
                # Update stats
                self._stats.cache_hits += 1
                access_time = time.time() - start_time
                self._stats.average_access_time = (
                    (self._stats.average_access_time * (self._stats.cache_hits - 1) + access_time) 
                    / self._stats.cache_hits
                )
                
                logger.debug(f"✅ Cache hit: {tool_name} ({access_time:.3f}s)")
                return entry.value
            
            self._stats.cache_misses += 1
            logger.debug(f"❌ Cache miss: {tool_name}")
            return None
    
    def set(self, tool_name: str, parameters: Dict[str, Any], result: Any):
        """Cache tool result with timestamp"""
        cache_key = self._create_cache_key(tool_name, parameters)
        
        with self._lock:
            # Create cache entry
            entry = CacheEntry(
                value=result,
                timestamp=time.time()
            )
            
            # Evict if necessary
            self._evict_lru()
            
            # Store entry
            self._cache[cache_key] = entry
            self._stats.total_size_bytes += entry.size_bytes
            
            # Track tool keys
            if tool_name not in self._tool_keys:
                self._tool_keys[tool_name] = set()
            self._tool_keys[tool_name].add(cache_key)
            
            # Check memory limit
            self._evict_by_memory()
            
            logger.debug(f"💾 Cached result: {tool_name} ({entry.size_bytes} bytes)")
    
    def invalidate_tool(self, tool_name: str):
        """Invalidate all cached results for a specific tool"""
        with self._lock:
            if tool_name in self._tool_keys:
                keys_to_remove = list(self._tool_keys[tool_name])
                for key in keys_to_remove:
                    if key in self._cache:
                        entry = self._cache[key]
                        del self._cache[key]
                        self._stats.total_size_bytes -= entry.size_bytes
                        self._stats.evictions += 1
                
                self._tool_keys[tool_name].clear()
                logger.info(f"🗑️ Invalidated {len(keys_to_remove)} cache entries for tool: {tool_name}")
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            entry_count = len(self._cache)
            self._cache.clear()
            self._tool_keys.clear()
            self._stats.total_size_bytes = 0
            self._stats.evictions += entry_count
            
            logger.info(f"🗑️ Cache cleared: {entry_count} entries removed")
    
    def cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            current_time = time.time()
            expired_keys = []
            
            for key, entry in self._cache.items():
                if (current_time - entry.timestamp) > self.ttl_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                entry = self._cache[key]
                del self._cache[key]
                self._stats.total_size_bytes -= entry.size_bytes
                self._stats.evictions += 1
                
                # Update tool key tracking
                for tool_name, keys in self._tool_keys.items():
                    if key in keys:
                        keys.discard(key)
                        break
            
            if expired_keys:
                logger.debug(f"🧹 Cleanup removed {len(expired_keys)} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        with self._lock:
            return {
                "cache_performance": {
                    "total_requests": self._stats.total_requests,
                    "cache_hits": self._stats.cache_hits,
                    "cache_misses": self._stats.cache_misses,
                    "hit_rate": round(self._stats.hit_rate, 2),
                    "miss_rate": round(self._stats.miss_rate, 2),
                    "average_access_time": round(self._stats.average_access_time, 4)
                },
                "memory_usage": {
                    "total_entries": len(self._cache),
                    "max_entries": self.max_size,
                    "memory_usage_bytes": self._stats.total_size_bytes,
                    "memory_usage_mb": round(self._stats.total_size_bytes / 1024 / 1024, 2),
                    "max_memory_mb": self.max_memory_bytes // 1024 // 1024,
                    "memory_utilization": round((self._stats.total_size_bytes / self.max_memory_bytes) * 100, 2)
                },
                "eviction_stats": {
                    "total_evictions": self._stats.evictions,
                    "ttl_seconds": self.ttl_seconds
                },
                "tool_distribution": {
                    tool_name: len(keys) for tool_name, keys in self._tool_keys.items()
                }
            }
    
    def get_entry_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about cache entries"""
        with self._lock:
            entries = []
            for key, entry in self._cache.items():
                age = time.time() - entry.timestamp
                entries.append({
                    "cache_key": key[:8] + "...",
                    "age_seconds": round(age, 2),
                    "access_count": entry.access_count,
                    "size_bytes": entry.size_bytes,
                    "expired": self._is_expired(entry)
                })
            return sorted(entries, key=lambda x: x["age_seconds"], reverse=True)

# Global cache instance
_global_cache: Optional[ToolResultCache] = None

def get_tool_cache() -> ToolResultCache:
    """Get or create the global tool cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = ToolResultCache()
    return _global_cache

def configure_tool_cache(max_size: int = 1000, 
                        ttl_seconds: int = 300, 
                        max_memory_mb: int = 100) -> ToolResultCache:
    """Configure the global tool cache"""
    global _global_cache
    _global_cache = ToolResultCache(
        max_size=max_size,
        ttl_seconds=ttl_seconds,
        max_memory_mb=max_memory_mb
    )
    return _global_cache

def cached_tool(ttl: int = 300, 
               use_cache: bool = True,
               cache_key_func: Optional[callable] = None):
    """Decorator to cache tool execution results
    
    Args:
        ttl: Time to live in seconds (overrides global TTL for this tool)
        use_cache: Whether to use caching for this tool
        cache_key_func: Custom function to generate cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not use_cache:
                return func(*args, **kwargs)
            
            cache = get_tool_cache()
            tool_name = func.__name__
            
            # Create parameters dict
            params = kwargs.copy()
            if args:
                params['_args'] = args
            
            # Check cache first
            cached_result = cache.get(tool_name, params)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache the result
            cache.set(tool_name, params, result)
            
            logger.debug(f"🔧 Tool {tool_name} executed and cached in {execution_time:.3f}s")
            return result
        
        # Add cache management methods to the function
        wrapper.invalidate_cache = lambda: get_tool_cache().invalidate_tool(func.__name__)
        wrapper.get_cache_stats = lambda: get_tool_cache().get_stats()
        
        return wrapper
    return decorator

# Async version of the cached_tool decorator
def async_cached_tool(ttl: int = 300, use_cache: bool = True):
    """Async decorator to cache tool execution results"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not use_cache:
                return await func(*args, **kwargs)
            
            cache = get_tool_cache()
            tool_name = func.__name__
            
            # Create parameters dict
            params = kwargs.copy()
            if args:
                params['_args'] = args
            
            # Check cache first
            cached_result = cache.get(tool_name, params)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache the result
            cache.set(tool_name, params, result)
            
            logger.debug(f"🔧 Async tool {tool_name} executed and cached in {execution_time:.3f}s")
            return result
        
        # Add cache management methods
        async_wrapper.invalidate_cache = lambda: get_tool_cache().invalidate_tool(func.__name__)
        async_wrapper.get_cache_stats = lambda: get_tool_cache().get_stats()
        
        return async_wrapper
    return decorator

# Cache management utilities
class CacheManager:
    """Tool cache management utilities"""
    
    @staticmethod
    def get_global_stats() -> Dict[str, Any]:
        """Get global cache statistics"""
        return get_tool_cache().get_stats()
    
    @staticmethod
    def clear_all_cache():
        """Clear all cached results"""
        get_tool_cache().clear()
    
    @staticmethod
    def invalidate_tool(tool_name: str):
        """Invalidate cache for specific tool"""
        get_tool_cache().invalidate_tool(tool_name)
    
    @staticmethod
    def cleanup_expired():
        """Manually trigger cleanup of expired entries"""
        get_tool_cache().cleanup_expired()
    
    @staticmethod
    def get_cache_health() -> Dict[str, Any]:
        """Get cache health information"""
        stats = get_tool_cache().get_stats()
        
        hit_rate = stats["cache_performance"]["hit_rate"]
        memory_util = stats["memory_usage"]["memory_utilization"]
        
        # Determine health status
        if hit_rate > 70 and memory_util < 90:
            status = "healthy"
        elif hit_rate > 50 and memory_util < 95:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "hit_rate": hit_rate,
            "memory_utilization": memory_util,
            "recommendations": _get_cache_recommendations(stats)
        }
    
def _get_cache_recommendations(stats: Dict[str, Any]) -> List[str]:
    """Generate cache optimization recommendations"""
    recommendations = []
    
    hit_rate = stats["cache_performance"]["hit_rate"]
    memory_util = stats["memory_usage"]["memory_utilization"]
    
    if hit_rate < 50:
        recommendations.append("Consider increasing TTL or cache size - low hit rate")
    
    if memory_util > 90:
        recommendations.append("Consider increasing memory limit or reducing TTL")
    
    if stats["eviction_stats"]["total_evictions"] > stats["cache_performance"]["cache_hits"]:
        recommendations.append("High eviction rate - consider increasing cache size")
    
    if not recommendations:
        recommendations.append("Cache performance is optimal")
    
    return recommendations

if __name__ == "__main__":
    # Test the caching system
    cache = ToolResultCache(max_size=100, ttl_seconds=60)
    
    # Test basic operations
    cache.set("test_tool", {"param": "value"}, {"result": "test_data"})
    result = cache.get("test_tool", {"param": "value"})
    
    print("🧪 Tool Cache Test Results")
    print("=" * 30)
    print(f"Cache test result: {result}")
    print(f"Cache statistics:")
    print(json.dumps(cache.get_stats(), indent=2))