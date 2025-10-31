# Complex Agent Workflows with CrewAI

## Overview

This guide explains how to implement sophisticated multi-agent workflows using CrewAI in the Myndy ecosystem. You'll learn how to orchestrate multiple specialized agents to handle complex, multi-step processes that require collaboration across different domains.

## Architecture Overview

### Current Agent System

**5 Specialized Agents**:
1. **Memory Librarian** - Entity management, knowledge organization, conversation history
2. **Research Specialist** - Information gathering, fact verification, document analysis
3. **Personal Assistant** - Calendar, tasks, email, time management
4. **Health Analyst** - Health data analysis, wellness insights, activity tracking
5. **Finance Tracker** - Expense tracking, financial analysis, budget management

**1 Coordination Agent**:
- **Context Manager** - Intelligent routing, delegation decisions, optimization

```
┌─────────────────────────────────────────────────────────────┐
│                  MULTI-AGENT ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐                                       │
│  │ Context Manager  │ ──► Analyzes request complexity      │
│  │   (Coordinator)  │ ──► Routes to optimal agent(s)       │
│  └────────┬─────────┘ ──► Decides collaboration strategy   │
│           │                                                  │
│           ├──────────┬──────────┬──────────┬──────────┐    │
│           │          │          │          │          │     │
│           ▼          ▼          ▼          ▼          ▼     │
│  ┌────────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────┐  │
│  │   Memory   │ │Research│ │Personal│ │ Health │ │Fin │  │
│  │ Librarian  │ │Specialist│Assistant│ Analyst│ │Trk │  │
│  └────────────┘ └────────┘ └────────┘ └────────┘ └────┘  │
│       │              │          │          │          │     │
│       └──────────────┴──────────┴──────────┴──────────┘    │
│                      Shared Memory & Context                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Myndy-AI Backend (85+ Tools)                   │  │
│  │  • Memory System  • Calendar  • Health • Finance     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Concepts

### 1. Sequential Workflows

Agents execute tasks one after another, with each agent building on previous results.

**Use Cases**:
- Life analysis (health → finance → productivity)
- Research projects (gather → analyze → summarize)
- Planning workflows (analyze → plan → schedule → budget)

**Example**:
```python
from crews import create_personal_productivity_crew

# Create the crew
crew = create_personal_productivity_crew(verbose=True)

# Create sequential tasks
task1 = crew.create_health_optimization_task("cardiovascular fitness")
task2 = crew.create_financial_planning_task(
    "Save for gym equipment and nutrition plan",
    timeframe="3 months"
)

# Execute sequentially - each agent sees previous results
results = crew.execute_tasks([task1, task2])
```

### 2. Parallel Workflows

Multiple agents work simultaneously on different aspects of the same problem.

**Use Cases**:
- Comprehensive analysis (multiple domains at once)
- Information gathering from different sources
- Multi-dimensional assessment

**Example**:
```python
from crewai import Crew, Task, Process

# Create parallel process crew
crew_manager = create_personal_productivity_crew()
agents = crew_manager.get_agents()

# Create independent tasks
tasks = [
    Task(
        description="Analyze last month's health metrics",
        agent=agents["health_analyst"],
        expected_output="Health analysis report"
    ),
    Task(
        description="Analyze last month's spending",
        agent=agents["finance_tracker"],
        expected_output="Financial analysis report"
    ),
    Task(
        description="Review calendar efficiency",
        agent=agents["personal_assistant"],
        expected_output="Time management analysis"
    )
]

# Execute in parallel
parallel_crew = Crew(
    agents=list(agents.values()),
    tasks=tasks,
    process=Process.parallel,  # Execute simultaneously
    verbose=True
)

results = parallel_crew.kickoff()
```

### 3. Collaborative Workflows

Agents work together, delegating subtasks and sharing context.

**Use Cases**:
- Complex research requiring multiple expertise areas
- Planning that requires coordination across domains
- Analysis requiring cross-referencing multiple data sources

**Example**:
```python
# Collaborative research project
task = Task(
    description="""
    Research optimal strategies for improving sleep quality:

    1. Research Specialist: Gather scientific literature on sleep optimization
    2. Health Analyst: Analyze my current sleep patterns and identify issues
    3. Finance Tracker: Budget for any recommended tools or supplements
    4. Personal Assistant: Create implementation schedule
    5. Memory Librarian: Document findings and track progress

    Collaborate to create a comprehensive, personalized sleep improvement plan.
    """,
    agent=agents["research_specialist"],  # Lead agent
    expected_output="Comprehensive sleep optimization plan with all aspects covered"
)

