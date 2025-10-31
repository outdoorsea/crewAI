"""
Simple Agents Module
Creates lightweight CrewAI agents optimized for fast responses
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from crewai import Agent

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from tools.myndy_bridge import MyndyToolBridge
    from config.llm_config import get_agent_llm
    TOOLS_AVAILABLE = True
    # Initialize tool bridge
    tool_bridge = MyndyToolBridge()
except ImportError as e:
    TOOLS_AVAILABLE = False
    tool_bridge = None
    logging.warning(f"Tools not available: {e}")

logger = logging.getLogger(__name__)

class SimpleAgent:
    """Lightweight agent wrapper for fast responses"""
    
    def __init__(self, name: str, role: str, description: str, llm_model: str = "llama3.2"):
        self.name = name
        self.role = role
        self.description = description
        self.llm_model = llm_model
        
        # Try to create actual CrewAI agent (even without tools)
        self.crewai_agent = None
        try:
            self._create_crewai_agent()
        except Exception as e:
            logger.warning(f"Failed to create CrewAI agent for {role}: {e}")
    
    def _create_crewai_agent(self):
        """Create actual CrewAI agent"""
        logger.info(f"🔧 Creating CrewAI agent for {self.role}")
        try:
            # Get tools for this agent role
            tools = tool_bridge.get_tools_for_agent(self.role) if tool_bridge else []
            logger.info(f"🛠️ Found {len(tools)} tools for {self.role}")
            
            # Get LLM for this agent
            logger.info(f"🧠 Getting LLM for {self.role}")
            llm = get_agent_llm(self.role)
            logger.info(f"✅ LLM obtained for {self.role}: {type(llm).__name__}")
            
            # Create tool usage instructions
            tool_instructions = ""
            if tools:
                tool_names = [tool.name for tool in tools[:3]]
                tool_instructions = f"\n\nIMPORTANT: You have access to these tools: {', '.join(tool_names)}. USE THEM when relevant to answer user questions. Always try to use appropriate tools before giving general advice."
            
            # Create simplified agent configuration
            self.crewai_agent = Agent(
                role=self.name,
                goal=f"Assist users with {self.description.lower()} efficiently and accurately. Use available tools when appropriate.",
                backstory=f"You are an expert {self.name.lower()} who specializes in {self.description.lower()}. You have access to specialized tools and should use them to provide accurate, helpful responses.{tool_instructions}",
                tools=tools[:3] if tools else [],  # Limit tools for speed
                llm=llm,
                verbose=True,  # Enable to see tool usage
                allow_delegation=False,  # No delegation for speed
                max_iter=5,  # Increase for tool usage
                max_execution_time=25  # Increase timeout for tool usage
            )
            
            logger.info(f"✅ CrewAI agent created successfully for {self.role}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create CrewAI agent for {self.role}: {e}")
            logger.error(f"❌ Exception details: {type(e).__name__}: {str(e)}")
            self.crewai_agent = None
    
    def execute_task(self, task_description: str) -> str:
        """Execute a task using the agent"""
        logger.info(f"🚀 Executing task for {self.role}: crewai_agent={'✅' if self.crewai_agent else '❌'}")
        
        if self.crewai_agent:
            try:
                logger.info(f"🤖 Using CrewAI agent for {self.role}")
                # Use the CrewAI agent if available
                from crewai import Task, Crew
                
                task = Task(
                    description=task_description,
                    agent=self.crewai_agent,
                    expected_output="A helpful response to the user's request"
                )
                
                crew = Crew(
                    agents=[self.crewai_agent],
                    tasks=[task],
                    verbose=False
                )
                
                result = crew.kickoff()
                return str(result) if result else self._generate_fallback_response(task_description)
                
            except Exception as e:
                logger.warning(f"❌ CrewAI execution failed for {self.role}: {e}")
                return self._generate_fallback_response(task_description)
        else:
            logger.info(f"⚠️ No CrewAI agent available for {self.role}, using fallback")
            return self._generate_fallback_response(task_description)
    
    def _generate_fallback_response(self, task_description: str) -> str:
        """Generate a fallback response when CrewAI fails"""
        return f"I'm your {self.name}. You asked: {task_description}\n\nI specialize in {self.description.lower()}. For full functionality, ensure all dependencies are properly configured."

def create_simple_agents(
    verbose: bool = False,
    allow_delegation: bool = False,
    max_iter: int = 3,
    max_execution_time: int = 45
) -> Dict[str, SimpleAgent]:
    """
    Create a set of simple agents optimized for fast responses
    
    Args:
        verbose: Enable verbose logging
        allow_delegation: Allow agents to delegate (disabled for speed)
        max_iter: Maximum iterations per agent
        max_execution_time: Maximum execution time per agent
        
    Returns:
        Dictionary of agent_role -> SimpleAgent
    """
    
    agents = {}
    
    # Define agent configurations
    agent_configs = {
        "personal_assistant": {
            "name": "Personal Assistant",
            "description": "Calendar management, email processing, task organization, and general productivity",
            "llm_model": "llama3.2"
        },
        "memory_librarian": {
            "name": "Memory Librarian", 
            "description": "Memory management, entity relationships, and information organization",
            "llm_model": "llama3.2"
        },
        "research_specialist": {
            "name": "Research Specialist",
            "description": "Web research, document analysis, and fact verification",
            "llm_model": "mixtral"
        },
        "health_analyst": {
            "name": "Health Analyst",
            "description": "Health data analysis, fitness tracking, and wellness insights",
            "llm_model": "llama3.2"
        },
        "finance_tracker": {
            "name": "Finance Tracker",
            "description": "Expense tracking, budget analysis, and financial planning",
            "llm_model": "llama3.2"
        },
        "shadow_agent": {
            "name": "Shadow Agent",
            "description": "Behavioral analysis, conversation monitoring, and memory updates",
            "llm_model": "llama3.2"
        }
    }
    
    # Create agents
    for role, config in agent_configs.items():
        try:
            agent = SimpleAgent(
                name=config["name"],
                role=role,
                description=config["description"],
                llm_model=config["llm_model"]
            )
            agents[role] = agent
            logger.info(f"✅ Created simple agent: {role}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create agent {role}: {e}")
    
    logger.info(f"🎉 Created {len(agents)} simple agents")
    return agents

def test_simple_agents():
    """Test function for simple agents"""
    print("🧪 Testing Simple Agents...")
    
    agents = create_simple_agents()
    
    if agents:
        # Test personal assistant
        if "personal_assistant" in agents:
            response = agents["personal_assistant"].execute_task("What time is it?")
            print(f"Personal Assistant: {response}")
        
        print(f"✅ Successfully created {len(agents)} agents")
    else:
        print("❌ No agents created")

if __name__ == "__main__":
    test_simple_agents()