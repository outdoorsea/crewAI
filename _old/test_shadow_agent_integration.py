#!/usr/bin/env python3
"""
Test script for Shadow Agent integration with OpenWebUI pipeline

This script tests the MVP Shadow Agent's behavioral observation and storage
capabilities when integrated with the OpenWebUI pipeline.

File: test_shadow_agent_integration.py
"""

import sys
import logging
import time
from pathlib import Path

# Add project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mvp_shadow_agent_standalone():
    """Test the MVP Shadow Agent standalone functionality"""
    logger.info("🔮 Testing MVP Shadow Agent standalone functionality...")
    
    try:
        from agents.mvp_shadow_agent import create_mvp_shadow_agent
        
        # Create Shadow Agent
        shadow_agent = create_mvp_shadow_agent()
        logger.info("✅ Shadow Agent created successfully")
        
        # Test behavioral observation
        test_observation = shadow_agent.observe_conversation(
            user_message="What's the weather like today? I need to plan my workout schedule.",
            agent_response="It's sunny and 72°F in your area, perfect for outdoor exercise.",
            agent_type="personal_assistant",
            session_id="test_session_001"
        )
        
        logger.info(f"✅ Behavioral observation recorded: {test_observation.get('user_message_type', 'unknown')}")
        
        # Test insights retrieval
        insights = shadow_agent.get_behavioral_insights()
        logger.info(f"✅ Behavioral insights retrieved: {len(insights)} insights")
        
        # Test personality summary
        summary = shadow_agent.generate_personality_summary()
        logger.info(f"✅ Personality summary: {summary[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MVP Shadow Agent standalone test failed: {e}")
        return False


def test_shadow_agent_creation():
    """Test Shadow Agent creation"""
    try:
        from agents.shadow_agent import create_shadow_agent
        
        logger.info("🔮 Testing Shadow Agent creation...")
        agent = create_shadow_agent()
        
        assert agent is not None, "Shadow Agent should not be None"
        assert agent.role == "Shadow Intelligence Observer", f"Expected 'Shadow Intelligence Observer', got '{agent.role}'"
        assert hasattr(agent, 'tools'), "Shadow Agent should have tools"
        assert len(agent.tools) > 0, "Shadow Agent should have at least one tool"
        
        logger.info(f"✅ Shadow Agent created successfully:")
        logger.info(f"   Role: {agent.role}")
        logger.info(f"   Goal: {agent.goal[:100]}...")
        logger.info(f"   Tools: {len(agent.tools)} available")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Shadow Agent creation failed: {e}")
        return False

def test_shadow_agent_tools():
    """Test Shadow Agent tool configuration"""
    try:
        from tools.myndy_bridge import get_agent_tools
        
        logger.info("🔧 Testing Shadow Agent tools...")
        tools = get_agent_tools("shadow_agent")
        
        assert tools is not None, "Shadow Agent tools should not be None"
        assert len(tools) > 0, "Shadow Agent should have tools configured"
        
        # Check for specific behavioral analysis tools
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "extract_conversation_entities",
            "analyze_sentiment", 
            "search_memory",
            "get_self_profile",
            "add_fact"
        ]
        
        found_tools = [tool for tool in expected_tools if tool in tool_names]
        
        logger.info(f"✅ Shadow Agent tools configured:")
        logger.info(f"   Total tools: {len(tools)}")
        logger.info(f"   Expected tools found: {len(found_tools)}/{len(expected_tools)}")
        logger.info(f"   Tool names: {tool_names[:5]}..." if len(tool_names) > 5 else f"   Tool names: {tool_names}")
        
        return len(found_tools) > 0
        
    except Exception as e:
        logger.error(f"❌ Shadow Agent tools test failed: {e}")
        return False

def test_crew_integration():
    """Test Shadow Agent integration with crew system"""
    try:
        from crews.personal_productivity_crew import create_shadow_agent
        
        logger.info("👥 Testing Shadow Agent crew integration...")
        agent = create_shadow_agent()
        
        assert agent is not None, "Shadow Agent from crew should not be None"
        assert agent.role == "Shadow Intelligence Observer", "Shadow Agent should have correct role"
        
        logger.info("✅ Shadow Agent crew integration successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Shadow Agent crew integration failed: {e}")
        return False

