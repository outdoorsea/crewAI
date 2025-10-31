#!/usr/bin/env python3
"""
Test script to verify intelligent routing

File: test_routing.py
"""

import sys
from pathlib import Path

# Setup paths
CREWAI_PATH = Path("/Users/jeremy/crewAI")
sys.path.insert(0, str(CREWAI_PATH))

def test_routing():
    """Test the intelligent routing system"""
    print("🧪 Testing Intelligent Routing")
    print("=" * 50)
    
    # Import the pipeline
    from pipeline.crewai_memex_pipeline import IntelligentRouter
    
    router = IntelligentRouter()
    
    test_messages = [
        "What is the temperature in Seattle right now?",
        "Can you remember my contact John Smith?",
        "Analyze this document for sentiment",
        "What are my expenses this month?",
        "How many steps did I walk today?",
        "What time is it?",
        "Schedule a meeting for tomorrow",
        "What's the weather forecast?"
    ]
    
    for message in test_messages:
        print(f"\n📝 Message: '{message}'")
        decision = router.analyze_message(message)
        print(f"🎯 Routed to: {decision.primary_agent}")
        print(f"🔥 Confidence: {decision.confidence:.2f}")
        print(f"💭 Reasoning: {decision.reasoning}")

if __name__ == "__main__":
    test_routing()