# Enable delegation for collaboration
for agent in agents.values():
    agent.allow_delegation = True

results = crew.execute_task(task)
```

## Complex Workflow Patterns

### Pattern 1: Data-Driven Decision Making

**Scenario**: Make a major life decision based on comprehensive personal data analysis.

```python
def create_data_driven_decision_workflow(decision: str, options: list):
    """
    Create a workflow that analyzes personal data to inform a decision.

    Example: "Should I change jobs?" with options ["Stay", "Switch to Company X"]
    """
    crew = create_personal_productivity_crew()
    agents = crew.get_agents()

    tasks = [
        # Task 1: Memory context
        Task(
            description=f"""
            Analyze memory for context about {decision}:
            - Past discussions about career satisfaction
            - Related experiences and outcomes
            - Relevant relationships and conversations
            - Historical patterns in similar decisions
            """,
            agent=agents["memory_librarian"],
            expected_output="Contextual analysis from personal history"
        ),

        # Task 2: Financial impact
        Task(
            description=f"""
            Analyze financial implications of {decision}:
            Options: {options}
            - Current financial position
            - Impact on budget and savings
            - Risk assessment
            - Long-term financial projections
            """,
            agent=agents["finance_tracker"],
            expected_output="Financial impact analysis for each option"
        ),

        # Task 3: Life impact
        Task(
            description=f"""
            Analyze lifestyle implications of {decision}:
            - Schedule and time commitment changes
            - Health and wellness impacts
            - Work-life balance considerations
            - Personal goals alignment
            """,
            agent=agents["personal_assistant"],
            expected_output="Lifestyle impact analysis"
        ),

        # Task 4: Research
        Task(
            description=f"""
            Research external factors for {decision}:
            - Industry trends and outlook
            - Company reputation and culture
            - Career growth opportunities
            - Expert opinions and advice
            """,
            agent=agents["research_specialist"],
            expected_output="External research findings"
        ),

        # Task 5: Synthesis and recommendation
        Task(
            description=f"""
            Synthesize all analyses and provide decision recommendation:

            Consider:
            - Memory context analysis
            - Financial impact assessment
            - Lifestyle implications
            - External research

            Provide clear recommendation with:
            - Pros and cons for each option
            - Risk assessment
            - Decision framework
            - Implementation timeline if proceeding
            """,
            agent=agents["memory_librarian"],  # Coordinator
            expected_output="Comprehensive decision recommendation"
        )
    ]

    crew_instance = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=True
    )

    return crew_instance.kickoff()


# Usage
decision_result = create_data_driven_decision_workflow(
    decision="Should I change jobs?",
    options=["Stay at current company", "Accept offer from Company X"]
)
```

### Pattern 2: Continuous Monitoring & Alerting

**Scenario**: Set up agents to continuously monitor various aspects of life and alert on issues.

```python
from crewai import Task
import schedule
import time