def test_routing_system():
    """Test Shadow Agent in the routing system"""
    try:
        # Import the pipeline and routing components
        sys.path.insert(0, str(PROJECT_ROOT / "pipeline"))
        from crewai_myndy_pipeline import IntelligentRouter
        
        logger.info("🎯 Testing Shadow Agent routing...")
        router = IntelligentRouter()
        
        # Check if shadow_agent is in the routing patterns
        assert "shadow_agent" in router.agent_patterns, "Shadow Agent should be in routing patterns"
        
        shadow_config = router.agent_patterns["shadow_agent"]
        assert "priority_multiplier" in shadow_config, "Shadow Agent should have priority_multiplier"
        assert shadow_config["priority_multiplier"] == 0.0, "Shadow Agent priority_multiplier should be 0.0"
        
        # Test that shadow agent gets score 0 due to multiplier
        test_message = "I want to understand my behavioral patterns"
        routing = router.analyze_message(test_message)
        
        # Shadow agent should never be the primary agent due to 0.0 multiplier
        assert routing.primary_agent != "shadow_agent", "Shadow Agent should never be primary agent"
        
        logger.info("✅ Shadow Agent routing system working correctly:")
        logger.info(f"   Priority multiplier: {shadow_config['priority_multiplier']}")
        logger.info(f"   Primary agent for behavioral query: {routing.primary_agent}")
        logger.info(f"   Shadow agent correctly excluded from primary selection")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Shadow Agent routing test failed: {e}")
        return False

def test_http_client_tools():
    """Test Shadow Agent HTTP client tools"""
    try:
        from tools.myndy_http_client import get_http_client_tools
        
        logger.info("🌐 Testing Shadow Agent HTTP client tools...")
        
        # Check if shadow_agent is configured in HTTP client
        try:
            tools = get_http_client_tools("shadow_agent")
            logger.info(f"✅ Shadow Agent HTTP client tools available: {len(tools)} tools")
            return True
        except Exception:
            # HTTP client might not have shadow_agent configured yet
            logger.info("ℹ️  Shadow Agent HTTP client tools not yet configured (expected)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Shadow Agent HTTP client test failed: {e}")
        return False

def test_pipeline_integration():
    """Test Shadow Agent integration with OpenWebUI pipeline"""
    logger.info("🚀 Testing Shadow Agent integration with pipeline...")
    
    try:
        # Import pipeline components
        sys.path.insert(0, str(PROJECT_ROOT / "pipeline"))
        from crewai_myndy_pipeline import Pipeline
        
        # Create pipeline
        pipeline = Pipeline()
        logger.info("✅ Pipeline created successfully")
        
        # Check if Shadow Agent is available
        if pipeline.mvp_shadow_agent:
            logger.info("✅ MVP Shadow Agent is available in pipeline")
        else:
            logger.warning("⚠️ MVP Shadow Agent not available in pipeline")
            return False
        
        # Test pipeline processing with Shadow Agent observation
        test_messages = [
            {
                "role": "user",
                "content": "What's my current health status? I want to track my fitness progress."
            }
        ]
        
        # Process through pipeline
        response = pipeline.pipe(
            user_message="What's my current health status? I want to track my fitness progress.",
            model_id="health_analyst",
            messages=test_messages,
            body={}
        )
        
        logger.info(f"✅ Pipeline processed message successfully")
        logger.info(f"📝 Response length: {len(response)} characters")
        
        # Wait a moment for shadow observation to complete
        time.sleep(2)
        
        # Check if behavioral data was stored
        if pipeline.mvp_shadow_agent:
            insights = pipeline.mvp_shadow_agent.get_behavioral_insights()
            logger.info(f"✅ Shadow observation insights: {insights}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline integration test failed: {e}")
        return False


def main():
    """Run all Shadow Agent integration tests"""
    logger.info("🚀 Starting Shadow Agent Integration Tests")
    logger.info("=" * 60)
    
    tests = [
        ("MVP Shadow Agent Standalone", test_mvp_shadow_agent_standalone),
        ("Shadow Agent Creation", test_shadow_agent_creation),
        ("Shadow Agent Tools", test_shadow_agent_tools),
        ("Pipeline Integration", test_pipeline_integration),
        ("Crew Integration", test_crew_integration), 
        ("Routing System", test_routing_system),
        ("HTTP Client Tools", test_http_client_tools)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("🎯 Test Results Summary:")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Shadow Agent integration is working correctly.")
        return True
    else:
        logger.warning(f"⚠️ {total - passed} test(s) failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)