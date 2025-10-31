"""
CrewAI Performance Monitoring Tools

HTTP client tools for accessing Myndy-AI performance monitoring APIs,
allowing agents to monitor system performance and respond to issues.

File: tools/performance_monitoring.py
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List
from crewai_tools import tool

# Import environment configuration
try:
    from ..config.env_config import env_config
    MYNDY_API_BASE = env_config.myndy_api_base_url
except ImportError:
    # Fallback if running standalone
    import os
    MYNDY_API_BASE = os.getenv("CREWAI_MYNDY_API_URL", "http://localhost:8081")

logger = logging.getLogger("crewai.performance_monitoring")
DEFAULT_TIMEOUT = 10

def get_headers() -> Dict[str, str]:
    """Get standard headers for API requests"""
    return {
        "X-API-Key": "development-test-key",
        "X-User-ID": "crewai_agent",
        "X-User-Name": "CrewAI Performance Agent",
        "Content-Type": "application/json"
    }

@tool
def get_system_performance_metrics(time_window_minutes: int = 5) -> str:
    """
    Get comprehensive system performance metrics from Myndy-AI API.
    
    Args:
        time_window_minutes: Time window for metrics (1-60 minutes)
    
    Returns:
        JSON string with system and service performance metrics
    """
    try:
        logger.info(f"🔍 Getting performance metrics for {time_window_minutes} minute window")
        
        response = requests.get(
            f"{MYNDY_API_BASE}/api/v1/performance/metrics",
            params={"window_minutes": time_window_minutes},
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Format key metrics for readability
            summary = {
                "timestamp": data.get("timestamp"),
                "monitoring_window_minutes": data.get("monitoring_window_minutes"),
                "system_metrics": {
                    "cpu_percent": data.get("system", {}).get("cpu_percent", {}),
                    "memory_percent": data.get("system", {}).get("memory_percent", {}),
                    "disk_usage_percent": data.get("system", {}).get("disk_usage_percent", {})
                },
                "service_metrics": {
                    "requests_per_second": data.get("service", {}).get("requests_per_second"),
                    "avg_response_time": data.get("service", {}).get("avg_response_time"),
                    "error_rate": data.get("service", {}).get("error_rate"),
                    "cache_hit_rate": data.get("service", {}).get("cache_hit_rate")
                },
                "active_requests": data.get("active_requests"),
                "total_metrics_collected": data.get("total_metrics_collected")
            }
            
            return json.dumps(summary, indent=2)
        else:
            error_msg = f"Failed to get performance metrics: HTTP {response.status_code}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error getting performance metrics: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "fallback": "Performance monitoring unavailable"})
    except Exception as e:
        error_msg = f"Error getting performance metrics: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@tool
def get_system_health_status() -> str:
    """
    Get current system health status from Myndy-AI API.
    
    Returns:
        JSON string with health status and any issues detected
    """
    try:
        logger.info("🏥 Getting system health status")
        
        response = requests.get(
            f"{MYNDY_API_BASE}/api/v1/performance/health",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Format health status for readability
            health_summary = {
                "status": data.get("status"),
                "timestamp": data.get("timestamp"),
                "issues": data.get("issues", []),
                "monitoring_enabled": data.get("monitoring_enabled"),
                "collection_interval": data.get("collection_interval")
            }
            
            return json.dumps(health_summary, indent=2)
        else:
            error_msg = f"Failed to get health status: HTTP {response.status_code}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error getting health status: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "fallback": "Health monitoring unavailable"})
    except Exception as e:
        error_msg = f"Error getting health status: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@tool
def record_custom_performance_metric(name: str, value: float, tags: str = "{}", metadata: str = "{}") -> str:
    """
    Record a custom performance metric in Myndy-AI system.
    
    Args:
        name: Metric name (e.g., "agent.task_completion_time")
        value: Numeric value for the metric
        tags: JSON string with metric tags (e.g., '{"agent": "research", "task": "search"}')
        metadata: JSON string with additional metadata
    
    Returns:
        JSON string confirming metric recording
    """
    try:
        logger.info(f"📝 Recording custom metric: {name} = {value}")
        
        # Parse JSON strings
        try:
            tags_dict = json.loads(tags) if tags else {}
            metadata_dict = json.loads(metadata) if metadata else {}
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid JSON in tags or metadata: {e}"})
        
        payload = {
            "name": name,
            "value": float(value),
            "tags": tags_dict,
            "metadata": metadata_dict
        }
        
        response = requests.post(
            f"{MYNDY_API_BASE}/api/v1/performance/metrics/custom",
            json=payload,
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            return json.dumps({
                "success": True,
                "message": data.get("message"),
                "metric_name": name,
                "metric_value": value
            }, indent=2)
        else:
            error_msg = f"Failed to record metric: HTTP {response.status_code}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error recording metric: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error recording custom metric: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@tool
def query_specific_performance_metrics(metric_names: str, time_window_minutes: int = 5, tags: str = "{}") -> str:
    """
    Query specific performance metrics with filtering.
    
    Args:
        metric_names: JSON list of metric names (e.g., '["system.cpu_percent", "service.requests_per_second"]')
        time_window_minutes: Time window for query (1-60 minutes)
        tags: JSON string with tag filters (e.g., '{"type": "system"}')
    
    Returns:
        JSON string with filtered metrics data
    """
    try:
        logger.info(f"🔍 Querying specific metrics: {metric_names}")
        
        # Parse JSON strings
        try:
            metric_names_list = json.loads(metric_names) if metric_names else None
            tags_dict = json.loads(tags) if tags else {}
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid JSON in metric_names or tags: {e}"})
        
        payload = {
            "metric_names": metric_names_list,
            "time_window_minutes": time_window_minutes,
            "tags": tags_dict
        }
        
        response = requests.post(
            f"{MYNDY_API_BASE}/api/v1/performance/metrics/query",
            json=payload,
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Format response for readability
            query_result = {
                "total_count": data.get("total_count"),
                "query_parameters": data.get("query"),
                "metrics": data.get("metrics", [])[:20]  # Limit to first 20 for readability
            }
            
            if len(data.get("metrics", [])) > 20:
                query_result["note"] = f"Showing first 20 of {data.get('total_count')} metrics"
            
            return json.dumps(query_result, indent=2)
        else:
            error_msg = f"Failed to query metrics: HTTP {response.status_code}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error querying metrics: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error querying metrics: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@tool
def get_performance_monitoring_status() -> str:
    """
    Get the current status of the performance monitoring system.
    
    Returns:
        JSON string with monitoring configuration and status
    """
    try:
        logger.info("📊 Getting performance monitoring status")
        
        response = requests.get(
            f"{MYNDY_API_BASE}/api/v1/performance/monitoring/status",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Format status for readability
            status_summary = {
                "monitoring_enabled": data.get("monitoring_enabled"),
                "monitoring_running": data.get("monitoring_running"),
                "collection_interval_seconds": data.get("collection_interval_seconds"),
                "buffer_max_size": data.get("buffer_max_size"),
                "uptime_seconds": data.get("uptime_seconds"),
                "performance_thresholds": data.get("thresholds", {})
            }
            
            return json.dumps(status_summary, indent=2)
        else:
            error_msg = f"Failed to get monitoring status: HTTP {response.status_code}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error getting monitoring status: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error getting monitoring status: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@tool
def get_performance_stats_summary() -> str:
    """
    Get a comprehensive summary of performance monitoring statistics.
    
    Returns:
        JSON string with monitoring efficiency, buffer usage, and service overview
    """
    try:
        logger.info("📈 Getting performance stats summary")
        
        response = requests.get(
            f"{MYNDY_API_BASE}/api/v1/performance/stats/summary",
            headers=get_headers(),
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Format summary for readability
            stats_summary = {
                "monitoring_status": data.get("monitoring_status", {}),
                "buffer_status": data.get("buffer_status", {}),
                "service_overview": data.get("service_overview", {}),
                "performance_thresholds": data.get("thresholds", {}),
                "timestamp": data.get("timestamp")
            }
            
            return json.dumps(stats_summary, indent=2)
        else:
            error_msg = f"Failed to get stats summary: HTTP {response.status_code}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error getting stats summary: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error getting stats summary: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@tool
def restart_performance_monitoring() -> str:
    """
    Restart the performance monitoring system in Myndy-AI.
    
    This tool should be used when performance monitoring appears to be
    stuck or not collecting metrics properly.
    
    Returns:
        JSON string confirming restart status
    """
    try:
        logger.info("🔄 Restarting performance monitoring system")
        
        response = requests.post(
            f"{MYNDY_API_BASE}/api/v1/performance/monitoring/restart",
            headers=get_headers(),
            timeout=15  # Longer timeout for restart
        )
        
        if response.status_code == 200:
            data = response.json()
            return json.dumps({
                "success": True,
                "message": data.get("message"),
                "timestamp": data.get("timestamp")
            }, indent=2)
        else:
            error_msg = f"Failed to restart monitoring: HTTP {response.status_code}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error restarting monitoring: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error restarting monitoring: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

# Tool list for easy registration
PERFORMANCE_MONITORING_TOOLS = [
    get_system_performance_metrics,
    get_system_health_status,
    record_custom_performance_metric,
    query_specific_performance_metrics,
    get_performance_monitoring_status,
    get_performance_stats_summary,
    restart_performance_monitoring
]