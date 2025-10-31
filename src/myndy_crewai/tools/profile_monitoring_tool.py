"""
Profile Monitoring Tool for CrewAI Agents

This tool enables agents to monitor and update the user's self-profile including
preferences, goals, values, personality traits, and important relationships.

File: tools/profile_monitoring_tool.py
"""

import sys
import json
import logging
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
        from memory.self_profile_model import SelfProfile, Preference, Goal, Affiliation, ImportantPerson
        logger.debug("Successfully imported myndy memory profile components")
    except ImportError as e:
        logger.warning(f"Could not import myndy memory profile components: {e}")
        SelfProfile = None
        Preference = None
        Goal = None
        Affiliation = None
        ImportantPerson = None
    
    # Try to import qdrant components separately (these may fail)
    try:
        from qdrant.collections.memory import memory_manager
        logger.debug("Successfully imported qdrant memory manager")
    except ImportError as e:
        logger.warning(f"Could not import qdrant memory manager: {e}")
        memory_manager = None
else:
    logger.warning(f"Myndy-AI path not found: {env_config.myndy_path}")
    SelfProfile = None
    Preference = None
    Goal = None
    Affiliation = None
    ImportantPerson = None
    memory_manager = None

class ProfileMonitoringTool:
    """Tool for monitoring and updating user profile information."""
    
    def __init__(self):
        """Initialize the profile monitoring tool."""
        try:
            if memory_manager and SelfProfile:
                self.memory_manager = memory_manager  # Use new qdrant architecture directly
                logger.info("Successfully initialized ProfileMonitoringTool with qdrant memory manager")
            else:
                logger.warning("Memory components not available, using fallback storage")
                self.memory_manager = None
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            self.memory_manager = None
        
        # Always initialize fallback storage
        self.user_profiles: Dict[str, SelfProfile] = {}
        self.self_crud = None  # Will be set if memory_manager is available
        
    def get_or_create_profile(self, user_id: str = "default", name: str = None):
        """Get existing profile or create a new one."""
        if not SelfProfile:
            # Return a basic dict if SelfProfile is not available
            profile_name = name or f"User_{user_id}"
            return {
                "id": user_id,
                "name": profile_name,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "preferences": [],
                "goals": [],
                "important_people": [],
                "values": [],
                "personality_traits": {}
            }
        
        if self.self_crud:
            # Use persistent storage with new architecture
            profile = self.self_crud.get_self_profile()  # Gets first profile by default
            if not profile:
                # Create new profile
                profile_name = name or f"User_{user_id}"
                profile_data = {
                    "id": user_id,
                    "name": profile_name,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                success, profile = self.self_crud.create_self_profile(profile_data)
                if not success or not profile:
                    # Fallback to in-memory if creation fails
                    profile = SelfProfile(**profile_data)
            return profile
        else:
            # Fallback to in-memory storage
            if user_id not in self.user_profiles:
                profile_name = name or f"User_{user_id}"
                self.user_profiles[user_id] = SelfProfile(
                    id=user_id,
                    name=profile_name,
                    created_at=datetime.utcnow().isoformat(),
                    updated_at=datetime.utcnow().isoformat()
                )
            return self.user_profiles[user_id]
    
    def get_profile(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get the user's profile information.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile information as a dictionary
        """
        try:
            profile = self.get_or_create_profile(user_id)
            return profile.dict()
        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return {"error": str(e)}
    
    def update_basic_info(self, user_id: str = "default", name: str = None,
                         birthdate: str = None, pronouns: List[str] = None,
                         biography: str = None) -> Dict[str, Any]:
        """
        Update basic profile information.
        
        Args:
            user_id: User identifier
            name: User's name
            birthdate: Birthdate in ISO format
            pronouns: List of pronouns
            biography: Biographical information
            
        Returns:
            Updated profile information
        """
        try:
            profile = self.get_or_create_profile(user_id, name)
            
            if name:
                profile.name = name
            if birthdate:
                profile.birthdate = birthdate
            if pronouns:
                profile.pronouns = pronouns
            if biography:
                profile.biography = biography
            
            profile.updated_at = datetime.utcnow().isoformat()
            
            return {
                "success": True,
                "updated_at": profile.updated_at,
                "basic_info": {
                    "name": profile.name,
                    "birthdate": profile.birthdate,
                    "pronouns": profile.pronouns,
                    "biography": profile.biography
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating basic info: {e}")
            return {"error": str(e), "success": False}
    
    def add_preference(self, user_id: str = "default", category: str = None,
                      value: str = None, strength: float = 0.8,
                      notes: str = None) -> Dict[str, Any]:
        """
        Add a user preference.
        
        Args:
            user_id: User identifier
            category: Preference category (food, music, color, etc.)
            value: Preference value
            strength: Preference strength (0.0-1.0)
            notes: Additional notes
            
        Returns:
            Updated preferences information
        """
        if not category or not value:
            return {"error": "Category and value are required", "success": False}
        
        try:
            if self.self_crud:
                # Use persistent storage with new architecture
                success, updated_profile = self.self_crud.add_preference(
                    profile_id=None,  # Will use first profile
                    category=category,
                    value=value,
                    strength=strength,
                    notes=notes
                )
                
                if success and updated_profile:
                    return {
                        "success": True,
                        "preference_added": {
                            "category": category,
                            "value": value,
                            "strength": strength
                        },
                        "total_preferences": len(updated_profile.preferences) if updated_profile.preferences else 0
                    }
                else:
                    return {"error": "Failed to add preference to persistent storage", "success": False}
            else:
                # Fallback to in-memory storage
                profile = self.get_or_create_profile(user_id)
                profile.add_preference(category, value, strength, notes)
                
                return {
                    "success": True,
                    "preference_added": {
                        "category": category,
                        "value": value,
                        "strength": strength
                    },
                    "total_preferences": len(profile.preferences) if profile.preferences else 0
                }
            
        except Exception as e:
            logger.error(f"Error adding preference: {e}")
            return {"error": str(e), "success": False}
    
    def add_goal(self, user_id: str = "default", title: str = None,
                description: str = None, category: str = None,
                target_date: str = None, priority: int = 5) -> Dict[str, Any]:
        """
        Add a user goal.
        
        Args:
            user_id: User identifier
            title: Goal title
            description: Goal description
            category: Goal category (personal, professional, health, etc.)
            target_date: Target completion date (ISO format)
            priority: Priority level (1-10)
            
        Returns:
            Updated goals information
        """
        if not title or not description or not category:
            return {"error": "Title, description, and category are required", "success": False}
        
        try:
            profile = self.get_or_create_profile(user_id)
            profile.add_goal(title, description, category, target_date, priority)
            
            return {
                "success": True,
                "goal_added": {
                    "title": title,
                    "category": category,
                    "priority": priority
                },
                "total_goals": len(profile.goals)
            }
            
        except Exception as e:
            logger.error(f"Error adding goal: {e}")
            return {"error": str(e), "success": False}
    
    def add_important_person(self, user_id: str = "default", name: str = None,
                           relationship: str = None, significance: str = None) -> Dict[str, Any]:
        """
        Add an important person to the profile.
        
        Args:
            user_id: User identifier
            name: Person's name
            relationship: Relationship type (partner, family, friend, etc.)
            significance: Why this person is important
            
        Returns:
            Updated important people information
        """
        if not name or not relationship:
            return {"error": "Name and relationship are required", "success": False}
        
        try:
            profile = self.get_or_create_profile(user_id)
            profile.add_important_person(name, relationship, significance=significance)
            
            return {
                "success": True,
                "person_added": {
                    "name": name,
                    "relationship": relationship,
                    "significance": significance
                },
                "total_important_people": len(profile.important_people)
            }
            
        except Exception as e:
            logger.error(f"Error adding important person: {e}")
            return {"error": str(e), "success": False}
    
    def update_values(self, user_id: str = "default", values: List[str] = None) -> Dict[str, Any]:
        """
        Update user's core values.
        
        Args:
            user_id: User identifier
            values: List of core values
            
        Returns:
            Updated values information
        """
        if not values:
            return {"error": "Values list is required", "success": False}
        
        try:
            profile = self.get_or_create_profile(user_id)
            profile.values = values
            profile.updated_at = datetime.utcnow().isoformat()
            
            return {
                "success": True,
                "values_updated": values,
                "total_values": len(values)
            }
            
        except Exception as e:
            logger.error(f"Error updating values: {e}")
            return {"error": str(e), "success": False}
    
    def update_personality_traits(self, user_id: str = "default", 
                                 traits: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Update personality traits with strength values.
        
        Args:
            user_id: User identifier
            traits: Dictionary of trait names to strength values (0.0-1.0)
            
        Returns:
            Updated personality traits information
        """
        if not traits:
            return {"error": "Traits dictionary is required", "success": False}
        
        try:
            profile = self.get_or_create_profile(user_id)
            
            if not profile.personality_traits:
                profile.personality_traits = {}
            
            # Update traits
            profile.personality_traits.update(traits)
            profile.updated_at = datetime.utcnow().isoformat()
            
            return {
                "success": True,
                "traits_updated": traits,
                "total_traits": len(profile.personality_traits)
            }
            
        except Exception as e:
            logger.error(f"Error updating personality traits: {e}")
            return {"error": str(e), "success": False}
    
    def get_profile_summary(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get a summary of the user's profile for agent context.
        
        Args:
            user_id: User identifier
            
        Returns:
            Condensed profile summary for agent use
        """
        try:
            if user_id not in self.user_profiles:
                return {
                    "user_id": user_id,
                    "status": "No profile available",
                    "recommendation": "Ask user about their preferences and goals"
                }
            
            profile = self.user_profiles[user_id]
            
            summary = {
                "user_id": user_id,
                "name": profile.name,
                "last_updated": profile.updated_at,
                "values": profile.values[:5] if profile.values else [],  # Top 5 values
                "preferences_count": len(profile.preferences) if profile.preferences else 0,
                "goals_count": len(profile.goals) if profile.goals else 0,
                "important_people_count": len(profile.important_people) if profile.important_people else 0,
            }
            
            # Add recent preferences by category
            if profile.preferences:
                prefs_by_category = {}
                for pref in profile.preferences[-10:]:  # Last 10 preferences
                    if pref.category not in prefs_by_category:
                        prefs_by_category[pref.category] = []
                    prefs_by_category[pref.category].append(pref.value)
                summary["recent_preferences"] = prefs_by_category
            
            # Add active goals
            if profile.goals:
                active_goals = [
                    {"title": goal.title, "category": goal.category, "priority": goal.priority}
                    for goal in profile.goals if goal.status == "active"
                ]
                summary["active_goals"] = active_goals[:5]  # Top 5 active goals
            
            # Add top personality traits
            if profile.personality_traits:
                top_traits = sorted(
                    profile.personality_traits.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                summary["top_personality_traits"] = dict(top_traits)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting profile summary: {e}")
            return {"error": str(e)}

# Global instance
_profile_tool = ProfileMonitoringTool()

# Tool functions for registry
def get_user_profile(user_id: str = "default") -> str:
    """Get the complete user profile."""
    result = _profile_tool.get_profile(user_id)
    return json.dumps(result, indent=2)

def update_user_basic_info(user_id: str = "default", name: str = None,
                          birthdate: str = None, biography: str = None) -> str:
    """Update basic user information like name, birthdate, and biography."""
    pronouns = None  # Could be extracted from conversation
    result = _profile_tool.update_basic_info(user_id, name, birthdate, pronouns, biography)
    return json.dumps(result, indent=2)

def add_user_preference(user_id: str = "default", category: str = None,
                       value: str = None, strength: float = 0.8) -> str:
    """Add a user preference in a specific category."""
    result = _profile_tool.add_preference(user_id, category, value, strength)
    return json.dumps(result, indent=2)

def add_user_goal(user_id: str = "default", title: str = None,
                 description: str = None, category: str = None,
                 priority: int = 5) -> str:
    """Add a user goal with title, description, and category."""
    result = _profile_tool.add_goal(user_id, title, description, category, None, priority)
    return json.dumps(result, indent=2)

def add_important_person(user_id: str = "default", name: str = None,
                        relationship: str = None, significance: str = None) -> str:
    """Add an important person to the user's profile."""
    result = _profile_tool.add_important_person(user_id, name, relationship, significance)
    return json.dumps(result, indent=2)

def update_user_values(user_id: str = "default", values_list: str = None) -> str:
    """Update user's core values (provide as comma-separated string)."""
    if values_list:
        values = [v.strip() for v in values_list.split(",")]
        result = _profile_tool.update_values(user_id, values)
    else:
        result = {"error": "Values list is required", "success": False}
    return json.dumps(result, indent=2)

def get_profile_summary(user_id: str = "default") -> str:
    """Get a summary of user's profile for agent context."""
    result = _profile_tool.get_profile_summary(user_id)
    return json.dumps(result, indent=2)