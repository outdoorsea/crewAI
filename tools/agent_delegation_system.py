"""
Agent Delegation System

This system provides sophisticated delegation and task handoff mechanisms
that allow agents to intelligently route work to the most appropriate
agent based on capabilities, workload, and context.

File: tools/agent_delegation_system.py
"""

import json
import logging
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class DelegationReason(Enum):
    """Reasons for task delegation."""
    EXPERTISE_REQUIRED = "expertise_required"
    WORKLOAD_BALANCING = "workload_balancing"
    BETTER_CAPABILITY = "better_capability"
    PRIORITY_ESCALATION = "priority_escalation"
    RESOURCE_AVAILABILITY = "resource_availability"
    CONTEXT_SWITCH = "context_switch"
    USER_REQUEST = "user_request"

class HandoffStatus(Enum):
    """Status of task handoffs."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentCapability:
    """Represents an agent's capability."""
    name: str
    proficiency: float  # 0.0 to 1.0
    confidence: float   # 0.0 to 1.0
    last_used: Optional[datetime] = None
    success_rate: float = 1.0

@dataclass
class AgentProfile:
    """Profile of an agent including capabilities and current state."""
    agent_id: str
    agent_type: str
    capabilities: List[AgentCapability]
    current_workload: int
    max_workload: int
    last_active: datetime
    success_rate: float
    average_response_time: float  # in seconds
    specializations: List[str]
    preferred_task_types: List[str]

@dataclass
class DelegationRequest:
    """Request to delegate a task to another agent."""
    id: str
    from_agent: str
    to_agent: str
    task_description: str
    required_capabilities: List[str]
    priority: int
    reason: DelegationReason
    context: Dict[str, Any]
    deadline: Optional[datetime]
    created_at: datetime
    status: HandoffStatus
    acceptance_deadline: datetime
    response_message: Optional[str] = None
    estimated_effort: Optional[int] = None  # in minutes

@dataclass
class TaskHandoff:
    """Complete task handoff including context and progress."""
    id: str
    original_task_id: str
    from_agent: str
    to_agent: str
    task_context: Dict[str, Any]
    progress_data: Dict[str, Any]
    handoff_reason: str
    created_at: datetime
    completed_at: Optional[datetime]
    status: HandoffStatus
    success: Optional[bool] = None

