"""
Redis Distributed Cache Tools for CrewAI

HTTP client tools for CrewAI agents to interact with the Redis distributed 
cache system in myndy-ai, enabling agents to cache and retrieve data.

File: tools/redis_cache_tools.py
"""

import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from crewai_tools import tool

# Import environment configuration
try:
    from ..config.env_config import env_config
    MYNDY_API_BASE = env_config.myndy_api_base_url
except ImportError:
    # Fallback if running standalone
    import os
    MYNDY_API_BASE = os.getenv("CREWAI_MYNDY_API_URL", "http://localhost:8081")

logger = logging.getLogger("crewai.redis_cache_tools")
DEFAULT_TIMEOUT = 30

def get_headers() -> Dict[str, str]:
    """Get headers for API requests"""
    return {
        "Content-Type": "application/json",
        "X-API-Key": "development-test-key"
    }

@tool
def cache_get_value(key: str, namespace: str = "api_responses", default_value: str = None) -> str:
    """
    Get a value from the distributed cache
    
    Args:
        key: The cache key to retrieve
        namespace: Cache namespace (default: 'api_responses')
        default_value: Value to return if key not found
    
    Returns:
        JSON string with cache operation result
    """
    try:
        response = requests.post(
            f"{MYNDY_API_BASE}/api/v1/cache/get",
            json={
                "key": key,
                "namespace": namespace,
                "default_value": default_value
            },
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "data": result.get("data"),
                "cache_hit": result.get("success", False)
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache get failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "fallback_used": True
        }, indent=2)

