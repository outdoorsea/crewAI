#!/usr/bin/env python3
"""
Test script to verify comprehensive memory storage tools are working
"""

import sys
from pathlib import Path

# Add the crewAI directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.myndy_ai_beta import PipelineBeta

def test_memory_storage():
    """Test comprehensive memory storage with tool visibility"""
    print("🧪 Testing Comprehensive Memory Storage")
    print("=" * 50)
    
    # Initialize pipeline with tool visibility enabled
    pipeline = PipelineBeta()
    pipeline.valves.verbose_coordination = True
    pipeline.valves.trace_tool_selection = True
    pipeline.valves.show_agent_thoughts = True
    pipeline.valves.show_tool_execution = True
    pipeline.valves.show_tool_results = True
    
    print("🧠 Enhanced Visibility: Tool execution enabled")
    print("=" * 50)
    
    # Test case with entities that should trigger memory storage
    test_message = "Brent Bushnell is the owner of Two Bit Circus and my friend. We're working on Dream Park, an AR game for Oculus Quest 2."
    
    print(f"💭 Test Message: {test_message}")
    print()
    
    try:
        # Create test messages
        messages = [{"role": "user", "content": test_message}]
        
        # Run through pipeline
        response = pipeline.pipe(
            user_message=test_message,
            model_id="memory_librarian",  # Force memory librarian
            messages=messages,
            body={}
        )
        
        print(f"📝 Response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_storage()