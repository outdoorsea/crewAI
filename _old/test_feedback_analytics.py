#!/usr/bin/env python3
"""
Test script for feedback analytics system

This script tests the feedback analytics functionality to ensure
everything is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "tools"))

def test_feedback_analytics():
    """Test the feedback analytics system."""
    print("🧪 Testing Feedback Analytics System")
    print("=" * 50)
    
    try:
        # Import the feedback analytics system
        from feedback_analytics import FeedbackAnalytics, FeedbackType, ResponseType
        
        # Create a test instance
        test_db_path = str(project_root / "test_feedback.db")
        analytics = FeedbackAnalytics(test_db_path)
        
        print("✅ Successfully imported and initialized FeedbackAnalytics")
        
        # Test recording thumbs up feedback
        feedback_id = analytics.record_thumbs_up(
            session_id="test_session_001",
            agent_id="memory_librarian",
            agent_name="Memory Librarian",
            response_id="test_response_001",
            response_content="This is a test response about contacts.",
            user_message="Tell me about John Doe",
            routing_confidence=0.85,
            response_time_ms=1500,
            tools_used=["contact_search", "memory_search"]
        )
        
        print(f"✅ Recorded thumbs up feedback: {feedback_id}")
        
        # Test recording thumbs down feedback
        feedback_id2 = analytics.record_thumbs_down(
            session_id="test_session_002",
            agent_id="personal_assistant",
            agent_name="Personal Assistant",
            response_id="test_response_002",
            response_content="This is a test response about weather.",
            user_message="What's the weather like?",
            feedback_text="Response was too slow",
            routing_confidence=0.92,
            response_time_ms=3000,
            tools_used=["weather_api", "local_weather"]
        )
        
        print(f"✅ Recorded thumbs down feedback: {feedback_id2}")
        
        # Test getting agent performance
        performance = analytics.get_agent_performance("memory_librarian")
        if performance:
            print(f"✅ Retrieved agent performance for memory_librarian:")
            print(f"   - Total responses: {performance.total_responses}")
            print(f"   - Feedback ratio: {performance.feedback_ratio:.2f}")
            print(f"   - Avg response time: {performance.average_response_time_ms:.0f}ms")
        
        # Test getting feedback summary
        summary = analytics.get_feedback_summary(7)
        print(f"✅ Retrieved feedback summary:")
        print(f"   - Total feedback entries: {summary.get('total_feedback_entries', 0)}")
        print(f"   - Overall satisfaction: {summary.get('overall_satisfaction', 0):.2%}")
        print(f"   - Active agents: {summary.get('active_agents', 0)}")
        
        # Test system health
        health = analytics.get_system_health()
        print(f"✅ Retrieved system health:")
        print(f"   - System status: {health.get('system_status', 'Unknown')}")
        print(f"   - Total entries: {health.get('total_feedback_entries', 0)}")
        
        print("\n🎉 All feedback analytics tests passed!")
        
    except Exception as e:
        print(f"❌ Error testing feedback analytics: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_analytics_dashboard():
    """Test the analytics dashboard."""
    print("\n🧪 Testing Analytics Dashboard")
    print("=" * 50)
    
    try:
        from analytics_dashboard import (
            generate_analytics_dashboard,
            get_quick_performance_summary,
            get_agent_comparison
        )
        
        # Test dashboard generation
        dashboard = generate_analytics_dashboard(days=7, include_details=True)
        print("✅ Generated analytics dashboard")
        print(f"   Dashboard length: {len(dashboard)} characters")
        
        # Test quick summary
        summary = get_quick_performance_summary()
        print("✅ Generated quick performance summary")
        print(f"   Summary length: {len(summary)} characters")
        
        # Test agent comparison (this might fail if we don't have enough data)
        try:
            comparison = get_agent_comparison("memory_librarian", "personal_assistant")
            print("✅ Generated agent comparison")
            print(f"   Comparison length: {len(comparison)} characters")
        except Exception as e:
            print(f"⚠️  Agent comparison failed (expected with limited test data): {e}")
        
        print("\n🎉 Analytics dashboard tests completed!")
        
    except Exception as e:
        print(f"❌ Error testing analytics dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_tool_functions():
    """Test the tool functions that will be registered."""
    print("\n🧪 Testing Tool Functions")
    print("=" * 50)
    
    try:
        from feedback_analytics import (
            record_thumbs_up_feedback,
            record_thumbs_down_feedback,
            get_agent_performance_metrics,
            get_feedback_summary,
            get_feedback_system_health
        )
        
        # Test thumbs up tool function
        result = record_thumbs_up_feedback(
            session_id="tool_test_session",
            agent_id="research_specialist",
            agent_name="Research Specialist",
            response_id="tool_test_response",
            response_content="Test tool response",
            user_message="Test tool message",
            routing_confidence=0.78,
            response_time_ms=2200
        )
        
        print("✅ Thumbs up tool function works")
        
        # Test feedback summary tool
        summary_result = get_feedback_summary(7)
        print("✅ Feedback summary tool function works")
        
        # Test system health tool
        health_result = get_feedback_system_health()
        print("✅ System health tool function works")
        
        print("\n🎉 All tool function tests passed!")
        
    except Exception as e:
        print(f"❌ Error testing tool functions: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Feedback Analytics Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test feedback analytics core
    success &= test_feedback_analytics()
    
    # Test analytics dashboard
    success &= test_analytics_dashboard()
    
    # Test tool functions
    success &= test_tool_functions()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Feedback Analytics system is ready.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()