@tool
def cache_set_value(key: str, value: Union[str, dict, list, int, float], namespace: str = "api_responses", ttl_seconds: int = None) -> str:
    """
    Set a value in the distributed cache
    
    Args:
        key: The cache key to set
        value: The value to cache (can be string, dict, list, number)
        namespace: Cache namespace (default: 'api_responses')
        ttl_seconds: Time to live in seconds (optional)
    
    Returns:
        JSON string with cache operation result
    """
    try:
        cache_data = {
            "key": key,
            "value": value,
            "namespace": namespace
        }
        
        if ttl_seconds is not None:
            cache_data["ttl_seconds"] = ttl_seconds
        
        response = requests.post(
            f"{MYNDY_API_BASE}/api/v1/cache/set",
            json=cache_data,
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "key": key,
                "cached": result.get("success", False),
                "namespace": namespace
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache set failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_delete_value(key: str, namespace: str = "api_responses") -> str:
    """
    Delete a value from the distributed cache
    
    Args:
        key: The cache key to delete
        namespace: Cache namespace (default: 'api_responses')
    
    Returns:
        JSON string with cache operation result
    """
    try:
        response = requests.delete(
            f"{MYNDY_API_BASE}/api/v1/cache/delete/{namespace}/{key}",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "key": key,
                "deleted": result.get("success", False),
                "namespace": namespace
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache delete failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_exists_check(key: str, namespace: str = "api_responses") -> str:
    """
    Check if a key exists in the distributed cache
    
    Args:
        key: The cache key to check
        namespace: Cache namespace (default: 'api_responses')
    
    Returns:
        JSON string with existence check result
    """
    try:
        response = requests.get(
            f"{MYNDY_API_BASE}/api/v1/cache/exists/{namespace}/{key}",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": True,
                "key": key,
                "exists": result.get("data", {}).get("exists", False),
                "namespace": namespace,
                "message": result.get("message", "")
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache exists check failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_get_multiple_values(keys: List[str], namespace: str = "api_responses") -> str:
    """
    Get multiple values from the distributed cache at once
    
    Args:
        keys: List of cache keys to retrieve
        namespace: Cache namespace (default: 'api_responses')
    
    Returns:
        JSON string with bulk cache operation result
    """
    try:
        response = requests.post(
            f"{MYNDY_API_BASE}/api/v1/cache/get-multiple",
            json={
                "keys": keys,
                "namespace": namespace
            },
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "values": result.get("data", {}).get("values", {}),
                "hit_rate": result.get("data", {}).get("hit_rate", 0),
                "found_keys": result.get("data", {}).get("found_keys", []),
                "requested_keys": keys,
                "namespace": namespace
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache get multiple failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_set_multiple_values(key_value_pairs: Dict[str, Any], namespace: str = "api_responses", ttl_seconds: int = None) -> str:
    """
    Set multiple values in the distributed cache at once
    
    Args:
        key_value_pairs: Dictionary of key-value pairs to cache
        namespace: Cache namespace (default: 'api_responses')
        ttl_seconds: Time to live in seconds (optional)
    
    Returns:
        JSON string with bulk cache operation result
    """
    try:
        cache_data = {
            "key_value_pairs": key_value_pairs,
            "namespace": namespace
        }
        
        if ttl_seconds is not None:
            cache_data["ttl_seconds"] = ttl_seconds
        
        response = requests.post(
            f"{MYNDY_API_BASE}/api/v1/cache/set-multiple",
            json=cache_data,
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "successful_sets": result.get("data", {}).get("successful_sets", 0),
                "total_keys": len(key_value_pairs),
                "success_rate": result.get("data", {}).get("success_rate", 0),
                "namespace": namespace
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache set multiple failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_clear_namespace(namespace: str) -> str:
    """
    Clear all keys in a specific cache namespace
    
    Args:
        namespace: Cache namespace to clear
    
    Returns:
        JSON string with clear operation result
    """
    try:
        response = requests.delete(
            f"{MYNDY_API_BASE}/api/v1/cache/clear/{namespace}",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "namespace": namespace,
                "deleted_count": result.get("data", {}).get("deleted_count", 0)
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache clear namespace failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_invalidate_pattern(pattern: str, namespace: str = "api_responses") -> str:
    """
    Invalidate cache entries matching a specific pattern
    
    Args:
        pattern: Pattern to match for invalidation
        namespace: Cache namespace (default: 'api_responses')
    
    Returns:
        JSON string with invalidation operation result
    """
    try:
        response = requests.post(
            f"{MYNDY_API_BASE}/api/v1/cache/invalidate",
            json={
                "pattern": pattern,
                "namespace": namespace
            },
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "pattern": pattern,
                "namespace": namespace,
                "invalidated_count": result.get("data", {}).get("invalidated_count", 0)
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache invalidate pattern failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_get_statistics() -> str:
    """
    Get comprehensive cache statistics across all namespaces
    
    Returns:
        JSON string with detailed cache statistics
    """
    try:
        response = requests.get(
            f"{MYNDY_API_BASE}/api/v1/cache/stats",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": True,
                "overall_metrics": result.get("overall", {}),
                "namespace_stats": result.get("namespaces", {}),
                "health_info": result.get("health", {}),
                "timestamp": result.get("timestamp", "")
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache statistics failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_get_health_status() -> str:
    """
    Get cache health status and connectivity information
    
    Returns:
        JSON string with cache health information
    """
    try:
        response = requests.get(
            f"{MYNDY_API_BASE}/api/v1/cache/health",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": True,
                "healthy": result.get("status") == "healthy",
                "status": result.get("status", "unknown"),
                "details": result.get("details", {}),
                "timestamp": result.get("timestamp", "")
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text,
                "healthy": False
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "healthy": False
        }, indent=2)

@tool
def cache_warm_data(warming_data: Dict[str, Any], namespace: str = "api_responses") -> str:
    """
    Warm cache with precomputed data for improved performance
    
    Args:
        warming_data: Dictionary of key-value pairs to warm cache with
        namespace: Cache namespace (default: 'api_responses')
    
    Returns:
        JSON string with cache warming result
    """
    try:
        response = requests.post(
            f"{MYNDY_API_BASE}/api/v1/cache/warm",
            json={
                "warming_data": warming_data,
                "namespace": namespace
            },
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "namespace": namespace,
                "warmed_count": result.get("data", {}).get("warmed_count", 0),
                "total_items": len(warming_data)
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_list_namespaces() -> str:
    """
    List all available cache namespaces with their descriptions
    
    Returns:
        JSON string with available cache namespaces
    """
    try:
        response = requests.get(
            f"{MYNDY_API_BASE}/api/v1/cache/namespaces",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": True,
                "namespaces": result.get("namespaces", {}),
                "total_namespaces": result.get("total_namespaces", 0),
                "timestamp": result.get("timestamp", "")
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache namespaces list failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@tool
def cache_get_namespace_info(namespace: str) -> str:
    """
    Get detailed information about a specific cache namespace
    
    Args:
        namespace: Cache namespace to get information about
    
    Returns:
        JSON string with namespace information
    """
    try:
        response = requests.get(
            f"{MYNDY_API_BASE}/api/v1/cache/namespace/{namespace}/info",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                "success": True,
                "namespace": namespace,
                "info": result.get("namespace_info", {}),
                "timestamp": result.get("timestamp", "")
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": response.text
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Cache namespace info failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

# List of all cache tools for easy import
REDIS_CACHE_TOOLS = [
    cache_get_value,
    cache_set_value,
    cache_delete_value,
    cache_exists_check,
    cache_get_multiple_values,
    cache_set_multiple_values,
    cache_clear_namespace,
    cache_invalidate_pattern,
    cache_get_statistics,
    cache_get_health_status,
    cache_warm_data,
    cache_list_namespaces,
    cache_get_namespace_info
]