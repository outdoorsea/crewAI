#!/usr/bin/env python3
"""
Demo script for feedback analytics system

This script demonstrates how the feedback analytics system works
in practice with realistic data.
"""

import sys
from pathlib import Path
import random
import time
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "tools"))

def simulate_realistic_feedback():
    """Simulate realistic feedback data for demonstration."""
    print("🎭 Simulating Realistic Feedback Data")
    print("=" * 50)
    
    from feedback_analytics import FeedbackAnalytics, FeedbackType
    
    # Create analytics instance
    demo_db_path = str(project_root / "demo_feedback.db")
    analytics = FeedbackAnalytics(demo_db_path)
    
    # Sample user messages and responses
    scenarios = [
        {
            "user_message": "What's the weather like today?",
            "agent": "personal_assistant",
            "response": "The weather in San Francisco is 68°F and partly cloudy with a 10% chance of rain.",
            "tools": ["weather_api", "local_weather"],
            "thumbs_up_chance": 0.9,  # Weather queries usually work well
            "response_time_range": (800, 2000)
        },
        {
            "user_message": "Tell me about John Doe's contact information",
            "agent": "memory_librarian", 
            "response": "I found John Doe in your contacts. He works at Acme Corp and his email is john@acme.com.",
            "tools": ["contact_search", "memory_search"],
            "thumbs_up_chance": 0.85,
            "response_time_range": (1200, 3000)
        },
        {
            "user_message": "Analyze the sentiment of this text: 'I love this product!'",
            "agent": "research_specialist",
            "response": "The sentiment analysis shows this text has a positive sentiment with 95% confidence.",
            "tools": ["analyze_sentiment", "text_analysis"],
            "thumbs_up_chance": 0.8,
            "response_time_range": (1500, 4000)
        },
        {
            "user_message": "How much did I spend on groceries last month?",
            "agent": "finance_tracker",
            "response": "You spent $342.18 on groceries last month across 12 transactions.",
            "tools": ["search_transactions", "get_spending_summary"],
            "thumbs_up_chance": 0.75,
            "response_time_range": (2000, 5000)
        },
        {
            "user_message": "Show me my sleep patterns for this week",
            "agent": "health_analyst",
            "response": "Your average sleep duration this week was 7.2 hours with good sleep quality.",
            "tools": ["health_query", "sleep_analysis"],
            "thumbs_up_chance": 0.7,
            "response_time_range": (1800, 4500)
        }
    ]
    
    agent_names = {
        "personal_assistant": "Personal Assistant",
        "memory_librarian": "Memory Librarian", 
        "research_specialist": "Research Specialist",
        "finance_tracker": "Finance Tracker",
        "health_analyst": "Health Analyst"
    }
    
    # Simulate feedback over the last 7 days
    feedback_count = 0
    start_date = datetime.now() - timedelta(days=7)
    
    for day in range(7):
        # More activity on weekdays
        daily_interactions = random.randint(3, 8) if day < 5 else random.randint(1, 4)
        
        for interaction in range(daily_interactions):
            scenario = random.choice(scenarios)
            
            # Generate session and response IDs
            session_id = f"demo_session_{day}_{interaction}"
            response_id = f"demo_response_{day}_{interaction}_{scenario['agent']}"
            
            # Calculate response time
            min_time, max_time = scenario['response_time_range']
            response_time = random.randint(min_time, max_time)
            
            # Determine feedback based on scenario probability
            is_positive = random.random() < scenario['thumbs_up_chance']
            
            # Add some routing confidence variation
            routing_confidence = random.uniform(0.7, 0.95)
            
            # Record feedback
            if is_positive:
                feedback_id = analytics.record_thumbs_up(
                    session_id=session_id,
                    agent_id=scenario['agent'],
                    agent_name=agent_names[scenario['agent']],
                    response_id=response_id,
                    response_content=scenario['response'],
                    user_message=scenario['user_message'],
                    routing_confidence=routing_confidence,
                    response_time_ms=response_time,
                    tools_used=scenario['tools']
                )
            else:
                # Occasional negative feedback
                negative_reasons = [
                    "Response was too slow",
                    "Information was incorrect", 
                    "Didn't understand my request",
                    "Missing important details"
                ]
                feedback_text = random.choice(negative_reasons)
                
                feedback_id = analytics.record_thumbs_down(
                    session_id=session_id,
                    agent_id=scenario['agent'],
                    agent_name=agent_names[scenario['agent']],
                    response_id=response_id,
                    response_content=scenario['response'],
                    user_message=scenario['user_message'],
                    feedback_text=feedback_text,
                    routing_confidence=routing_confidence,
                    response_time_ms=response_time,
                    tools_used=scenario['tools']
                )
            
            feedback_count += 1
            
            # Small delay to make timestamps more realistic
            time.sleep(0.01)
    
    print(f"✅ Simulated {feedback_count} feedback entries over 7 days")
    return analytics

