#!/usr/bin/env python3
"""
Complex Multi-Agent Workflow Demonstration

This script demonstrates sophisticated multi-agent workflows using CrewAI
in the Myndy ecosystem. Run this to see agents collaborating on complex tasks.

File: examples/complex_workflow_demo.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from crews import create_personal_productivity_crew
from crewai import Task, Crew, Process


def demo_sequential_workflow():
    """
    Demo 1: Sequential workflow where each agent builds on previous results.

    Scenario: Plan a health improvement initiative with budget and schedule.
    """
    print("\n" + "=" * 70)
    print("DEMO 1: Sequential Workflow - Health Improvement Planning")
    print("=" * 70 + "\n")

    crew_manager = create_personal_productivity_crew(verbose=True)
    agents = crew_manager.get_agents()

    tasks = [
        Task(
            description="""
            Analyze current health status and identify one key area for improvement.
            Focus on metrics we have data for. Recommend a specific, achievable goal.
            """,
            agent=agents["health_analyst"],
            expected_output="Health analysis with one specific improvement recommendation"
        ),

        Task(
            description="""
            Based on the health recommendation above, research best practices
            for achieving that goal. Find 3-5 actionable strategies.
            """,
            agent=agents["research_specialist"],
            expected_output="Research summary with actionable strategies"
        ),

        Task(
            description="""
            Based on the strategies above, create a budget for implementing
            this health improvement plan. Include any equipment, subscriptions,
            or services needed.
            """,
            agent=agents["finance_tracker"],
            expected_output="Budget breakdown with cost justifications"
        ),

        Task(
            description="""
            Based on the plan and budget above, create a 30-day implementation
            schedule. Include specific activities, time blocks, and milestones.
            """,
            agent=agents["personal_assistant"],
            expected_output="30-day implementation schedule"
        ),

        Task(
            description="""
            Document the complete health improvement plan in memory for tracking.
            Include all components: goal, research, budget, and schedule.
            Create a tracking framework for progress monitoring.
            """,
            agent=agents["memory_librarian"],
            expected_output="Complete documented plan with tracking setup"
        )
    ]

    sequential_crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=True
    )

    print("Executing sequential workflow...")
    result = sequential_crew.kickoff()

    print("\n" + "=" * 70)
    print("SEQUENTIAL WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"\nResult:\n{result}\n")


def demo_parallel_workflow():
    """
    Demo 2: Parallel workflow where multiple agents work simultaneously.

    Scenario: Comprehensive life analysis across multiple domains.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: Parallel Workflow - Comprehensive Life Analysis")
    print("=" * 70 + "\n")

    crew_manager = create_personal_productivity_crew(verbose=True)
    agents = crew_manager.get_agents()

    tasks = [
        Task(
            description="""
            Analyze last month's health and wellness:
            - Sleep patterns
            - Activity levels
            - Overall wellness trends
            Provide summary with key insights.
            """,
            agent=agents["health_analyst"],
            expected_output="Health analysis summary"
        ),

        Task(
            description="""
            Analyze last month's financial health:
            - Spending patterns
            - Budget adherence
            - Savings progress
            Provide summary with key insights.
            """,
            agent=agents["finance_tracker"],
            expected_output="Financial analysis summary"
        ),

        Task(
            description="""
            Analyze last month's productivity:
            - Task completion rates
            - Schedule efficiency
            - Time management
            Provide summary with key insights.
            """,
            agent=agents["personal_assistant"],
            expected_output="Productivity analysis summary"
        ),

        Task(
            description="""
            Analyze last month's memory and relationships:
            - Key interactions
            - Important events
            - Relationship patterns
            Provide summary with key insights.
            """,
            agent=agents["memory_librarian"],
            expected_output="Memory and relationship summary"
        )
    ]

    parallel_crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.parallel,  # Execute simultaneously
        verbose=True,
        memory=True
    )

    print("Executing parallel workflow (agents working simultaneously)...")
    result = parallel_crew.kickoff()

    print("\n" + "=" * 70)
    print("PARALLEL WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"\nResult:\n{result}\n")


def demo_collaborative_workflow():
    """
    Demo 3: Collaborative workflow where agents delegate and share context.

    Scenario: Complex research project requiring multiple expertise areas.
    """
    print("\n" + "=" * 70)
    print("DEMO 3: Collaborative Workflow - Complex Research Project")
    print("=" * 70 + "\n")

    crew_manager = create_personal_productivity_crew(verbose=True)
    agents = crew_manager.get_agents()

    # Enable delegation for collaboration
    for agent in agents.values():
        agent.allow_delegation = True

    task = Task(
        description="""
        Research and create a comprehensive plan for "improving sleep quality":

        This requires collaboration:
        1. Research Specialist: Gather scientific literature on sleep optimization
        2. Health Analyst: Analyze current sleep patterns and identify specific issues
        3. Finance Tracker: Budget for any sleep aids, tools, or environmental improvements
        4. Personal Assistant: Create bedtime routine and schedule adjustments
        5. Memory Librarian: Document findings and set up progress tracking

        Work together to create a holistic, personalized sleep improvement plan.
        Each agent should contribute their expertise and coordinate with others.
        """,
        agent=agents["research_specialist"],  # Lead agent
        expected_output="""
        Comprehensive sleep optimization plan including:
        - Scientific research summary
        - Personal sleep analysis
        - Budget for improvements
        - Implementation schedule
        - Tracking system setup
        """
    )

    collaborative_crew = Crew(
        agents=list(agents.values()),
        tasks=[task],
        process=Process.sequential,
        verbose=True,
        memory=True
    )

    print("Executing collaborative workflow (agents will delegate subtasks)...")
    result = collaborative_crew.kickoff()

    print("\n" + "=" * 70)
    print("COLLABORATIVE WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"\nResult:\n{result}\n")


def demo_adaptive_workflow():
    """
    Demo 4: Adaptive workflow that changes based on intermediate results.

    Scenario: Health concern analysis that adapts routing based on severity.
    """
    print("\n" + "=" * 70)
    print("DEMO 4: Adaptive Workflow - Health Concern Analysis")
    print("=" * 70 + "\n")

    crew_manager = create_personal_productivity_crew(verbose=True)
    agents = crew_manager.get_agents()

    # Step 1: Analyze severity
    print("Step 1: Analyzing health concern severity...")

    analysis_task = Task(
        description="""
        Analyze this health concern: "I've been feeling more tired than usual lately"

        Assess and categorize:
        - Severity: minor/moderate/serious
        - Urgency: routine/urgent/emergency
        - Required action: monitoring/planning/immediate

        Based on available health data.
        """,
        agent=agents["health_analyst"],
        expected_output="Severity assessment with recommended action level"
    )

    analysis = crew_manager.execute_task(analysis_task)
    print(f"\nSeverity Analysis:\n{analysis}\n")

    # Step 2: Adaptive routing based on analysis
    if "serious" in analysis.lower() or "urgent" in analysis.lower():
        print("→ HIGH SEVERITY: Creating immediate action plan...")

        action_task = Task(
            description="""
            URGENT health concern identified. Create immediate action plan:
            - Immediate steps to take
            - When to seek medical attention
            - Monitoring protocol
            - Emergency contacts
            """,
            agent=agents["health_analyst"],
            expected_output="Immediate action plan"
        )

        result = crew_manager.execute_task(action_task)

    elif "moderate" in analysis.lower():
        print("→ MODERATE SEVERITY: Creating comprehensive improvement plan...")

        tasks = [
            Task(
                description="Research common causes and solutions for fatigue",
                agent=agents["research_specialist"],
                expected_output="Research findings"
            ),
            Task(
                description="Create health improvement plan addressing fatigue",
                agent=agents["health_analyst"],
                expected_output="Health improvement plan"
            ),
            Task(
                description="Schedule lifestyle adjustments for better energy",
                agent=agents["personal_assistant"],
                expected_output="Schedule with adjustments"
            )
        ]

        result = crew_manager.execute_tasks(tasks)

    else:
        print("→ MINOR SEVERITY: Setting up monitoring...")

        monitoring_task = Task(
            description="""
            Set up routine monitoring for mild fatigue:
            - Daily energy level tracking
            - Sleep quality monitoring
            - Activity level recording
            - Weekly review schedule
            """,
            agent=agents["health_analyst"],
            expected_output="Monitoring setup"
        )

        result = crew_manager.execute_task(monitoring_task)

    print("\n" + "=" * 70)
    print("ADAPTIVE WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"\nResult:\n{result}\n")


def demo_complex_goal_planning():
    """
    Demo 5: Complex multi-phase goal planning workflow.

    Scenario: Complete goal planning from concept to tracking.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: Complex Goal Planning - Marathon Training")
    print("=" * 70 + "\n")

    crew_manager = create_personal_productivity_crew(verbose=True)
    agents = crew_manager.get_agents()

    print("Phase 1: Feasibility Analysis")
    print("-" * 70)

    feasibility_tasks = [
        Task(
            description="""
            Research marathon training requirements:
            - Typical training duration
            - Common training programs
            - Success factors
            - Risk factors
            """,
            agent=agents["research_specialist"],
            expected_output="Feasibility analysis"
        ),

        Task(
            description="""
            Assess current fitness level for marathon training:
            - Current running capability
            - Health baseline
            - Injury risk factors
            - Training readiness
            """,
            agent=agents["health_analyst"],
            expected_output="Fitness readiness assessment"
        )
    ]

    feasibility_results = crew_manager.execute_tasks(feasibility_tasks)
    print(f"\nFeasibility Analysis Complete:\n{feasibility_results}\n")

    print("\nPhase 2: Detailed Planning")
    print("-" * 70)

    planning_tasks = [
        Task(
            description="""
            Create 16-week marathon training plan:
            - Weekly mileage progression
            - Long run schedule
            - Cross-training days
            - Rest and recovery
            - Milestone races
            """,
            agent=agents["health_analyst"],
            expected_output="16-week training plan"
        ),

        Task(
            description="""
            Create budget for marathon training:
            - Running shoes and gear
            - Race registration
            - Nutrition and hydration
            - Optional coaching or apps
            Total cost and monthly breakdown
            """,
            agent=agents["finance_tracker"],
            expected_output="Training budget"
        ),

        Task(
            description="""
            Integrate training into schedule:
            - Morning vs. evening runs
            - Weekend long run timing
            - Recovery day placement
            - Work schedule coordination
            """,
            agent=agents["personal_assistant"],
            expected_output="Integrated training schedule"
        )
    ]

    planning_results = crew_manager.execute_tasks(planning_tasks)
    print(f"\nDetailed Planning Complete:\n{planning_results}\n")

    print("\nPhase 3: Documentation and Tracking Setup")
    print("-" * 70)

    documentation_task = Task(
        description="""
        Document complete marathon training plan:
        - Goal statement and motivation
        - 16-week training schedule
        - Budget allocation
        - Progress tracking metrics
        - Weekly review process
        - Success criteria

        Store in memory system for ongoing reference and updates.
        """,
        agent=agents["memory_librarian"],
        expected_output="Complete goal documentation"
    )

    documentation = crew_manager.execute_task(documentation_task)
    print(f"\nDocumentation Complete:\n{documentation}\n")

    print("\n" + "=" * 70)
    print("COMPLEX GOAL PLANNING COMPLETE")
    print("=" * 70)


def main():
    """Main demo execution."""
    print("\n" + "=" * 70)
    print("COMPLEX MULTI-AGENT WORKFLOW DEMONSTRATIONS")
    print("=" * 70)
    print("\nThese demos showcase sophisticated agent collaboration patterns:")
    print("1. Sequential - Agents build on each other's work")
    print("2. Parallel - Agents work simultaneously on different aspects")
    print("3. Collaborative - Agents delegate and share context")
    print("4. Adaptive - Workflow changes based on intermediate results")
    print("5. Complex Multi-Phase - Complete goal planning process")
    print("\nEach demo is independent and can be run separately.\n")

    demos = {
        "1": ("Sequential Workflow", demo_sequential_workflow),
        "2": ("Parallel Workflow", demo_parallel_workflow),
        "3": ("Collaborative Workflow", demo_collaborative_workflow),
        "4": ("Adaptive Workflow", demo_adaptive_workflow),
        "5": ("Complex Goal Planning", demo_complex_goal_planning),
        "all": ("All Demos", None)
    }

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("Available demos:")
        for key, (name, _) in demos.items():
            if key != "all":
                print(f"  {key}. {name}")
        print(f"  all. Run all demos")
        print("\nUsage: python complex_workflow_demo.py [demo_number]")
        print("Example: python complex_workflow_demo.py 1")
        choice = input("\nSelect demo number (or 'all'): ").strip()

    if choice == "all":
        for key in ["1", "2", "3", "4", "5"]:
            demos[key][1]()
            input("\nPress Enter to continue to next demo...")
    elif choice in demos:
        demos[choice][1]()
    else:
        print(f"Invalid choice: {choice}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("ALL DEMONSTRATIONS COMPLETE")
    print("=" * 70)
    print("\nFor more information, see: COMPLEX_AGENT_WORKFLOWS_GUIDE.md\n")


if __name__ == "__main__":
    main()
