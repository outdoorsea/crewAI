"""
Status Monitoring Tool for CrewAI Agents

This tool enables agents to monitor and update the user's current status including
mood, location, health metrics, activity, and contextual information.

File: tools/status_monitoring_tool.py
"""

import sys
import json
import logging
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configure logging first
logger = logging.getLogger(__name__)

# Add parent directory to path for config imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.env_config import env_config

# Setup Myndy-AI path from environment
myndy_available = env_config.setup_myndy_path()

if myndy_available:
    # Try to import memory models first (these should work)
    try:
        from memory.status_model import Status, StatusUpdate, Location, HealthStats, CalendarEvent, StatusAttribute
        logger.debug("Successfully imported myndy memory model components")
    except ImportError as e:
        logger.warning(f"Could not import myndy memory model components: {e}")
        Status = None
        StatusUpdate = None  
        Location = None
        HealthStats = None
        CalendarEvent = None
        StatusAttribute = None
    
    # Try to import qdrant components separately (these may fail)
    try:
        from qdrant.collections.memory import memory_manager
        logger.debug("Successfully imported qdrant memory manager")
    except ImportError as e:
        logger.warning(f"Could not import qdrant memory manager: {e}")
        memory_manager = None
else:
    logger.warning(f"Myndy-AI path not found: {env_config.myndy_path}")
    Status = None
    StatusUpdate = None  
    Location = None
    HealthStats = None
    CalendarEvent = None
    StatusAttribute = None
    memory_manager = None
    CalendarEvent = None
    StatusAttribute = None
    memory_manager = None
from pydantic import BaseModel, Field

