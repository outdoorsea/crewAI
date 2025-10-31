"""
Basic Usage Example for CrewAI-Myndy Integration

This example demonstrates how to use the CrewAI integration with Myndy
for basic personal productivity tasks.

File: examples/basic_usage.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from crews import create_personal_productivity_crew
from memory import get_memory_bridge


def main():
    """Demonstrate basic usage of the CrewAI-Myndy integration."""
    
    print("CrewAI-Myndy Integration - Basic Usage Example")
    print("=" * 50)
    
    # Create the personal productivity crew
    print("1. Creating Personal Productivity Crew...")
    crew_manager = create_personal_productivity_crew(verbose=True)
    
    # Get available agents
    agents = crew_manager.get_agents()
    print(f"✅ Created crew with {len(agents)} agents:")
    for role, agent in agents.items():
        print(f"   • {role}: {agent.role}")
    
    # Check memory system
    print("\n2. Checking Memory System...")
    memory_bridge = get_memory_bridge("demo_user")
    memory_stats = memory_bridge.get_memory_stats()
    print(f"Memory system available: {memory_stats.get('available', False)}")
    
    # Example 1: Life Analysis Task
    print("\n3. Creating Life Analysis Task...")
    life_analysis_task = crew_manager.create_life_analysis_task("last 7 days")
    print(f"✅ Task created: {life_analysis_task.description[:100]}...")
    
    # Example 2: Research Task
    print("\n4. Creating Research Task...")
    research_task = crew_manager.create_research_project_task(
        topic="Personal productivity best practices",
        depth="detailed"
    )
    print(f"✅ Task created: {research_task.description[:100]}...")
    
    # Example 3: Health Optimization Task
    print("\n5. Creating Health Optimization Task...")
    health_task = crew_manager.create_health_optimization_task("sleep quality")
    print(f"✅ Task created: {health_task.description[:100]}...")
    
    # Example 4: Financial Planning Task
    print("\n6. Creating Financial Planning Task...")
    finance_task = crew_manager.create_financial_planning_task(
        goal="Save $5000 for emergency fund",
        timeframe="6 months"
    )
    print(f"✅ Task created: {finance_task.description[:100]}...")
    
    print("\n" + "=" * 50)
    print("Basic setup completed successfully!")
    print("\nTo execute tasks, you would run:")
    print("  result = crew_manager.execute_task(task)")
    print("\nNote: Task execution requires:")
    print("  • CrewAI dependencies installed")
    print("  • Ollama running with appropriate models")
    print("  • Myndy system properly configured")


if __name__ == "__main__":
    main()