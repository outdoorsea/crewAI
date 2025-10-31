"""
Analytics Dashboard for Feedback and Performance Metrics

This tool provides a comprehensive dashboard view of agent performance,
user feedback, and system health metrics.

File: tools/analytics_dashboard.py
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

def generate_analytics_dashboard(days: int = 7, include_details: bool = True) -> str:
    """
    Generate a comprehensive analytics dashboard.
    
    Args:
        days: Number of days to include in the analysis
        include_details: Whether to include detailed breakdowns
    
    Returns:
        Formatted dashboard report
    """
    try:
        # Import feedback analytics
        from feedback_analytics import _feedback_analytics as analytics
        
        # Get summary data
        summary = analytics.get_feedback_summary(days)
        all_metrics = analytics.get_all_agent_performance()
        system_health = analytics.get_system_health()
        
        # Build dashboard
        dashboard_lines = []
        
        # Header
        dashboard_lines.append("# 📊 Myndy AI Analytics Dashboard")
        dashboard_lines.append(f"**Report Period:** Last {days} days")
        dashboard_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        dashboard_lines.append("")
        
        # System Health Overview
        dashboard_lines.append("## 🏥 System Health")
        dashboard_lines.append(f"- **Status:** {system_health.get('system_status', 'Unknown').title()}")
        dashboard_lines.append(f"- **Total Feedback Entries:** {system_health.get('total_feedback_entries', 0):,}")
        dashboard_lines.append(f"- **Recent Activity (24h):** {system_health.get('recent_activity_24h', 0):,}")
        dashboard_lines.append(f"- **Database Size:** {system_health.get('database_size_bytes', 0) / 1024:.1f} KB")
        dashboard_lines.append("")
        
        # Overall Performance Summary
        dashboard_lines.append("## 📈 Overall Performance Summary")
        dashboard_lines.append(f"- **Total Feedback:** {summary.get('total_feedback_entries', 0):,}")
        dashboard_lines.append(f"- **Positive Feedback:** {summary.get('positive_feedback', 0):,} ({summary.get('overall_satisfaction', 0)*100:.1f}%)")
        dashboard_lines.append(f"- **Negative Feedback:** {summary.get('negative_feedback', 0):,}")
        dashboard_lines.append(f"- **Active Agents:** {summary.get('active_agents', 0)}")
        dashboard_lines.append(f"- **Unique Sessions:** {summary.get('unique_sessions', 0):,}")
        dashboard_lines.append(f"- **Avg Response Time:** {summary.get('average_response_time_ms', 0):.0f}ms")
        dashboard_lines.append("")
        
        # Agent Performance Leaderboard
        if all_metrics:
            dashboard_lines.append("## 🏆 Agent Performance Leaderboard")
            
            # Sort agents by feedback ratio (satisfaction)
            sorted_agents = sorted(
                all_metrics.items(),
                key=lambda x: x[1].feedback_ratio,
                reverse=True
            )
            
            dashboard_lines.append("| Rank | Agent | Responses | Satisfaction | Avg Time | Recent Activity |")
            dashboard_lines.append("|------|-------|-----------|--------------|----------|-----------------|")
            
            for i, (agent_id, metrics) in enumerate(sorted_agents, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
                satisfaction = f"{metrics.feedback_ratio*100:.1f}%"
                avg_time = f"{metrics.average_response_time_ms:.0f}ms"
                recent = f"{metrics.responses_last_24h} (24h)"
                
                dashboard_lines.append(
                    f"| {emoji} {i} | {metrics.agent_name} | {metrics.total_responses:,} | {satisfaction} | {avg_time} | {recent} |"
                )
            
            dashboard_lines.append("")
        
        # Detailed Agent Breakdown
        if include_details and all_metrics:
            dashboard_lines.append("## 🔍 Detailed Agent Analysis")
            
            for agent_id, metrics in sorted_agents:
                dashboard_lines.append(f"### {metrics.agent_name}")
                dashboard_lines.append("")
                
                # Performance metrics
                dashboard_lines.append("**Performance Metrics:**")
                dashboard_lines.append(f"- Total Responses: {metrics.total_responses:,}")
                dashboard_lines.append(f"- Positive Feedback: {metrics.positive_feedback:,}")
                dashboard_lines.append(f"- Negative Feedback: {metrics.negative_feedback:,}")
                dashboard_lines.append(f"- Satisfaction Rate: {metrics.feedback_ratio*100:.1f}%")
                dashboard_lines.append(f"- Average Rating: {metrics.average_rating:.2f}/5.0")
                dashboard_lines.append("")
                
                # Response performance
                dashboard_lines.append("**Response Performance:**")
                dashboard_lines.append(f"- Average Response Time: {metrics.average_response_time_ms:.0f}ms")
                dashboard_lines.append(f"- Routing Confidence: {metrics.average_routing_confidence*100:.1f}%")
                dashboard_lines.append(f"- Tools Used: {metrics.total_tools_used}")
                dashboard_lines.append(f"- Collaboration Rate: {metrics.collaboration_frequency*100:.1f}%")
                dashboard_lines.append("")
                
                # Activity trends
                dashboard_lines.append("**Activity Trends:**")
                dashboard_lines.append(f"- Last 24 hours: {metrics.responses_last_24h}")
                dashboard_lines.append(f"- Last 7 days: {metrics.responses_last_7d}")
                dashboard_lines.append(f"- Last 30 days: {metrics.responses_last_30d}")
                dashboard_lines.append("")
                
                # Performance assessment
                performance_assessment = _assess_agent_performance(metrics)
                dashboard_lines.append(f"**Assessment:** {performance_assessment}")
                dashboard_lines.append("")
        
        # Trends and Insights
        if summary.get('agent_breakdown'):
            dashboard_lines.append("## 📊 Recent Trends & Insights")
            
            agent_breakdown = summary['agent_breakdown']
            
            # Top performing agent
            if agent_breakdown:
                top_agent = max(agent_breakdown, key=lambda x: x['feedback_ratio'])
                dashboard_lines.append(f"🌟 **Top Performer:** {top_agent['agent_name']} ({top_agent['feedback_ratio']*100:.1f}% satisfaction)")
                
                # Most active agent
                most_active = max(agent_breakdown, key=lambda x: x['total_responses'])
                dashboard_lines.append(f"⚡ **Most Active:** {most_active['agent_name']} ({most_active['total_responses']} responses)")
                
                # Fastest response
                fastest = min(agent_breakdown, key=lambda x: x['avg_response_time_ms'])
                dashboard_lines.append(f"🚀 **Fastest Response:** {fastest['agent_name']} ({fastest['avg_response_time_ms']:.0f}ms avg)")
                
            dashboard_lines.append("")
        
        # Recommendations
        recommendations = _generate_recommendations(summary, all_metrics)
        if recommendations:
            dashboard_lines.append("## 💡 Recommendations")
            for rec in recommendations:
                dashboard_lines.append(f"- {rec}")
            dashboard_lines.append("")
        
        # Footer
        dashboard_lines.append("---")
        dashboard_lines.append("*This dashboard is automatically generated from user feedback and system metrics.*")
        dashboard_lines.append("*Use feedback tools to record 👍/👎 ratings for continuous improvement.*")
        
        return "\n".join(dashboard_lines)
        
    except Exception as e:
        logger.error(f"Error generating analytics dashboard: {e}")
        return f"Error generating dashboard: {str(e)}"

def _assess_agent_performance(metrics) -> str:
    """Generate a performance assessment for an agent."""
    assessments = []
    
    # Satisfaction assessment
    if metrics.feedback_ratio >= 0.8:
        assessments.append("🟢 Excellent satisfaction")
    elif metrics.feedback_ratio >= 0.6:
        assessments.append("🟡 Good satisfaction")
    else:
        assessments.append("🔴 Needs improvement")
    
    # Response time assessment
    if metrics.average_response_time_ms <= 2000:
        assessments.append("🟢 Fast response")
    elif metrics.average_response_time_ms <= 5000:
        assessments.append("🟡 Moderate response time")
    else:
        assessments.append("🔴 Slow response")
    
    # Activity assessment
    if metrics.responses_last_24h >= 10:
        assessments.append("🟢 High activity")
    elif metrics.responses_last_24h >= 3:
        assessments.append("🟡 Moderate activity")
    else:
        assessments.append("🟡 Low activity")
    
    return " | ".join(assessments)

def _generate_recommendations(summary: Dict[str, Any], all_metrics: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations based on analytics data."""
    recommendations = []
    
    try:
        # Overall satisfaction check
        overall_satisfaction = summary.get('overall_satisfaction', 0)
        if overall_satisfaction < 0.7:
            recommendations.append("Overall satisfaction is below 70%. Consider reviewing routing logic and agent performance.")
        
        # Check for low-performing agents
        if all_metrics:
            for agent_id, metrics in all_metrics.items():
                if metrics.total_responses >= 5:  # Only for agents with sufficient data
                    if metrics.feedback_ratio < 0.5:
                        recommendations.append(f"Agent {metrics.agent_name} has low satisfaction ({metrics.feedback_ratio*100:.1f}%). Review tool selection and task descriptions.")
                    
                    if metrics.average_response_time_ms > 10000:  # 10 seconds
                        recommendations.append(f"Agent {metrics.agent_name} has slow response times ({metrics.average_response_time_ms:.0f}ms). Consider optimizing tool execution.")
        
        # Activity recommendations
        total_feedback = summary.get('total_feedback_entries', 0)
        if total_feedback < 10:
            recommendations.append("Low feedback volume. Consider encouraging user feedback to improve analytics accuracy.")
        
        # Agent utilization
        agent_breakdown = summary.get('agent_breakdown', [])
        if len(agent_breakdown) > 1:
            # Check for imbalanced usage
            total_responses = sum(agent['total_responses'] for agent in agent_breakdown)
            for agent in agent_breakdown:
                usage_percentage = agent['total_responses'] / total_responses if total_responses > 0 else 0
                if usage_percentage > 0.6:  # One agent handling >60% of requests
                    recommendations.append(f"Agent {agent['agent_name']} is handling {usage_percentage*100:.1f}% of requests. Consider improving routing logic for better distribution.")
        
        # System health recommendations
        if summary.get('unique_sessions', 0) > 0:
            feedback_per_session = total_feedback / summary['unique_sessions']
            if feedback_per_session < 0.1:  # Less than 10% feedback rate
                recommendations.append("Low feedback rate per session. Consider making feedback collection more prominent or easier.")
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        recommendations.append("Unable to generate recommendations due to data processing error.")
    
    return recommendations