class AgentDelegationSystem:
    """System for managing agent delegation and task handoffs."""
    
    def __init__(self):
        """Initialize the delegation system."""
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.delegation_requests: Dict[str, DelegationRequest] = {}
        self.task_handoffs: Dict[str, TaskHandoff] = {}
        self.delegation_lock = threading.Lock()
        
        # Performance tracking
        self.delegation_history: List[Dict[str, Any]] = []
        self.capability_ratings: Dict[str, Dict[str, float]] = {}  # agent_id -> capability -> rating
        
        # Initialize default agent profiles
        self._initialize_default_profiles()
        
        logger.info("Agent Delegation System initialized")
    
    def _initialize_default_profiles(self):
        """Initialize default profiles for known agent types."""
        default_profiles = {
            "memory_librarian": {
                "capabilities": [
                    AgentCapability("memory_management", 0.95, 0.9),
                    AgentCapability("entity_tracking", 0.9, 0.85),
                    AgentCapability("conversation_history", 0.95, 0.9),
                    AgentCapability("relationship_mapping", 0.85, 0.8),
                    AgentCapability("context_preservation", 0.9, 0.85)
                ],
                "specializations": ["memory", "entities", "relationships"],
                "preferred_task_types": ["memory_search", "entity_management", "context_retrieval"]
            },
            "research_specialist": {
                "capabilities": [
                    AgentCapability("text_analysis", 0.9, 0.85),
                    AgentCapability("information_extraction", 0.95, 0.9),
                    AgentCapability("sentiment_analysis", 0.85, 0.8),
                    AgentCapability("document_processing", 0.9, 0.85),
                    AgentCapability("pattern_recognition", 0.8, 0.75)
                ],
                "specializations": ["analysis", "research", "documents"],
                "preferred_task_types": ["text_analysis", "research", "information_extraction"]
            },
            "personal_assistant": {
                "capabilities": [
                    AgentCapability("calendar_management", 0.9, 0.85),
                    AgentCapability("task_coordination", 0.85, 0.8),
                    AgentCapability("scheduling", 0.9, 0.85),
                    AgentCapability("general_assistance", 0.8, 0.75),
                    AgentCapability("workflow_management", 0.75, 0.7)
                ],
                "specializations": ["coordination", "scheduling", "assistance"],
                "preferred_task_types": ["calendar", "scheduling", "coordination"]
            },
            "health_analyst": {
                "capabilities": [
                    AgentCapability("health_data_analysis", 0.95, 0.9),
                    AgentCapability("fitness_tracking", 0.9, 0.85),
                    AgentCapability("wellness_recommendations", 0.85, 0.8),
                    AgentCapability("health_pattern_recognition", 0.8, 0.75),
                    AgentCapability("activity_monitoring", 0.9, 0.85)
                ],
                "specializations": ["health", "fitness", "wellness"],
                "preferred_task_types": ["health_analysis", "fitness_tracking", "wellness_planning"]
            },
            "finance_tracker": {
                "capabilities": [
                    AgentCapability("expense_tracking", 0.95, 0.9),
                    AgentCapability("budget_analysis", 0.9, 0.85),
                    AgentCapability("financial_planning", 0.85, 0.8),
                    AgentCapability("transaction_management", 0.95, 0.9),
                    AgentCapability("spending_analysis", 0.9, 0.85)
                ],
                "specializations": ["finance", "budgeting", "expenses"],
                "preferred_task_types": ["expense_tracking", "budget_analysis", "financial_planning"]
            }
        }
        
        for agent_type, profile_data in default_profiles.items():
            self.agent_profiles[agent_type] = AgentProfile(
                agent_id=agent_type,
                agent_type=agent_type,
                capabilities=profile_data["capabilities"],
                current_workload=0,
                max_workload=5,
                last_active=datetime.utcnow(),
                success_rate=0.95,
                average_response_time=30.0,
                specializations=profile_data["specializations"],
                preferred_task_types=profile_data["preferred_task_types"]
            )
    
    def find_best_agent(self, task_description: str, required_capabilities: List[str],
                       exclude_agents: List[str] = None, priority: int = 5) -> Dict[str, Any]:
        """
        Find the best agent to handle a task based on capabilities and current state.
        
        Args:
            task_description: Description of the task
            required_capabilities: List of required capabilities
            exclude_agents: Agents to exclude from consideration
            priority: Task priority (1-10)
            
        Returns:
            Best agent recommendation with reasoning
        """
        try:
            exclude_agents = exclude_agents or []
            candidates = []
            
            for agent_id, profile in self.agent_profiles.items():
                if agent_id in exclude_agents:
                    continue
                
                # Calculate capability match score
                capability_score = self._calculate_capability_match(profile, required_capabilities)
                
                # Calculate workload score (lower workload = higher score)
                workload_score = 1.0 - (profile.current_workload / max(profile.max_workload, 1))
                
                # Calculate availability score based on last activity
                time_since_active = (datetime.utcnow() - profile.last_active).total_seconds()
                availability_score = min(1.0, time_since_active / 300)  # 5 minutes for full availability
                
                # Calculate overall score
                overall_score = (
                    capability_score * 0.5 +
                    workload_score * 0.3 +
                    availability_score * 0.1 +
                    profile.success_rate * 0.1
                )
                
                candidates.append({
                    "agent_id": agent_id,
                    "agent_type": profile.agent_type,
                    "overall_score": overall_score,
                    "capability_score": capability_score,
                    "workload_score": workload_score,
                    "availability_score": availability_score,
                    "current_workload": profile.current_workload,
                    "max_workload": profile.max_workload,
                    "success_rate": profile.success_rate,
                    "reasoning": self._generate_selection_reasoning(
                        profile, capability_score, workload_score, availability_score
                    )
                })
            
            # Sort by overall score
            candidates.sort(key=lambda x: x["overall_score"], reverse=True)
            
            if not candidates:
                return {
                    "success": False,
                    "error": "No suitable agents found",
                    "required_capabilities": required_capabilities
                }
            
            best_agent = candidates[0]
            
            return {
                "success": True,
                "recommended_agent": best_agent["agent_id"],
                "agent_type": best_agent["agent_type"],
                "confidence": best_agent["overall_score"],
                "reasoning": best_agent["reasoning"],
                "alternatives": candidates[1:3],  # Top 2 alternatives
                "capability_match": best_agent["capability_score"]
            }
            
        except Exception as e:
            logger.error(f"Error finding best agent: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_capability_match(self, profile: AgentProfile, required_capabilities: List[str]) -> float:
        """Calculate how well an agent's capabilities match the requirements."""
        if not required_capabilities:
            return 0.5  # Neutral score if no specific capabilities required
        
        total_match = 0.0
        matched_capabilities = 0
        
        for required_cap in required_capabilities:
            best_match = 0.0
            
            # Check direct capability matches
            for capability in profile.capabilities:
                if required_cap.lower() in capability.name.lower():
                    match_score = capability.proficiency * capability.confidence
                    best_match = max(best_match, match_score)
            
            # Check specialization matches
            for specialization in profile.specializations:
                if required_cap.lower() in specialization.lower():
                    best_match = max(best_match, 0.7)
            
            # Check preferred task type matches
            for task_type in profile.preferred_task_types:
                if required_cap.lower() in task_type.lower():
                    best_match = max(best_match, 0.6)
            
            if best_match > 0:
                total_match += best_match
                matched_capabilities += 1
        
        if matched_capabilities == 0:
            return 0.1  # Very low score if no capabilities match
        
        return total_match / len(required_capabilities)
    
    def _generate_selection_reasoning(self, profile: AgentProfile, capability_score: float,
                                    workload_score: float, availability_score: float) -> str:
        """Generate human-readable reasoning for agent selection."""
        reasons = []
        
        if capability_score > 0.8:
            reasons.append("excellent capability match")
        elif capability_score > 0.6:
            reasons.append("good capability match")
        elif capability_score > 0.4:
            reasons.append("moderate capability match")
        else:
            reasons.append("limited capability match")
        
        if workload_score > 0.8:
            reasons.append("low current workload")
        elif workload_score > 0.5:
            reasons.append("moderate workload")
        else:
            reasons.append("high workload")
        
        if profile.success_rate > 0.9:
            reasons.append("high success rate")
        elif profile.success_rate > 0.7:
            reasons.append("good track record")
        
        return ", ".join(reasons)
    
    def create_delegation_request(self, from_agent: str, task_description: str,
                                required_capabilities: List[str], priority: int = 5,
                                reason: DelegationReason = DelegationReason.EXPERTISE_REQUIRED,
                                context: Dict[str, Any] = None,
                                preferred_agent: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a delegation request.
        
        Args:
            from_agent: Agent making the delegation request
            task_description: Description of the task to delegate
            required_capabilities: Required capabilities for the task
            priority: Task priority (1-10)
            reason: Reason for delegation
            context: Additional context for the task
            preferred_agent: Optional preferred agent for delegation
            
        Returns:
            Delegation request result
        """
        try:
            with self.delegation_lock:
                # Find best agent if not specified
                if preferred_agent:
                    to_agent = preferred_agent
                    confidence = 0.8  # Assume reasonable confidence for user preference
                else:
                    best_agent_result = self.find_best_agent(
                        task_description, required_capabilities, [from_agent], priority
                    )
                    
                    if not best_agent_result["success"]:
                        return best_agent_result
                    
                    to_agent = best_agent_result["recommended_agent"]
                    confidence = best_agent_result["confidence"]
                
                # Create delegation request
                request_id = f"delegation_{uuid.uuid4()}"
                delegation_request = DelegationRequest(
                    id=request_id,
                    from_agent=from_agent,
                    to_agent=to_agent,
                    task_description=task_description,
                    required_capabilities=required_capabilities,
                    priority=priority,
                    reason=reason,
                    context=context or {},
                    deadline=None,
                    created_at=datetime.utcnow(),
                    status=HandoffStatus.PENDING,
                    acceptance_deadline=datetime.utcnow() + timedelta(minutes=5)
                )
                
                self.delegation_requests[request_id] = delegation_request
                
                # Update workload prediction
                if to_agent in self.agent_profiles:
                    self.agent_profiles[to_agent].current_workload += 1
                
                logger.info(f"Created delegation request {request_id} from {from_agent} to {to_agent}")
                
                return {
                    "success": True,
                    "delegation_id": request_id,
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "confidence": confidence,
                    "reason": reason.value,
                    "acceptance_deadline": delegation_request.acceptance_deadline.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error creating delegation request: {e}")
            return {"success": False, "error": str(e)}
    
    def respond_to_delegation(self, delegation_id: str, accepting_agent: str,
                            accept: bool, response_message: str = None,
                            estimated_effort: Optional[int] = None) -> Dict[str, Any]:
        """
        Respond to a delegation request.
        
        Args:
            delegation_id: ID of the delegation request
            accepting_agent: Agent responding to the request
            accept: Whether to accept the delegation
            response_message: Optional message with the response
            estimated_effort: Estimated effort in minutes
            
        Returns:
            Response result
        """
        try:
            with self.delegation_lock:
                if delegation_id not in self.delegation_requests:
                    return {"success": False, "error": f"Delegation request {delegation_id} not found"}
                
                request = self.delegation_requests[delegation_id]
                
                if request.to_agent != accepting_agent:
                    return {"success": False, "error": "Only the target agent can respond to this delegation"}
                
                if request.status != HandoffStatus.PENDING:
                    return {"success": False, "error": f"Delegation request is already {request.status.value}"}
                
                # Update request status
                if accept:
                    request.status = HandoffStatus.ACCEPTED
                    logger.info(f"Delegation {delegation_id} accepted by {accepting_agent}")
                else:
                    request.status = HandoffStatus.REJECTED
                    # Reduce workload prediction since task was rejected
                    if accepting_agent in self.agent_profiles:
                        self.agent_profiles[accepting_agent].current_workload = max(
                            0, self.agent_profiles[accepting_agent].current_workload - 1
                        )
                    logger.info(f"Delegation {delegation_id} rejected by {accepting_agent}")
                
                request.response_message = response_message
                request.estimated_effort = estimated_effort
                
                return {
                    "success": True,
                    "delegation_id": delegation_id,
                    "accepted": accept,
                    "responding_agent": accepting_agent,
                    "response_message": response_message
                }
                
        except Exception as e:
            logger.error(f"Error responding to delegation: {e}")
            return {"success": False, "error": str(e)}
    
    def create_task_handoff(self, original_task_id: str, from_agent: str, to_agent: str,
                          task_context: Dict[str, Any], progress_data: Dict[str, Any],
                          handoff_reason: str) -> Dict[str, Any]:
        """
        Create a complete task handoff with context and progress.
        
        Args:
            original_task_id: ID of the original task
            from_agent: Agent handing off the task
            to_agent: Agent receiving the task
            task_context: Complete context of the task
            progress_data: Current progress and state
            handoff_reason: Reason for the handoff
            
        Returns:
            Handoff creation result
        """
        try:
            with self.delegation_lock:
                handoff_id = f"handoff_{uuid.uuid4()}"
                
                task_handoff = TaskHandoff(
                    id=handoff_id,
                    original_task_id=original_task_id,
                    from_agent=from_agent,
                    to_agent=to_agent,
                    task_context=task_context,
                    progress_data=progress_data,
                    handoff_reason=handoff_reason,
                    created_at=datetime.utcnow(),
                    completed_at=None,
                    status=HandoffStatus.IN_PROGRESS
                )
                
                self.task_handoffs[handoff_id] = task_handoff
                
                # Update agent workloads
                if from_agent in self.agent_profiles:
                    self.agent_profiles[from_agent].current_workload = max(
                        0, self.agent_profiles[from_agent].current_workload - 1
                    )
                
                if to_agent in self.agent_profiles:
                    self.agent_profiles[to_agent].current_workload += 1
                
                logger.info(f"Created task handoff {handoff_id} from {from_agent} to {to_agent}")
                
                return {
                    "success": True,
                    "handoff_id": handoff_id,
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "original_task_id": original_task_id
                }
                
        except Exception as e:
            logger.error(f"Error creating task handoff: {e}")
            return {"success": False, "error": str(e)}
    
    def complete_handoff(self, handoff_id: str, completing_agent: str, 
                        success: bool, results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Mark a task handoff as completed.
        
        Args:
            handoff_id: ID of the handoff
            completing_agent: Agent completing the handoff
            success: Whether the handoff was successful
            results: Optional results data
            
        Returns:
            Completion result
        """
        try:
            with self.delegation_lock:
                if handoff_id not in self.task_handoffs:
                    return {"success": False, "error": f"Task handoff {handoff_id} not found"}
                
                handoff = self.task_handoffs[handoff_id]
                
                if handoff.to_agent != completing_agent:
                    return {"success": False, "error": "Only the receiving agent can complete this handoff"}
                
                handoff.status = HandoffStatus.COMPLETED if success else HandoffStatus.FAILED
                handoff.completed_at = datetime.utcnow()
                handoff.success = success
                
                # Update agent workload
                if completing_agent in self.agent_profiles:
                    self.agent_profiles[completing_agent].current_workload = max(
                        0, self.agent_profiles[completing_agent].current_workload - 1
                    )
                
                # Record in history for learning
                self.delegation_history.append({
                    "handoff_id": handoff_id,
                    "from_agent": handoff.from_agent,
                    "to_agent": handoff.to_agent,
                    "success": success,
                    "completion_time": handoff.completed_at.isoformat(),
                    "duration_minutes": (handoff.completed_at - handoff.created_at).total_seconds() / 60
                })
                
                logger.info(f"Completed handoff {handoff_id} with success={success}")
                
                return {
                    "success": True,
                    "handoff_id": handoff_id,
                    "completed_successfully": success,
                    "completion_time": handoff.completed_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error completing handoff: {e}")
            return {"success": False, "error": str(e)}
    
    def get_agent_workload(self, agent_id: str) -> Dict[str, Any]:
        """Get current workload and status for an agent."""
        try:
            if agent_id not in self.agent_profiles:
                return {"success": False, "error": f"Agent {agent_id} not found"}
            
            profile = self.agent_profiles[agent_id]
            
            # Calculate pending delegations
            pending_delegations = len([req for req in self.delegation_requests.values()
                                     if req.to_agent == agent_id and req.status == HandoffStatus.PENDING])
            
            # Calculate active handoffs
            active_handoffs = len([handoff for handoff in self.task_handoffs.values()
                                 if handoff.to_agent == agent_id and handoff.status == HandoffStatus.IN_PROGRESS])
            
            return {
                "success": True,
                "agent_id": agent_id,
                "current_workload": profile.current_workload,
                "max_workload": profile.max_workload,
                "capacity_utilization": profile.current_workload / max(profile.max_workload, 1),
                "pending_delegations": pending_delegations,
                "active_handoffs": active_handoffs,
                "last_active": profile.last_active.isoformat(),
                "success_rate": profile.success_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting agent workload: {e}")
            return {"success": False, "error": str(e)}
    
    def get_delegation_status(self) -> Dict[str, Any]:
        """Get overall delegation system status."""
        try:
            pending_requests = len([req for req in self.delegation_requests.values()
                                  if req.status == HandoffStatus.PENDING])
            
            active_handoffs = len([handoff for handoff in self.task_handoffs.values()
                                 if handoff.status == HandoffStatus.IN_PROGRESS])
            
            recent_completions = len([entry for entry in self.delegation_history
                                    if datetime.fromisoformat(entry["completion_time"]) > 
                                    datetime.utcnow() - timedelta(hours=1)])
            
            return {
                "total_agents": len(self.agent_profiles),
                "pending_delegation_requests": pending_requests,
                "active_handoffs": active_handoffs,
                "recent_completions": recent_completions,
                "total_delegation_history": len(self.delegation_history),
                "system_health": "healthy" if pending_requests < 10 and active_handoffs < 20 else "busy"
            }
            
        except Exception as e:
            logger.error(f"Error getting delegation status: {e}")
            return {"error": str(e)}


# Global instance
_delegation_system = AgentDelegationSystem()

# Tool functions for registry
def find_best_agent_for_task(task_description: str, required_capabilities: str,
                            exclude_agents: str = None, priority: int = 5) -> str:
    """Find the best agent to handle a task based on capabilities."""
    capabilities_list = [cap.strip() for cap in required_capabilities.split(",")]
    exclude_list = [agent.strip() for agent in exclude_agents.split(",")] if exclude_agents else []
    
    result = _delegation_system.find_best_agent(task_description, capabilities_list, exclude_list, priority)
    return json.dumps(result, indent=2)

def delegate_task_to_agent(from_agent: str, task_description: str, required_capabilities: str,
                         priority: int = 5, reason: str = "expertise_required",
                         preferred_agent: str = None) -> str:
    """Create a delegation request to hand off a task to another agent."""
    try:
        capabilities_list = [cap.strip() for cap in required_capabilities.split(",")]
        reason_enum = DelegationReason(reason)
        
        result = _delegation_system.create_delegation_request(
            from_agent, task_description, capabilities_list, priority, reason_enum, {}, preferred_agent
        )
        return json.dumps(result, indent=2)
    except ValueError as e:
        return json.dumps({"success": False, "error": f"Invalid reason: {e}"}, indent=2)

def respond_to_task_delegation(delegation_id: str, accepting_agent: str, accept: bool,
                             response_message: str = None, estimated_effort: int = None) -> str:
    """Respond to a delegation request (accept or reject)."""
    result = _delegation_system.respond_to_delegation(
        delegation_id, accepting_agent, accept, response_message, estimated_effort
    )
    return json.dumps(result, indent=2)

def create_task_handoff(original_task_id: str, from_agent: str, to_agent: str,
                       task_context: str, progress_data: str, handoff_reason: str) -> str:
    """Create a complete task handoff with context and progress."""
    try:
        context_data = json.loads(task_context) if task_context else {}
        progress_dict = json.loads(progress_data) if progress_data else {}
        
        result = _delegation_system.create_task_handoff(
            original_task_id, from_agent, to_agent, context_data, progress_dict, handoff_reason
        )
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {e}"}, indent=2)

def get_agent_workload_status(agent_id: str) -> str:
    """Get current workload and status for an agent."""
    result = _delegation_system.get_agent_workload(agent_id)
    return json.dumps(result, indent=2)

def get_delegation_system_status() -> str:
    """Get overall delegation system status."""
    result = _delegation_system.get_delegation_status()
    return json.dumps(result, indent=2)