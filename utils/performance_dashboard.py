"""
Performance Dashboard Utilities for CrewAI

Utilities for analyzing performance metrics, generating reports,
and providing insights for agents to make performance-based decisions.

File: utils/performance_dashboard.py
"""

import json
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger("crewai.performance_dashboard")

@dataclass
class PerformanceAlert:
    """Performance alert data structure"""
    severity: str  # "info", "warning", "critical"
    category: str  # "system", "service", "cache", etc.
    metric: str
    current_value: float
    threshold: float
    message: str
    timestamp: float
    recommendation: Optional[str] = None

@dataclass
class PerformanceInsight:
    """Performance insight data structure"""
    category: str
    title: str
    description: str
    metrics: Dict[str, Any]
    trend: str  # "improving", "degrading", "stable"
    importance: str  # "low", "medium", "high"
    action_items: List[str]

class PerformanceAnalyzer:
    """Analyze performance metrics and generate insights"""
    
    def __init__(self):
        # Performance thresholds for alerting
        self.thresholds = {
            "cpu_percent": {"warning": 70.0, "critical": 85.0},
            "memory_percent": {"warning": 75.0, "critical": 90.0},
            "disk_usage_percent": {"warning": 80.0, "critical": 95.0},
            "avg_response_time": {"warning": 1000.0, "critical": 3000.0},  # ms
            "error_rate": {"warning": 2.0, "critical": 5.0},  # %
            "cache_hit_rate": {"warning": 70.0, "critical": 50.0},  # % (lower is worse)
            "requests_per_second": {"warning": 5.0, "critical": 2.0}  # (lower is worse)
        }
    
    def analyze_metrics(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance metrics and generate comprehensive report.
        
        Args:
            metrics_data: Performance metrics from API
            
        Returns:
            Comprehensive analysis report with alerts and insights
        """
        try:
            logger.info("📊 Analyzing performance metrics")
            
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": "unknown",
                "alerts": [],
                "insights": [],
                "recommendations": [],
                "summary": {}
            }
            
            # Extract system and service metrics
            system_metrics = metrics_data.get("system", {})
            service_metrics = metrics_data.get("service", {})
            
            # Generate alerts
            alerts = self._generate_alerts(system_metrics, service_metrics)
            analysis["alerts"] = [alert.__dict__ for alert in alerts]
            
            # Generate insights
            insights = self._generate_insights(system_metrics, service_metrics, metrics_data)
            analysis["insights"] = [insight.__dict__ for insight in insights]
            
            # Determine overall health
            analysis["overall_health"] = self._determine_overall_health(alerts)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(alerts, insights)
            
            # Create summary
            analysis["summary"] = self._create_summary(system_metrics, service_metrics, alerts)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_alerts(self, system_metrics: Dict, service_metrics: Dict) -> List[PerformanceAlert]:
        """Generate performance alerts based on thresholds"""
        alerts = []
        
        # System metric alerts
        for metric, thresholds in self.thresholds.items():
            if metric in ["cpu_percent", "memory_percent", "disk_usage_percent"]:
                current_value = system_metrics.get(metric, {}).get("current", 0)
                
                if current_value >= thresholds.get("critical", 999):
                    alerts.append(PerformanceAlert(
                        severity="critical",
                        category="system",
                        metric=metric,
                        current_value=current_value,
                        threshold=thresholds["critical"],
                        message=f"Critical {metric.replace('_', ' ')}: {current_value:.1f}%",
                        timestamp=datetime.now().timestamp(),
                        recommendation=self._get_system_recommendation(metric)
                    ))
                elif current_value >= thresholds.get("warning", 999):
                    alerts.append(PerformanceAlert(
                        severity="warning",
                        category="system",
                        metric=metric,
                        current_value=current_value,
                        threshold=thresholds["warning"],
                        message=f"High {metric.replace('_', ' ')}: {current_value:.1f}%",
                        timestamp=datetime.now().timestamp(),
                        recommendation=self._get_system_recommendation(metric)
                    ))
        
        # Service metric alerts
        for metric, thresholds in self.thresholds.items():
            if metric in ["avg_response_time", "error_rate"]:
                current_value = service_metrics.get(metric, 0)
                
                if current_value >= thresholds.get("critical", 999):
                    alerts.append(PerformanceAlert(
                        severity="critical",
                        category="service",
                        metric=metric,
                        current_value=current_value,
                        threshold=thresholds["critical"],
                        message=f"Critical {metric.replace('_', ' ')}: {current_value:.1f}",
                        timestamp=datetime.now().timestamp(),
                        recommendation=self._get_service_recommendation(metric)
                    ))
                elif current_value >= thresholds.get("warning", 999):
                    alerts.append(PerformanceAlert(
                        severity="warning",
                        category="service",
                        metric=metric,
                        current_value=current_value,
                        threshold=thresholds["warning"],
                        message=f"High {metric.replace('_', ' ')}: {current_value:.1f}",
                        timestamp=datetime.now().timestamp(),
                        recommendation=self._get_service_recommendation(metric)
                    ))
            
            # Cache and RPS alerts (reverse logic - lower is worse)
            elif metric in ["cache_hit_rate", "requests_per_second"]:
                current_value = service_metrics.get(metric, 100)
                
                if current_value <= thresholds.get("critical", 0):
                    alerts.append(PerformanceAlert(
                        severity="critical",
                        category="service",
                        metric=metric,
                        current_value=current_value,
                        threshold=thresholds["critical"],
                        message=f"Critical {metric.replace('_', ' ')}: {current_value:.1f}",
                        timestamp=datetime.now().timestamp(),
                        recommendation=self._get_service_recommendation(metric)
                    ))
                elif current_value <= thresholds.get("warning", 0):
                    alerts.append(PerformanceAlert(
                        severity="warning",
                        category="service",
                        metric=metric,
                        current_value=current_value,
                        threshold=thresholds["warning"],
                        message=f"Low {metric.replace('_', ' ')}: {current_value:.1f}",
                        timestamp=datetime.now().timestamp(),
                        recommendation=self._get_service_recommendation(metric)
                    ))
        
        return alerts
    
    def _generate_insights(self, system_metrics: Dict, service_metrics: Dict, full_data: Dict) -> List[PerformanceInsight]:
        """Generate performance insights and trends"""
        insights = []
        
        # System resource insights
        cpu_current = system_metrics.get("cpu_percent", {}).get("current", 0)
        memory_current = system_metrics.get("memory_percent", {}).get("current", 0)
        
        if cpu_current > 0 or memory_current > 0:
            resource_efficiency = 100 - max(cpu_current, memory_current)
            
            insights.append(PerformanceInsight(
                category="system",
                title="Resource Utilization Analysis",
                description=f"System is utilizing {max(cpu_current, memory_current):.1f}% of peak resources",
                metrics={
                    "cpu_percent": cpu_current,
                    "memory_percent": memory_current,
                    "efficiency_score": resource_efficiency
                },
                trend="stable",  # Would need historical data to determine trend
                importance="medium" if max(cpu_current, memory_current) > 50 else "low",
                action_items=self._get_resource_action_items(cpu_current, memory_current)
            ))
        
        # Service performance insights
        rps = service_metrics.get("requests_per_second", 0)
        response_time = service_metrics.get("avg_response_time", 0)
        error_rate = service_metrics.get("error_rate", 0)
        cache_hit_rate = service_metrics.get("cache_hit_rate", 0)
        
        # Throughput analysis
        if rps > 0:
            throughput_score = min(100, (rps / 50) * 100)  # Assume 50 RPS as excellent
            
            insights.append(PerformanceInsight(
                category="service",
                title="API Throughput Performance",
                description=f"Processing {rps:.1f} requests per second with {response_time:.0f}ms average response time",
                metrics={
                    "requests_per_second": rps,
                    "avg_response_time": response_time,
                    "throughput_score": throughput_score
                },
                trend="stable",
                importance="high" if rps < 5 else "medium",
                action_items=self._get_throughput_action_items(rps, response_time)
            ))
        
        # Cache performance insights
        if cache_hit_rate > 0:
            insights.append(PerformanceInsight(
                category="cache",
                title="Cache Performance Analysis",
                description=f"Cache is achieving {cache_hit_rate:.1f}% hit rate",
                metrics={
                    "cache_hit_rate": cache_hit_rate,
                    "cache_efficiency": "excellent" if cache_hit_rate > 80 else "good" if cache_hit_rate > 60 else "poor"
                },
                trend="stable",
                importance="medium",
                action_items=self._get_cache_action_items(cache_hit_rate)
            ))
        
        # Error rate insights
        if error_rate >= 0:
            reliability_score = max(0, 100 - (error_rate * 20))  # 5% error = 0% reliability
            
            insights.append(PerformanceInsight(
                category="reliability",
                title="Service Reliability Analysis",
                description=f"Service reliability at {reliability_score:.1f}% with {error_rate:.2f}% error rate",
                metrics={
                    "error_rate": error_rate,
                    "reliability_score": reliability_score,
                    "uptime_estimate": max(0, 100 - error_rate)
                },
                trend="stable",
                importance="high" if error_rate > 2 else "low",
                action_items=self._get_reliability_action_items(error_rate)
            ))
        
        return insights
    
    def _determine_overall_health(self, alerts: List[PerformanceAlert]) -> str:
        """Determine overall system health based on alerts"""
        if not alerts:
            return "excellent"
        
        critical_alerts = [a for a in alerts if a.severity == "critical"]
        warning_alerts = [a for a in alerts if a.severity == "warning"]
        
        if critical_alerts:
            return "critical"
        elif len(warning_alerts) >= 3:
            return "degraded"
        elif warning_alerts:
            return "warning"
        else:
            return "good"
    
    def _generate_recommendations(self, alerts: List[PerformanceAlert], insights: List[PerformanceInsight]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Alert-based recommendations
        critical_alerts = [a for a in alerts if a.severity == "critical"]
        warning_alerts = [a for a in alerts if a.severity == "warning"]
        
        if critical_alerts:
            recommendations.append("🚨 URGENT: Address critical performance issues immediately")
            for alert in critical_alerts[:3]:  # Top 3 critical issues
                if alert.recommendation:
                    recommendations.append(f"  • {alert.recommendation}")
        
        if warning_alerts:
            recommendations.append("⚠️ Monitor warning-level performance metrics")
            
        # Insight-based recommendations
        high_importance_insights = [i for i in insights if i.importance == "high"]
        for insight in high_importance_insights[:2]:  # Top 2 high-importance insights
            for action in insight.action_items[:2]:  # Top 2 actions per insight
                recommendations.append(f"📈 {action}")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ System performing well - consider proactive optimization")
            recommendations.append("📊 Continue monitoring key performance indicators")
        
        return recommendations
    
    def _create_summary(self, system_metrics: Dict, service_metrics: Dict, alerts: List[PerformanceAlert]) -> Dict[str, Any]:
        """Create performance summary"""
        return {
            "system_health": {
                "cpu_usage": system_metrics.get("cpu_percent", {}).get("current", 0),
                "memory_usage": system_metrics.get("memory_percent", {}).get("current", 0),
                "disk_usage": system_metrics.get("disk_usage_percent", {}).get("current", 0)
            },
            "service_performance": {
                "requests_per_second": service_metrics.get("requests_per_second", 0),
                "avg_response_time_ms": service_metrics.get("avg_response_time", 0),
                "error_rate_percent": service_metrics.get("error_rate", 0),
                "cache_hit_rate_percent": service_metrics.get("cache_hit_rate", 0)
            },
            "alert_summary": {
                "total_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a.severity == "critical"]),
                "warning_alerts": len([a for a in alerts if a.severity == "warning"])
            }
        }
    
    # Helper methods for recommendations
    
    def _get_system_recommendation(self, metric: str) -> str:
        """Get system-specific recommendations"""
        recommendations = {
            "cpu_percent": "Consider reducing concurrent operations or optimizing CPU-intensive tasks",
            "memory_percent": "Review memory usage patterns and consider increasing available memory",
            "disk_usage_percent": "Clean up temporary files or consider expanding disk capacity"
        }
        return recommendations.get(metric, "Monitor system resources closely")
    
    def _get_service_recommendation(self, metric: str) -> str:
        """Get service-specific recommendations"""
        recommendations = {
            "avg_response_time": "Optimize database queries and enable more aggressive caching",
            "error_rate": "Review error logs and fix underlying issues causing failures",
            "cache_hit_rate": "Tune cache TTL settings and consider expanding cache size",
            "requests_per_second": "Check for bottlenecks in request processing pipeline"
        }
        return recommendations.get(metric, "Review service configuration and optimization")
    
    def _get_resource_action_items(self, cpu: float, memory: float) -> List[str]:
        """Get resource-specific action items"""
        actions = []
        if cpu > 70:
            actions.append("Optimize CPU-intensive operations")
        if memory > 70:
            actions.append("Review memory allocation and garbage collection")
        if cpu < 30 and memory < 30:
            actions.append("Resources are underutilized - consider increasing workload")
        return actions or ["Monitor resource usage trends"]
    
    def _get_throughput_action_items(self, rps: float, response_time: float) -> List[str]:
        """Get throughput-specific action items"""
        actions = []
        if rps < 5:
            actions.append("Investigate low request throughput")
        if response_time > 1000:
            actions.append("Optimize response time with caching and query optimization")
        if rps > 0 and response_time < 500:
            actions.append("Excellent performance - maintain current optimizations")
        return actions or ["Monitor API performance metrics"]
    
    def _get_cache_action_items(self, hit_rate: float) -> List[str]:
        """Get cache-specific action items"""
        if hit_rate > 80:
            return ["Excellent cache performance - maintain current configuration"]
        elif hit_rate > 60:
            return ["Good cache performance - consider expanding cache size"]
        else:
            return ["Poor cache performance - review TTL settings and cache strategy"]
    
    def _get_reliability_action_items(self, error_rate: float) -> List[str]:
        """Get reliability-specific action items"""
        if error_rate < 1:
            return ["Excellent reliability - maintain current error handling"]
        elif error_rate < 3:
            return ["Good reliability - monitor error patterns"]
        else:
            return ["Poor reliability - urgently review and fix error sources"]

def format_performance_report(analysis: Dict[str, Any]) -> str:
    """
    Format performance analysis into a readable report.
    
    Args:
        analysis: Performance analysis from PerformanceAnalyzer
        
    Returns:
        Formatted string report
    """
    if "error" in analysis:
        return f"❌ Performance analysis failed: {analysis['error']}"
    
    report = []
    report.append("📊 PERFORMANCE MONITORING REPORT")
    report.append("=" * 50)
    
    # Overall health
    health = analysis.get("overall_health", "unknown")
    health_emoji = {
        "excellent": "🟢",
        "good": "🟡", 
        "warning": "🟠",
        "degraded": "🔴",
        "critical": "🚨"
    }
    
    report.append(f"\n{health_emoji.get(health, '❓')} Overall Health: {health.upper()}")
    
    # Summary
    summary = analysis.get("summary", {})
    if summary:
        report.append(f"\n📈 System Summary:")
        system = summary.get("system_health", {})
        service = summary.get("service_performance", {})
        
        report.append(f"   CPU: {system.get('cpu_usage', 0):.1f}% | Memory: {system.get('memory_usage', 0):.1f}% | Disk: {system.get('disk_usage', 0):.1f}%")
        report.append(f"   RPS: {service.get('requests_per_second', 0):.1f} | Response: {service.get('avg_response_time_ms', 0):.0f}ms | Errors: {service.get('error_rate_percent', 0):.2f}%")
    
    # Alerts
    alerts = analysis.get("alerts", [])
    if alerts:
        report.append(f"\n🚨 Alerts ({len(alerts)} total):")
        for alert in alerts[:5]:  # Show top 5 alerts
            severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
            emoji = severity_emoji.get(alert["severity"], "❓")
            report.append(f"   {emoji} {alert['message']}")
    
    # Recommendations
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        report.append(f"\n💡 Recommendations:")
        for rec in recommendations[:5]:  # Show top 5 recommendations
            report.append(f"   {rec}")
    
    # Insights
    insights = analysis.get("insights", [])
    if insights:
        report.append(f"\n🔍 Key Insights:")
        for insight in insights[:3]:  # Show top 3 insights
            report.append(f"   • {insight['title']}: {insight['description']}")
    
    report.append(f"\n📅 Report generated: {analysis.get('timestamp', 'unknown')}")
    
    return "\n".join(report)