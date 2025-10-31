"""
Feedback Analytics System

This system collects, stores, and analyzes user feedback (👍/👎 ratings) for 
CrewAI agents to enable performance tracking, A/B testing, and continuous improvement.

File: tools/feedback_analytics.py
"""

import json
import logging
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    RATING = "rating"  # 1-5 star rating
    TEXT_FEEDBACK = "text_feedback"

class ResponseType(Enum):
    """Types of responses being rated."""
    AGENT_RESPONSE = "agent_response"
    TOOL_EXECUTION = "tool_execution"
    ROUTING_DECISION = "routing_decision"
    COLLABORATION = "collaboration"

@dataclass
class FeedbackEntry:
    """Individual feedback entry."""
    id: str
    session_id: str
    user_id: Optional[str]
    timestamp: datetime
    
    # Response details
    agent_id: str
    agent_name: str
    response_type: ResponseType
    response_id: str
    response_content: str
    routing_confidence: float
    response_time_ms: int
    
    # Feedback details
    feedback_type: FeedbackType
    feedback_value: Any  # Could be bool, int, or str
    feedback_text: Optional[str]
    
    # Context
    user_message: str
    conversation_context: Dict[str, Any]
    tools_used: List[str]
    collaboration_agents: List[str]

@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for an agent."""
    agent_id: str
    agent_name: str
    
    # Feedback metrics
    total_responses: int
    positive_feedback: int
    negative_feedback: int
    average_rating: float
    feedback_ratio: float  # positive / total
    
    # Performance metrics
    average_response_time_ms: float
    average_routing_confidence: float
    total_tools_used: int
    collaboration_frequency: float
    
    # Time-based metrics
    responses_last_24h: int
    responses_last_7d: int
    responses_last_30d: int
    
    # Calculated at runtime
    calculated_at: datetime

class FeedbackAnalytics:
    """System for collecting and analyzing user feedback."""
    
    def __init__(self, db_path: str = None):
        """Initialize the feedback analytics system."""
        if db_path is None:
            db_path = str(Path.home() / "myndy" / "feedback" / "analytics.db")
        
        self.db_path = db_path
        self.analytics_lock = threading.Lock()
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        
        # In-memory cache for recent feedback
        self.recent_feedback: Dict[str, FeedbackEntry] = {}
        self.cache_size = 1000
        
        # Performance tracking
        self.response_times: Dict[str, List[float]] = {}
        self.routing_accuracy: Dict[str, List[float]] = {}
        
        logger.info(f"Feedback Analytics System initialized with database: {self.db_path}")
    
    def _initialize_database(self):
        """Initialize SQLite database for feedback storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_entries (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    timestamp TEXT NOT NULL,
                    
                    agent_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    response_type TEXT NOT NULL,
                    response_id TEXT NOT NULL,
                    response_content TEXT,
                    routing_confidence REAL,
                    response_time_ms INTEGER,
                    
                    feedback_type TEXT NOT NULL,
                    feedback_value TEXT,
                    feedback_text TEXT,
                    
                    user_message TEXT,
                    conversation_context TEXT,
                    tools_used TEXT,
                    collaboration_agents TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_performance_cache (
                    agent_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    calculated_at TEXT NOT NULL
                )
            """)
            
            # Create indexes for faster queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON feedback_entries(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback_entries(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON feedback_entries(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback_entries(feedback_type)")
            
            conn.commit()
            logger.info("Feedback database initialized successfully")
    
    def record_feedback(self, session_id: str, agent_id: str, agent_name: str,
                       response_id: str, response_content: str, user_message: str,
                       feedback_type: FeedbackType, feedback_value: Any,
                       response_type: ResponseType = ResponseType.AGENT_RESPONSE,
                       routing_confidence: float = 0.0, response_time_ms: int = 0,
                       feedback_text: str = None, tools_used: List[str] = None,
                       collaboration_agents: List[str] = None,
                       conversation_context: Dict[str, Any] = None,
                       user_id: str = None) -> str:
        """
        Record user feedback for an agent response.
        
        Returns:
            Feedback entry ID
        """
        try:
            with self.analytics_lock:
                feedback_id = f"feedback_{uuid.uuid4()}"
                
                feedback_entry = FeedbackEntry(
                    id=feedback_id,
                    session_id=session_id,
                    user_id=user_id,
                    timestamp=datetime.utcnow(),
                    
                    agent_id=agent_id,
                    agent_name=agent_name,
                    response_type=response_type,
                    response_id=response_id,
                    response_content=response_content[:1000],  # Truncate for storage
                    routing_confidence=routing_confidence,
                    response_time_ms=response_time_ms,
                    
                    feedback_type=feedback_type,
                    feedback_value=feedback_value,
                    feedback_text=feedback_text,
                    
                    user_message=user_message[:1000],  # Truncate for storage
                    conversation_context=conversation_context or {},
                    tools_used=tools_used or [],
                    collaboration_agents=collaboration_agents or []
                )
                
                # Store in database
                self._store_feedback_entry(feedback_entry)
                
                # Cache recent feedback
                self._cache_feedback_entry(feedback_entry)
                
                # Update performance tracking
                self._update_performance_tracking(feedback_entry)
                
                logger.info(f"Recorded {feedback_type.value} feedback for agent {agent_id}")
                
                return feedback_id
                
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return None
    
    def _store_feedback_entry(self, entry: FeedbackEntry):
        """Store feedback entry in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO feedback_entries (
                    id, session_id, user_id, timestamp,
                    agent_id, agent_name, response_type, response_id, response_content,
                    routing_confidence, response_time_ms,
                    feedback_type, feedback_value, feedback_text,
                    user_message, conversation_context, tools_used, collaboration_agents
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id, entry.session_id, entry.user_id, entry.timestamp.isoformat(),
                entry.agent_id, entry.agent_name, entry.response_type.value,
                entry.response_id, entry.response_content, entry.routing_confidence,
                entry.response_time_ms, entry.feedback_type.value, 
                json.dumps(entry.feedback_value), entry.feedback_text,
                entry.user_message, json.dumps(entry.conversation_context),
                json.dumps(entry.tools_used), json.dumps(entry.collaboration_agents)
            ))
            conn.commit()
    
    def _cache_feedback_entry(self, entry: FeedbackEntry):
        """Cache feedback entry in memory for quick access."""
        self.recent_feedback[entry.id] = entry
        
        # Maintain cache size
        if len(self.recent_feedback) > self.cache_size:
            # Remove oldest entries
            sorted_entries = sorted(self.recent_feedback.items(), 
                                  key=lambda x: x[1].timestamp)
            for old_id, _ in sorted_entries[:len(self.recent_feedback) - self.cache_size]:
                del self.recent_feedback[old_id]
    
    def _update_performance_tracking(self, entry: FeedbackEntry):
        """Update in-memory performance tracking."""
        agent_id = entry.agent_id
        
        # Track response times
        if agent_id not in self.response_times:
            self.response_times[agent_id] = []
        self.response_times[agent_id].append(entry.response_time_ms)
        
        # Keep only recent response times (last 100)
        if len(self.response_times[agent_id]) > 100:
            self.response_times[agent_id] = self.response_times[agent_id][-100:]
        
        # Track routing accuracy
        if agent_id not in self.routing_accuracy:
            self.routing_accuracy[agent_id] = []
        self.routing_accuracy[agent_id].append(entry.routing_confidence)
        
        # Keep only recent routing scores (last 100)
        if len(self.routing_accuracy[agent_id]) > 100:
            self.routing_accuracy[agent_id] = self.routing_accuracy[agent_id][-100:]
    
    def get_agent_performance(self, agent_id: str, 
                             recalculate: bool = False) -> Optional[AgentPerformanceMetrics]:
        """
        Get performance metrics for a specific agent.
        
        Args:
            agent_id: Agent to get metrics for
            recalculate: Force recalculation instead of using cache
            
        Returns:
            Agent performance metrics or None if not found
        """
        try:
            # Check cache first unless forced recalculation
            if not recalculate:
                cached_metrics = self._get_cached_metrics(agent_id)
                if cached_metrics and cached_metrics.calculated_at > datetime.utcnow() - timedelta(minutes=5):
                    return cached_metrics
            
            # Calculate fresh metrics
            metrics = self._calculate_agent_metrics(agent_id)
            
            if metrics:
                # Cache the results
                self._cache_agent_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting agent performance for {agent_id}: {e}")
            return None
    
    def _get_cached_metrics(self, agent_id: str) -> Optional[AgentPerformanceMetrics]:
        """Get cached performance metrics for an agent."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT metrics_json, calculated_at FROM agent_performance_cache WHERE agent_id = ?",
                    (agent_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    metrics_data = json.loads(row[0])
                    metrics_data['calculated_at'] = datetime.fromisoformat(row[1])
                    return AgentPerformanceMetrics(**metrics_data)
                    
        except Exception as e:
            logger.debug(f"Error getting cached metrics: {e}")
            
        return None
    
    def _calculate_agent_metrics(self, agent_id: str) -> Optional[AgentPerformanceMetrics]:
        """Calculate fresh performance metrics for an agent."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get agent name
                cursor = conn.execute(
                    "SELECT agent_name FROM feedback_entries WHERE agent_id = ? LIMIT 1",
                    (agent_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                
                agent_name = row[0]
                
                # Calculate basic metrics
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_responses,
                        SUM(CASE WHEN feedback_type = 'thumbs_up' THEN 1 ELSE 0 END) as positive,
                        SUM(CASE WHEN feedback_type = 'thumbs_down' THEN 1 ELSE 0 END) as negative,
                        AVG(CASE WHEN feedback_type = 'rating' THEN CAST(feedback_value as REAL) ELSE NULL END) as avg_rating,
                        AVG(response_time_ms) as avg_response_time,
                        AVG(routing_confidence) as avg_routing_confidence,
                        COUNT(DISTINCT tools_used) as total_tools,
                        SUM(CASE WHEN collaboration_agents != '[]' THEN 1 ELSE 0 END) as collaboration_count
                    FROM feedback_entries 
                    WHERE agent_id = ?
                """, (agent_id,))
                
                row = cursor.fetchone()
                total_responses, positive, negative, avg_rating, avg_response_time, avg_routing_confidence, total_tools, collaboration_count = row
                
                if total_responses == 0:
                    return None
                
                # Calculate time-based metrics
                now = datetime.utcnow()
                
                # Last 24 hours
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM feedback_entries 
                    WHERE agent_id = ? AND timestamp >= ?
                """, (agent_id, (now - timedelta(hours=24)).isoformat()))
                responses_24h = cursor.fetchone()[0]
                
                # Last 7 days
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM feedback_entries 
                    WHERE agent_id = ? AND timestamp >= ?
                """, (agent_id, (now - timedelta(days=7)).isoformat()))
                responses_7d = cursor.fetchone()[0]
                
                # Last 30 days
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM feedback_entries 
                    WHERE agent_id = ? AND timestamp >= ?
                """, (agent_id, (now - timedelta(days=30)).isoformat()))
                responses_30d = cursor.fetchone()[0]
                
                # Calculate derived metrics
                feedback_ratio = positive / total_responses if total_responses > 0 else 0.0
                collaboration_frequency = collaboration_count / total_responses if total_responses > 0 else 0.0
                
                return AgentPerformanceMetrics(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    total_responses=total_responses,
                    positive_feedback=positive or 0,
                    negative_feedback=negative or 0,
                    average_rating=avg_rating or 0.0,
                    feedback_ratio=feedback_ratio,
                    average_response_time_ms=avg_response_time or 0.0,
                    average_routing_confidence=avg_routing_confidence or 0.0,
                    total_tools_used=total_tools or 0,
                    collaboration_frequency=collaboration_frequency,
                    responses_last_24h=responses_24h,
                    responses_last_7d=responses_7d,
                    responses_last_30d=responses_30d,
                    calculated_at=now
                )
                
        except Exception as e:
            logger.error(f"Error calculating metrics for {agent_id}: {e}")
            return None
    
    def _cache_agent_metrics(self, metrics: AgentPerformanceMetrics):
        """Cache agent performance metrics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Convert metrics to dict, excluding calculated_at for JSON serialization
                metrics_dict = asdict(metrics)
                metrics_dict.pop('calculated_at')  # Store separately
                
                conn.execute("""
                    INSERT OR REPLACE INTO agent_performance_cache 
                    (agent_id, agent_name, metrics_json, calculated_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    metrics.agent_id, 
                    metrics.agent_name,
                    json.dumps(metrics_dict),
                    metrics.calculated_at.isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error caching metrics: {e}")
    
    def get_all_agent_performance(self) -> Dict[str, AgentPerformanceMetrics]:
        """Get performance metrics for all agents."""
        try:
            # Get list of all agents
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT DISTINCT agent_id FROM feedback_entries")
                agent_ids = [row[0] for row in cursor.fetchall()]
            
            # Get metrics for each agent
            all_metrics = {}
            for agent_id in agent_ids:
                metrics = self.get_agent_performance(agent_id)
                if metrics:
                    all_metrics[agent_id] = metrics
            
            return all_metrics
            
        except Exception as e:
            logger.error(f"Error getting all agent performance: {e}")
            return {}
    
    def get_feedback_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get a summary of feedback over the specified period."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                # Overall stats
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_feedback,
                        SUM(CASE WHEN feedback_type = 'thumbs_up' THEN 1 ELSE 0 END) as positive,
                        SUM(CASE WHEN feedback_type = 'thumbs_down' THEN 1 ELSE 0 END) as negative,
                        COUNT(DISTINCT agent_id) as active_agents,
                        COUNT(DISTINCT session_id) as unique_sessions,
                        AVG(response_time_ms) as avg_response_time
                    FROM feedback_entries 
                    WHERE timestamp >= ?
                """, (start_date.isoformat(),))
                
                row = cursor.fetchone()
                total_feedback, positive, negative, active_agents, unique_sessions, avg_response_time = row
                
                # Agent breakdown
                cursor = conn.execute("""
                    SELECT 
                        agent_id,
                        agent_name,
                        COUNT(*) as responses,
                        SUM(CASE WHEN feedback_type = 'thumbs_up' THEN 1 ELSE 0 END) as positive,
                        AVG(response_time_ms) as avg_time
                    FROM feedback_entries 
                    WHERE timestamp >= ?
                    GROUP BY agent_id, agent_name
                    ORDER BY responses DESC
                """, (start_date.isoformat(),))
                
                agent_breakdown = []
                for row in cursor.fetchall():
                    agent_id, agent_name, responses, pos, avg_time = row
                    agent_breakdown.append({
                        "agent_id": agent_id,
                        "agent_name": agent_name,
                        "total_responses": responses,
                        "positive_feedback": pos or 0,
                        "feedback_ratio": (pos or 0) / responses if responses > 0 else 0,
                        "avg_response_time_ms": avg_time or 0
                    })
                
                return {
                    "period_days": days,
                    "total_feedback_entries": total_feedback or 0,
                    "positive_feedback": positive or 0,
                    "negative_feedback": negative or 0,
                    "overall_satisfaction": (positive or 0) / (total_feedback or 1),
                    "active_agents": active_agents or 0,
                    "unique_sessions": unique_sessions or 0,
                    "average_response_time_ms": avg_response_time or 0,
                    "agent_breakdown": agent_breakdown,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating feedback summary: {e}")
            return {"error": str(e)}
    
    def record_thumbs_up(self, session_id: str, agent_id: str, agent_name: str,
                        response_id: str, response_content: str, user_message: str,
                        **kwargs) -> str:
        """Convenience method to record thumbs up feedback."""
        return self.record_feedback(
            session_id=session_id,
            agent_id=agent_id,
            agent_name=agent_name,
            response_id=response_id,
            response_content=response_content,
            user_message=user_message,
            feedback_type=FeedbackType.THUMBS_UP,
            feedback_value=True,
            **kwargs
        )
    
    def record_thumbs_down(self, session_id: str, agent_id: str, agent_name: str,
                          response_id: str, response_content: str, user_message: str,
                          feedback_text: str = None, **kwargs) -> str:
        """Convenience method to record thumbs down feedback."""
        return self.record_feedback(
            session_id=session_id,
            agent_id=agent_id,
            agent_name=agent_name,
            response_id=response_id,
            response_content=response_content,
            user_message=user_message,
            feedback_type=FeedbackType.THUMBS_DOWN,
            feedback_value=False,
            feedback_text=feedback_text,
            **kwargs
        )
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get total feedback count
                cursor = conn.execute("SELECT COUNT(*) FROM feedback_entries")
                total_feedback = cursor.fetchone()[0]
                
                # Get recent activity (last 24 hours)
                recent_cutoff = datetime.utcnow() - timedelta(hours=24)
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM feedback_entries WHERE timestamp >= ?",
                    (recent_cutoff.isoformat(),)
                )
                recent_activity = cursor.fetchone()[0]
                
                # Get database size
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    "total_feedback_entries": total_feedback,
                    "recent_activity_24h": recent_activity,
                    "database_size_bytes": db_size,
                    "cache_size": len(self.recent_feedback),
                    "system_status": "healthy" if recent_activity > 0 else "idle",
                    "last_updated": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"error": str(e), "system_status": "error"}


# Global instance
_feedback_analytics = FeedbackAnalytics()

# Tool functions for registry
def record_thumbs_up_feedback(session_id: str, agent_id: str, agent_name: str,
                             response_id: str, response_content: str, user_message: str,
                             routing_confidence: float = 0.0, response_time_ms: int = 0,
                             tools_used: str = None) -> str:
    """Record thumbs up feedback for an agent response."""
    tools_list = tools_used.split(",") if tools_used else []
    feedback_id = _feedback_analytics.record_thumbs_up(
        session_id=session_id,
        agent_id=agent_id,
        agent_name=agent_name,
        response_id=response_id,
        response_content=response_content,
        user_message=user_message,
        routing_confidence=routing_confidence,
        response_time_ms=response_time_ms,
        tools_used=tools_list
    )
    return json.dumps({"success": True, "feedback_id": feedback_id}, indent=2)

def record_thumbs_down_feedback(session_id: str, agent_id: str, agent_name: str,
                               response_id: str, response_content: str, user_message: str,
                               feedback_text: str = None, routing_confidence: float = 0.0,
                               response_time_ms: int = 0, tools_used: str = None) -> str:
    """Record thumbs down feedback for an agent response."""
    tools_list = tools_used.split(",") if tools_used else []
    feedback_id = _feedback_analytics.record_thumbs_down(
        session_id=session_id,
        agent_id=agent_id,
        agent_name=agent_name,
        response_id=response_id,
        response_content=response_content,
        user_message=user_message,
        feedback_text=feedback_text,
        routing_confidence=routing_confidence,
        response_time_ms=response_time_ms,
        tools_used=tools_list
    )
    return json.dumps({"success": True, "feedback_id": feedback_id}, indent=2)

def get_agent_performance_metrics(agent_id: str, recalculate: bool = False) -> str:
    """Get performance metrics for a specific agent."""
    metrics = _feedback_analytics.get_agent_performance(agent_id, recalculate)
    if metrics:
        metrics_dict = asdict(metrics)
        metrics_dict['calculated_at'] = metrics_dict['calculated_at'].isoformat()
        return json.dumps(metrics_dict, indent=2)
    else:
        return json.dumps({"error": f"No metrics found for agent {agent_id}"}, indent=2)

def get_all_agent_performance_metrics() -> str:
    """Get performance metrics for all agents."""
    all_metrics = _feedback_analytics.get_all_agent_performance()
    
    # Convert to serializable format
    serializable_metrics = {}
    for agent_id, metrics in all_metrics.items():
        metrics_dict = asdict(metrics)
        metrics_dict['calculated_at'] = metrics_dict['calculated_at'].isoformat()
        serializable_metrics[agent_id] = metrics_dict
    
    return json.dumps(serializable_metrics, indent=2)

def get_feedback_summary(days: int = 7) -> str:
    """Get feedback summary for the specified number of days."""
    summary = _feedback_analytics.get_feedback_summary(days)
    return json.dumps(summary, indent=2)

def get_feedback_system_health() -> str:
    """Get overall feedback system health metrics."""
    health = _feedback_analytics.get_system_health()
    return json.dumps(health, indent=2)