def get_quick_performance_summary() -> str:
    """Get a quick performance summary for agents."""
    try:
        from feedback_analytics import _feedback_analytics as analytics
        
        # Get recent summary (last 24 hours)
        summary = analytics.get_feedback_summary(1)
        system_health = analytics.get_system_health()
        
        lines = []
        lines.append("## 📊 Quick Performance Summary (Last 24h)")
        lines.append("")
        lines.append(f"**System Status:** {system_health.get('system_status', 'Unknown').title()}")
        lines.append(f"**Recent Feedback:** {summary.get('total_feedback_entries', 0)} entries")
        lines.append(f"**Satisfaction Rate:** {summary.get('overall_satisfaction', 0)*100:.1f}%")
        lines.append(f"**Average Response Time:** {summary.get('average_response_time_ms', 0):.0f}ms")
        lines.append("")
        
        # Agent breakdown
        agent_breakdown = summary.get('agent_breakdown', [])
        if agent_breakdown:
            lines.append("**Top Agents by Activity:**")
            sorted_agents = sorted(agent_breakdown, key=lambda x: x['total_responses'], reverse=True)[:3]
            for i, agent in enumerate(sorted_agents, 1):
                satisfaction = agent['feedback_ratio'] * 100
                lines.append(f"{i}. {agent['agent_name']}: {agent['total_responses']} responses ({satisfaction:.1f}% satisfaction)")
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.error(f"Error generating quick summary: {e}")
        return f"Error generating summary: {str(e)}"