def demonstrate_analytics(analytics):
    """Demonstrate the analytics capabilities."""
    print("\n📊 Demonstrating Analytics Capabilities")
    print("=" * 50)
    
    # Get system health
    health = analytics.get_system_health()
    print(f"System Status: {health['system_status']}")
    print(f"Total Feedback Entries: {health['total_feedback_entries']:,}")
    print(f"Recent Activity (24h): {health['recent_activity_24h']}")
    
    # Get feedback summary
    summary = analytics.get_feedback_summary(7)
    print(f"\n📈 7-Day Summary:")
    print(f"Overall Satisfaction: {summary['overall_satisfaction']:.1%}")
    print(f"Total Feedback: {summary['total_feedback_entries']}")
    print(f"Active Agents: {summary['active_agents']}")
    print(f"Average Response Time: {summary['average_response_time_ms']:.0f}ms")
    
    # Show agent breakdown
    print(f"\n🎯 Agent Performance:")
    agent_breakdown = summary.get('agent_breakdown', [])
    for agent in sorted(agent_breakdown, key=lambda x: x['feedback_ratio'], reverse=True):
        print(f"  {agent['agent_name']}: {agent['feedback_ratio']:.1%} satisfaction ({agent['total_responses']} responses)")
    
    # Get detailed metrics for top agent
    if agent_breakdown:
        top_agent = max(agent_breakdown, key=lambda x: x['feedback_ratio'])
        detailed_metrics = analytics.get_agent_performance(top_agent['agent_id'])
        
        if detailed_metrics:
            print(f"\n🏆 Top Performer: {detailed_metrics.agent_name}")
            print(f"  Satisfaction Rate: {detailed_metrics.feedback_ratio:.1%}")
            print(f"  Average Response Time: {detailed_metrics.average_response_time_ms:.0f}ms")
            print(f"  Routing Confidence: {detailed_metrics.average_routing_confidence:.1%}")
            print(f"  Recent Activity: {detailed_metrics.responses_last_24h} (24h), {detailed_metrics.responses_last_7d} (7d)")

def demonstrate_dashboard():
    """Demonstrate the analytics dashboard."""
    print("\n📋 Demonstrating Analytics Dashboard")
    print("=" * 50)
    
    from analytics_dashboard import generate_analytics_dashboard, get_quick_performance_summary
    
    # Generate quick summary
    quick_summary = get_quick_performance_summary()
    print("Quick Performance Summary:")
    print(quick_summary)
    
    # Generate full dashboard
    print("\n" + "=" * 60)
    print("FULL ANALYTICS DASHBOARD")
    print("=" * 60)
    
    full_dashboard = generate_analytics_dashboard(days=7, include_details=True)
    print(full_dashboard)

def demonstrate_tool_functions():
    """Demonstrate the tool functions that agents can use."""
    print("\n🔧 Demonstrating Tool Functions")
    print("=" * 50)
    
    from feedback_analytics import (
        get_feedback_summary,
        get_feedback_system_health,
        get_all_agent_performance_metrics
    )
    
    # Test feedback summary tool
    print("Feedback Summary Tool:")
    summary_result = get_feedback_summary(7)
    print(summary_result[:200] + "..." if len(summary_result) > 200 else summary_result)
    
    print("\nSystem Health Tool:")
    health_result = get_feedback_system_health()
    print(health_result[:200] + "..." if len(health_result) > 200 else health_result)
    
    print("\nAll Agent Performance Tool:")
    performance_result = get_all_agent_performance_metrics()
    print(performance_result[:300] + "..." if len(performance_result) > 300 else performance_result)

def main():
    """Run the complete demonstration."""
    print("🚀 Feedback Analytics System Demonstration")
    print("=" * 60)
    
    # Simulate realistic feedback data
    analytics = simulate_realistic_feedback()
    
    # Demonstrate analytics capabilities
    demonstrate_analytics(analytics)
    
    # Demonstrate dashboard
    demonstrate_dashboard()
    
    # Demonstrate tool functions
    demonstrate_tool_functions()
    
    print("\n" + "=" * 60)
    print("🎉 Demonstration Complete!")
    print("\nThe feedback analytics system is ready for production use.")
    print("Agents can now:")
    print("- Track user satisfaction with 👍/👎 ratings")
    print("- Monitor their own performance metrics")
    print("- Generate analytics dashboards")
    print("- Compare performance with other agents")
    print("- Identify areas for improvement")

if __name__ == "__main__":
    main()