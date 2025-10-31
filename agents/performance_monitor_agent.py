"""
Performance Monitor Agent for CrewAI

Specialized agent responsible for monitoring system performance,
analyzing metrics, detecting issues, and providing optimization recommendations.

File: agents/performance_monitor_agent.py
"""

import logging
from crewai import Agent
from tools.performance_monitoring import PERFORMANCE_MONITORING_TOOLS
from utils.llm_config import get_agent_llm

logger = logging.getLogger("crewai.performance_monitor_agent")

def create_performance_monitor_agent(verbose: bool = False, 
                                   allow_delegation: bool = False,
                                   max_iter: int = 3,
                                   max_execution_time: int = 300) -> Agent:
    """
    Create the Performance Monitor Agent.
    
    This agent specializes in:
    - Monitoring system performance metrics in real-time
    - Analyzing performance trends and identifying bottlenecks
    - Detecting performance issues and alerting on problems
    - Providing optimization recommendations and insights
    - Recording custom metrics for application monitoring
    
    Args:
        verbose: Enable verbose logging for debugging
        allow_delegation: Allow agent to delegate tasks to other agents
        max_iter: Maximum iterations for task completion
        max_execution_time: Maximum execution time in seconds
    
    Returns:
        Configured Performance Monitor Agent
    """
    
    agent = Agent(
        role="Performance Monitor and Analyst",
        
        goal="""Monitor system performance in real-time, analyze metrics trends, detect performance issues,
        and provide actionable insights for optimization. Ensure the Myndy-AI system operates efficiently 
        by tracking CPU, memory, disk usage, API response times, error rates, and cache performance.
        Alert on performance degradation and recommend specific improvements.""",
        
        backstory="""You are an expert performance monitoring specialist with deep knowledge of system 
        resource management, API performance optimization, and infrastructure monitoring. You have 
        experience with high-performance distributed systems and understand the critical metrics that 
        indicate system health.

        Your expertise includes:
        - Real-time performance monitoring and alerting
        - System resource optimization (CPU, memory, disk, network)
        - API performance analysis (response times, throughput, error rates)
        - Cache performance tuning and hit rate optimization
        - Database and connection pool monitoring
        - Performance trend analysis and capacity planning
        - Bottleneck identification and resolution
        
        You use comprehensive performance monitoring tools to track system metrics, analyze trends,
        detect anomalies, and provide specific recommendations for optimization. You understand that
        performance monitoring is crucial for maintaining user experience and system reliability.
        
        When monitoring performance, you:
        1. Regularly check system health status and key performance indicators
        2. Analyze metrics trends to identify potential issues before they become critical
        3. Monitor API performance including response times, error rates, and throughput
        4. Track cache performance and optimization opportunities
        5. Record custom metrics for specialized monitoring needs
        6. Provide clear, actionable recommendations for performance improvements
        7. Alert on threshold violations and performance degradation
        8. Correlate metrics across different system components
        
        Your monitoring approach is proactive, data-driven, and focused on maintaining optimal
        system performance for the best user experience.""",
        
        tools=PERFORMANCE_MONITORING_TOOLS,
        llm=get_agent_llm("mixtral"),  # Use advanced model for complex analysis
        verbose=verbose,
        allow_delegation=allow_delegation,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        memory=True
    )
    
    logger.info("🎯 Performance Monitor Agent created successfully")
    return agent