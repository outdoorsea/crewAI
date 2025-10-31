#!/usr/bin/env python3
"""
Test script to demonstrate terminal logging in action
"""

from crewai_myndy_pipeline import Pipeline

def test_pipeline_logging():
    """Test pipeline with terminal logging"""
    print("=" * 60)
    print("🧪 Testing Myndy AI Pipeline Terminal Logging")
    print("=" * 60)
    print()
    
    # Initialize pipeline (will show initialization logs)
    print("🚀 Initializing pipeline...")
    pipeline = Pipeline()
    print()
    
    # Test model listing
    print("📋 Testing model listing...")
    models = pipeline.get_models()
    print(f"✅ Retrieved {len(models)} models")
    print()
    
    # Test message processing with different agents
    test_messages = [
        {
            "message": "What's the weather like today?",
            "model": "auto",
            "expected_agent": "personal_assistant"
        },
        {
            "message": "Remember that John Doe works at Google",
            "model": "auto", 
            "expected_agent": "memory_librarian"
        },
        {
            "message": "Track my recent expenses",
            "model": "finance_tracker",
            "expected_agent": "finance_tracker"
        }
    ]
    
    print("🎯 Testing message processing with logging...")
    print()
    
    for i, test in enumerate(test_messages, 1):
        print(f"🧪 Test {i}: {test['message'][:50]}...")
        
        # Create mock messages array
        messages = [{"role": "user", "content": test["message"]}]
        
        try:
            # This will trigger all the logging we added
            response = pipeline.pipe(
                user_message=test["message"],
                model_id=test["model"],
                messages=messages,
                body={}
            )
            print(f"✅ Response received (length: {len(response)} chars)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    print()
    print("🎉 Terminal logging test completed!")
    print("📝 Check the logs above to see the detailed pipeline execution flow")

if __name__ == "__main__":
    test_pipeline_logging()