"""
Enhanced Shadow Agent - LLM-Driven Behavioral Intelligence Observer

Combines the architectural strengths of shadow_agent.py with the practical HTTP integration
of mvp_shadow_agent.py, while using LLM decision-making for all behavioral analysis
instead of hardcoded rules.

File: agents/enhanced_shadow_agent.py
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

from crewai import Agent
from config.llm_config import get_agent_llm
from tools.myndy_bridge import get_agent_tools

logger = logging.getLogger("crewai.enhanced_shadow_agent")


class EnhancedShadowAgent:
    """
    Enhanced Shadow Agent with LLM-driven behavioral analysis
    
    Combines CrewAI agent architecture with HTTP-based myndy-ai integration,
    using LLM intelligence for all behavioral decisions and pattern recognition.
    """
    
    def __init__(self, myndy_api_base_url: str = "http://localhost:8000", 
                 max_iter: int = 25, max_execution_time: int = 180):
        """
        Initialize Enhanced Shadow Agent
        
        Args:
            myndy_api_base_url: Base URL for myndy-ai FastAPI server
            max_iter: Maximum iterations for agent execution
            max_execution_time: Maximum execution time in seconds
        """
        self.myndy_api_base_url = myndy_api_base_url.rstrip('/')
        self.max_iter = max_iter
        self.max_execution_time = max_execution_time
        self.session = httpx.Client(timeout=10.0)
        self.logger = logger
        
        # API headers for myndy-ai communication
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": "development-enhanced-shadow-agent-key",
            "User-Agent": "Enhanced-Shadow-Agent/2.0"
        }
        
        # Create CrewAI agent for LLM-driven analysis
        self.agent = self._create_crewai_agent(max_iter, max_execution_time)
        
        self.logger.info("🔮 Enhanced Shadow Agent initialized with LLM intelligence")
    
    def _create_crewai_agent(self, max_iter: int, max_execution_time: int) -> Agent:
        """Create the CrewAI agent for behavioral analysis"""
        tools = get_agent_tools("shadow_agent")
        
        return Agent(
            role="Enhanced Behavioral Intelligence Observer",
            goal="Use advanced LLM reasoning to analyze behavioral patterns and provide deep insights",
            backstory="""I am an advanced AI behavioral analyst with sophisticated pattern recognition
            capabilities. Unlike simple rule-based systems, I use advanced reasoning to understand
            human behavior, communication patterns, emotional states, and preferences.
            
            My analysis goes beyond keyword matching - I understand context, nuance, tone, and
            implicit meanings in human communication. I can detect subtle patterns that emerge
            over time and provide intelligent insights about user preferences and behavioral trends.
            
            I work silently in the background, continuously learning and building sophisticated
            models of user behavior that enhance every interaction across the entire system.""",
            
            verbose=False,
            allow_delegation=False,
            max_iter=max_iter,
            max_execution_time=max_execution_time,
            llm=get_agent_llm("shadow_agent"),
            tools=tools
        )
    
    def observe_conversation(self, user_message: str, agent_response: str, 
                           agent_type: str, session_id: str) -> Dict[str, Any]:
        """
        Observe a conversation using LLM-driven behavioral analysis
        
        Args:
            user_message: The user's input message
            agent_response: The agent's response
            agent_type: Type of agent that responded
            session_id: Current conversation session ID
            
        Returns:
            Dictionary with LLM-analyzed behavioral observations
        """
        try:
            # Use LLM to analyze the conversation
            analysis_prompt = self._create_behavioral_analysis_prompt(
                user_message, agent_response, agent_type, session_id
            )
            
            # Execute LLM analysis
            llm_analysis = self.agent.llm.invoke(analysis_prompt)
            
            # Parse LLM response into structured data
            observations = self._parse_llm_analysis(llm_analysis, {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "user_message": user_message,
                "agent_response": agent_response,
                "agent_type": agent_type
            })
            
            # Store behavioral data via myndy-ai API
            self._store_behavioral_observation(observations)
            
            # Update user behavioral model
            self._update_behavioral_model(observations)
            
            self.logger.debug(f"🔮 LLM-driven observation recorded for session {session_id}")
            return observations
            
        except Exception as e:
            self.logger.warning(f"Enhanced shadow observation failed: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    def _create_behavioral_analysis_prompt(self, user_message: str, agent_response: str, 
                                         agent_type: str, session_id: str) -> str:
        """Create a comprehensive prompt for LLM behavioral analysis"""
        return f"""
        As an advanced behavioral intelligence analyst, analyze this conversation interaction using sophisticated reasoning:

        **Conversation Data:**
        - User Message: "{user_message}"
        - Agent Response: "{agent_response}"
        - Agent Type: {agent_type}
        - Session ID: {session_id}
        - Timestamp: {datetime.utcnow().isoformat()}
        - Time of Day: {datetime.now().hour}:00

        **Analysis Requirements:**
        Provide a comprehensive behavioral analysis in JSON format with the following structure:

        {{
            "message_classification": {{
                "primary_type": "question|request|command|appreciation|complaint|casual_conversation",
                "secondary_types": ["additional", "types", "if", "applicable"],
                "confidence": 0.0-1.0,
                "reasoning": "Explain your classification reasoning"
            }},
            "communication_style": {{
                "style": "concise|detailed|formal|casual|technical|emotional|urgent|polite",
                "tone": "neutral|positive|negative|excited|frustrated|confused|confident",
                "formality_level": "very_informal|informal|neutral|formal|very_formal",
                "confidence": 0.0-1.0,
                "reasoning": "Explain your style analysis"
            }},
            "urgency_assessment": {{
                "level": "low|medium|high|critical",
                "indicators": ["specific", "words", "or", "patterns", "that", "indicate", "urgency"],
                "time_sensitivity": "immediate|today|this_week|flexible|not_time_sensitive",
                "confidence": 0.0-1.0,
                "reasoning": "Explain urgency determination"
            }},
            "topic_analysis": {{
                "primary_topics": ["main", "topics", "discussed"],
                "secondary_topics": ["related", "or", "implied", "topics"],
                "domain_categories": ["health|finance|work|personal|technology|entertainment|education|etc"],
                "complexity_level": "simple|moderate|complex|expert_level",
                "confidence": 0.0-1.0,
                "reasoning": "Explain topic identification process"
            }},
            "emotional_intelligence": {{
                "detected_emotions": ["happy|sad|frustrated|excited|worried|confident|confused|etc"],
                "emotional_intensity": "very_low|low|moderate|high|very_high",
                "emotional_context": "What emotional context surrounds this message",
                "user_satisfaction_indicators": ["positive", "or", "negative", "satisfaction", "signals"],
                "confidence": 0.0-1.0,
                "reasoning": "Explain emotional analysis"
            }},
            "behavioral_patterns": {{
                "communication_preferences": "What this reveals about user's communication preferences",
                "interaction_style": "How user prefers to interact with AI systems",
                "information_processing": "How user processes and requests information",
                "decision_making_style": "Patterns in how user makes decisions or requests",
                "learning_indicators": "Signs of how user learns or wants to be taught",
                "confidence": 0.0-1.0,
                "reasoning": "Explain behavioral pattern analysis"
            }},
            "contextual_insights": {{
                "user_expertise_level": "beginner|intermediate|advanced|expert",
                "likely_next_needs": ["what", "user", "might", "need", "next"],
                "personalization_opportunities": ["ways", "to", "personalize", "future", "interactions"],
                "relationship_building": "How this interaction affects user-AI relationship",
                "trust_indicators": "Signs of trust or distrust in the interaction",
                "confidence": 0.0-1.0,
                "reasoning": "Explain contextual analysis"
            }},
            "agent_performance_feedback": {{
                "response_appropriateness": "How well the agent response matched user needs",
                "missed_opportunities": ["things", "the", "agent", "could", "have", "done", "better"],
                "successful_elements": ["what", "worked", "well", "in", "the", "response"],
                "suggestions_for_improvement": "How future similar interactions could be enhanced",
                "confidence": 0.0-1.0,
                "reasoning": "Explain performance analysis"
            }}
        }}

        **Important Guidelines:**
        1. Use sophisticated reasoning, not simple keyword matching
        2. Consider context, nuance, and implicit meanings
        3. Provide confidence scores for all assessments
        4. Explain your reasoning for each analysis
        5. Look for subtle patterns and implications
        6. Consider cultural and linguistic nuances
        7. Focus on actionable insights for improving future interactions

        Respond ONLY with the JSON structure filled with your analysis.
        """
    
    def _parse_llm_analysis(self, llm_response: str, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM analysis response into structured observations"""
        try:
            # Extract JSON from LLM response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                llm_analysis = json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in LLM response")
            
            # Combine base data with LLM analysis
            observations = {
                **base_data,
                "llm_analysis": llm_analysis,
                "analysis_method": "llm_driven",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Extract key insights for easy access
            observations.update({
                "message_type": llm_analysis.get("message_classification", {}).get("primary_type", "unknown"),
                "communication_style": llm_analysis.get("communication_style", {}).get("style", "unknown"),
                "urgency_level": llm_analysis.get("urgency_assessment", {}).get("level", "unknown"),
                "primary_topics": llm_analysis.get("topic_analysis", {}).get("primary_topics", ["general"]),
                "detected_emotions": llm_analysis.get("emotional_intelligence", {}).get("detected_emotions", ["neutral"]),
                "user_expertise_level": llm_analysis.get("contextual_insights", {}).get("user_expertise_level", "unknown")
            })
            
            return observations
            
        except Exception as e:
            self.logger.warning(f"Error parsing LLM analysis: {e}")
            # Fallback to basic structure
            return {
                **base_data,
                "analysis_method": "fallback",
                "error": str(e),
                "message_type": "unknown",
                "communication_style": "unknown",
                "urgency_level": "medium",
                "primary_topics": ["general"],
                "detected_emotions": ["neutral"]
            }
    
    def _store_behavioral_observation(self, observation: Dict[str, Any]) -> bool:
        """Store behavioral observation via myndy-ai memory API"""
        try:
            # Create rich journal entry with LLM insights
            journal_data = {
                "content": f"Enhanced Shadow Agent Analysis: {observation.get('message_type', 'unknown')} interaction with {observation.get('communication_style', 'unknown')} style. "
                          f"Topics: {', '.join(observation.get('primary_topics', ['general']))}. "
                          f"Emotions: {', '.join(observation.get('detected_emotions', ['neutral']))}. "
                          f"Urgency: {observation.get('urgency_level', 'unknown')}.",
                "category": "behavioral_observation_enhanced",
                "mood": observation.get("detected_emotions", ["neutral"])[0],
                "tags": (observation.get("primary_topics", []) + 
                        [observation.get("message_type", "unknown"), 
                         observation.get("communication_style", "unknown"),
                         f"urgency_{observation.get('urgency_level', 'unknown')}",
                         "llm_analyzed"]),
                "metadata": {
                    "session_id": observation["session_id"],
                    "agent_type": observation.get("agent_type"),
                    "analysis_method": observation.get("analysis_method", "llm_driven"),
                    "llm_analysis": observation.get("llm_analysis", {}),
                    "user_expertise_level": observation.get("user_expertise_level", "unknown"),
                    "observation_source": "enhanced_shadow_agent",
                    "analysis_timestamp": observation.get("analysis_timestamp")
                }
            }
            
            response = self.session.post(
                f"{self.myndy_api_base_url}/api/v1/memory/journal",
                json=journal_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.logger.debug("✅ Enhanced behavioral observation stored successfully")
                return True
            else:
                self.logger.warning(f"Failed to store observation: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.warning(f"Error storing behavioral observation: {e}")
            return False
    
    def _update_behavioral_model(self, observation: Dict[str, Any]) -> bool:
        """Update user behavioral model with LLM insights"""
        try:
            llm_analysis = observation.get("llm_analysis", {})
            
            # Create behavioral pattern status update
            behavioral_data = {
                "mood": observation.get("detected_emotions", ["neutral"])[0],
                "activity": f"analyzing_with_{observation.get('agent_type', 'unknown_agent')}",
                "notes": f"LLM Analysis - Style: {observation.get('communication_style', 'unknown')}, "
                        f"Expertise: {observation.get('user_expertise_level', 'unknown')}, "
                        f"Communication preference: {llm_analysis.get('behavioral_patterns', {}).get('communication_preferences', 'unknown')}",
                "availability": "available"
            }
            
            response = self.session.post(
                f"{self.myndy_api_base_url}/api/v1/status/update",
                json=behavioral_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.logger.debug("✅ Enhanced behavioral model updated successfully")
                
                # Store sophisticated behavioral insights as facts
                insights = llm_analysis.get("behavioral_patterns", {})
                contextual_insights = llm_analysis.get("contextual_insights", {})
                
                fact_data = {
                    "content": f"User behavioral profile: {insights.get('communication_preferences', 'Unknown preferences')}. "
                              f"Interaction style: {insights.get('interaction_style', 'Unknown style')}. "
                              f"Information processing: {insights.get('information_processing', 'Unknown processing')}. "
                              f"Expertise level: {contextual_insights.get('user_expertise_level', 'unknown')}.",
                    "category": "behavioral_profile_llm",
                    "confidence": llm_analysis.get("behavioral_patterns", {}).get("confidence", 0.7),
                    "source": "enhanced_shadow_agent",
                    "tags": ["behavioral_pattern", "llm_analysis", "communication_profile"] + 
                           observation.get("primary_topics", [])
                }
                
                fact_response = self.session.post(
                    f"{self.myndy_api_base_url}/api/v1/memory/facts",
                    json=fact_data,
                    headers=self.headers
                )
                
                if fact_response.status_code == 200:
                    self.logger.debug("✅ Enhanced behavioral fact stored successfully")
                else:
                    self.logger.warning(f"Failed to store behavioral fact: {fact_response.status_code}")
                    
                return True
            else:
                self.logger.warning(f"Failed to update behavioral model: {response.status_code}")
                return False
            
        except Exception as e:
            self.logger.warning(f"Error updating behavioral model: {e}")
            return False
    
    def get_behavioral_insights(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive behavioral insights using stored LLM analysis"""
        try:
            # Search for enhanced behavioral observations
            search_data = {
                "query": "Enhanced Shadow Agent Analysis behavioral llm_analyzed",
                "limit": 100,
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
                
                # Use LLM to analyze patterns across observations
                insights = self._generate_comprehensive_insights(behavioral_data)
                return insights
            else:
                return {"error": f"Failed to fetch behavioral data: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Error getting behavioral insights: {e}"}
    
    def _generate_comprehensive_insights(self, behavioral_data: List[Dict]) -> Dict[str, Any]:
        """Use LLM to generate comprehensive insights from behavioral data"""
        if not behavioral_data:
            return {"message": "No behavioral data available"}
        
        try:
            # Prepare data summary for LLM analysis
            recent_observations = behavioral_data[-20:]  # Last 20 observations
            
            insights_prompt = f"""
            As an advanced behavioral analyst, analyze these behavioral observations to generate comprehensive user insights:

            **Behavioral Data Summary:**
            Total Observations: {len(behavioral_data)}
            Recent Observations (Last 20): {len(recent_observations)}

            **Recent Observation Details:**
            {json.dumps([{
                "content": obs.get("content", ""),
                "timestamp": obs.get("timestamp", ""),
                "metadata": obs.get("metadata", {})
            } for obs in recent_observations], indent=2)}

            **Generate Comprehensive Behavioral Profile:**
            Provide your analysis in JSON format:

            {{
                "communication_profile": {{
                    "dominant_style": "primary communication style across observations",
                    "style_consistency": "how consistent the style is (0.0-1.0)",
                    "style_evolution": "how communication style has evolved over time",
                    "preferred_interaction_mode": "how user prefers to interact"
                }},
                "behavioral_patterns": {{
                    "request_patterns": "common patterns in how user makes requests",
                    "information_seeking": "how user typically seeks information",
                    "decision_making": "patterns in user decision-making process",
                    "learning_style": "how user prefers to learn and receive information"
                }},
                "emotional_intelligence": {{
                    "emotional_range": "range of emotions typically expressed",
                    "emotional_triggers": "what tends to trigger different emotions",
                    "satisfaction_indicators": "what indicates user satisfaction",
                    "stress_patterns": "signs of stress or frustration"
                }},
                "topic_expertise": {{
                    "expert_areas": "topics where user shows expertise",
                    "learning_areas": "topics where user is learning/growing",
                    "interest_evolution": "how interests have changed over time",
                    "knowledge_gaps": "areas where user might need more support"
                }},
                "interaction_optimization": {{
                    "preferred_response_style": "how user prefers responses formatted",
                    "optimal_detail_level": "preferred level of detail in responses",
                    "timing_preferences": "when user is most active/engaged",
                    "personalization_opportunities": "specific ways to personalize interactions"
                }},
                "predictive_insights": {{
                    "likely_future_needs": "what user might need in the future",
                    "growth_areas": "areas where user is likely to develop",
                    "potential_challenges": "challenges user might face",
                    "support_strategies": "how to best support this user"
                }},
                "confidence_scores": {{
                    "overall_analysis_confidence": 0.0-1.0,
                    "pattern_reliability": 0.0-1.0,
                    "prediction_accuracy": 0.0-1.0
                }}
            }}

            Focus on actionable insights that will improve user experience across all interactions.
            """
            
            llm_insights = self.agent.llm.invoke(insights_prompt)
            
            # Parse LLM insights
            json_start = llm_insights.find('{')
            json_end = llm_insights.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = llm_insights[json_start:json_end]
                parsed_insights = json.loads(json_str)
                
                # Add metadata
                parsed_insights.update({
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "data_points_analyzed": len(behavioral_data),
                    "recent_activity_window": len(recent_observations),
                    "analysis_method": "llm_comprehensive"
                })
                
                return parsed_insights
            else:
                raise ValueError("No valid JSON in LLM response")
                
        except Exception as e:
            self.logger.warning(f"Error generating comprehensive insights: {e}")
            # Fallback to basic analysis
            return self._basic_pattern_analysis(behavioral_data)
    
    def _basic_pattern_analysis(self, behavioral_data: List[Dict]) -> Dict[str, Any]:
        """Fallback basic pattern analysis if LLM analysis fails"""
        # Simple aggregation for fallback
        total_observations = len(behavioral_data)
        recent_observations = len(behavioral_data[-7:])
        
        return {
            "total_observations": total_observations,
            "recent_observations": recent_observations,
            "analysis_method": "basic_fallback",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Basic analysis due to LLM processing error"
        }
    
    def generate_personality_summary(self) -> str:
        """Generate comprehensive personality summary using LLM analysis"""
        insights = self.get_behavioral_insights()
        
        if "error" in insights:
            return "Not enough behavioral data available for personality analysis."
        
        try:
            summary_prompt = f"""
            Based on this comprehensive behavioral analysis, generate a concise but insightful personality summary:

            **Behavioral Analysis:**
            {json.dumps(insights, indent=2)}

            **Generate a 2-3 sentence personality summary that captures:**
            1. Primary communication style and preferences
            2. Key behavioral patterns and traits
            3. How to best interact with this user

            Make it conversational and actionable for other AI agents.
            """
            
            summary = self.agent.llm.invoke(summary_prompt)
            return summary.strip()
            
        except Exception as e:
            self.logger.warning(f"Error generating personality summary: {e}")
            # Fallback summary
            return f"User shows consistent behavioral patterns. Based on {insights.get('total_observations', 0)} observations."
    
    def get_contextual_recommendations(self, current_request: str, agent_type: str) -> Dict[str, Any]:
        """Get LLM-driven contextual recommendations for current interaction"""
        try:
            insights = self.get_behavioral_insights()
            
            recommendations_prompt = f"""
            As a behavioral intelligence advisor, provide specific recommendations for this interaction:

            **Current Context:**
            - User Request: "{current_request}"
            - Agent Type: {agent_type}
            - Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

            **User Behavioral Profile:**
            {json.dumps(insights, indent=2)}

            **Provide Specific Recommendations in JSON format:**
            {{
                "communication_approach": {{
                    "recommended_style": "specific style for this interaction",
                    "tone_suggestions": "recommended tone based on user patterns",
                    "detail_level": "appropriate level of detail for response",
                    "format_preferences": "how to format the response"
                }},
                "content_recommendations": {{
                    "key_points_to_include": ["important", "points", "to", "cover"],
                    "additional_context": "extra context that would be valuable",
                    "proactive_suggestions": ["things", "to", "suggest", "proactively"],
                    "potential_follow_ups": ["likely", "follow", "up", "questions"]
                }},
                "personalization_opportunities": {{
                    "user_specific_touches": "ways to personalize this specific response",
                    "reference_previous_interactions": "relevant past interactions to reference",
                    "adapt_to_expertise_level": "how to adapt to user's expertise level",
                    "emotional_considerations": "emotional context to consider"
                }},
                "interaction_optimization": {{
                    "timing_considerations": "optimal timing for this response",
                    "tool_recommendations": ["best", "tools", "for", "this", "agent", "to", "use"],
                    "collaboration_suggestions": "whether other agents should be involved",
                    "success_metrics": "how to measure success of this interaction"
                }},
                "risk_mitigation": {{
                    "potential_issues": ["possible", "problems", "to", "avoid"],
                    "sensitivity_areas": "areas requiring extra sensitivity",
                    "fallback_strategies": "backup approaches if primary approach fails"
                }}
            }}
            """
            
            recommendations = self.agent.llm.invoke(recommendations_prompt)
            
            # Parse recommendations
            json_start = recommendations.find('{')
            json_end = recommendations.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = recommendations[json_start:json_end]
                parsed_recommendations = json.loads(json_str)
                
                parsed_recommendations.update({
                    "generated_timestamp": datetime.utcnow().isoformat(),
                    "request_context": current_request,
                    "agent_context": agent_type
                })
                
                return parsed_recommendations
            else:
                raise ValueError("No valid JSON in recommendations")
                
        except Exception as e:
            self.logger.warning(f"Error generating contextual recommendations: {e}")
            return {
                "error": str(e),
                "fallback_recommendation": "Use standard interaction approach",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def __del__(self):
        """Clean up HTTP session"""
        try:
            self.session.close()
        except:
            pass


def create_enhanced_shadow_agent(myndy_api_base_url: str = "http://localhost:8000",
                               max_iter: int = 25, max_execution_time: int = 180) -> EnhancedShadowAgent:
    """
    Factory function to create Enhanced Shadow Agent
    
    Args:
        myndy_api_base_url: Base URL for myndy-ai FastAPI server
        max_iter: Maximum iterations for agent execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Configured EnhancedShadowAgent instance
    """
    return EnhancedShadowAgent(myndy_api_base_url, max_iter, max_execution_time)


# Legacy CrewAI agent creation for backward compatibility
def create_shadow_agent(max_iter: int = 25, max_execution_time: int = 180) -> Agent:
    """
    Create a traditional CrewAI Shadow Agent (for backward compatibility)
    
    Args:
        max_iter: Maximum iterations for agent execution
        max_execution_time: Maximum execution time in seconds
        
    Returns:
        Agent: Configured Shadow Agent
    """
    tools = get_agent_tools("shadow_agent")
    
    return Agent(
        role="Enhanced Shadow Intelligence Observer",
        goal="Use advanced LLM reasoning to silently observe, analyze, and enhance user interactions",
        backstory="""I am an enhanced behavioral intelligence observer with sophisticated LLM-driven
        analysis capabilities. I work silently in the background, using advanced reasoning to understand
        human behavior, communication patterns, and preferences without relying on simple rules.
        
        My LLM-powered analysis provides deep insights into user behavior that help personalize
        every interaction across the entire system. I learn continuously and adapt my understanding
        based on sophisticated pattern recognition and contextual analysis.""",
        
        verbose=False,
        allow_delegation=False,
        max_iter=max_iter,
        max_execution_time=max_execution_time,
        llm=get_agent_llm("shadow_agent"),
        tools=tools
    )


if __name__ == "__main__":
    # Test the Enhanced Shadow Agent
    agent = create_enhanced_shadow_agent()
    
    # Test behavioral observation with LLM analysis
    test_observation = agent.observe_conversation(
        user_message="I'm feeling overwhelmed with my project deadlines and need help organizing my priorities. Can you help me create a strategic plan?",
        agent_response="I understand you're feeling overwhelmed. Let me help you break down your projects and create a priority matrix...",
        agent_type="personal_assistant", 
        session_id="test_session_enhanced_123"
    )
    
    print("🔮 Enhanced Shadow Agent Test:")
    print(f"LLM-Driven Observation: {json.dumps(test_observation, indent=2)}")
    
    # Test comprehensive insights
    insights = agent.get_behavioral_insights()
    print(f"\nComprehensive Insights: {json.dumps(insights, indent=2)}")
    
    # Test contextual recommendations
    recommendations = agent.get_contextual_recommendations(
        "What's my schedule for tomorrow?", 
        "personal_assistant"
    )
    print(f"\nContextual Recommendations: {json.dumps(recommendations, indent=2)}")
    
    # Test personality summary
    summary = agent.generate_personality_summary()
    print(f"\nLLM-Generated Personality Summary: {summary}")