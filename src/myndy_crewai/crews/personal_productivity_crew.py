"""
Personal Productivity Crew

A comprehensive crew that combines all specialized agents to provide
complete personal productivity and life management capabilities.

File: crews/personal_productivity_crew.py
"""

from crewai import Crew, Task, Process
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import agents using explicit module paths to avoid conflicts
import importlib.util
import os

def _load_agent_functions():
    """Load agent creation functions using explicit module paths"""
    agents_dir = PROJECT_ROOT / "agents"
    
    # Load memory librarian
    memory_spec = importlib.util.spec_from_file_location(
        "memory_librarian", str(agents_dir / "memory_librarian.py")
    )
    memory_module = importlib.util.module_from_spec(memory_spec)
    memory_spec.loader.exec_module(memory_module)
    
    # Load research specialist
    research_spec = importlib.util.spec_from_file_location(
        "research_specialist", str(agents_dir / "research_specialist.py")
    )
    research_module = importlib.util.module_from_spec(research_spec)
    research_spec.loader.exec_module(research_module)
    
    # Load personal assistant
    assistant_spec = importlib.util.spec_from_file_location(
        "personal_assistant", str(agents_dir / "personal_assistant.py")
    )
    assistant_module = importlib.util.module_from_spec(assistant_spec)
    assistant_spec.loader.exec_module(assistant_module)
    
    # Load health analyst
    health_spec = importlib.util.spec_from_file_location(
        "health_analyst", str(agents_dir / "health_analyst.py")
    )
    health_module = importlib.util.module_from_spec(health_spec)
    health_spec.loader.exec_module(health_module)
    
    # Load finance tracker
    finance_spec = importlib.util.spec_from_file_location(
        "finance_tracker", str(agents_dir / "finance_tracker.py")
    )
    finance_module = importlib.util.module_from_spec(finance_spec)
    finance_spec.loader.exec_module(finance_module)
    
    # Load context manager
    context_spec = importlib.util.spec_from_file_location(
        "context_manager", str(agents_dir / "context_manager.py")
    )
    context_module = importlib.util.module_from_spec(context_spec)
    context_spec.loader.exec_module(context_module)
    
    # Load shadow agent
    shadow_spec = importlib.util.spec_from_file_location(
        "shadow_agent", str(agents_dir / "shadow_agent.py")
    )
    shadow_module = importlib.util.module_from_spec(shadow_spec)
    shadow_spec.loader.exec_module(shadow_module)
    
    return {
        'create_context_manager': context_module.create_context_manager,
        'create_memory_librarian': memory_module.create_memory_librarian,
        'create_research_specialist': research_module.create_research_specialist,
        'create_personal_assistant': assistant_module.create_personal_assistant,
        'create_health_analyst': health_module.create_health_analyst,
        'create_finance_tracker': finance_module.create_finance_tracker,
        'create_shadow_agent': shadow_module.create_shadow_agent
    }

# Load agent functions
_agent_functions = _load_agent_functions()
create_context_manager = _agent_functions['create_context_manager']
create_memory_librarian = _agent_functions['create_memory_librarian']
create_research_specialist = _agent_functions['create_research_specialist']
create_personal_assistant = _agent_functions['create_personal_assistant']
create_health_analyst = _agent_functions['create_health_analyst']
create_finance_tracker = _agent_functions['create_finance_tracker']
create_shadow_agent = _agent_functions['create_shadow_agent']


