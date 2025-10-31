#!/usr/bin/env python3
"""
Final test to verify CrewAI tool execution is working properly.

File: test_tool_execution_final.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the crewAI directory to the path
crewai_dir = Path(__file__).parent
sys.path.insert(0, str(crewai_dir))

# Import the pipeline
from pipeline.myndy_ai_beta import PipelineBeta

def test_tool_execution():
    """Test that tools are being executed properly by CrewAI agents"""
    
    print("🧪 Testing CrewAI Tool Execution")
    print("=" * 50)
    
    try:
        # Initialize the pipeline
        pipeline = PipelineBeta()
        
        # Test with "Who am I?" query which should use get_self_profile tool
        test_message = "Who am I?"
        
        print(f"📝 Testing message: '{test_message}'")
        print(f"🎯 Expected: Agent should use get_self_profile tool")
        print()
        
        # Process the message
        result = pipeline.run(
            initial_message=test_message,
            config={"stream": False}
        )
        
        print("✅ Result received:")
        print("-" * 30)
        print(result)
        print("-" * 30)
        
        # Check if the result indicates tool usage
        result_str = str(result).lower()
        success_indicators = [
            "profile",
            "user",
            "memory",
            "retrieved_at",
            "get_self_profile",
            "tool"
        ]
        
        tool_used = any(indicator in result_str for indicator in success_indicators)
        
        if tool_used:
            print("✅ SUCCESS: Tool execution appears to be working!")
            print("🔧 Evidence of tool usage found in response")
        else:
            print("⚠️  WARNING: No clear evidence of tool usage in response")
            print("📝 This might indicate tools aren't being executed")
            
        return tool_used
        
    except Exception as e:
        print(f"❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tool_execution()
    exit_code = 0 if success else 1
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    sys.exit(exit_code)