class ContinuousMonitoringCrew:
    """Crew that continuously monitors personal data and alerts on issues."""

    def __init__(self):
        self.crew = create_personal_productivity_crew(verbose=False)
        self.agents = self.crew.get_agents()
        self.alert_callbacks = []

    def create_monitoring_tasks(self):
        """Create tasks that check for issues."""
        return {
            "health": Task(
                description="""
                Monitor health metrics for concerning trends:
                - Check for irregular sleep patterns
                - Monitor activity levels below threshold
                - Identify stress indicators
                - Flag any concerning vital signs

                Alert if issues found.
                """,
                agent=self.agents["health_analyst"],
                expected_output="Health status report with any alerts"
            ),

            "finance": Task(
                description="""
                Monitor financial health for issues:
                - Check for budget overruns
                - Identify unusual spending patterns
                - Monitor savings goals progress
                - Flag any concerning transactions

                Alert if issues found.
                """,
                agent=self.agents["finance_tracker"],
                expected_output="Financial status report with any alerts"
            ),

            "productivity": Task(
                description="""
                Monitor productivity and schedule:
                - Check for missed tasks
                - Identify scheduling conflicts
                - Monitor work-life balance
                - Flag overcommitments

                Alert if issues found.
                """,
                agent=self.agents["personal_assistant"],
                expected_output="Productivity status report with any alerts"
            )
        }

    def run_monitoring_cycle(self):
        """Run one monitoring cycle across all domains."""
        tasks = self.create_monitoring_tasks()

        for domain, task in tasks.items():
            try:
                result = self.crew.execute_task(task)

                # Check if result contains alerts
                if self._contains_alert(result):
                    self._handle_alert(domain, result)

            except Exception as e:
                print(f"Monitoring error in {domain}: {e}")

    def _contains_alert(self, result: str) -> bool:
        """Check if result contains an alert."""
        alert_keywords = ["alert", "warning", "concern", "issue", "problem"]
        return any(keyword in result.lower() for keyword in alert_keywords)

    def _handle_alert(self, domain: str, result: str):
        """Handle an alert from monitoring."""
        print(f"⚠️  ALERT in {domain}: {result}")
        # Could send notification, email, etc.

    def start_continuous_monitoring(self, interval_hours: int = 24):
        """Start continuous monitoring on a schedule."""
        # Run monitoring every N hours
        schedule.every(interval_hours).hours.do(self.run_monitoring_cycle)

        print(f"Started continuous monitoring (every {interval_hours} hours)")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


# Usage
monitor = ContinuousMonitoringCrew()
# monitor.start_continuous_monitoring(interval_hours=6)  # Every 6 hours
```

### Pattern 3: Goal Planning & Tracking

**Scenario**: Create a comprehensive goal with plan, tracking, and adjustment.

```python
def create_goal_planning_workflow(goal: str, timeframe: str):
    """
    Create a comprehensive goal planning and tracking workflow.

    Example: "Run a marathon" with timeframe "6 months"
    """
    crew = create_personal_productivity_crew()
    agents = crew.get_agents()

    # Phase 1: Planning
    planning_tasks = [
        Task(
            description=f"""
            Analyze feasibility of goal: {goal} in {timeframe}

            Research:
            - Typical training requirements
            - Common pitfalls and challenges
            - Success strategies and best practices
            - Required resources and equipment
            """,
            agent=agents["research_specialist"],
            expected_output="Goal feasibility analysis with recommendations"
        ),

        Task(
            description=f"""
            Create health baseline and training plan for: {goal}

            Analyze:
            - Current fitness level and health metrics
            - Training progression requirements
            - Injury prevention strategies
            - Recovery and rest needs

            Create detailed training plan with phases.
            """,
            agent=agents["health_analyst"],
            expected_output="Comprehensive training plan with health considerations"
        ),

        Task(
            description=f"""
            Create schedule integration for: {goal}

            Plan:
            - Training session scheduling
            - Time blocking for workouts
            - Calendar integration
            - Contingency planning for conflicts
            """,
            agent=agents["personal_assistant"],
            expected_output="Integrated schedule for goal achievement"
        ),

        Task(
            description=f"""
            Budget planning for: {goal}

            Calculate:
            - Equipment and gear costs
            - Race registration fees
            - Nutrition and supplements
            - Optional coaching or classes

            Create budget allocation plan.
            """,
            agent=agents["finance_tracker"],
            expected_output="Complete budget for goal achievement"
        ),

        Task(
            description=f"""
            Document complete goal plan and set up tracking:

            Create:
            - Goal documentation with all plans integrated
            - Progress tracking methodology
            - Milestone definitions
            - Success criteria

            Store in memory for ongoing reference.
            """,
            agent=agents["memory_librarian"],
            expected_output="Complete goal documentation and tracking system"
        )
    ]

    # Execute planning phase
    planning_crew = Crew(
        agents=list(agents.values()),
        tasks=planning_tasks,
        process=Process.sequential,
        verbose=True,
        memory=True
    )

    planning_result = planning_crew.kickoff()

    # Phase 2: Tracking (ongoing)
    tracking_task = Task(
        description=f"""
        Track progress on goal: {goal}

        Weekly review:
        - Health metrics (via Health Analyst)
        - Schedule adherence (via Personal Assistant)
        - Budget tracking (via Finance Tracker)
        - Overall progress assessment

        Provide weekly progress report and adjustments needed.
        """,
        agent=agents["memory_librarian"],
        expected_output="Weekly progress report with recommendations"
    )

    return {
        "plan": planning_result,
        "tracking_task": tracking_task
    }


