"""
MVP Shadow Agent - Behavioral Intelligence Observer

A minimal viable implementation of the Shadow Agent that works with OpenWebUI
to silently observe conversations and store behavioral data in the background.

File: agents/mvp_shadow_agent.py
"""

import sys
import json
import logging
import httpx
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("crewai.mvp_shadow_agent")

class MVPShadowAgent:
    """
    MVP Shadow Agent for behavioral observation and data storage
    
    This agent runs silently in the background during conversations,
    analyzing user behavior and storing insights via the myndy-ai memory API.
    """
    
    def __init__(self, myndy_api_base_url: str = "http://localhost:8000"):
        """
        Initialize MVP Shadow Agent
        
        Args:
            myndy_api_base_url: Base URL for myndy-ai FastAPI server
        """
        self.myndy_api_base_url = myndy_api_base_url.rstrip('/')
        self.session = httpx.Client(timeout=5.0)
        self.logger = logger
        
        # API headers for myndy-ai communication
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "MVP-Shadow-Agent/1.0"
        }
        
        self.logger.info("🔮 MVP Shadow Agent initialized")
    
    def observe_conversation(self, user_message: str, agent_response: str, 
                           agent_type: str, session_id: str) -> Dict[str, Any]:
        """
        Observe a conversation and extract behavioral insights
        
        Args:
            user_message: The user's input message
            agent_response: The agent's response
            agent_type: Type of agent that responded
            session_id: Current conversation session ID
            
        Returns:
            Dictionary with behavioral observations
        """
        try:
            # Extract behavioral patterns from the conversation
            observations = {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "user_message_length": len(user_message),
                "user_message_type": self._classify_message_type(user_message),
                "preferred_agent": agent_type,
                "communication_style": self._analyze_communication_style(user_message),
                "topics": self._extract_topics(user_message),
                "urgency_level": self._assess_urgency(user_message),
                "time_of_day": datetime.now().hour,
                "interaction_context": {
                    "primary_agent": agent_type,
                    "message_complexity": self._assess_complexity(user_message),
                    "emotional_indicators": self._detect_emotional_indicators(user_message)
                }
            }
            
            # Store behavioral data
            self._store_behavioral_observation(observations)
            
            # Update user preferences based on patterns
            self._update_user_preferences(observations)
            
            self.logger.debug(f"🔮 Shadow observation recorded for session {session_id}")
            return observations
            
        except Exception as e:
            self.logger.warning(f"Shadow observation failed: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    def _classify_message_type(self, message: str) -> str:
        """Classify the type of user message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["?", "what", "how", "when", "where", "why", "who"]):
            return "question"
        elif any(word in message_lower for word in ["please", "can you", "help", "need"]):
            return "request"
        elif any(word in message_lower for word in ["thank", "great", "awesome", "good"]):
            return "appreciation"
        elif any(word in message_lower for word in ["schedule", "remind", "calendar", "meeting"]):
            return "scheduling"
        elif any(word in message_lower for word in ["remember", "save", "store", "note"]):
            return "memory_storage"
        else:
            return "general"
    
    def _analyze_communication_style(self, message: str) -> str:
        """Analyze user's communication style"""
        if len(message) < 20:
            return "concise"
        elif len(message) > 100:
            return "detailed"
        elif "please" in message.lower() or "thank" in message.lower():
            return "polite"
        elif message.count("!") > 1 or message.isupper():
            return "urgent"
        else:
            return "casual"
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extract key topics from the message"""
        topics = []
        message_lower = message.lower()
        
        # Define topic keywords
        topic_keywords = {
            "health": ["health", "fitness", "exercise", "sleep", "medical"],
            "finance": ["money", "budget", "expense", "payment", "financial"],
            "work": ["work", "job", "meeting", "project", "deadline"],
            "calendar": ["schedule", "appointment", "calendar", "meeting", "time"],
            "personal": ["family", "friend", "relationship", "personal"],
            "technology": ["tech", "software", "computer", "app", "system"],
            "weather": ["weather", "temperature", "forecast", "rain", "sunny"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ["general"]
    
    def _assess_urgency(self, message: str) -> str:
        """Assess the urgency level of the message"""
        urgent_indicators = ["urgent", "asap", "immediately", "now", "emergency", "!"]
        message_lower = message.lower()
        
        if any(indicator in message_lower for indicator in urgent_indicators):
            return "high"
        elif any(word in message_lower for word in ["soon", "today", "quickly"]):
            return "medium"
        else:
            return "low"
    
    def _assess_complexity(self, message: str) -> str:
        """Assess the complexity of the user's request"""
        if len(message.split()) < 5:
            return "simple"
        elif len(message.split()) > 20:
            return "complex"
        else:
            return "moderate"
    
    def _detect_emotional_indicators(self, message: str) -> List[str]:
        """Detect emotional indicators in the message"""
        emotions = []
        message_lower = message.lower()
        
        emotion_keywords = {
            "happy": ["happy", "great", "awesome", "excellent", "wonderful", "😊", "😄"],
            "frustrated": ["frustrated", "annoying", "difficult", "problem", "issue", "😤"],
            "confused": ["confused", "unclear", "don't understand", "help", "🤔"],
            "excited": ["excited", "amazing", "fantastic", "can't wait", "🎉"],
            "worried": ["worried", "concerned", "anxious", "nervous", "😟"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                emotions.append(emotion)
        
        return emotions if emotions else ["neutral"]
    
    def _store_behavioral_observation(self, observation: Dict[str, Any]) -> bool:
        """Store behavioral observation via myndy-ai memory API"""
        try:
            # Store as a journal entry with behavioral context
            journal_data = {
                "content": f"Shadow Agent Observation: {observation['user_message_type']} message with {observation['communication_style']} style",
                "category": "behavioral_observation",
                "mood": observation.get("emotional_indicators", ["neutral"])[0] if observation.get("emotional_indicators") else "neutral",
                "tags": observation["topics"] + [observation["user_message_type"], observation["communication_style"]],
                "metadata": {
                    "session_id": observation["session_id"],
                    "message_length": observation["user_message_length"],
                    "urgency_level": observation["urgency_level"],
                    "time_of_day": observation["time_of_day"],
                    "complexity": observation["interaction_context"]["message_complexity"],
                    "emotional_indicators": observation["interaction_context"]["emotional_indicators"],
                    "observation_source": "shadow_agent"
                }
            }
            
            response = self.session.post(
                f"{self.myndy_api_base_url}/api/v1/memory/journal",
                json=journal_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.logger.debug("✅ Behavioral observation stored successfully")
                return True
            else:
                self.logger.warning(f"Failed to store observation: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.warning(f"Error storing behavioral observation: {e}")
            return False
    
    def _update_user_preferences(self, observation: Dict[str, Any]) -> bool:
        """Update user preferences based on behavioral patterns"""
        try:
            # Create a behavioral pattern status update
            behavioral_data = {
                "mood": observation.get("emotional_indicators", ["neutral"])[0] if observation.get("emotional_indicators") else "neutral",
                "activity": f"interacting_with_{observation.get('preferred_agent', 'unknown_agent')}",
                "notes": f"Communication style: {observation.get('communication_style', 'unknown')}, Message type: {observation.get('user_message_type', 'unknown')}, Topics: {', '.join(observation.get('topics', ['general']))}",
                "availability": "available"
            }
            
            # Store behavioral pattern as status update
            response = self.session.post(
                f"{self.myndy_api_base_url}/api/v1/status/update",
                json=behavioral_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.logger.debug("✅ User behavioral pattern updated successfully")
                
                # Also store as a fact for long-term learning
                fact_data = {
                    "content": f"User prefers {observation.get('communication_style', 'unknown')} communication style and shows interest in {', '.join(observation.get('topics', ['general']))}",
                    "category": "behavioral_preference",
                    "confidence": 0.7,
                    "source": "shadow_agent",
                    "tags": ["behavioral_pattern", "communication_preference"] + observation.get("topics", [])
                }
                
                fact_response = self.session.post(
                    f"{self.myndy_api_base_url}/api/v1/memory/facts",
                    json=fact_data,
                    headers=self.headers
                )
                
                if fact_response.status_code == 200:
                    self.logger.debug("✅ Behavioral fact stored successfully")
                else:
                    self.logger.warning(f"Failed to store behavioral fact: {fact_response.status_code}")
                    
                return True
            else:
                self.logger.warning(f"Failed to update behavioral pattern: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            self.logger.warning(f"Error updating user preferences: {e}")
            return False
    
    def get_behavioral_insights(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get behavioral insights for the user or session"""
        try:
            # Search for behavioral observations in journal entries
            search_data = {
                "query": "Shadow Agent Observation behavioral",
                "limit": 50,
                "include_people": False,
                "include_places": False,
                "include_groups": False
            }
            
            response = self.session.post(
                f"{self.myndy_api_base_url}/api/v1/memory/search",
                json=search_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                behavioral_data = data.get("results", [])
                
                # Analyze patterns
                insights = self._analyze_behavioral_patterns(behavioral_data)
                return insights
            else:
                return {"error": f"Failed to fetch behavioral data: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Error getting behavioral insights: {e}"}
    
    def _analyze_behavioral_patterns(self, behavioral_data: List[Dict]) -> Dict[str, Any]:
        """Analyze behavioral patterns from stored data"""
        if not behavioral_data:
            return {"message": "No behavioral data available"}
        
        # Extract patterns from journal entries and metadata
        communication_styles = []
        message_types = []
        topics = []
        time_patterns = []
        emotional_indicators = []
        
        for item in behavioral_data[-20:]:  # Last 20 observations
            try:
                # Extract from metadata if available
                metadata = item.get("metadata", {})
                if metadata:
                    if "communication_style" in str(metadata):
                        # Parse communication style from content or metadata
                        content = item.get("content", "")
                        if "concise" in content.lower():
                            communication_styles.append("concise")
                        elif "detailed" in content.lower():
                            communication_styles.append("detailed")
                        elif "polite" in content.lower():
                            communication_styles.append("polite")
                        elif "urgent" in content.lower():
                            communication_styles.append("urgent")
                        else:
                            communication_styles.append("casual")
                    
                    time_patterns.append(metadata.get("time_of_day"))
                    if metadata.get("emotional_indicators"):
                        emotional_indicators.extend(metadata.get("emotional_indicators", []))
                
                # Extract topics from content
                content = item.get("content", "").lower()
                item_topics = []
                topic_keywords = {
                    "health": ["health", "fitness", "exercise", "sleep", "medical"],
                    "finance": ["money", "budget", "expense", "payment", "financial"],
                    "work": ["work", "job", "meeting", "project", "deadline"],
                    "calendar": ["schedule", "appointment", "calendar", "meeting", "time"],
                    "personal": ["family", "friend", "relationship", "personal"],
                    "technology": ["tech", "software", "computer", "app", "system"],
                    "weather": ["weather", "temperature", "forecast", "rain", "sunny"]
                }
                
                for topic, keywords in topic_keywords.items():
                    if any(keyword in content for keyword in keywords):
                        item_topics.append(topic)
                
                topics.extend(item_topics if item_topics else ["general"])
                
                # Extract message types from content
                if "question" in content:
                    message_types.append("question")
                elif "request" in content:
                    message_types.append("request")
                elif "appreciation" in content:
                    message_types.append("appreciation")
                else:
                    message_types.append("general")
                    
            except Exception as e:
                self.logger.debug(f"Error parsing behavioral item: {e}")
                continue
        
        # Calculate patterns
        def most_common(items):
            return max(set(items), key=items.count) if items else "unknown"
        
        insights = {
            "most_common_communication_style": most_common(communication_styles),
            "most_common_message_type": most_common(message_types),
            "preferred_topics": list(set(topics))[:5],  # Top 5 unique topics
            "common_emotions": list(set(emotional_indicators))[:3],  # Top 3 emotions
            "active_hours": list(set(filter(None, time_patterns))),
            "total_observations": len(behavioral_data),
            "recent_observations": len(behavioral_data[-7:]),  # Last week
            "behavioral_consistency": len(set(communication_styles)) / len(communication_styles) if communication_styles else 0
        }
        
        return insights
    
    def generate_personality_summary(self) -> str:
        """Generate a brief personality summary based on behavioral data"""
        insights = self.get_behavioral_insights()
        
        if "error" in insights:
            return "Not enough behavioral data available for personality analysis."
        
        style = insights.get("most_common_communication_style", "unknown")
        message_type = insights.get("most_common_message_type", "unknown")
        topics = insights.get("preferred_topics", [])
        
        summary = f"Communication style: {style}. "
        summary += f"Tends to use {message_type} messages. "
        
        if topics:
            summary += f"Interested in: {', '.join(topics[:3])}. "
        
        observations = insights.get("total_observations", 0)
        summary += f"Based on {observations} behavioral observations."
        
        return summary
    
    def __del__(self):
        """Clean up HTTP session"""
        try:
            self.session.close()
        except:
            pass


def create_mvp_shadow_agent(myndy_api_base_url: str = "http://localhost:8000") -> MVPShadowAgent:
    """
    Factory function to create MVP Shadow Agent
    
    Args:
        myndy_api_base_url: Base URL for myndy-ai FastAPI server
        
    Returns:
        Configured MVPShadowAgent instance
    """
    return MVPShadowAgent(myndy_api_base_url)


if __name__ == "__main__":
    # Test the MVP Shadow Agent
    agent = create_mvp_shadow_agent()
    
    # Test behavioral observation
    test_observation = agent.observe_conversation(
        user_message="What's the weather like today?",
        agent_response="It's sunny and 72°F in your area.",
        agent_type="personal_assistant", 
        session_id="test_session_123"
    )
    
    print("🔮 MVP Shadow Agent Test:")
    print(f"Observation: {test_observation}")
    
    # Test behavioral insights
    insights = agent.get_behavioral_insights()
    print(f"Insights: {insights}")
    
    # Test personality summary
    summary = agent.generate_personality_summary()
    print(f"Personality Summary: {summary}")