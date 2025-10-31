"""
Cache Manager Agent for CrewAI

Specialized agent for managing and optimizing the Redis distributed caching 
system, providing cache operations, performance monitoring, and optimization 
recommendations.

File: agents/cache_manager_agent.py
"""

import logging
from typing import Dict, Any, List, Optional
from crewai import Agent

from tools.redis_cache_tools import REDIS_CACHE_TOOLS
from utils.llm_config import get_agent_llm

logger = logging.getLogger("crewai.cache_manager_agent")

def create_cache_manager_agent(
    verbose: bool = False,
    allow_delegation: bool = False,
    max_iter: int = 25,
    max_execution_time: Optional[int] = None
) -> Agent:
    """
    Create a Cache Manager Agent specialized in distributed cache operations
    
    This agent manages the Redis distributed caching system, monitors cache
    performance, provides optimization recommendations, and handles cache
    warming and invalidation strategies.
    
    Args:
        verbose: Enable verbose logging
        allow_delegation: Allow delegation to other agents
        max_iter: Maximum iterations for task execution
        max_execution_time: Maximum execution time in seconds
    
    Returns:
        Configured Cache Manager Agent
    """
    
    agent = Agent(
        role="Cache Manager and Performance Optimizer",
        
        goal="""Manage and optimize the Redis distributed caching system for maximum 
        performance. Monitor cache health, analyze hit rates, implement warming 
        strategies, handle cache invalidation, and provide data-driven optimization 
        recommendations to improve system responsiveness and reduce backend load.""",
        
        backstory="""You are an expert cache management specialist with deep knowledge 
        of distributed caching systems, Redis optimization, and performance tuning. 
        You understand cache strategies like LRU, LFU, and TTL-based eviction, and 
        can analyze cache performance metrics to identify bottlenecks and optimization 
        opportunities.
        
        Your expertise includes:
        - Redis distributed cache architecture and configuration
        - Cache namespace management and data organization
        - Performance monitoring and metric analysis
        - Cache warming strategies for improved hit rates
        - Intelligent invalidation patterns and cache coherence
        - Memory usage optimization and size limit management
        - Multi-namespace cache coordination for different data types
        
        You proactively monitor cache health, identify performance issues, implement 
        optimization strategies, and provide clear recommendations for improving 
        cache efficiency. You understand the trade-offs between cache size, TTL 
        values, and system performance, and can balance these factors for optimal 
        system responsiveness.""",
        
        tools=REDIS_CACHE_TOOLS,
        llm=get_agent_llm("mixtral"),  # Use advanced model for complex cache analysis
        verbose=verbose,
        allow_delegation=allow_delegation,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        memory=True  # Enable memory for learning cache patterns
    )
    
    return agent

def get_cache_optimization_recommendations() -> Dict[str, Any]:
    """
    Get cache optimization recommendations based on current performance
    
    Returns:
        Dictionary of optimization recommendations
    """
    return {
        "cache_warming": {
            "description": "Preload frequently accessed data",
            "triggers": ["Low hit rates", "Cold cache after restart"],
            "benefits": ["Improved response times", "Reduced backend load"]
        },
        "ttl_optimization": {
            "description": "Adjust TTL values based on data access patterns",
            "triggers": ["High memory usage", "Stale data issues"],
            "benefits": ["Better memory utilization", "Fresher data"]
        },
        "namespace_isolation": {
            "description": "Separate different data types into appropriate namespaces",
            "triggers": ["Cache contention", "Mixed data types"],
            "benefits": ["Better organization", "Targeted invalidation"]
        },
        "compression_tuning": {
            "description": "Enable compression for large values",
            "triggers": ["High memory usage", "Large cached objects"],
            "benefits": ["Reduced memory usage", "More cached items"]
        },
        "invalidation_strategies": {
            "description": "Implement intelligent cache invalidation",
            "triggers": ["Data consistency issues", "Stale cache entries"],
            "benefits": ["Data freshness", "Reduced inconsistencies"]
        }
    }

def get_cache_best_practices() -> List[str]:
    """
    Get cache management best practices
    
    Returns:
        List of best practices for cache management
    """
    return [
        "Monitor cache hit rates regularly and investigate drops below 80%",
        "Use appropriate TTL values: short for dynamic data, longer for static data",
        "Implement cache warming for critical data after system restarts",
        "Use namespace-specific configurations for different data types",
        "Monitor memory usage and adjust max_size limits as needed",
        "Implement pattern-based invalidation for related data updates",
        "Use compression for large objects to maximize cache capacity",
        "Monitor Redis health and connection pool performance",
        "Implement graceful degradation when cache is unavailable",
        "Use bulk operations (get_multiple, set_multiple) for better performance",
        "Analyze cache access patterns to optimize data organization",
        "Regular cache maintenance: clear unused namespaces and expired keys"
    ]

def get_cache_troubleshooting_guide() -> Dict[str, Dict[str, Any]]:
    """
    Get cache troubleshooting guide for common issues
    
    Returns:
        Dictionary of common issues and solutions
    """
    return {
        "low_hit_rate": {
            "symptoms": ["Hit rate below 70%", "Slow response times"],
            "causes": ["Cache not warmed", "TTL too short", "Frequent invalidation"],
            "solutions": ["Implement cache warming", "Increase TTL", "Review invalidation patterns"]
        },
        "high_memory_usage": {
            "symptoms": ["Memory usage above 90%", "Frequent evictions"],
            "causes": ["Large cached objects", "No size limits", "Long TTL values"],
            "solutions": ["Enable compression", "Set max_size limits", "Reduce TTL for non-critical data"]
        },
        "cache_unavailable": {
            "symptoms": ["Connection errors", "503 service unavailable"],
            "causes": ["Redis server down", "Network issues", "Connection pool exhausted"],
            "solutions": ["Check Redis server", "Verify network connectivity", "Increase connection pool size"]
        },
        "slow_cache_operations": {
            "symptoms": ["High response times", "Timeouts"],
            "causes": ["Redis overloaded", "Large values", "Network latency"],
            "solutions": ["Monitor Redis performance", "Use compression", "Check network configuration"]
        },
        "stale_data": {
            "symptoms": ["Outdated information", "Data inconsistency"],
            "causes": ["TTL too long", "Missing invalidation", "Cache not updated"],
            "solutions": ["Reduce TTL", "Implement invalidation patterns", "Use write-through caching"]
        }
    }

# Export agent creation function and utilities
__all__ = [
    "create_cache_manager_agent",
    "get_cache_optimization_recommendations",
    "get_cache_best_practices", 
    "get_cache_troubleshooting_guide"
]