# Usage
marathon_goal = create_goal_planning_workflow(
    goal="Run a marathon",
    timeframe="6 months"
)
```

### Pattern 4: Intelligent Context Switching

**Scenario**: Use Context Manager to intelligently route requests to optimal agent(s).

```python
def intelligent_request_handler(user_request: str, conversation_history: list = None):
    """
    Intelligently route user requests using Context Manager.

    This demonstrates how the Context Manager analyzes requests and makes
    smart routing decisions for optimal response.
    """
    from agents.context_manager import create_context_manager, create_context_analysis_task

    # Create context manager
    context_manager = create_context_manager()

    # Create analysis task
    analysis_task = Task(
        description=create_context_analysis_task(user_request, conversation_history),
        agent=context_manager,
        expected_output="""
        Routing analysis including:
        - Request classification (type, category, urgency)
        - Optimal routing strategy (direct/single/collaborative)
        - Agent recommendations (primary and secondary)
        - Execution approach (tools, context, outcome)
        """
    )

    # Analyze the request
    crew = create_personal_productivity_crew()
    routing_analysis = crew.execute_task(analysis_task)

    # Parse routing decision (simplified - would use actual parsing)
    if "collaborative" in routing_analysis.lower():
        # Route to multiple agents
        return handle_collaborative_request(user_request, routing_analysis)
    elif "health" in routing_analysis.lower():
        return handle_single_agent_request(user_request, "health_analyst")
    elif "finance" in routing_analysis.lower():
        return handle_single_agent_request(user_request, "finance_tracker")
    # ... more routing logic

    return routing_analysis


def handle_collaborative_request(request: str, analysis: str):
    """Handle request requiring multiple agents."""
    crew = create_personal_productivity_crew()

    task = Task(
        description=f"""
        {request}

        Routing Analysis: {analysis}

        Collaborate across agents as recommended in the analysis.
        """,
        agent=crew.get_agents()["memory_librarian"],  # Coordinator
        expected_output="Comprehensive response from collaborative effort"
    )

    return crew.execute_task(task)


def handle_single_agent_request(request: str, agent_type: str):
    """Handle request for single specialized agent."""
    crew = create_personal_productivity_crew()
    agents = crew.get_agents()

    task = Task(
        description=request,
        agent=agents[agent_type],
        expected_output="Direct response from specialist agent"
    )

    return crew.execute_task(task)


# Usage examples
response1 = intelligent_request_handler("What time is it in Tokyo?")
# → Routes to Personal Assistant (direct response)

response2 = intelligent_request_handler("Create a comprehensive wellness plan")
# → Routes to collaborative workflow (multiple agents)

response3 = intelligent_request_handler(
    "Am I spending too much on dining out?",
    conversation_history=["Last month I spent $800 on restaurants"]
)
# → Routes to Finance Tracker (single specialist)
```

## Advanced Patterns

### Pattern 5: Adaptive Workflow Based on Results

**Scenario**: Workflow adapts based on intermediate results.

```python
def adaptive_health_workflow(initial_concern: str):
    """
    Health workflow that adapts based on initial analysis.
    """
    crew = create_personal_productivity_crew()
    agents = crew.get_agents()

    # Step 1: Initial analysis
    analysis_task = Task(
        description=f"""
        Analyze health concern: {initial_concern}

        Assess:
        - Severity level (minor/moderate/serious)
        - Required expertise (general/specialist)
        - Urgency (routine/urgent/emergency)
        """,
        agent=agents["health_analyst"],
        expected_output="Health concern analysis with severity and urgency"
    )

    analysis = crew.execute_task(analysis_task)

    # Step 2: Adaptive routing based on analysis
    if "serious" in analysis.lower() or "emergency" in analysis.lower():
        # High severity - immediate recommendations
        return create_emergency_health_task(initial_concern, analysis)

    elif "moderate" in analysis.lower():
        # Medium severity - comprehensive plan
        return create_comprehensive_health_plan(initial_concern, analysis)

    else:
        # Low severity - routine monitoring
        return create_health_monitoring_task(initial_concern, analysis)