def get_agent_comparison(agent1_id: str, agent2_id: str) -> str:
    """Compare performance between two agents."""
    try:
        from feedback_analytics import _feedback_analytics as analytics
        
        metrics1 = analytics.get_agent_performance(agent1_id)
        metrics2 = analytics.get_agent_performance(agent2_id)
        
        if not metrics1 or not metrics2:
            return "Error: One or both agents not found or have insufficient data."
        
        lines = []
        lines.append(f"## 🆚 Agent Comparison: {metrics1.agent_name} vs {metrics2.agent_name}")
        lines.append("")
        
        # Comparison table
        lines.append("| Metric | " + metrics1.agent_name + " | " + metrics2.agent_name + " | Winner |")
        lines.append("|--------|" + "-" * len(metrics1.agent_name) + "|" + "-" * len(metrics2.agent_name) + "|--------|")
        
        # Total responses
        winner1 = "🏆" if metrics1.total_responses > metrics2.total_responses else ""
        winner2 = "🏆" if metrics2.total_responses > metrics1.total_responses else ""
        lines.append(f"| Total Responses | {metrics1.total_responses:,} {winner1} | {metrics2.total_responses:,} {winner2} | More responses |")
        
        # Satisfaction rate
        winner1 = "🏆" if metrics1.feedback_ratio > metrics2.feedback_ratio else ""
        winner2 = "🏆" if metrics2.feedback_ratio > metrics1.feedback_ratio else ""
        lines.append(f"| Satisfaction Rate | {metrics1.feedback_ratio*100:.1f}% {winner1} | {metrics2.feedback_ratio*100:.1f}% {winner2} | Higher satisfaction |")
        
        # Response time
        winner1 = "🏆" if metrics1.average_response_time_ms < metrics2.average_response_time_ms else ""
        winner2 = "🏆" if metrics2.average_response_time_ms < metrics1.average_response_time_ms else ""
        lines.append(f"| Avg Response Time | {metrics1.average_response_time_ms:.0f}ms {winner1} | {metrics2.average_response_time_ms:.0f}ms {winner2} | Faster response |")
        
        # Routing confidence
        winner1 = "🏆" if metrics1.average_routing_confidence > metrics2.average_routing_confidence else ""
        winner2 = "🏆" if metrics2.average_routing_confidence > metrics1.average_routing_confidence else ""
        lines.append(f"| Routing Confidence | {metrics1.average_routing_confidence*100:.1f}% {winner1} | {metrics2.average_routing_confidence*100:.1f}% {winner2} | Better routing |")
        
        # Recent activity
        winner1 = "🏆" if metrics1.responses_last_24h > metrics2.responses_last_24h else ""
        winner2 = "🏆" if metrics2.responses_last_24h > metrics1.responses_last_24h else ""
        lines.append(f"| Recent Activity (24h) | {metrics1.responses_last_24h} {winner1} | {metrics2.responses_last_24h} {winner2} | More active |")
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.error(f"Error comparing agents: {e}")
        return f"Error comparing agents: {str(e)}"

# Tool functions for registry
def generate_analytics_dashboard_tool(days: int = 7, include_details: bool = True) -> str:
    """Generate comprehensive analytics dashboard showing agent performance and user feedback."""
    return generate_analytics_dashboard(days, include_details)

def get_quick_performance_summary_tool() -> str:
    """Get a quick performance summary for the last 24 hours."""
    return get_quick_performance_summary()

def compare_agent_performance(agent1_id: str, agent2_id: str) -> str:
    """Compare performance metrics between two agents."""
    return get_agent_comparison(agent1_id, agent2_id)