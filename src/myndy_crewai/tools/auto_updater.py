"""
Automatic Update System for Status and Profile

This module automatically applies conversation analysis results to update
user status and profile information in real-time.

File: tools/auto_updater.py
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add paths
CREWAI_PATH = Path("/Users/jeremy/crewAI")
MYNDY_PATH = Path("/Users/jeremy/myndy")
sys.path.insert(0, str(CREWAI_PATH))
sys.path.insert(0, str(MYNDY_PATH))

from conversation_analyzer import ConversationAnalyzer, StatusUpdate, ProfileUpdate
from status_monitoring_tool import _status_tool
from profile_monitoring_tool import _profile_tool

logger = logging.getLogger(__name__)

class AutoUpdater:
    """Automatically applies conversation analysis results to user status/profile."""
    
    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize the auto updater.
        
        Args:
            min_confidence: Minimum confidence threshold for applying updates
        """
        self.min_confidence = min_confidence
        self.conversation_analyzer = ConversationAnalyzer()
        self.update_history: List[Dict[str, Any]] = []
    
    def process_message(self, message: str, user_id: str = "default", 
                       auto_apply: bool = True) -> Dict[str, Any]:
        """
        Process a conversation message and optionally apply updates automatically.
        
        Args:
            message: The conversation message to analyze
            user_id: User identifier
            auto_apply: Whether to automatically apply detected updates
            
        Returns:
            Dictionary with analysis results and update outcomes
        """
        try:
            # Analyze the message
            status_updates, profile_updates = self.conversation_analyzer.analyze_conversation(
                message, user_id
            )
            
            results = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "user_id": user_id,
                "analysis": {
                    "status_updates_detected": len(status_updates),
                    "profile_updates_detected": len(profile_updates)
                },
                "applied_updates": {
                    "status": [],
                    "profile": []
                },
                "skipped_updates": {
                    "status": [],
                    "profile": []
                }
            }
            
            if auto_apply:
                # Apply status updates
                for update in status_updates:
                    if update.confidence >= self.min_confidence:
                        try:
                            outcome = self._apply_status_update(update, user_id)
                            results["applied_updates"]["status"].append({
                                "type": update.type,
                                "value": update.value,
                                "confidence": update.confidence,
                                "outcome": outcome
                            })
                        except Exception as e:
                            logger.error(f"Failed to apply status update: {e}")
                            results["skipped_updates"]["status"].append({
                                "type": update.type,
                                "value": update.value,
                                "confidence": update.confidence,
                                "reason": str(e)
                            })
                    else:
                        results["skipped_updates"]["status"].append({
                            "type": update.type,
                            "value": update.value,
                            "confidence": update.confidence,
                            "reason": "Low confidence"
                        })
                
                # Apply profile updates
                for update in profile_updates:
                    if update.confidence >= self.min_confidence:
                        try:
                            outcome = self._apply_profile_update(update, user_id)
                            results["applied_updates"]["profile"].append({
                                "type": update.type,
                                "category": update.category,
                                "value": update.value,
                                "confidence": update.confidence,
                                "outcome": outcome
                            })
                        except Exception as e:
                            logger.error(f"Failed to apply profile update: {e}")
                            results["skipped_updates"]["profile"].append({
                                "type": update.type,
                                "category": update.category,
                                "value": update.value,
                                "confidence": update.confidence,
                                "reason": str(e)
                            })
                    else:
                        results["skipped_updates"]["profile"].append({
                            "type": update.type,
                            "category": update.category,
                            "value": update.value,
                            "confidence": update.confidence,
                            "reason": "Low confidence"
                        })
            
            # Store in history
            self.update_history.append(results)
            
            # Keep only last 100 entries
            if len(self.update_history) > 100:
                self.update_history = self.update_history[-100:]
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "user_id": user_id,
                "error": str(e)
            }
    
    def _apply_status_update(self, update: StatusUpdate, user_id: str) -> Dict[str, Any]:
        """Apply a status update to the user's status."""
        if update.type == "mood":
            result = _status_tool.update_mood(user_id=user_id, mood=update.value)
            return {"action": "update_mood", "result": "success", "mood": update.value}
        
        elif update.type == "activity":
            result = _status_tool.update_activity(user_id=user_id, activity=update.value)
            return {"action": "update_activity", "result": "success", "activity": update.value}
        
        elif update.type == "stress_level":
            result = _status_tool.update_mood(user_id=user_id, stress_level=update.value)
            return {"action": "update_stress", "result": "success", "stress_level": update.value}
        
        elif update.type == "attribute":
            attr_data = update.value
            result = _status_tool.add_status_attribute(
                user_id=user_id,
                name=attr_data["name"],
                level=attr_data["level"],
                active=attr_data["active"]
            )
            return {"action": "add_attribute", "result": "success", "attribute": attr_data["name"]}
        
        else:
            raise ValueError(f"Unknown status update type: {update.type}")
    
    def _apply_profile_update(self, update: ProfileUpdate, user_id: str) -> Dict[str, Any]:
        """Apply a profile update to the user's profile."""
        if update.type == "preference":
            result = _profile_tool.add_preference(
                user_id=user_id,
                category=update.category,
                value=update.value,
                strength=0.8  # Default strength for detected preferences
            )
            return {"action": "add_preference", "result": "success", 
                   "category": update.category, "value": update.value}
        
        elif update.type == "goal":
            goal_data = update.value
            result = _profile_tool.add_goal(
                user_id=user_id,
                title=goal_data["title"],
                description=goal_data["description"],
                category=goal_data["category"]
            )
            return {"action": "add_goal", "result": "success", "title": goal_data["title"]}
        
        elif update.type == "value":
            # Get current values and add new one
            current_profile = _profile_tool.get_or_create_profile(user_id)
            current_values = current_profile.values or []
            if update.value not in current_values:
                new_values = current_values + [update.value]
                result = _profile_tool.update_values(user_id=user_id, values=new_values)
                return {"action": "add_value", "result": "success", "value": update.value}
            else:
                return {"action": "add_value", "result": "already_exists", "value": update.value}
        
        elif update.type == "important_person":
            person_data = update.value
            result = _profile_tool.add_important_person(
                user_id=user_id,
                name=person_data["name"],
                relationship=person_data["relationship"],
                significance=person_data["significance"]
            )
            return {"action": "add_person", "result": "success", 
                   "name": person_data["name"], "relationship": person_data["relationship"]}
        
        else:
            raise ValueError(f"Unknown profile update type: {update.type}")
    
    def get_update_summary(self, user_id: str = "default") -> Dict[str, Any]:
        """Get a summary of recent updates for a user."""
        user_updates = [update for update in self.update_history if update.get("user_id") == user_id]
        
        if not user_updates:
            return {
                "user_id": user_id,
                "total_messages_processed": 0,
                "total_updates_applied": 0,
                "summary": "No conversation analysis history found"
            }
        
        total_status_applied = sum(len(update.get("applied_updates", {}).get("status", [])) 
                                 for update in user_updates)
        total_profile_applied = sum(len(update.get("applied_updates", {}).get("profile", [])) 
                                  for update in user_updates)
        
        recent_activity = user_updates[-5:] if len(user_updates) >= 5 else user_updates
        
        return {
            "user_id": user_id,
            "total_messages_processed": len(user_updates),
            "total_updates_applied": total_status_applied + total_profile_applied,
            "status_updates_applied": total_status_applied,
            "profile_updates_applied": total_profile_applied,
            "recent_activity": [
                {
                    "timestamp": update["timestamp"],
                    "message_snippet": update["message"][:50] + "..." if len(update["message"]) > 50 else update["message"],
                    "updates_applied": len(update.get("applied_updates", {}).get("status", [])) + 
                                     len(update.get("applied_updates", {}).get("profile", []))
                }
                for update in recent_activity
            ],
            "last_update": user_updates[-1]["timestamp"] if user_updates else None
        }
    
    def test_with_sample_messages(self) -> Dict[str, Any]:
        """Test the auto updater with sample conversation messages."""
        sample_messages = [
            "I'm feeling really happy today! Just got a promotion at work 😊",
            "I love pizza and sushi, they're my favorite foods",
            "I'm so tired and stressed out from all this work",
            "My goal is to learn Spanish this year and travel to Spain",
            "I believe in honesty and treating people with respect",
            "I was talking to my wife Sarah earlier about our vacation plans",
            "I'm at the gym working out, feeling energetic and motivated 💪",
            "I prefer rock music and jazz, especially when I'm coding"
        ]
        
        results = {
            "test_timestamp": datetime.utcnow().isoformat(),
            "messages_tested": len(sample_messages),
            "results": []
        }
        
        for i, message in enumerate(sample_messages):
            print(f"Testing message {i+1}: {message}")
            result = self.process_message(message, user_id="test_user", auto_apply=True)
            results["results"].append(result)
            
            # Print summary for each message
            status_applied = len(result.get("applied_updates", {}).get("status", []))
            profile_applied = len(result.get("applied_updates", {}).get("profile", []))
            print(f"  → Applied {status_applied} status updates, {profile_applied} profile updates")
        
        return results


# Global auto updater instance
_auto_updater = AutoUpdater()

def process_conversation_message(message: str, user_id: str = "default", 
                               auto_apply: bool = True) -> str:
    """
    Process a conversation message for automatic status/profile updates.
    
    Args:
        message: The conversation message
        user_id: User identifier
        auto_apply: Whether to automatically apply detected updates
        
    Returns:
        JSON string with processing results
    """
    result = _auto_updater.process_message(message, user_id, auto_apply)
    return json.dumps(result, indent=2)

def get_conversation_update_summary(user_id: str = "default") -> str:
    """
    Get a summary of conversation-driven updates for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        JSON string with update summary
    """
    result = _auto_updater.get_update_summary(user_id)
    return json.dumps(result, indent=2)

def test_conversation_updates() -> str:
    """
    Test the conversation update system with sample messages.
    
    Returns:
        JSON string with test results
    """
    result = _auto_updater.test_with_sample_messages()
    return json.dumps(result, indent=2)