def create_comprehensive_health_plan(concern: str, analysis: str):
    """Create comprehensive plan for moderate health concerns."""
    crew = create_personal_productivity_crew()
    agents = crew.get_agents()

    tasks = [
        # Research optimal approaches
        Task(
            description=f"Research solutions for: {concern}",
            agent=agents["research_specialist"],
            expected_output="Research-backed recommendations"
        ),

        # Create health plan
        Task(
            description=f"Create action plan for: {concern}",
            agent=agents["health_analyst"],
            expected_output="Detailed health action plan"
        ),

        # Budget planning
        Task(
            description="Budget for health plan implementation",
            agent=agents["finance_tracker"],
            expected_output="Budget allocation"
        ),

        # Schedule integration
        Task(
            description="Integrate health plan into schedule",
            agent=agents["personal_assistant"],
            expected_output="Scheduled health activities"
        )
    ]

    comprehensive_crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )

    return comprehensive_crew.kickoff()


# Usage
result = adaptive_health_workflow("I've been feeling tired lately")
# → Analyzes severity and creates appropriate level of response
```

### Pattern 6: Multi-Stage Pipeline with Checkpoints

**Scenario**: Long-running workflow with validation checkpoints.

```python
class PipelineWorkflow:
    """Multi-stage workflow with validation checkpoints."""

    def __init__(self, crew):
        self.crew = crew
        self.agents = crew.get_agents()
        self.results = {}
        self.checkpoints = []

    def add_stage(self, name: str, task: Task, validator=None):
        """Add a stage to the pipeline."""
        self.checkpoints.append({
            "name": name,
            "task": task,
            "validator": validator
        })

    def execute_pipeline(self):
        """Execute pipeline with validation at each checkpoint."""
        for checkpoint in self.checkpoints:
            print(f"\n{'='*60}")
            print(f"STAGE: {checkpoint['name']}")
            print(f"{'='*60}\n")

            # Execute stage
            result = self.crew.execute_task(checkpoint['task'])
            self.results[checkpoint['name']] = result

            # Validate if validator provided
            if checkpoint['validator']:
                is_valid, message = checkpoint['validator'](result)

                if not is_valid:
                    print(f"❌ Validation failed: {message}")
                    print("Pipeline halted.")
                    return {
                        "status": "failed",
                        "failed_stage": checkpoint['name'],
                        "message": message,
                        "results": self.results
                    }
                else:
                    print(f"✅ Validation passed: {message}")

            print(f"\n{checkpoint['name']} completed successfully\n")

        return {
            "status": "success",
            "results": self.results
        }


# Example: Home purchase decision pipeline
def create_home_purchase_pipeline():
    """Create pipeline for major purchase decision."""
    crew = create_personal_productivity_crew()
    agents = crew.get_agents()
    pipeline = PipelineWorkflow(crew)

    # Stage 1: Financial readiness
    pipeline.add_stage(
        "financial_readiness",
        Task(
            description="""
            Analyze financial readiness for home purchase:
            - Current savings and down payment capability
            - Monthly budget for mortgage
            - Credit profile and loan qualification
            - Emergency fund status
            """,
            agent=agents["finance_tracker"],
            expected_output="Financial readiness assessment"
        ),
        validator=lambda r: (
            (True, "Financial position adequate")
            if "adequate" in r.lower() or "ready" in r.lower()
            else (False, "Financial position not ready for purchase")
        )
    )

    # Stage 2: Research phase
    pipeline.add_stage(
        "market_research",
        Task(
            description="""
            Research housing market:
            - Current market conditions
            - Target neighborhoods
            - Price trends
            - Future outlook
            """,
            agent=agents["research_specialist"],
            expected_output="Market research report"
        ),
        validator=lambda r: (True, "Research completed")  # Always pass
    )

    # Stage 3: Lifestyle impact
    pipeline.add_stage(
        "lifestyle_assessment",
        Task(
            description="""
            Assess lifestyle impact of home purchase:
            - Commute times to work
            - Proximity to important locations
            - Schedule impacts
            - Life goals alignment
            """,
            agent=agents["personal_assistant"],
            expected_output="Lifestyle impact assessment"
        ),
        validator=lambda r: (True, "Assessment completed")
    )

    # Stage 4: Final recommendation
    pipeline.add_stage(
        "final_recommendation",
        Task(
            description="""
            Synthesize all analyses and provide recommendation:
            - Financial readiness summary
            - Market conditions assessment
            - Lifestyle impact evaluation
            - Clear go/no-go recommendation
            - If go: next steps and timeline
            """,
            agent=agents["memory_librarian"],
            expected_output="Final recommendation with action plan"
        ),
        validator=None  # No validation needed for final stage
    )

    return pipeline


