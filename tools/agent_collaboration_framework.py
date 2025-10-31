"""
Agent Collaboration Framework for CrewAI

This framework enables multi-agent coordination, task delegation, and collaborative
problem-solving for complex requests that require expertise from multiple agents.

File: tools/agent_collaboration_framework.py
"""

import json
import logging
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Status of collaborative tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"
    WAITING_FOR_INPUT = "waiting_for_input"

class AgentRole(Enum):
    """Available agent roles in the system."""
    MEMORY_LIBRARIAN = "memory_librarian"
    RESEARCH_SPECIALIST = "research_specialist"
    PERSONAL_ASSISTANT = "personal_assistant"
    HEALTH_ANALYST = "health_analyst"
    FINANCE_TRACKER = "finance_tracker"

@dataclass
class CollaborationTask:
    """Represents a task in the collaboration framework."""
    id: str
    title: str
    description: str
    required_agents: List[AgentRole]
    status: TaskStatus
    priority: int  # 1-10, with 10 being highest
    created_at: datetime
    updated_at: datetime
    owner_agent: Optional[AgentRole] = None
    assigned_agent: Optional[AgentRole] = None
    context: Dict[str, Any] = None
    results: Dict[str, Any] = None
    dependencies: List[str] = None  # Task IDs this task depends on
    timeout_seconds: Optional[int] = 300
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class AgentMessage:
    """Message passed between agents during collaboration."""
    id: str
    from_agent: AgentRole
    to_agent: AgentRole
    message_type: str  # request, response, delegation, notification
    content: Dict[str, Any]
    task_id: Optional[str] = None
    timestamp: datetime = None
    priority: int = 5

@dataclass
class CollaborationSession:
    """A collaboration session involving multiple agents."""
    id: str
    title: str
    participants: List[AgentRole]
    tasks: List[str]  # Task IDs
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    context: Dict[str, Any] = None
    results: Dict[str, Any] = None

