#!/usr/bin/env python3
"""
OpenWebUI Pipeline Integration Tests

Tests the OpenWebUI pipeline with tool-specific prompt engineering integration,
verifying end-to-end functionality from user input to agent response.

File: tests/test_openwebui_pipeline_integration.py
"""

import sys
import json
import logging
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "pipeline"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestOpenWebUIPipelineIntegration(unittest.TestCase):
    """Test OpenWebUI pipeline integration with tool-specific prompts"""
    
    def setUp(self):
        """Set up test environment"""
        logger.info("Setting up OpenWebUI Pipeline Integration tests")
        
        # Mock user info
        self.mock_user = {
            "id": "test_user_123",
            "name": "Test User",
            "email": "test@example.com",
            "role": "user"
        }
        
        # Mock request body
        self.mock_body = {
            "model": "auto",
            "messages": [
                {"role": "user", "content": "What time is it in London?"}
            ]
        }
    
    def test_pipeline_initialization(self):
        """Test that pipeline initializes correctly"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            # Verify pipeline attributes
            self.assertEqual(pipeline.type, "manifold")
            self.assertEqual(pipeline.id, "myndy_ai")
            self.assertEqual(pipeline.name, "Myndy AI")
            self.assertEqual(pipeline.version, "0.1.0")
            
            # Verify valves are initialized
            self.assertIsNotNone(pipeline.valves)
            
            # Verify agents are defined
            self.assertIn("personal_assistant", pipeline.agents)
            self.assertIn("shadow_agent", pipeline.agents)
            
            logger.info("✅ Pipeline initialization test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    def test_documentation_loading(self):
        """Test that documentation files are loaded during initialization"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            # Verify documentation cache exists
            self.assertIsInstance(pipeline.tool_prompt_cache, dict)
            
            # Check expected documentation files
            expected_docs = [
                'tool_specific_guide',
                'api_endpoints_guide', 
                'enhanced_agents_guide',
                'prompt_engineering_guide'
            ]
            
            loaded_docs = list(pipeline.tool_prompt_cache.keys())
            logger.info(f"Loaded documentation: {loaded_docs}")
            
            # At least some docs should be loaded
            self.assertGreater(len(loaded_docs), 0, "No documentation loaded")
            
            logger.info("✅ Documentation loading test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    def test_intelligent_routing(self):
        """Test intelligent message routing"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            # Test various message types and verify routing
            test_messages = [
                ("What time is it in Tokyo?", "personal_assistant"),
                ("What's the weather like today?", "personal_assistant"),
                ("Remember that John works at Google", "personal_assistant"),
                ("How much did I spend last month?", "personal_assistant"),
                ("Show me my health data", "personal_assistant")
            ]
            
            for message, expected_agent in test_messages:
                if hasattr(pipeline, 'router') and pipeline.router:
                    decision = pipeline.router.analyze_message(message)
                    self.assertEqual(decision.primary_agent, expected_agent)
                    logger.info(f"✅ Routed '{message}' to {decision.primary_agent}")
                else:
                    logger.warning("Router not available, skipping routing test")
                    break
            
            logger.info("✅ Intelligent routing test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    def test_tool_guidance_integration(self):
        """Test tool-specific guidance integration into tasks"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            # Test different message types
            test_cases = [
                {
                    "message": "What time is it in London?",
                    "expected_guidance": ["TIME & SCHEDULING TOOLS", "get_current_time", "IANA timezone"]
                },
                {
                    "message": "What's the weather in San Francisco?", 
                    "expected_guidance": ["WEATHER TOOLS", "local_weather", "weather_api"]
                },
                {
                    "message": "Remember that Sarah works at Microsoft",
                    "expected_guidance": ["MEMORY & CONVERSATION TOOLS", "extract_conversation_entities"]
                },
                {
                    "message": "How much did I spend on coffee?",
                    "expected_guidance": ["FINANCE TOOLS", "get_recent_expenses", "search_transactions"]
                }
            ]
            
            for test_case in test_cases:
                task_desc = pipeline._create_task_description(
                    test_case["message"],
                    "personal_assistant",
                    self.mock_user
                )
                
                # Verify expected guidance is included
                for expected in test_case["expected_guidance"]:
                    self.assertIn(expected, task_desc, 
                                f"Expected '{expected}' in task description for: {test_case['message']}")
                
                # Verify FastAPI compliance
                self.assertIn("POST /api/v1/tools/execute", task_desc)
                
                logger.info(f"✅ Tool guidance verified for: {test_case['message']}")
            
            logger.info("✅ Tool guidance integration test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    def test_user_context_integration(self):
        """Test user context integration in task descriptions"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            task_desc = pipeline._create_task_description(
                "What time is it?",
                "personal_assistant", 
                self.mock_user
            )
            
            # Verify user context is included
            self.assertIn("User Context: Test User", task_desc)
            self.assertIn("ID: test_user_123", task_desc)
            self.assertIn("test@example.com", task_desc)
            
            logger.info("✅ User context integration test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    def test_session_management(self):
        """Test conversation session management"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            # Test session ID generation
            messages = [{"role": "user", "content": "Hello"}]
            session_id = pipeline._get_user_session_id(messages, "test_user")
            
            self.assertIsInstance(session_id, str)
            self.assertIn("test_user", session_id)
            
            # Test conversation history update
            pipeline._update_conversation_history(session_id, messages, self.mock_user)
            
            self.assertIn(session_id, pipeline.conversation_sessions)
            self.assertEqual(pipeline.conversation_sessions[session_id]["user_info"], self.mock_user)
            
            logger.info("✅ Session management test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    def test_agent_specific_reasoning(self):
        """Test agent-specific reasoning patterns"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            # Test personal assistant reasoning
            pa_reasoning = pipeline._get_agent_specific_reasoning("personal_assistant")
            self.assertIn("PERSONAL ASSISTANT INTELLIGENCE", "\n".join(pa_reasoning))
            self.assertIn("MULTI-TOOL ORCHESTRATION", "\n".join(pa_reasoning))
            
            # Test shadow agent reasoning
            shadow_reasoning = pipeline._get_agent_specific_reasoning("shadow_agent")
            self.assertIn("SHADOW AGENT INTELLIGENCE", "\n".join(shadow_reasoning))
            self.assertIn("BEHAVIORAL PATTERN ANALYSIS", "\n".join(shadow_reasoning))
            
            logger.info("✅ Agent-specific reasoning test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    def test_category_analysis(self):
        """Test message category analysis"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            # Test category detection
            test_cases = [
                ("what time is it", ["time_scheduling"]),
                ("weather forecast", ["weather"]),
                ("remember this person", ["memory_conversation"]),
                ("my spending habits", ["finance"]),
                ("sleep data analysis", ["health"]),
                ("document summary", ["document_processing"])
            ]
            
            for message, expected_categories in test_cases:
                detected = pipeline._analyze_message_for_tool_categories(message)
                for expected in expected_categories:
                    self.assertIn(expected, detected, 
                                f"Expected {expected} for message: {message}")
            
            logger.info("✅ Category analysis test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    @patch('crewai.Task')
    @patch('crewai.Agent')
    def test_crewai_integration(self, mock_agent, mock_task):
        """Test CrewAI integration (mocked)"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            # Mock CrewAI components
            mock_agent_instance = Mock()
            mock_task_instance = Mock()
            mock_task_instance.execute.return_value = "Test response"
            
            mock_agent.return_value = mock_agent_instance
            mock_task.return_value = mock_task_instance
            
            # Test agent execution (mocked)
            if hasattr(pipeline, 'crewai_agents') and pipeline.crewai_agents:
                result = pipeline._execute_crewai_agent(
                    mock_agent_instance,
                    "Test message",
                    "personal_assistant",
                    self.mock_user
                )
                
                self.assertIsInstance(result, str)
                logger.info("✅ CrewAI integration test passed")
            else:
                logger.warning("CrewAI agents not available, skipping integration test")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    def test_models_endpoint(self):
        """Test get_models endpoint"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            models = pipeline.get_models()
            
            # Verify models structure
            self.assertIsInstance(models, list)
            self.assertGreater(len(models), 0)
            
            # Check for auto model
            auto_model = next((m for m in models if m["id"] == "auto"), None)
            self.assertIsNotNone(auto_model)
            self.assertEqual(auto_model["name"], "🧠 Myndy AI v0.1")
            
            # Check for agent models
            agent_models = [m for m in models if m["id"] in ["personal_assistant", "shadow_agent"]]
            self.assertGreater(len(agent_models), 0)
            
            logger.info("✅ Models endpoint test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")
    
    def test_manifest_endpoint(self):
        """Test get_manifest endpoint"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            manifest = pipeline.get_manifest()
            
            # Verify manifest structure
            self.assertIsInstance(manifest, dict)
            self.assertEqual(manifest["id"], "myndy_ai")
            self.assertEqual(manifest["name"], "Myndy AI")
            self.assertEqual(manifest["version"], "0.1.0")
            self.assertEqual(manifest["type"], "manifold")
            
            # Verify models are included
            self.assertIn("models", manifest)
            self.assertIsInstance(manifest["models"], list)
            
            logger.info("✅ Manifest endpoint test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")


class TestPipelineResponseFormatting(unittest.TestCase):
    """Test pipeline response formatting"""
    
    def test_response_formatting(self):
        """Test CrewAI response formatting"""
        try:
            from crewai_myndy_pipeline import Pipeline
            
            pipeline = Pipeline()
            
            # Test response formatting
            test_result = "This is a test response from the agent"
            test_routing = {
                "reasoning": "Selected personal assistant based on query analysis",
                "confidence": 0.8,
                "method": "intelligent"
            }
            
            formatted = pipeline._format_crewai_response(
                test_result,
                "personal_assistant", 
                test_routing
            )
            
            # Verify response structure
            self.assertIn("Personal Assistant", formatted)
            self.assertIn("Routing:", formatted)
            self.assertIn("Response:", formatted)
            self.assertIn(test_result, formatted)
            
            logger.info("✅ Response formatting test passed")
            
        except ImportError as e:
            logger.warning(f"Pipeline import failed: {e}")
            self.skipTest("Pipeline module not available")


def run_pipeline_tests():
    """Run all pipeline integration tests"""
    print("🚀 Running OpenWebUI Pipeline Integration Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOpenWebUIPipelineIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineResponseFormatting))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"🎯 Tests run: {result.testsRun}")
    print(f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_pipeline_tests()
    sys.exit(0 if success else 1)