# Usage
pipeline = create_home_purchase_pipeline()
result = pipeline.execute_pipeline()

if result["status"] == "success":
    print("\n✅ Pipeline completed successfully!")
    print(f"Final recommendation: {result['results']['final_recommendation']}")
else:
    print(f"\n❌ Pipeline failed at: {result['failed_stage']}")
    print(f"Reason: {result['message']}")
```

## Best Practices

### 1. Agent Specialization

✅ **DO**:
- Keep agents focused on their domain expertise
- Assign clear, specific roles and goals
- Provide appropriate tools for each agent's function

❌ **DON'T**:
- Give all tools to all agents (creates confusion)
- Mix unrelated responsibilities in one agent
- Create generic "do everything" agents

### 2. Task Design

✅ **DO**:
- Write clear, specific task descriptions
- Define expected outputs explicitly
- Provide context and constraints
- Break complex tasks into subtasks

❌ **DON'T**:
- Write vague tasks like "analyze everything"
- Omit success criteria
- Create tasks that are too broad or too narrow

### 3. Collaboration Patterns

✅ **DO**:
- Enable delegation when collaboration is needed
- Share context between sequential tasks
- Use memory to maintain state across interactions
- Implement clear handoff protocols between agents

❌ **DON'T**:
- Enable delegation for sensitive data agents (health, finance)
- Lose context between task transitions
- Create circular dependencies between agents

### 4. Error Handling

✅ **DO**:
```python
try:
    result = crew.execute_task(task)
    if not validate_result(result):
        # Fallback or retry logic
        result = crew.execute_task(fallback_task)
except Exception as e:
    logger.error(f"Task execution failed: {e}")
    # Graceful degradation
    result = generate_error_response(e)
```

❌ **DON'T**:
- Let exceptions crash the workflow
- Ignore validation failures
- Proceed with invalid intermediate results

### 5. Performance Optimization

✅ **DO**:
- Use parallel processing for independent tasks
- Cache expensive operations
- Set appropriate timeouts
- Monitor and optimize iteration counts

❌ **DON'T**:
- Run everything sequentially when parallelizable
- Allow infinite iterations
- Ignore performance metrics

## Real-World Examples

### Example 1: Weekly Life Review

```python
def weekly_life_review():
    """Automated weekly review across all life domains."""
    crew = create_personal_productivity_crew()

    # Create comprehensive review task
    task = crew.create_life_analysis_task("last 7 days")

    # Execute with full crew collaboration
    review = crew.execute_task(task)

    # Store in memory for trend analysis
    memory_task = Task(
        description=f"Store weekly review and compare to previous weeks",
        agent=crew.get_agents()["memory_librarian"],
        expected_output="Review stored with trend analysis"
    )

    crew.execute_task(memory_task)

    return review

