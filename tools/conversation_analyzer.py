"""
Conversation Analyzer for Automatic Status/Profile Updates

This module analyzes conversation content to extract user status and profile
information, enabling automatic updates to the user's status and profile.

File: tools/conversation_analyzer.py
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StatusUpdate:
    """Represents a detected status update from conversation."""
    type: str  # mood, activity, stress_level, attribute
    value: Any
    confidence: float
    source_text: str

@dataclass
class ProfileUpdate:
    """Represents a detected profile update from conversation."""
    type: str  # preference, goal, value, important_person, basic_info
    category: Optional[str] = None
    value: Any = None
    metadata: Dict[str, Any] = None
    confidence: float = 0.0
    source_text: str = ""

class ConversationAnalyzer:
    """Analyzes conversations to extract status and profile updates."""
    
    def __init__(self):
        """Initialize the conversation analyzer."""
        self.mood_patterns = {
            'happy': [
                r'\b(happy|excited|joyful|thrilled|elated|cheerful|glad|pleased)\b',
                r'\b(feeling great|in a good mood|on cloud nine)\b',
                r'😊|😄|😃|🎉|✨'
            ],
            'sad': [
                r'\b(sad|depressed|down|upset|disappointed|blue|melancholy)\b',
                r'\b(feeling down|having a rough time|not doing well)\b',
                r'😢|😭|💔|😞'
            ],
            'anxious': [
                r'\b(anxious|worried|nervous|stressed|overwhelmed|concerned)\b',
                r'\b(feeling anxious|stressed out|freaking out)\b',
                r'😰|😟|😕'
            ],
            'angry': [
                r'\b(angry|mad|furious|irritated|annoyed|frustrated)\b',
                r'\b(pissed off|fed up|losing it)\b',
                r'😠|😡|🤬'
            ],
            'tired': [
                r'\b(tired|exhausted|drained|fatigued|sleepy|worn out)\b',
                r'\b(need sleep|so tired|running on empty)\b',
                r'😴|🥱'
            ],
            'energetic': [
                r'\b(energetic|pumped|motivated|ready|hyped|charged)\b',
                r'\b(full of energy|feeling great|ready to go)\b',
                r'💪|⚡|🔥'
            ]
        }
        
        self.activity_patterns = {
            'working': [
                r'\b(working|at work|in the office|coding|programming|meeting)\b',
                r'\b(at my desk|in a meeting|on a call)\b'
            ],
            'exercising': [
                r'\b(exercising|working out|at the gym|running|jogging|yoga)\b',
                r'\b(just finished workout|going to gym|hit the gym)\b'
            ],
            'eating': [
                r'\b(eating|having lunch|dinner|breakfast|meal|cooking)\b',
                r'\b(just ate|grabbing food|making dinner)\b'
            ],
            'traveling': [
                r'\b(traveling|on a trip|vacation|flight|airport|hotel)\b',
                r'\b(heading to|flying to|visiting)\b'
            ],
            'studying': [
                r'\b(studying|reading|learning|class|school|homework)\b',
                r'\b(hitting the books|cramming|exam prep)\b'
            ],
            'relaxing': [
                r'\b(relaxing|chilling|resting|lounging|taking it easy)\b',
                r'\b(watching tv|reading a book|just hanging out)\b'
            ]
        }
        
        self.stress_indicators = {
            'high': [
                r'\b(overwhelmed|swamped|crazy busy|losing it|breaking down)\b',
                r'\b(too much|can\'t handle|stressed out)\b'
            ],
            'medium': [
                r'\b(busy|hectic|lots going on|bit stressed|under pressure)\b',
                r'\b(managing|handling it|getting by)\b'
            ],
            'low': [
                r'\b(calm|peaceful|relaxed|chill|no stress|easy day)\b',
                r'\b(taking it easy|not much happening|quiet day)\b'
            ]
        }
        
        self.attribute_patterns = {
            'hungry': [r'\b(hungry|starving|need food|famished)\b'],
            'tired': [r'\b(tired|sleepy|exhausted|need sleep)\b'],
            'busy': [r'\b(busy|swamped|packed schedule|no time)\b'],
            'sick': [r'\b(sick|ill|not feeling well|under the weather)\b'],
            'focused': [r'\b(focused|concentrated|in the zone|productive)\b'],
            'distracted': [r'\b(distracted|can\'t focus|all over the place)\b']
        }
        
        self.preference_patterns = {
            'food': [
                r'\b(love|like|enjoy|favorite|prefer).{0,20}\b(pizza|sushi|coffee|tea|chocolate|ice cream|pasta)\b',
                r'\b(pizza|sushi|coffee|tea|chocolate|ice cream|pasta).{0,20}\b(is|are).{0,10}\b(great|amazing|delicious|my favorite)\b'
            ],
            'music': [
                r'\b(love|like|enjoy|favorite|prefer).{0,20}\b(rock|pop|jazz|classical|hip hop|country|electronic)\b',
                r'\b(listening to|playing|jamming to).{0,20}\b(rock|pop|jazz|classical|hip hop|country|electronic)\b'
            ],
            'activities': [
                r'\b(love|like|enjoy|favorite|prefer).{0,20}\b(reading|hiking|cooking|gaming|traveling|photography)\b',
                r'\b(into|really enjoy|passionate about).{0,20}\b(reading|hiking|cooking|gaming|traveling|photography)\b'
            ]
        }
        
        self.goal_patterns = [
            r'\b(want to|planning to|goal is to|hoping to|trying to|working toward)\s+(.+?)(?:\.|!|\?|$)',
            r'\b(my goal|my plan|i want|i hope|i\'m trying)\s+(.+?)(?:\.|!|\?|$)',
            r'\b(working on|focusing on|aiming for)\s+(.+?)(?:\.|!|\?|$)'
        ]
        
        self.value_patterns = [
            r'\b(i believe|i value|important to me|care about|stands for)\s+(.+?)(?:\.|!|\?|$)',
            r'\b(my values|what matters|i prioritize)\s+(.+?)(?:\.|!|\?|$)'
        ]
        
        self.important_person_patterns = [
            r'\b(my (wife|husband|partner|boyfriend|girlfriend|mom|dad|mother|father|brother|sister|friend|boss|colleague))\s+(\w+)',
            r'\b(\w+)\s+is my (wife|husband|partner|boyfriend|girlfriend|mom|dad|mother|father|brother|sister|friend|boss|colleague)',
            r'\b(met|talked to|saw|with)\s+my (wife|husband|partner|boyfriend|girlfriend|mom|dad|mother|father|brother|sister|friend|boss|colleague)\s+(\w+)'
        ]

    def analyze_conversation(self, message: str, user_id: str = "default") -> Tuple[List[StatusUpdate], List[ProfileUpdate]]:
        """
        Analyze a conversation message for status and profile updates.
        
        Args:
            message: The conversation message to analyze
            user_id: User identifier
            
        Returns:
            Tuple of (status_updates, profile_updates)
        """
        message_lower = message.lower()
        status_updates = []
        profile_updates = []
        
        # Analyze mood
        mood_update = self._detect_mood(message_lower, message)
        if mood_update:
            status_updates.append(mood_update)
        
        # Analyze activity
        activity_update = self._detect_activity(message_lower, message)
        if activity_update:
            status_updates.append(activity_update)
        
        # Analyze stress level
        stress_update = self._detect_stress_level(message_lower, message)
        if stress_update:
            status_updates.append(stress_update)
        
        # Analyze status attributes
        attribute_updates = self._detect_attributes(message_lower, message)
        status_updates.extend(attribute_updates)
        
        # Analyze preferences
        preference_updates = self._detect_preferences(message_lower, message)
        profile_updates.extend(preference_updates)
        
        # Analyze goals
        goal_updates = self._detect_goals(message, message)
        profile_updates.extend(goal_updates)
        
        # Analyze values
        value_updates = self._detect_values(message, message)
        profile_updates.extend(value_updates)
        
        # Analyze important people
        person_updates = self._detect_important_people(message, message)
        profile_updates.extend(person_updates)
        
        return status_updates, profile_updates
    
    def _detect_mood(self, message_lower: str, original_message: str) -> Optional[StatusUpdate]:
        """Detect mood from message."""
        for mood, patterns in self.mood_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    confidence = 0.8 if any(emoji in original_message for emoji in ['😊', '😢', '😠', '😰']) else 0.6
                    return StatusUpdate(
                        type="mood",
                        value=mood,
                        confidence=confidence,
                        source_text=original_message
                    )
        return None
    
    def _detect_activity(self, message_lower: str, original_message: str) -> Optional[StatusUpdate]:
        """Detect current activity from message."""
        for activity, patterns in self.activity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return StatusUpdate(
                        type="activity",
                        value=activity,
                        confidence=0.7,
                        source_text=original_message
                    )
        return None
    
    def _detect_stress_level(self, message_lower: str, original_message: str) -> Optional[StatusUpdate]:
        """Detect stress level from message."""
        stress_mapping = {'low': 2, 'medium': 5, 'high': 8}
        
        for level, patterns in self.stress_indicators.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return StatusUpdate(
                        type="stress_level",
                        value=stress_mapping[level],
                        confidence=0.6,
                        source_text=original_message
                    )
        return None
    
    def _detect_attributes(self, message_lower: str, original_message: str) -> List[StatusUpdate]:
        """Detect status attributes from message."""
        attributes = []
        
        for attribute, patterns in self.attribute_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    attributes.append(StatusUpdate(
                        type="attribute",
                        value={"name": attribute, "level": 7, "active": True},
                        confidence=0.7,
                        source_text=original_message
                    ))
                    break  # Only add each attribute once per message
        
        return attributes
    
    def _detect_preferences(self, message_lower: str, original_message: str) -> List[ProfileUpdate]:
        """Detect user preferences from message."""
        preferences = []
        
        for category, patterns in self.preference_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, message_lower, re.IGNORECASE)
                for match in matches:
                    # Extract the specific item mentioned
                    items = ['pizza', 'sushi', 'coffee', 'tea', 'chocolate', 'ice cream', 'pasta',
                            'rock', 'pop', 'jazz', 'classical', 'hip hop', 'country', 'electronic',
                            'reading', 'hiking', 'cooking', 'gaming', 'traveling', 'photography']
                    
                    for item in items:
                        if item in match.group():
                            preferences.append(ProfileUpdate(
                                type="preference",
                                category=category,
                                value=item,
                                confidence=0.7,
                                source_text=original_message
                            ))
                            break
        
        return preferences
    
    def _detect_goals(self, message: str, original_message: str) -> List[ProfileUpdate]:
        """Detect user goals from message."""
        goals = []
        
        for pattern in self.goal_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                goal_text = match.group(2).strip()
                if len(goal_text) > 5:  # Filter out very short matches
                    goals.append(ProfileUpdate(
                        type="goal",
                        category="personal",
                        value={
                            "title": goal_text[:50],  # Truncate long titles
                            "description": goal_text,
                            "category": "personal"
                        },
                        confidence=0.6,
                        source_text=original_message
                    ))
        
        return goals
    
    def _detect_values(self, message: str, original_message: str) -> List[ProfileUpdate]:
        """Detect user values from message."""
        values = []
        
        for pattern in self.value_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                value_text = match.group(2).strip()
                if len(value_text) > 3:  # Filter out very short matches
                    values.append(ProfileUpdate(
                        type="value",
                        value=value_text,
                        confidence=0.6,
                        source_text=original_message
                    ))
        
        return values
    
    def _detect_important_people(self, message: str, original_message: str) -> List[ProfileUpdate]:
        """Detect mentions of important people from message."""
        people = []
        
        for pattern in self.important_person_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 3:
                    name = groups[2] if groups[2] else groups[0]
                    relationship = groups[1] if len(groups) > 1 else "unknown"
                    
                    people.append(ProfileUpdate(
                        type="important_person",
                        value={
                            "name": name.title(),
                            "relationship": relationship.lower(),
                            "significance": f"Mentioned in conversation"
                        },
                        confidence=0.5,
                        source_text=original_message
                    ))
        
        return people

    def get_analysis_summary(self, status_updates: List[StatusUpdate], 
                           profile_updates: List[ProfileUpdate]) -> Dict[str, Any]:
        """Get a summary of the analysis results."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status_updates": {
                "count": len(status_updates),
                "types": list(set(update.type for update in status_updates)),
                "high_confidence": [update for update in status_updates if update.confidence > 0.7]
            },
            "profile_updates": {
                "count": len(profile_updates),
                "types": list(set(update.type for update in profile_updates)),
                "high_confidence": [update for update in profile_updates if update.confidence > 0.7]
            },
            "total_updates": len(status_updates) + len(profile_updates)
        }


# Global analyzer instance
_conversation_analyzer = ConversationAnalyzer()

def analyze_message_for_updates(message: str, user_id: str = "default") -> str:
    """
    Analyze a message for status and profile updates.
    
    Args:
        message: The message to analyze
        user_id: User identifier
        
    Returns:
        JSON string with analysis results
    """
    try:
        status_updates, profile_updates = _conversation_analyzer.analyze_conversation(message, user_id)
        summary = _conversation_analyzer.get_analysis_summary(status_updates, profile_updates)
        
        # Convert dataclasses to dictionaries for JSON serialization
        status_data = []
        for update in status_updates:
            status_data.append({
                "type": update.type,
                "value": update.value,
                "confidence": update.confidence,
                "source_text": update.source_text
            })
        
        profile_data = []
        for update in profile_updates:
            profile_data.append({
                "type": update.type,
                "category": update.category,
                "value": update.value,
                "metadata": update.metadata,
                "confidence": update.confidence,
                "source_text": update.source_text
            })
        
        result = {
            "analysis_summary": summary,
            "status_updates": status_data,
            "profile_updates": profile_data,
            "message_analyzed": message,
            "user_id": user_id
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error analyzing message: {e}")
        return json.dumps({"error": str(e)}, indent=2)