class AgentCollaborationFramework:
    """Framework for managing multi-agent collaboration."""
    
    def __init__(self):
        """Initialize the collaboration framework."""
        self.tasks: Dict[str, CollaborationTask] = {}
        self.sessions: Dict[str, CollaborationSession] = {}
        self.messages: List[AgentMessage] = []
        self.agent_capabilities: Dict[AgentRole, List[str]] = {}
        self.collaboration_lock = threading.Lock()
        
        # Initialize agent capabilities
        self._initialize_agent_capabilities()
        
        logger.info("Agent Collaboration Framework initialized")
    
    def _initialize_agent_capabilities(self):
        """Initialize the capabilities of each agent type."""
        self.agent_capabilities = {
            AgentRole.MEMORY_LIBRARIAN: [
                "entity_management",
                "conversation_history",
                "relationship_mapping",
                "memory_search",
                "context_preservation",
                "biographical_data"
            ],
            AgentRole.RESEARCH_SPECIALIST: [
                "text_analysis",
                "sentiment_analysis",
                "document_processing",
                "information_extraction",
                "research_synthesis",
                "pattern_recognition"
            ],
            AgentRole.PERSONAL_ASSISTANT: [
                "calendar_management",
                "task_scheduling",
                "weather_information",
                "time_management",
                "productivity_planning",
                "daily_coordination"
            ],
            AgentRole.HEALTH_ANALYST: [
                "health_data_analysis",
                "fitness_tracking",
                "wellness_recommendations",
                "health_pattern_recognition",
                "activity_monitoring",
                "health_goal_tracking"
            ],
            AgentRole.FINANCE_TRACKER: [
                "expense_tracking",
                "budget_analysis",
                "transaction_management",
                "financial_planning",
                "spending_patterns",
                "financial_goal_monitoring"
            ]
        }
    
    def create_collaboration_session(self, title: str, description: str,
                                   required_capabilities: List[str],
                                   priority: int = 5) -> Dict[str, Any]:
        """
        Create a new collaboration session for a complex request.
        
        Args:
            title: Session title
            description: Session description
            required_capabilities: List of capabilities needed
            priority: Session priority (1-10)
            
        Returns:
            Session creation result
        """
        try:
            with self.collaboration_lock:
                session_id = f"session_{uuid.uuid4()}"
                
                # Determine required agents based on capabilities
                required_agents = self._determine_required_agents(required_capabilities)
                
                # Create initial task
                task_id = f"task_{uuid.uuid4()}"
                task = CollaborationTask(
                    id=task_id,
                    title=title,
                    description=description,
                    required_agents=required_agents,
                    status=TaskStatus.PENDING,
                    priority=priority,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    context={"capabilities_needed": required_capabilities},
                    dependencies=[],
                    results={}
                )
                
                # Create session
                session = CollaborationSession(
                    id=session_id,
                    title=title,
                    participants=required_agents,
                    tasks=[task_id],
                    status=TaskStatus.PENDING,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    context={"description": description, "priority": priority}
                )
                
                self.tasks[task_id] = task
                self.sessions[session_id] = session
                
                logger.info(f"Created collaboration session {session_id} with {len(required_agents)} agents")
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "task_id": task_id,
                    "required_agents": [agent.value for agent in required_agents],
                    "capabilities_needed": required_capabilities
                }
                
        except Exception as e:
            logger.error(f"Error creating collaboration session: {e}")
            return {"success": False, "error": str(e)}
    
    def _determine_required_agents(self, required_capabilities: List[str]) -> List[AgentRole]:
        """Determine which agents are needed based on required capabilities."""
        required_agents = set()
        
        for capability in required_capabilities:
            for agent_role, capabilities in self.agent_capabilities.items():
                if any(cap in capability.lower() for cap in capabilities):
                    required_agents.add(agent_role)
        
        # Ensure at least one agent is assigned
        if not required_agents:
            required_agents.add(AgentRole.PERSONAL_ASSISTANT)  # Default coordinator
        
        return list(required_agents)
    
    def delegate_task(self, task_id: str, from_agent: AgentRole, 
                     to_agent: AgentRole, delegation_reason: str) -> Dict[str, Any]:
        """
        Delegate a task from one agent to another.
        
        Args:
            task_id: ID of task to delegate
            from_agent: Agent delegating the task
            to_agent: Agent receiving the task
            delegation_reason: Reason for delegation
            
        Returns:
            Delegation result
        """
        try:
            with self.collaboration_lock:
                if task_id not in self.tasks:
                    return {"success": False, "error": f"Task {task_id} not found"}
                
                task = self.tasks[task_id]
                
                # Check if target agent can handle the task
                if to_agent not in task.required_agents:
                    task.required_agents.append(to_agent)
                
                # Update task assignment
                previous_agent = task.assigned_agent
                task.assigned_agent = to_agent
                task.status = TaskStatus.DELEGATED
                task.updated_at = datetime.utcnow()
                
                # Create delegation message
                message = AgentMessage(
                    id=f"msg_{uuid.uuid4()}",
                    from_agent=from_agent,
                    to_agent=to_agent,
                    message_type="delegation",
                    content={
                        "task_id": task_id,
                        "delegation_reason": delegation_reason,
                        "task_context": task.context,
                        "previous_agent": previous_agent.value if previous_agent else None
                    },
                    task_id=task_id,
                    timestamp=datetime.utcnow(),
                    priority=task.priority
                )
                
                self.messages.append(message)
                
                logger.info(f"Delegated task {task_id} from {from_agent.value} to {to_agent.value}")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "from_agent": from_agent.value,
                    "to_agent": to_agent.value,
                    "message_id": message.id
                }
                
        except Exception as e:
            logger.error(f"Error delegating task: {e}")
            return {"success": False, "error": str(e)}
    
    def request_collaboration(self, requesting_agent: AgentRole, 
                            target_agent: AgentRole, request_type: str,
                            request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request collaboration from another agent.
        
        Args:
            requesting_agent: Agent making the request
            target_agent: Agent being requested to help
            request_type: Type of collaboration needed
            request_data: Data associated with the request
            
        Returns:
            Collaboration request result
        """
        try:
            message = AgentMessage(
                id=f"msg_{uuid.uuid4()}",
                from_agent=requesting_agent,
                to_agent=target_agent,
                message_type="request",
                content={
                    "request_type": request_type,
                    "request_data": request_data,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timestamp=datetime.utcnow(),
                priority=request_data.get("priority", 5)
            )
            
            self.messages.append(message)
            
            logger.info(f"Collaboration request from {requesting_agent.value} to {target_agent.value}: {request_type}")
            
            return {
                "success": True,
                "message_id": message.id,
                "request_type": request_type,
                "from_agent": requesting_agent.value,
                "to_agent": target_agent.value
            }
            
        except Exception as e:
            logger.error(f"Error requesting collaboration: {e}")
            return {"success": False, "error": str(e)}
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          results: Optional[Dict[str, Any]] = None,
                          agent: Optional[AgentRole] = None) -> Dict[str, Any]:
        """
        Update the status of a collaboration task.
        
        Args:
            task_id: ID of task to update
            status: New status
            results: Optional results data
            agent: Agent updating the status
            
        Returns:
            Update result
        """
        try:
            with self.collaboration_lock:
                if task_id not in self.tasks:
                    return {"success": False, "error": f"Task {task_id} not found"}
                
                task = self.tasks[task_id]
                previous_status = task.status
                
                task.status = status
                task.updated_at = datetime.utcnow()
                
                if results:
                    if task.results is None:
                        task.results = {}
                    task.results.update(results)
                
                if agent:
                    task.assigned_agent = agent
                
                # Check if session can be updated
                self._update_session_status(task_id)
                
                logger.info(f"Updated task {task_id} status from {previous_status.value} to {status.value}")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "previous_status": previous_status.value,
                    "new_status": status.value,
                    "updated_by": agent.value if agent else None
                }
                
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return {"success": False, "error": str(e)}
    
    def _update_session_status(self, task_id: str):
        """Update session status based on task completion."""
        for session in self.sessions.values():
            if task_id in session.tasks:
                # Check if all tasks in session are completed
                all_completed = True
                any_failed = False
                
                for tid in session.tasks:
                    if tid in self.tasks:
                        task_status = self.tasks[tid].status
                        if task_status not in [TaskStatus.COMPLETED]:
                            all_completed = False
                        if task_status == TaskStatus.FAILED:
                            any_failed = True
                
                if any_failed:
                    session.status = TaskStatus.FAILED
                elif all_completed:
                    session.status = TaskStatus.COMPLETED
                else:
                    session.status = TaskStatus.IN_PROGRESS
                
                session.updated_at = datetime.utcnow()
    
    def get_agent_messages(self, agent: AgentRole, 
                          since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get messages for a specific agent.
        
        Args:
            agent: Agent to get messages for
            since: Optional timestamp to filter messages
            
        Returns:
            List of messages for the agent
        """
        try:
            messages = []
            cutoff_time = since or datetime.utcnow() - timedelta(hours=24)
            
            for message in self.messages:
                if (message.to_agent == agent and 
                    message.timestamp >= cutoff_time):
                    messages.append({
                        "id": message.id,
                        "from_agent": message.from_agent.value,
                        "message_type": message.message_type,
                        "content": message.content,
                        "task_id": message.task_id,
                        "timestamp": message.timestamp.isoformat(),
                        "priority": message.priority
                    })
            
            # Sort by priority and timestamp
            messages.sort(key=lambda x: (-x["priority"], x["timestamp"]))
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting agent messages: {e}")
            return []
    
    def get_collaboration_status(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of collaboration sessions and tasks.
        
        Args:
            session_id: Optional specific session to get status for
            
        Returns:
            Collaboration status information
        """
        try:
            if session_id:
                if session_id not in self.sessions:
                    return {"error": f"Session {session_id} not found"}
                
                session = self.sessions[session_id]
                session_tasks = [self.tasks[tid] for tid in session.tasks if tid in self.tasks]
                
                return {
                    "session": asdict(session),
                    "tasks": [asdict(task) for task in session_tasks],
                    "message_count": len([m for m in self.messages if m.task_id in session.tasks])
                }
            else:
                # Return overview of all sessions
                active_sessions = [s for s in self.sessions.values() 
                                 if s.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]]
                
                return {
                    "total_sessions": len(self.sessions),
                    "active_sessions": len(active_sessions),
                    "total_tasks": len(self.tasks),
                    "total_messages": len(self.messages),
                    "recent_sessions": [asdict(s) for s in active_sessions[-5:]]
                }
                
        except Exception as e:
            logger.error(f"Error getting collaboration status: {e}")
            return {"error": str(e)}
    
    def cleanup_old_data(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Clean up old collaboration data.
        
        Args:
            max_age_hours: Maximum age of data to keep
            
        Returns:
            Cleanup results
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Clean up completed/failed sessions
            sessions_cleaned = 0
            for session_id, session in list(self.sessions.items()):
                if (session.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and 
                    session.updated_at < cutoff_time):
                    del self.sessions[session_id]
                    sessions_cleaned += 1
            
            # Clean up old tasks
            tasks_cleaned = 0
            for task_id, task in list(self.tasks.items()):
                if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and 
                    task.updated_at < cutoff_time):
                    del self.tasks[task_id]
                    tasks_cleaned += 1
            
            # Clean up old messages
            messages_cleaned = 0
            self.messages = [m for m in self.messages if m.timestamp >= cutoff_time]
            messages_cleaned = len(self.messages)
            
            return {
                "success": True,
                "sessions_cleaned": sessions_cleaned,
                "tasks_cleaned": tasks_cleaned,
                "messages_cleaned": messages_cleaned,
                "cutoff_time": cutoff_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return {"success": False, "error": str(e)}


# Global instance
_collaboration_framework = AgentCollaborationFramework()

# Tool functions for registry
def create_collaboration_session(title: str, description: str, 
                               required_capabilities: str, priority: int = 5) -> str:
    """Create a new collaboration session for complex requests."""
    capabilities_list = [cap.strip() for cap in required_capabilities.split(",")]
    result = _collaboration_framework.create_collaboration_session(
        title, description, capabilities_list, priority
    )
    return json.dumps(result, indent=2)

def delegate_task(task_id: str, from_agent: str, to_agent: str, 
                 delegation_reason: str) -> str:
    """Delegate a task from one agent to another."""
    try:
        from_role = AgentRole(from_agent)
        to_role = AgentRole(to_agent)
        result = _collaboration_framework.delegate_task(task_id, from_role, to_role, delegation_reason)
        return json.dumps(result, indent=2)
    except ValueError as e:
        return json.dumps({"success": False, "error": f"Invalid agent role: {e}"}, indent=2)

def request_collaboration(requesting_agent: str, target_agent: str, 
                        request_type: str, request_data: str) -> str:
    """Request collaboration from another agent."""
    try:
        requesting_role = AgentRole(requesting_agent)
        target_role = AgentRole(target_agent)
        data = json.loads(request_data) if request_data else {}
        result = _collaboration_framework.request_collaboration(
            requesting_role, target_role, request_type, data
        )
        return json.dumps(result, indent=2)
    except (ValueError, json.JSONDecodeError) as e:
        return json.dumps({"success": False, "error": f"Invalid input: {e}"}, indent=2)

def update_task_status(task_id: str, status: str, results: str = None, 
                      agent: str = None) -> str:
    """Update the status of a collaboration task."""
    try:
        status_enum = TaskStatus(status)
        results_data = json.loads(results) if results else None
        agent_role = AgentRole(agent) if agent else None
        result = _collaboration_framework.update_task_status(
            task_id, status_enum, results_data, agent_role
        )
        return json.dumps(result, indent=2)
    except (ValueError, json.JSONDecodeError) as e:
        return json.dumps({"success": False, "error": f"Invalid input: {e}"}, indent=2)

def get_agent_messages(agent: str, since_hours: int = 24) -> str:
    """Get messages for a specific agent."""
    try:
        agent_role = AgentRole(agent)
        since_time = datetime.utcnow() - timedelta(hours=since_hours)
        messages = _collaboration_framework.get_agent_messages(agent_role, since_time)
        return json.dumps({"messages": messages}, indent=2)
    except ValueError as e:
        return json.dumps({"error": f"Invalid agent role: {e}"}, indent=2)

def get_collaboration_status(session_id: str = None) -> str:
    """Get status of collaboration sessions and tasks."""
    result = _collaboration_framework.get_collaboration_status(session_id)
    return json.dumps(result, indent=2)