# Schedule to run every Sunday
import schedule
schedule.every().sunday.at("20:00").do(weekly_life_review)
```

### Example 2: Dynamic Goal Adjustment

```python
def adjust_goal_based_on_progress(goal_id: str):
    """Dynamically adjust goal plan based on actual progress."""
    crew = create_personal_productivity_crew()
    agents = crew.get_agents()

    # Retrieve goal and progress from memory
    memory_task = Task(
        description=f"Retrieve goal {goal_id} and all progress data",
        agent=agents["memory_librarian"],
        expected_output="Goal details and progress history"
    )

    goal_data = crew.execute_task(memory_task)

    # Analyze progress
    analysis_task = Task(
        description=f"""
        Analyze goal progress:
        {goal_data}

        Assess:
        - On track vs. behind/ahead of schedule
        - Obstacles encountered
        - Success patterns
        - Required adjustments
        """,
        agent=agents["memory_librarian"],
        expected_output="Progress analysis with adjustment recommendations"
    )

    analysis = crew.execute_task(analysis_task)

    # If adjustments needed, create new plan
    if "adjustment" in analysis.lower():
        adjustment_task = Task(
            description=f"""
            Create adjusted plan based on:
            {analysis}

            Coordinate across:
            - Schedule changes (Personal Assistant)
            - Budget adjustments (Finance Tracker)
            - Health plan modifications (Health Analyst)
            """,
            agent=agents["memory_librarian"],
            expected_output="Updated goal plan with all adjustments"
        )

        adjusted_plan = crew.execute_task(adjustment_task)
        return adjusted_plan

    return analysis

# Run monthly to keep goals on track
```

## Extending the System

### Adding New Agents

```python
# 1. Create agent definition
def create_my_custom_agent(verbose=True):
    from crewai import Agent
    from config import get_agent_llm
    from tools import load_myndy_tools_for_agent

    agent = Agent(
        role="Custom Specialist",
        goal="Specific domain expertise",
        backstory="Detailed background and capabilities",
        tools=load_myndy_tools_for_agent("custom_tools"),
        llm=get_agent_llm("custom_agent"),
        verbose=verbose,
        memory=True
    )

    return agent

# 2. Add to crew
def create_extended_crew():
    from crews import create_personal_productivity_crew

    base_crew = create_personal_productivity_crew()
    agents = base_crew.get_agents()

    # Add custom agent
    agents["custom_specialist"] = create_my_custom_agent()

    return agents
```

### Creating Custom Workflows

```python
# Create workflow template
class CustomWorkflowTemplate:
    """Template for creating reusable workflows."""

    def __init__(self, crew, name: str):
        self.crew = crew
        self.name = name
        self.agents = crew.get_agents()

    def create_tasks(self, **kwargs):
        """Override this to define workflow tasks."""
        raise NotImplementedError

    def validate_results(self, results):
        """Override this to add validation logic."""
        return True

    def execute(self, **kwargs):
        """Execute the workflow."""
        tasks = self.create_tasks(**kwargs)
        results = self.crew.execute_tasks(tasks)

        if self.validate_results(results):
            return {
                "status": "success",
                "workflow": self.name,
                "results": results
            }
        else:
            return {
                "status": "failed",
                "workflow": self.name,
                "results": results
            }

# Use template
class QuarterlyReviewWorkflow(CustomWorkflowTemplate):
    """Quarterly life review workflow."""

    def create_tasks(self, quarter: str):
        return [
            Task(
                description=f"Analyze {quarter} health data",
                agent=self.agents["health_analyst"],
                expected_output="Quarterly health report"
            ),
            # ... more tasks
        ]
```

## Troubleshooting

### Common Issues

**Issue**: Agents not collaborating properly
**Solution**: Ensure `allow_delegation=True` and provide clear delegation instructions in task descriptions

**Issue**: Tasks taking too long
**Solution**: Set appropriate `max_iter` and `max_execution_time` values

**Issue**: Inconsistent results
**Solution**: Enable `memory=True` on crew and agents to maintain context

**Issue**: Tool execution failures
**Solution**: Verify myndy-ai backend is running and tools are properly registered

## Next Steps

1. **Start Simple**: Begin with single-agent tasks to understand agent behavior
2. **Add Complexity**: Gradually introduce multi-agent workflows
3. **Monitor Performance**: Track execution times and iteration counts
4. **Iterate**: Refine task descriptions and agent configurations based on results
5. **Extend**: Add custom agents and workflows for your specific needs

## Resources

- **Agent Documentation**: `agents/README.md` (if exists) or individual agent files
- **Crew Documentation**: `crews/personal_productivity_crew.py`
- **Tool Bridge**: `tools/myndy_bridge.py`
- **Examples**: `examples/` directory

---

**Created**: October 7, 2025
**Version**: 1.0
**Status**: Production Ready
