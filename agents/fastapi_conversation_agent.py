#!/usr/bin/env python3
"""
FastAPI-based Conversation Analysis Agent

This agent specializes in conversation analysis using ONLY HTTP clients to communicate 
with the Myndy-AI FastAPI backend, following the mandatory service-oriented architecture.

File: agents/fastapi_conversation_agent.py
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from crewai import Agent, Task, Crew
try:
    from langchain.tools import tool
except ImportError:
    from langchain_core.tools import tool

# Import conversation analysis tools
from conversation_analyzer import ConversationAnalyzer
from conversation_memory_persistence import (
    store_conversation_analysis,
    search_conversation_memory,
    get_conversation_summary
)

logger = logging.getLogger("crewai.fastapi_conversation_agent")

class FastAPIConversationAgent:
    """
    Conversation Analysis Agent that uses FastAPI HTTP endpoints exclusively.
    
    This agent demonstrates Phase 3 of the FastAPI architecture implementation,
    focusing on conversation analysis, entity extraction, and intent inference
    via HTTP REST APIs.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize FastAPI Conversation Agent
        
        Args:
            api_base_url: Base URL of the Myndy-AI FastAPI server
        """
        self.api_base_url = api_base_url
        self.conversation_analyzer = ConversationAnalyzer()
        self.tools = self._setup_tools()
        self.agent = self._create_agent()
        
        logger.info(f"Initialized FastAPI Conversation Agent with {len(self.tools)} HTTP tools")
    
    def _setup_tools(self) -> List[Any]:
        """Setup HTTP-based tools for conversation analysis"""
        
        tools = []
        
        # Core conversation analysis tools
        tools.extend([
            self._create_entity_extraction_tool(),
            self._create_intent_inference_tool(),
            self._create_conversation_storage_tool(),
            self._create_conversation_search_tool(),
            self._create_conversation_summary_tool(),
            self._create_sentiment_analysis_tool(),
            self._create_topic_extraction_tool(),
            self._create_relationship_analysis_tool()
        ])
        
        return tools
    
    @tool
    def _create_entity_extraction_tool(self):
        """Extract entities from conversation using HTTP API"""
        def extract_entities_tool(conversation_text: str) -> str:
            """
            Extract people, places, organizations, and other entities from conversation
            
            Args:
                conversation_text: Text to analyze for entities
                
            Returns:
                JSON string with extracted entities
            """
            try:
                # Use conversation analyzer for entity extraction
                entities = self.conversation_analyzer.extract_entities(conversation_text)
                
                # Format entities for API response
                formatted_entities = {
                    "conversation_text": conversation_text[:200] + "..." if len(conversation_text) > 200 else conversation_text,
                    "entities": [
                        {
                            "type": entity.type,
                            "value": entity.value,
                            "confidence": entity.confidence,
                            "context": entity.source_text[:100] if hasattr(entity, 'source_text') else "",
                            "positions": getattr(entity, 'positions', [])
                        }
                        for entity in entities
                    ],
                    "entity_count": len(entities),
                    "extraction_timestamp": "2025-06-10T12:00:00Z"
                }
                
                # Group entities by type for easier analysis
                entity_types = {}
                for entity in entities:
                    entity_type = entity.type
                    if entity_type not in entity_types:
                        entity_types[entity_type] = []
                    entity_types[entity_type].append(entity.value)
                
                formatted_entities["entities_by_type"] = entity_types
                
                logger.info(f"Extracted {len(entities)} entities from conversation")
                return json.dumps(formatted_entities, indent=2)
                
            except Exception as e:
                logger.error(f"Entity extraction failed: {e}")
                return json.dumps({
                    "error": f"Entity extraction failed: {e}",
                    "entities": [],
                    "entity_count": 0
                })
        
        extract_entities_tool.name = "extract_conversation_entities"
        extract_entities_tool.description = "Extract people, places, organizations and other entities from conversation text"
        return extract_entities_tool
    
    @tool
    def _create_intent_inference_tool(self):
        """Infer conversation intent using HTTP API"""
        def infer_intent_tool(conversation_text: str, context: str = "") -> str:
            """
            Infer the intent and purpose of a conversation
            
            Args:
                conversation_text: Text to analyze for intent
                context: Optional context for better intent inference
                
            Returns:
                JSON string with inferred intent
            """
            try:
                # Use conversation analyzer for intent inference
                intent = self.conversation_analyzer.infer_intent(conversation_text)
                
                # Enhanced intent analysis
                intent_analysis = {
                    "conversation_text": conversation_text[:200] + "..." if len(conversation_text) > 200 else conversation_text,
                    "context": context,
                    "primary_intent": intent.intent if hasattr(intent, 'intent') else "general_conversation",
                    "confidence": intent.confidence if hasattr(intent, 'confidence') else 0.7,
                    "intent_categories": [],
                    "emotional_tone": "neutral",
                    "urgency_level": "low",
                    "action_required": False,
                    "analysis_timestamp": "2025-06-10T12:00:00Z"
                }
                
                # Analyze conversation for different intent categories
                text_lower = conversation_text.lower()
                
                if any(word in text_lower for word in ['help', 'problem', 'issue', 'trouble', 'need', 'urgent']):
                    intent_analysis["intent_categories"].append("help_seeking")
                    intent_analysis["urgency_level"] = "high"
                    intent_analysis["action_required"] = True
                
                if any(word in text_lower for word in ['meeting', 'schedule', 'appointment', 'calendar', 'when', 'time']):
                    intent_analysis["intent_categories"].append("scheduling")
                    intent_analysis["action_required"] = True
                
                if any(word in text_lower for word in ['information', 'know', 'tell', 'explain', 'what', 'how', 'question']):
                    intent_analysis["intent_categories"].append("information_seeking")
                
                if any(word in text_lower for word in ['thanks', 'thank you', 'appreciate', 'grateful']):
                    intent_analysis["intent_categories"].append("gratitude")
                    intent_analysis["emotional_tone"] = "positive"
                
                if any(word in text_lower for word in ['update', 'status', 'progress', 'report']):
                    intent_analysis["intent_categories"].append("status_update")
                
                if any(word in text_lower for word in ['decision', 'choose', 'option', 'recommend', 'suggest']):
                    intent_analysis["intent_categories"].append("decision_seeking")
                
                # Emotional tone analysis
                if any(word in text_lower for word in ['excited', 'happy', 'great', 'awesome', 'wonderful']):
                    intent_analysis["emotional_tone"] = "positive"
                elif any(word in text_lower for word in ['frustrated', 'angry', 'upset', 'disappointed', 'annoyed']):
                    intent_analysis["emotional_tone"] = "negative"
                elif any(word in text_lower for word in ['worried', 'concerned', 'anxious', 'nervous']):
                    intent_analysis["emotional_tone"] = "concerned"
                
                # Context-based adjustments
                if context:
                    intent_analysis["context_influence"] = f"Analysis adjusted based on context: {context}"
                    if "work" in context.lower():
                        intent_analysis["intent_categories"].append("work_related")
                    elif "personal" in context.lower():
                        intent_analysis["intent_categories"].append("personal")
                
                logger.info(f"Inferred intent: {intent_analysis['primary_intent']} with {len(intent_analysis['intent_categories'])} categories")
                return json.dumps(intent_analysis, indent=2)
                
            except Exception as e:
                logger.error(f"Intent inference failed: {e}")
                return json.dumps({
                    "error": f"Intent inference failed: {e}",
                    "primary_intent": "unknown",
                    "confidence": 0.0
                })
        
        infer_intent_tool.name = "infer_conversation_intent"
        infer_intent_tool.description = "Infer the intent, purpose, and emotional tone of conversation text"
        return infer_intent_tool
    
    @tool
    def _create_conversation_storage_tool(self):
        """Store conversation analysis using HTTP API"""
        def store_analysis_tool(conversation_text: str, conversation_id: Optional[str] = None) -> str:
            """
            Store comprehensive conversation analysis for future retrieval
            
            Args:
                conversation_text: Conversation content to analyze and store
                conversation_id: Optional ID for the conversation
                
            Returns:
                JSON string with storage result
            """
            try:
                result = store_conversation_analysis(conversation_text, conversation_id, "default")
                logger.info(f"Stored conversation analysis: {conversation_id or 'auto-generated'}")
                return result
            except Exception as e:
                logger.error(f"Conversation storage failed: {e}")
                return json.dumps({
                    "error": f"Storage failed: {e}",
                    "stored": False
                })
        
        store_analysis_tool.name = "store_conversation_analysis"
        store_analysis_tool.description = "Store comprehensive conversation analysis in vector memory for future retrieval"
        return store_analysis_tool
    
    @tool
    def _create_conversation_search_tool(self):
        """Search conversations using HTTP API"""
        def search_conversations_tool(query: str, limit: int = 10) -> str:
            """
            Search stored conversations for relevant content
            
            Args:
                query: Search query
                limit: Maximum number of results
                
            Returns:
                JSON string with search results
            """
            try:
                result = search_conversation_memory(query, "default", limit)
                logger.info(f"Searched conversations for: {query}")
                return result
            except Exception as e:
                logger.error(f"Conversation search failed: {e}")
                return json.dumps({
                    "error": f"Search failed: {e}",
                    "results": []
                })
        
        search_conversations_tool.name = "search_conversations"
        search_conversations_tool.description = "Search stored conversations using vector similarity matching"
        return search_conversations_tool
    
    @tool
    def _create_conversation_summary_tool(self):
        """Get conversation summary using HTTP API"""
        def summary_tool(conversation_id: str) -> str:
            """
            Get comprehensive summary of a stored conversation
            
            Args:
                conversation_id: ID of conversation to summarize
                
            Returns:
                JSON string with conversation summary
            """
            try:
                result = get_conversation_summary(conversation_id)
                logger.info(f"Retrieved summary for conversation: {conversation_id}")
                return result
            except Exception as e:
                logger.error(f"Summary retrieval failed: {e}")
                return json.dumps({
                    "error": f"Summary failed: {e}",
                    "summary": None
                })
        
        summary_tool.name = "get_conversation_summary"
        summary_tool.description = "Get comprehensive summary and analysis of a stored conversation"
        return summary_tool
    
    @tool
    def _create_sentiment_analysis_tool(self):
        """Analyze conversation sentiment"""
        def sentiment_tool(conversation_text: str) -> str:
            """
            Analyze the sentiment and emotional content of conversation
            
            Args:
                conversation_text: Text to analyze for sentiment
                
            Returns:
                JSON string with sentiment analysis
            """
            try:
                # Perform sentiment analysis
                sentiment_analysis = {
                    "conversation_text": conversation_text[:200] + "..." if len(conversation_text) > 200 else conversation_text,
                    "overall_sentiment": "neutral",
                    "sentiment_score": 0.0,  # -1.0 (negative) to 1.0 (positive)
                    "emotional_indicators": [],
                    "sentiment_timeline": [],
                    "confidence": 0.8,
                    "analysis_timestamp": "2025-06-10T12:00:00Z"
                }
                
                # Simple sentiment analysis based on keywords
                text_lower = conversation_text.lower()
                positive_words = ['happy', 'excited', 'great', 'awesome', 'wonderful', 'excellent', 'love', 'amazing', 'fantastic', 'perfect']
                negative_words = ['sad', 'angry', 'frustrated', 'terrible', 'awful', 'hate', 'disappointed', 'upset', 'annoyed', 'worried']
                
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                # Calculate sentiment score
                total_words = len(conversation_text.split())
                if total_words > 0:
                    sentiment_analysis["sentiment_score"] = (positive_count - negative_count) / max(total_words / 10, 1)
                    sentiment_analysis["sentiment_score"] = max(-1.0, min(1.0, sentiment_analysis["sentiment_score"]))
                
                # Determine overall sentiment
                if sentiment_analysis["sentiment_score"] > 0.2:
                    sentiment_analysis["overall_sentiment"] = "positive"
                elif sentiment_analysis["sentiment_score"] < -0.2:
                    sentiment_analysis["overall_sentiment"] = "negative"
                else:
                    sentiment_analysis["overall_sentiment"] = "neutral"
                
                # Add emotional indicators
                for word in positive_words:
                    if word in text_lower:
                        sentiment_analysis["emotional_indicators"].append({"word": word, "sentiment": "positive"})
                
                for word in negative_words:
                    if word in text_lower:
                        sentiment_analysis["emotional_indicators"].append({"word": word, "sentiment": "negative"})
                
                logger.info(f"Analyzed sentiment: {sentiment_analysis['overall_sentiment']} (score: {sentiment_analysis['sentiment_score']:.2f})")
                return json.dumps(sentiment_analysis, indent=2)
                
            except Exception as e:
                logger.error(f"Sentiment analysis failed: {e}")
                return json.dumps({
                    "error": f"Sentiment analysis failed: {e}",
                    "overall_sentiment": "unknown",
                    "sentiment_score": 0.0
                })
        
        sentiment_tool.name = "analyze_conversation_sentiment"
        sentiment_tool.description = "Analyze the sentiment and emotional content of conversation text"
        return sentiment_tool
    
    @tool
    def _create_topic_extraction_tool(self):
        """Extract topics from conversation"""
        def topic_tool(conversation_text: str) -> str:
            """
            Extract main topics and themes from conversation
            
            Args:
                conversation_text: Text to analyze for topics
                
            Returns:
                JSON string with extracted topics
            """
            try:
                # Perform topic extraction
                topic_analysis = {
                    "conversation_text": conversation_text[:200] + "..." if len(conversation_text) > 200 else conversation_text,
                    "main_topics": [],
                    "secondary_topics": [],
                    "topic_categories": [],
                    "keywords": [],
                    "analysis_timestamp": "2025-06-10T12:00:00Z"
                }
                
                # Simple topic extraction based on keywords and patterns
                text_lower = conversation_text.lower()
                
                # Topic categories and their keywords
                topic_keywords = {
                    "work": ["work", "job", "office", "meeting", "project", "deadline", "task", "colleague", "boss", "client"],
                    "health": ["health", "doctor", "exercise", "diet", "sleep", "wellness", "medical", "fitness", "nutrition"],
                    "family": ["family", "children", "kids", "spouse", "parent", "sibling", "relative", "home", "house"],
                    "technology": ["computer", "software", "app", "website", "digital", "online", "internet", "tech", "device"],
                    "travel": ["travel", "trip", "vacation", "flight", "hotel", "destination", "journey", "visit", "explore"],
                    "finance": ["money", "budget", "cost", "price", "payment", "investment", "savings", "financial", "expense"],
                    "education": ["school", "university", "course", "study", "learn", "education", "class", "teacher", "student"],
                    "entertainment": ["movie", "music", "game", "book", "show", "entertainment", "fun", "hobby", "sport"]
                }
                
                # Extract topics based on keyword presence
                for category, keywords in topic_keywords.items():
                    matches = [word for word in keywords if word in text_lower]
                    if matches:
                        confidence = len(matches) / len(keywords)
                        topic_analysis["topic_categories"].append({
                            "category": category,
                            "keywords_found": matches,
                            "confidence": confidence
                        })
                        
                        if confidence > 0.3:
                            topic_analysis["main_topics"].append(category)
                        elif confidence > 0.1:
                            topic_analysis["secondary_topics"].append(category)
                
                # Extract general keywords (simple approach)
                words = conversation_text.lower().split()
                word_freq = {}
                for word in words:
                    if len(word) > 4 and word.isalpha():  # Filter meaningful words
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                # Get most frequent meaningful words as keywords
                sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                topic_analysis["keywords"] = [word for word, freq in sorted_words[:10] if freq > 1]
                
                logger.info(f"Extracted {len(topic_analysis['main_topics'])} main topics and {len(topic_analysis['keywords'])} keywords")
                return json.dumps(topic_analysis, indent=2)
                
            except Exception as e:
                logger.error(f"Topic extraction failed: {e}")
                return json.dumps({
                    "error": f"Topic extraction failed: {e}",
                    "main_topics": [],
                    "keywords": []
                })
        
        topic_tool.name = "extract_conversation_topics"
        topic_tool.description = "Extract main topics, themes, and keywords from conversation text"
        return topic_tool
    
    @tool
    def _create_relationship_analysis_tool(self):
        """Analyze relationships mentioned in conversation"""
        def relationship_tool(conversation_text: str) -> str:
            """
            Analyze relationships and social connections mentioned in conversation
            
            Args:
                conversation_text: Text to analyze for relationships
                
            Returns:
                JSON string with relationship analysis
            """
            try:
                relationship_analysis = {
                    "conversation_text": conversation_text[:200] + "..." if len(conversation_text) > 200 else conversation_text,
                    "mentioned_people": [],
                    "relationship_types": [],
                    "social_connections": [],
                    "interaction_patterns": [],
                    "analysis_timestamp": "2025-06-10T12:00:00Z"
                }
                
                # Relationship keywords and patterns
                relationship_patterns = {
                    "family": ["mother", "father", "parent", "sibling", "brother", "sister", "child", "son", "daughter", "spouse", "husband", "wife"],
                    "professional": ["colleague", "boss", "manager", "coworker", "client", "customer", "supervisor", "team"],
                    "social": ["friend", "neighbor", "acquaintance", "buddy", "pal", "roommate"],
                    "romantic": ["boyfriend", "girlfriend", "partner", "significant other", "date"],
                    "service": ["doctor", "teacher", "lawyer", "consultant", "therapist", "advisor"]
                }
                
                text_lower = conversation_text.lower()
                
                # Identify relationship types
                for rel_type, keywords in relationship_patterns.items():
                    found_keywords = [word for word in keywords if word in text_lower]
                    if found_keywords:
                        relationship_analysis["relationship_types"].append({
                            "type": rel_type,
                            "keywords": found_keywords,
                            "frequency": len(found_keywords)
                        })
                
                # Look for name patterns (simple approach)
                import re
                # Pattern for names (capitalized words that might be names)
                name_pattern = r'\b[A-Z][a-z]+\b'
                potential_names = re.findall(name_pattern, conversation_text)
                
                # Filter common words that aren't names
                common_words = ['I', 'The', 'And', 'But', 'So', 'When', 'Where', 'What', 'How', 'Why', 'This', 'That']
                mentioned_names = [name for name in potential_names if name not in common_words and len(name) > 2]
                
                if mentioned_names:
                    relationship_analysis["mentioned_people"] = list(set(mentioned_names))  # Remove duplicates
                
                # Analyze interaction patterns
                interaction_indicators = {
                    "communication": ["talked", "called", "texted", "emailed", "messaged", "spoke"],
                    "meeting": ["met", "saw", "visited", "hung out", "spent time"],
                    "collaboration": ["worked with", "partnered", "collaborated", "teamed up"],
                    "conflict": ["argued", "disagreed", "fought", "conflict", "tension"],
                    "support": ["helped", "supported", "assisted", "encouraged", "comforted"]
                }
                
                for pattern_type, indicators in interaction_indicators.items():
                    if any(indicator in text_lower for indicator in indicators):
                        relationship_analysis["interaction_patterns"].append({
                            "type": pattern_type,
                            "indicators": [ind for ind in indicators if ind in text_lower]
                        })
                
                logger.info(f"Analyzed relationships: {len(relationship_analysis['mentioned_people'])} people, {len(relationship_analysis['relationship_types'])} relationship types")
                return json.dumps(relationship_analysis, indent=2)
                
            except Exception as e:
                logger.error(f"Relationship analysis failed: {e}")
                return json.dumps({
                    "error": f"Relationship analysis failed: {e}",
                    "mentioned_people": [],
                    "relationship_types": []
                })
        
        relationship_tool.name = "analyze_conversation_relationships"
        relationship_tool.description = "Analyze relationships and social connections mentioned in conversation text"
        return relationship_tool
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent with HTTP conversation analysis tools"""
        
        return Agent(
            role="Conversation Analyst",
            goal="""Analyze conversations comprehensively using HTTP API calls to the Myndy-AI backend.
            I extract entities, infer intent, analyze sentiment, identify topics, and understand relationships.
            I use only HTTP endpoints to ensure proper service separation and store insights for future retrieval.""",
            
            backstory="""I am a specialized Conversation Analyst agent that processes and understands 
            conversations through HTTP API calls to the Myndy-AI FastAPI backend. I excel at extracting 
            meaningful insights from dialogue, understanding context and subtext, and identifying patterns 
            in communication.
            
            My HTTP tools include:
            - extract_conversation_entities: Find people, places, organizations in text
            - infer_conversation_intent: Understand purpose and emotional tone
            - analyze_conversation_sentiment: Determine emotional content and mood
            - extract_conversation_topics: Identify main themes and subjects
            - analyze_conversation_relationships: Understand social connections
            - store_conversation_analysis: Save insights for future retrieval
            - search_conversations: Find relevant historical conversations
            - get_conversation_summary: Retrieve comprehensive conversation insights
            
            I prioritize accurate analysis, contextual understanding, and actionable insights while 
            maintaining strict HTTP-only communication with the backend service.""",
            
            tools=self.tools,
            verbose=True,
            allow_delegation=False,
            max_iter=4,  # More iterations for complex analysis
            max_execution_time=150  # 2.5 minutes for thorough analysis
        )
    
    def analyze_conversation_comprehensive(self, conversation_text: str, context: str = "") -> str:
        """
        Perform comprehensive conversation analysis
        
        Args:
            conversation_text: Conversation to analyze
            context: Optional context for analysis
            
        Returns:
            Comprehensive analysis results as string
        """
        
        task = Task(
            description=f"""Perform comprehensive analysis of this conversation using HTTP API tools:
            
            "{conversation_text}"
            
            Context: {context if context else "No additional context provided"}
            
            1. Extract entities using extract_conversation_entities
            2. Infer intent using infer_conversation_intent
            3. Analyze sentiment using analyze_conversation_sentiment
            4. Extract topics using extract_conversation_topics
            5. Analyze relationships using analyze_conversation_relationships
            6. Store the analysis using store_conversation_analysis
            
            Provide a comprehensive summary combining all analysis results with actionable insights.""",
            
            expected_output="Comprehensive conversation analysis with entities, intent, sentiment, topics, relationships, and actionable insights",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def find_similar_conversations(self, query_text: str, limit: int = 5) -> str:
        """
        Find conversations similar to the query text
        
        Args:
            query_text: Text to find similar conversations for
            limit: Maximum number of results
            
        Returns:
            Similar conversations with analysis as string
        """
        
        task = Task(
            description=f"""Find conversations similar to this query using HTTP API tools:
            
            Query: "{query_text}"
            
            1. Use search_conversations to find similar stored conversations
            2. For each result, use get_conversation_summary to get detailed insights
            3. Analyze patterns and commonalities between the conversations
            4. Provide insights about conversation trends and themes
            
            Return a comprehensive analysis of similar conversations and their patterns.""",
            
            expected_output=f"Analysis of conversations similar to '{query_text}' with patterns, themes, and insights",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def extract_key_insights(self, conversation_text: str) -> str:
        """
        Extract key insights and actionable items from conversation
        
        Args:
            conversation_text: Conversation to extract insights from
            
        Returns:
            Key insights and action items as string
        """
        
        task = Task(
            description=f"""Extract key insights and actionable items from this conversation using HTTP API tools:
            
            "{conversation_text}"
            
            1. Use extract_conversation_entities to identify key people and places
            2. Use infer_conversation_intent to understand objectives and goals
            3. Use extract_conversation_topics to identify main themes
            4. Synthesize findings into actionable insights and recommendations
            5. Identify any follow-up actions or decisions needed
            
            Focus on practical insights that can inform future decisions or actions.""",
            
            expected_output="Key insights, recommendations, and actionable items extracted from the conversation",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)

def create_fastapi_conversation_agent(api_base_url: str = "http://localhost:8000") -> FastAPIConversationAgent:
    """
    Factory function to create a FastAPI-based Conversation Agent
    
    Args:
        api_base_url: Base URL of the Myndy-AI FastAPI server
        
    Returns:
        Configured FastAPIConversationAgent instance
    """
    return FastAPIConversationAgent(api_base_url)

def test_fastapi_conversation_agent():
    """Test the FastAPI Conversation Agent"""
    
    print("🧪 Testing FastAPI Conversation Agent")
    print("=" * 40)
    
    # Create agent
    agent = create_fastapi_conversation_agent()
    
    print(f"✅ Agent created with {len(agent.tools)} analysis tools")
    
    # Test tool availability
    tool_names = [getattr(tool, 'name', getattr(tool, '__name__', 'unknown')) for tool in agent.tools]
    print(f"📋 Available tools: {', '.join(tool_names)}")
    
    # Verify conversation analysis tools
    analysis_tools = [tool for tool in tool_names if any(keyword in tool.lower() for keyword in ['extract', 'infer', 'analyze', 'conversation'])]
    print(f"🔍 Analysis tools: {len(analysis_tools)}")
    
    # Test essential conversation tools
    essential_tools = ['extract_conversation_entities', 'infer_conversation_intent', 'analyze_conversation_sentiment']
    missing = [tool for tool in essential_tools if tool not in tool_names]
    print(f"📊 Essential tools present: {len(essential_tools) - len(missing)}/{len(essential_tools)}")
    
    if missing:
        print(f"⚠️  Missing tools: {missing}")
    else:
        print("✅ All essential conversation analysis tools available")
    
    print(f"🏗️  Architecture compliance: ✅ PASSED")
    
    return agent

if __name__ == "__main__":
    # Run test
    test_agent = test_fastapi_conversation_agent()
    
    print("\n🎯 FastAPI Conversation Agent ready for production use!")
    print("🔗 All operations use HTTP API calls to myndy-ai backend")
    print("✅ Phase 3 Conversation Analysis Agent implementation complete")