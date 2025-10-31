"""
Proactive Monitoring Tool for CrewAI Agents

This tool enables agents to proactively check and update user context by
monitoring status changes, analyzing conversations, and maintaining up-to-date
user profiles and status information.

File: tools/proactive_monitoring_tool.py
"""

import sys
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from threading import Timer, Lock

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

# Import status and profile tools with proper error handling
try:
    from status_monitoring_tool import StatusMonitoringTool
except ImportError:
    StatusMonitoringTool = None

try:
    from profile_monitoring_tool import ProfileMonitoringTool  
except ImportError:
    ProfileMonitoringTool = None

try:
    from conversation_analyzer import ConversationAnalyzer
except ImportError:
    ConversationAnalyzer = None

class ProactiveMonitoringTool:
    """Tool for proactive monitoring and updating of user context."""
    
    def __init__(self):
        """Initialize the proactive monitoring tool."""
        try:
            self.memory_manager = memory_manager  # Use new qdrant architecture directly
            
            # Initialize sub-tools with fallback handling
            self.status_tool = StatusMonitoringTool() if StatusMonitoringTool else None
            self.profile_tool = ProfileMonitoringTool() if ProfileMonitoringTool else None
            self.conversation_analyzer = ConversationAnalyzer() if ConversationAnalyzer else None
            
            # Monitoring state
            self.last_check_time = datetime.utcnow()
            self.monitoring_enabled = True
            self.monitoring_interval = 300  # 5 minutes by default
            self.monitoring_timer = None
            self.monitoring_lock = Lock()
            
            logger.info("Successfully initialized ProactiveMonitoringTool")
        except Exception as e:
            logger.error(f"Failed to initialize ProactiveMonitoringTool: {e}")
            # Set fallback values
            self.memory_manager = None
            self.status_crud = None
            self.self_crud = None
            self.status_tool = StatusMonitoringTool()
            self.profile_tool = ProfileMonitoringTool()
            self.conversation_analyzer = ConversationAnalyzer()
            self.last_check_time = datetime.utcnow()
            self.monitoring_enabled = False
            self.monitoring_interval = 300
            self.monitoring_timer = None
            self.monitoring_lock = Lock()
    
    def start_proactive_monitoring(self, user_id: str = "default", 
                                  interval_seconds: int = 300) -> Dict[str, Any]:
        """
        Start proactive monitoring for a user.
        
        Args:
            user_id: User identifier
            interval_seconds: Monitoring interval in seconds
            
        Returns:
            Status of monitoring startup
        """
        try:
            with self.monitoring_lock:
                self.monitoring_enabled = True
                self.monitoring_interval = interval_seconds
                
                # Schedule the first check
                self._schedule_next_check(user_id)
                
                logger.info(f"Started proactive monitoring for user {user_id} with {interval_seconds}s interval")
                return {
                    "success": True,
                    "message": f"Proactive monitoring started for user {user_id}",
                    "interval_seconds": interval_seconds,
                    "next_check_at": (datetime.utcnow() + timedelta(seconds=interval_seconds)).isoformat()
                }
        except Exception as e:
            logger.error(f"Error starting proactive monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_proactive_monitoring(self) -> Dict[str, Any]:
        """
        Stop proactive monitoring.
        
        Returns:
            Status of monitoring shutdown
        """
        try:
            with self.monitoring_lock:
                self.monitoring_enabled = False
                
                if self.monitoring_timer:
                    self.monitoring_timer.cancel()
                    self.monitoring_timer = None
                
                logger.info("Stopped proactive monitoring")
                return {
                    "success": True,
                    "message": "Proactive monitoring stopped"
                }
        except Exception as e:
            logger.error(f"Error stopping proactive monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    def _schedule_next_check(self, user_id: str):
        """Schedule the next proactive check."""
        if not self.monitoring_enabled:
            return
            
        # Cancel existing timer
        if self.monitoring_timer:
            self.monitoring_timer.cancel()
        
        # Schedule next check
        self.monitoring_timer = Timer(
            self.monitoring_interval,
            self._perform_proactive_check,
            args=[user_id]
        )
        self.monitoring_timer.start()
    
    def _perform_proactive_check(self, user_id: str):
        """Perform a proactive check of user context."""
        try:
            logger.info(f"Performing proactive check for user {user_id}")
            
            # Check and update status context
            status_updates = self._check_status_context(user_id)
            
            # Check and update profile context
            profile_updates = self._check_profile_context(user_id)
            
            # Check for external data sources that need syncing
            sync_results = self._sync_external_sources(user_id)
            
            # Update last check time
            self.last_check_time = datetime.utcnow()
            
            # Schedule next check if monitoring is still enabled
            if self.monitoring_enabled:
                self._schedule_next_check(user_id)
            
            logger.info(f"Completed proactive check for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error during proactive check: {e}")
            # Continue monitoring even if there's an error
            if self.monitoring_enabled:
                self._schedule_next_check(user_id)
    
    def _check_status_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Check and update status context."""
        updates = []
        
        try:
            # Get current status
            current_status = self.status_tool.get_current_status(user_id)
            
            # Check if status is stale (older than 1 hour)
            if current_status.get("timestamp"):
                status_time = datetime.fromisoformat(current_status["timestamp"].replace('Z', '+00:00'))
                if datetime.utcnow() - status_time > timedelta(hours=1):
                    # Status is stale, trigger a context refresh
                    updates.append({
                        "type": "status_refresh_needed",
                        "message": "User status is stale and may need updating",
                        "last_update": current_status["timestamp"]
                    })
            
            # Check for calendar integration
            if self.status_crud:
                sync_result = self.status_crud.sync_with_calendar(user_id)
                if sync_result[0]:  # Success
                    updates.append({
                        "type": "calendar_sync",
                        "message": "Successfully synced calendar events",
                        "status": sync_result[1].model_dump() if sync_result[1] else None
                    })
            
            # Check for health data integration
            if self.status_crud:
                health_sync_result = self.status_crud.sync_with_health_system(user_id)
                if health_sync_result[0]:  # Success
                    updates.append({
                        "type": "health_sync",
                        "message": "Successfully synced health data",
                        "status": health_sync_result[1].model_dump() if health_sync_result[1] else None
                    })
                
        except Exception as e:
            logger.error(f"Error checking status context: {e}")
            updates.append({
                "type": "error",
                "message": f"Error checking status context: {str(e)}"
            })
        
        return updates
    
    def _check_profile_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Check and update profile context."""
        updates = []
        
        try:
            # Get current profile
            current_profile = self.profile_tool.get_profile(user_id)
            
            # Check if profile needs enrichment based on recent activities
            if current_profile.get("preferences_count", 0) < 5:
                updates.append({
                    "type": "profile_enrichment_needed",
                    "message": "User profile has few preferences, consider asking about preferences",
                    "current_preference_count": current_profile.get("preferences_count", 0)
                })
            
            # Check if goals need updating
            if current_profile.get("goals_count", 0) == 0:
                updates.append({
                    "type": "goals_needed",
                    "message": "User has no recorded goals, consider discussing goals and aspirations",
                    "current_goal_count": current_profile.get("goals_count", 0)
                })
                
        except Exception as e:
            logger.error(f"Error checking profile context: {e}")
            updates.append({
                "type": "error",
                "message": f"Error checking profile context: {str(e)}"
            })
        
        return updates
    
    def _sync_external_sources(self, user_id: str) -> List[Dict[str, Any]]:
        """Sync with external data sources."""
        sync_results = []
        
        try:
            # Example: Check for email updates, calendar changes, health data, etc.
            # This would be expanded based on available integrations
            
            sync_results.append({
                "type": "external_sync_placeholder",
                "message": "External sync functionality ready for implementation",
                "sources_available": ["calendar", "health", "email", "location"]
            })
                
        except Exception as e:
            logger.error(f"Error syncing external sources: {e}")
            sync_results.append({
                "type": "error",
                "message": f"Error syncing external sources: {str(e)}"
            })
        
        return sync_results
    
    def analyze_conversation_for_updates(self, conversation_text: str, 
                                       user_id: str = "default") -> Dict[str, Any]:
        """
        Analyze conversation text for status and profile updates.
        
        Args:
            conversation_text: Text of the conversation to analyze
            user_id: User identifier
            
        Returns:
            Analysis results and any updates applied
        """
        try:
            # Analyze conversation for status updates
            status_updates = self.conversation_analyzer.analyze_status_updates(conversation_text)
            
            # Analyze conversation for profile updates  
            profile_updates = self.conversation_analyzer.analyze_profile_updates(conversation_text)
            
            applied_updates = []
            
            # Apply status updates
            for update in status_updates:
                if update.confidence > 0.7:  # Only apply high-confidence updates
                    try:
                        if update.type == "mood":
                            result = self.status_tool.update_mood(user_id, mood=update.value)
                        elif update.type == "activity":
                            result = self.status_tool.update_activity(user_id, activity=update.value)
                        elif update.type == "stress_level":
                            result = self.status_tool.update_mood(user_id, stress_level=update.value)
                        elif update.type == "attribute":
                            result = self.status_tool.add_status_attribute(
                                user_id, name=update.value, active=True
                            )
                        else:
                            continue  # Skip unknown update types
                        
                        if result.get("success"):
                            applied_updates.append({
                                "type": "status",
                                "update_type": update.type,
                                "value": update.value,
                                "confidence": update.confidence,
                                "source_text": update.source_text[:100] + "..." if len(update.source_text) > 100 else update.source_text
                            })
                    except Exception as e:
                        logger.error(f"Error applying status update: {e}")
            
            # Apply profile updates
            for update in profile_updates:
                if update.confidence > 0.7:  # Only apply high-confidence updates
                    try:
                        if update.type == "preference":
                            result = self.profile_tool.add_preference(
                                user_id, category=update.category, value=update.value
                            )
                        elif update.type == "goal":
                            metadata = update.metadata or {}
                            result = self.profile_tool.add_goal(
                                user_id, 
                                title=metadata.get("title", str(update.value)),
                                description=str(update.value),
                                category=update.category or "personal"
                            )
                        elif update.type == "important_person":
                            metadata = update.metadata or {}
                            result = self.profile_tool.add_important_person(
                                user_id,
                                name=str(update.value),
                                relationship=update.category or "unknown",
                                significance=metadata.get("significance")
                            )
                        else:
                            continue  # Skip unknown update types
                        
                        if result.get("success"):
                            applied_updates.append({
                                "type": "profile",
                                "update_type": update.type,
                                "category": update.category,
                                "value": update.value,
                                "confidence": update.confidence,
                                "source_text": update.source_text[:100] + "..." if len(update.source_text) > 100 else update.source_text
                            })
                    except Exception as e:
                        logger.error(f"Error applying profile update: {e}")
            
            return {
                "success": True,
                "status_updates_detected": len(status_updates),
                "profile_updates_detected": len(profile_updates),
                "updates_applied": len(applied_updates),
                "applied_updates": applied_updates,
                "analysis_summary": {
                    "high_confidence_status_updates": len([u for u in status_updates if u.confidence > 0.7]),
                    "high_confidence_profile_updates": len([u for u in profile_updates if u.confidence > 0.7])
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation for updates: {e}")
            return {"success": False, "error": str(e)}
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get the current monitoring status.
        
        Returns:
            Current monitoring status and configuration
        """
        try:
            return {
                "monitoring_enabled": self.monitoring_enabled,
                "monitoring_interval_seconds": self.monitoring_interval,
                "last_check_time": self.last_check_time.isoformat(),
                "next_check_in_seconds": self.monitoring_interval if self.monitoring_enabled else None,
                "has_persistent_storage": self.memory_manager is not None,
                "tools_available": {
                    "status_monitoring": True,
                    "profile_monitoring": True,
                    "conversation_analysis": True
                }
            }
        except Exception as e:
            logger.error(f"Error getting monitoring status: {e}")
            return {"error": str(e)}
    
    def force_context_refresh(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Force an immediate context refresh for the user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Results of the forced refresh
        """
        try:
            logger.info(f"Forcing context refresh for user {user_id}")
            
            # Perform immediate checks
            status_updates = self._check_status_context(user_id)
            profile_updates = self._check_profile_context(user_id)
            sync_results = self._sync_external_sources(user_id)
            
            self.last_check_time = datetime.utcnow()
            
            return {
                "success": True,
                "refresh_time": self.last_check_time.isoformat(),
                "status_updates": status_updates,
                "profile_updates": profile_updates,
                "sync_results": sync_results
            }
            
        except Exception as e:
            logger.error(f"Error forcing context refresh: {e}")
            return {"success": False, "error": str(e)}


# Global instance
_proactive_tool = ProactiveMonitoringTool()

# Tool functions for registry
def start_proactive_monitoring(user_id: str = "default", 
                              interval_seconds: int = 300) -> str:
    """Start proactive monitoring for a user."""
    result = _proactive_tool.start_proactive_monitoring(user_id, interval_seconds)
    return json.dumps(result, indent=2)

def stop_proactive_monitoring() -> str:
    """Stop proactive monitoring."""
    result = _proactive_tool.stop_proactive_monitoring()
    return json.dumps(result, indent=2)

def analyze_conversation_for_updates(conversation_text: str, 
                                   user_id: str = "default") -> str:
    """Analyze conversation text for status and profile updates."""
    result = _proactive_tool.analyze_conversation_for_updates(conversation_text, user_id)
    return json.dumps(result, indent=2)

def get_monitoring_status() -> str:
    """Get the current monitoring status."""
    result = _proactive_tool.get_monitoring_status()
    return json.dumps(result, indent=2)

def force_context_refresh(user_id: str = "default") -> str:
    """Force an immediate context refresh for the user."""
    result = _proactive_tool.force_context_refresh(user_id)
    return json.dumps(result, indent=2)