class StatusMonitoringTool:
    """Tool for monitoring and updating user status information."""
    
    def __init__(self):
        """Initialize the status monitoring tool."""
        try:
            self.memory_manager = memory_manager  # Use new qdrant architecture directly
            logger.info("Successfully initialized StatusMonitoringTool with qdrant memory manager")
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            # Fallback to in-memory storage
            self.memory_manager = None
            self.current_status: Optional[Status] = None
            self.status_history: List[Status] = []
        
    def get_current_status(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get the current status for a user using qdrant architecture.
        
        Args:
            user_id: User identifier
            
        Returns:
            Current status information as a dictionary
        """
        try:
            if self.memory_manager:
                # Search for latest status in qdrant
                results = self.memory_manager.search.search_text(
                    query=f"user_id:{user_id}",
                    model_types=["status"],
                    sections=["memory"],
                    limit=1
                )
                
                if results:
                    latest_status = results[0]
                    return {
                        "user_id": user_id,
                        "timestamp": latest_status.metadata.get("timestamp", datetime.utcnow().isoformat()),
                        "status_data": latest_status.metadata,
                        "score": latest_status.score
                    }
                else:
                    return {
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "No current status available",
                        "note": "Use update_status to set initial status"
                    }
            else:
                # Fallback to in-memory storage
                if self.current_status and self.current_status.user_id == user_id:
                    return self.current_status.model_dump() if hasattr(self.current_status, 'model_dump') else self.current_status.dict()
                else:
                    return {
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "No current status available",
                        "note": "Use update_status to set initial status"
                    }
        except Exception as e:
            logger.error(f"Error getting current status: {e}")
            return {"error": str(e)}
    
    def update_status(self, user_id: str = "default", **status_data) -> Dict[str, Any]:
        """
        Update the user's current status using qdrant architecture.
        
        Args:
            user_id: User identifier
            **status_data: Status fields to update (mood, activity, location, etc.)
            
        Returns:
            Updated status information
        """
        try:
            if self.memory_manager:
                # Prepare status data for qdrant storage
                status_data["user_id"] = user_id
                timestamp = datetime.utcnow()
                status_data["timestamp"] = timestamp.isoformat()
                
                # Create status document for qdrant
                status_content = f"User {user_id} status update: {', '.join([f'{k}={v}' for k, v in status_data.items()])}"
                
                # Store in qdrant using collection manager
                point_id = str(uuid.uuid4())
                
                # Use collection manager to save
                success = self.memory_manager.collections.save_model(
                    model_type="status",
                    model_data={
                        "id": point_id,
                        "content": status_content,
                        "metadata": status_data,
                        "section": "memory"
                    }
                )
                
                if success:
                    logger.info(f"Updated status for user {user_id} in qdrant")
                    return {
                        "success": True,
                        "updated_at": timestamp.isoformat(),
                        "status_id": point_id,
                        "current_status": status_data
                    }
                else:
                    return {"error": "Failed to save status to qdrant", "success": False}
            else:
                # Fallback to in-memory storage
                # Create new status or update existing
                if self.current_status and self.current_status.user_id == user_id:
                    # Update existing status
                    for field, value in status_data.items():
                        if hasattr(self.current_status, field):
                            setattr(self.current_status, field, value)
                    self.current_status.timestamp = datetime.utcnow()
                else:
                    # Create new status
                    status_data["user_id"] = user_id
                    status_data["timestamp"] = datetime.utcnow()
                    self.current_status = Status(**status_data)
                
                # Add to history
                self.status_history.append(self.current_status)
                
                # Keep only last 100 status updates
                if len(self.status_history) > 100:
                    self.status_history = self.status_history[-100:]
                
                logger.info(f"Updated status for user {user_id} (in-memory)")
                return {
                    "success": True,
                    "updated_at": self.current_status.timestamp.isoformat(),
                    "current_status": self.current_status.model_dump() if hasattr(self.current_status, 'model_dump') else self.current_status.dict()
                }
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return {"error": str(e), "success": False}
    
    def update_mood(self, user_id: str = "default", mood: str = None, 
                   stress_level: int = None, valence: float = None, 
                   arousal: float = None) -> Dict[str, Any]:
        """
        Update mood-related status information.
        
        Args:
            user_id: User identifier
            mood: Current mood (happy, sad, anxious, relaxed, angry, excited, neutral)
            stress_level: Stress level on 1-10 scale
            valence: Emotional valence (-1.0 to 1.0)
            arousal: Emotional arousal (-1.0 to 1.0)
            
        Returns:
            Updated status with mood information
        """
        mood_data = {}
        if mood:
            mood_data["mood"] = mood
        if stress_level is not None:
            mood_data["stress_level"] = stress_level
        if valence is not None:
            mood_data["valence"] = valence
        if arousal is not None:
            mood_data["arousal"] = arousal
            
        return self.update_status(user_id=user_id, **mood_data)
    
    def update_activity(self, user_id: str = "default", activity: str = None,
                       location_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update activity and location information.
        
        Args:
            user_id: User identifier
            activity: Current activity description
            location_data: Location information (latitude, longitude, etc.)
            
        Returns:
            Updated status with activity/location information
        """
        activity_data = {}
        if activity:
            activity_data["activity"] = activity
        if location_data:
            try:
                location = Location(**location_data)
                activity_data["location"] = location
            except Exception as e:
                logger.warning(f"Invalid location data: {e}")
                
        return self.update_status(user_id=user_id, **activity_data)
    
    def update_health_metrics(self, user_id: str = "default", **health_data) -> Dict[str, Any]:
        """
        Update health-related status information.
        
        Args:
            user_id: User identifier
            **health_data: Health metrics (heart_rate, steps, sleep_quality, etc.)
            
        Returns:
            Updated status with health information
        """
        try:
            health_stats = HealthStats(**health_data)
            return self.update_status(user_id=user_id, health=health_stats)
        except Exception as e:
            logger.error(f"Error updating health metrics: {e}")
            return {"error": str(e), "success": False}
    
    def add_status_attribute(self, user_id: str = "default", name: str = None,
                           level: int = None, active: bool = True) -> Dict[str, Any]:
        """
        Add a status attribute (like 'hungry', 'tired', 'busy').
        
        Args:
            user_id: User identifier
            name: Attribute name
            level: Intensity level (1-10)
            active: Whether the attribute is currently active
            
        Returns:
            Updated status with new attribute
        """
        if not name:
            return {"error": "Attribute name is required", "success": False}
        
        try:
            # Get current status or create new one
            if not self.current_status or self.current_status.user_id != user_id:
                self.update_status(user_id=user_id)
            
            # Initialize attributes if needed
            if not self.current_status.attributes:
                self.current_status.attributes = []
            
            # Create new attribute
            new_attribute = StatusAttribute(name=name, level=level, active=active)
            
            # Remove existing attribute with same name
            self.current_status.attributes = [
                attr for attr in self.current_status.attributes if attr.name != name
            ]
            
            # Add new attribute
            self.current_status.attributes.append(new_attribute)
            self.current_status.timestamp = datetime.utcnow()
            
            return {
                "success": True,
                "attribute_added": new_attribute.dict(),
                "current_status": self.current_status.dict()
            }
            
        except Exception as e:
            logger.error(f"Error adding status attribute: {e}")
            return {"error": str(e), "success": False}
    
    def get_status_summary(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get a summary of the user's current status for agent context.
        
        Args:
            user_id: User identifier
            
        Returns:
            Condensed status summary for agent use
        """
        try:
            if not self.current_status or self.current_status.user_id != user_id:
                return {
                    "user_id": user_id,
                    "status": "No current status available",
                    "recommendation": "Ask user about their current state"
                }
            
            status = self.current_status
            summary = {
                "user_id": user_id,
                "last_updated": status.timestamp.isoformat(),
                "mood": status.mood,
                "activity": status.activity,
                "stress_level": status.stress_level,
                "focus": status.focus,
                "active_attributes": []
            }
            
            # Add active attributes
            if status.attributes:
                summary["active_attributes"] = [
                    {"name": attr.name, "level": attr.level}
                    for attr in status.attributes if attr.active
                ]
            
            # Add health summary if available
            if status.health:
                summary["health"] = {
                    "heart_rate": status.health.heart_rate,
                    "steps": status.health.steps,
                    "sleep_quality": status.health.sleep_quality
                }
            
            # Add location if available
            if status.location:
                summary["location_available"] = True
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting status summary: {e}")
            return {"error": str(e)}

# Global instance
_status_tool = StatusMonitoringTool()

# Tool functions for registry
def get_current_status(user_id: str = "default") -> str:
    """Get the current status for a user."""
    result = _status_tool.get_current_status(user_id)
    return json.dumps(result, indent=2)

def update_user_status(user_id: str = "default", mood: str = None, 
                      activity: str = None, stress_level: int = None) -> str:
    """Update user status with mood, activity, and stress information."""
    status_data = {}
    if mood:
        status_data["mood"] = mood
    if activity:
        status_data["activity"] = activity
    if stress_level is not None:
        status_data["stress_level"] = stress_level
    
    result = _status_tool.update_status(user_id=user_id, **status_data)
    return json.dumps(result, indent=2)

def update_mood_status(user_id: str = "default", mood: str = None, 
                      stress_level: int = None) -> str:
    """Update mood and stress level."""
    result = _status_tool.update_mood(user_id, mood, stress_level)
    return json.dumps(result, indent=2)

def add_user_attribute(user_id: str = "default", attribute_name: str = None,
                      level: int = None, active: bool = True) -> str:
    """Add a status attribute like 'hungry', 'tired', 'busy'."""
    result = _status_tool.add_status_attribute(user_id, attribute_name, level, active)
    return json.dumps(result, indent=2)

def get_status_summary(user_id: str = "default") -> str:
    """Get a summary of user's current status for agent context."""
    result = _status_tool.get_status_summary(user_id)
    return json.dumps(result, indent=2)