class PersonalProductivityCrew:
    """
    Comprehensive crew for personal productivity and life management.
    
    This crew combines specialized agents to provide holistic support across
    memory management, research, personal assistance, health analysis, and
    financial tracking.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the Personal Productivity Crew.
        
        Args:
            verbose: Whether to enable verbose output for all agents
        """
        self.verbose = verbose
        self._agents = None
        self._crew = None
        
    def _create_agents(self):
        """Create all specialized agents for the crew."""
        if self._agents is None:
            self._agents = {
                "memory_librarian": create_memory_librarian(
                    verbose=self.verbose,
                    allow_delegation=True
                ),
                "research_specialist": create_research_specialist(
                    verbose=self.verbose,
                    allow_delegation=True
                ),
                "personal_assistant": create_personal_assistant(
                    verbose=self.verbose,
                    allow_delegation=True
                ),
                "health_analyst": create_health_analyst(
                    verbose=self.verbose,
                    allow_delegation=False  # Specialized domain
                ),
                "finance_tracker": create_finance_tracker(
                    verbose=self.verbose,
                    allow_delegation=False  # Sensitive data
                )
            }
        return self._agents
    
    def get_agents(self) -> Dict[str, Any]:
        """Get all agents in the crew."""
        return self._create_agents()
    
    def create_crew(self, process: Process = Process.sequential) -> Crew:
        """
        Create the crew with all agents.
        
        Args:
            process: The process type for task execution
            
        Returns:
            Configured Crew instance
        """
        if self._crew is None:
            agents = self._create_agents()
            
            self._crew = Crew(
                agents=list(agents.values()),
                process=process,
                verbose=self.verbose,
                memory=True  # Enable crew-level memory
            )
        
        return self._crew
    
    def create_life_analysis_task(self, time_period: str = "last 30 days") -> Task:
        """
        Create a comprehensive life analysis task.
        
        Args:
            time_period: Time period for analysis
            
        Returns:
            Configured Task instance
        """
        agents = self._create_agents()
        
        return Task(
            description=(
                f"Conduct a comprehensive life analysis for the {time_period}. "
                f"This should include:\n"
                f"1. Memory Librarian: Analyze key events, relationships, and conversations\n"
                f"2. Health Analyst: Review health metrics, fitness progress, and wellness trends\n"
                f"3. Finance Tracker: Examine spending patterns, budget adherence, and financial health\n"
                f"4. Personal Assistant: Review productivity, task completion, and time management\n"
                f"5. Research Specialist: Gather any external context or validation needed\n\n"
                f"Provide a holistic summary with insights and recommendations for improvement."
            ),
            expected_output=(
                "A comprehensive life analysis report including:\n"
                "- Executive summary of key insights\n"
                "- Health and wellness assessment\n"
                "- Financial health review\n"
                "- Productivity and time management analysis\n"
                "- Relationship and social interaction summary\n"
                "- Actionable recommendations for improvement\n"
                "- Goal setting suggestions for the next period"
            ),
            agent=agents["memory_librarian"]  # Lead agent for coordination
        )
    
    def create_research_project_task(self, topic: str, depth: str = "comprehensive") -> Task:
        """
        Create a research project task.
        
        Args:
            topic: Research topic
            depth: Research depth (basic, detailed, comprehensive)
            
        Returns:
            Configured Task instance
        """
        agents = self._create_agents()
        
        return Task(
            description=(
                f"Conduct {depth} research on: {topic}\n\n"
                f"1. Research Specialist: Lead the information gathering and analysis\n"
                f"2. Memory Librarian: Provide relevant personal context and past knowledge\n"
                f"3. Personal Assistant: Organize findings and create actionable next steps\n\n"
                f"Ensure all information is verified, properly sourced, and synthesized."
            ),
            expected_output=(
                f"A detailed research report on {topic} including:\n"
                "- Executive summary of key findings\n"
                "- Comprehensive analysis with sources\n"
                "- Personal relevance and context\n"
                "- Actionable recommendations\n"
                "- Further research suggestions\n"
                "- Properly cited sources and references"
            ),
            agent=agents["research_specialist"]
        )
    
    def create_health_optimization_task(self, focus_area: str = "overall wellness") -> Task:
        """
        Create a health optimization task.
        
        Args:
            focus_area: Specific health focus area
            
        Returns:
            Configured Task instance
        """
        agents = self._create_agents()
        
        return Task(
            description=(
                f"Create a health optimization plan focused on {focus_area}:\n\n"
                f"1. Health Analyst: Analyze current health data and identify improvement areas\n"
                f"2. Personal Assistant: Review schedule for workout and meal planning opportunities\n"
                f"3. Finance Tracker: Evaluate budget for health-related investments\n"
                f"4. Memory Librarian: Recall past successful health initiatives\n\n"
                f"Develop a personalized, data-driven health improvement plan."
            ),
            expected_output=(
                f"A personalized health optimization plan including:\n"
                "- Current health status assessment\n"
                "- Specific improvement goals and metrics\n"
                "- Detailed action plan with timeline\n"
                "- Budget considerations for health investments\n"
                "- Schedule integration for new health habits\n"
                "- Progress tracking methodology\n"
                "- Contingency plans for obstacles"
            ),
            agent=agents["health_analyst"]
        )
    
    def create_financial_planning_task(self, goal: str, timeframe: str = "6 months") -> Task:
        """
        Create a financial planning task.
        
        Args:
            goal: Financial goal description
            timeframe: Timeline for achieving the goal
            
        Returns:
            Configured Task instance
        """
        agents = self._create_agents()
        
        return Task(
            description=(
                f"Create a financial plan to achieve: {goal} within {timeframe}\n\n"
                f"1. Finance Tracker: Analyze current financial position and spending patterns\n"
                f"2. Research Specialist: Gather market data and financial planning strategies\n"
                f"3. Personal Assistant: Create implementation timeline and milestones\n"
                f"4. Memory Librarian: Reference past financial decisions and outcomes\n\n"
                f"Develop a realistic, actionable financial plan with clear steps."
            ),
            expected_output=(
                f"A comprehensive financial plan to achieve {goal} including:\n"
                "- Current financial position analysis\n"
                "- Specific savings and investment strategies\n"
                "- Monthly budget adjustments needed\n"
                "- Timeline with key milestones\n"
                "- Risk assessment and mitigation strategies\n"
                "- Progress tracking mechanisms\n"
                "- Alternative scenarios and contingency plans"
            ),
            agent=agents["finance_tracker"]
        )
    
    def execute_task(self, task: Task) -> str:
        """
        Execute a single task with the crew.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        crew = self.create_crew()
        crew.tasks = [task]
        return crew.kickoff()
    
    def execute_tasks(self, tasks: List[Task]) -> str:
        """
        Execute multiple tasks with the crew.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            Combined task execution results
        """
        crew = self.create_crew()
        crew.tasks = tasks
        return crew.kickoff()


def create_personal_productivity_crew(verbose: bool = True) -> PersonalProductivityCrew:
    """
    Convenience function to create a Personal Productivity Crew.
    
    Args:
        verbose: Whether to enable verbose output
        
    Returns:
        PersonalProductivityCrew instance
    """
    return PersonalProductivityCrew(verbose=verbose)


if __name__ == "__main__":
    # Test crew creation
    print("Personal Productivity Crew Test")
    print("=" * 40)
    
    try:
        crew_manager = create_personal_productivity_crew(verbose=False)
        agents = crew_manager.get_agents()
        
        print(f"✅ Crew created successfully")
        print(f"Agents available: {len(agents)}")
        
        for role, agent in agents.items():
            print(f"  • {role}: {agent.role}")
        
        # Test task creation
        task = crew_manager.create_life_analysis_task("last 7 days")
        print(f"\n✅ Test task created: Life Analysis")
        print(f"Task description length: {len(task.description)} characters")
        
    except Exception as e:
        print(f"❌ Failed to create crew: {e}")