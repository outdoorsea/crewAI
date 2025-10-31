"""
Conversation Memory Persistence Tool

This tool stores conversation analysis results in Qdrant vector database using 
the new myndy-ai/qdrant architecture, enabling long-term memory and retrieval
of conversation context, insights, and extracted information.

File: tools/conversation_memory_persistence.py
"""

import sys
import json
import logging
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Add myndy-ai to path
MYNDY_PATH = Path(__file__).parent.parent.parent / "myndy-ai"
sys.path.insert(0, str(MYNDY_PATH))

from qdrant.core.client import qdrant_client
from qdrant.core.collection_manager import collection_manager
from qdrant.core.embedding_manager import embedding_manager
from qdrant.search.vector_search import vector_search
from qdrant.collections.memory import memory_manager

# Import conversation analyzer for processing
sys.path.insert(0, str(Path(__file__).parent))
from conversation_analyzer import ConversationAnalyzer

logger = logging.getLogger(__name__)

class ConversationMemoryPersistence:
    """Tool for persisting conversation analysis results in vector memory."""
    
    def __init__(self):
        """Initialize the conversation memory persistence tool."""
        try:
            # Initialize conversation analyzer
            self.conversation_analyzer = ConversationAnalyzer()
            
            # Check qdrant availability
            health_check = qdrant_client.healthcheck()
            if health_check.get("connected"):
                self.qdrant_available = True
                logger.info("Successfully connected to Qdrant for conversation memory persistence")
            else:
                self.qdrant_available = False
                logger.warning("Qdrant not available, conversation memory will be limited")
                
        except Exception as e:
            logger.error(f"Failed to initialize conversation memory persistence: {e}")
            self.conversation_analyzer = ConversationAnalyzer()
            self.qdrant_available = False
    
    def store_conversation_analysis(self, conversation_text: str, 
                                  conversation_id: Optional[str] = None,
                                  user_id: str = "default",
                                  metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store conversation analysis results in vector memory.
        
        Args:
            conversation_text: Text of the conversation to analyze and store
            conversation_id: Optional conversation identifier
            user_id: User identifier
            metadata: Optional additional metadata to store
            
        Returns:
            Storage result with IDs and analysis summary
        """
        try:
            if not self.qdrant_available:
                return {
                    "success": False,
                    "error": "Qdrant vector database not available",
                    "fallback_analysis": self._analyze_conversation_locally(conversation_text)
                }
            
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = f"conv_{uuid.uuid4()}"
            
            # Analyze conversation
            analysis_result = self._comprehensive_conversation_analysis(conversation_text, user_id)
            
            # Prepare metadata
            storage_metadata = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_version": "1.0",
                "content_length": len(conversation_text),
                "analysis_summary": analysis_result.get("summary", {}),
                **(metadata or {})
            }
            
            stored_items = []
            
            # Store main conversation content
            main_embedding = embedding_manager.get_text_embedding(conversation_text)
            main_collection = collection_manager.get_collection_name("conversation", "memory")
            
            # Ensure collection exists
            if not qdrant_client.collection_exists(main_collection):
                qdrant_client.create_collection(main_collection, vector_size=len(main_embedding))
            
            # Store main conversation
            main_point_id = f"{conversation_id}_main"
            main_payload = {
                "content": conversation_text,
                "type": "conversation_main",
                "metadata": storage_metadata,
                "analysis": analysis_result
            }
            
            success = qdrant_client.upsert_points(
                collection_name=main_collection,
                points=[{
                    "id": main_point_id,
                    "vector": main_embedding,
                    "payload": main_payload
                }]
            )
            
            if success:
                stored_items.append({
                    "type": "main_conversation",
                    "id": main_point_id,
                    "collection": main_collection
                })
            
            # Store extracted entities
            entities = analysis_result.get("entities", [])
            if entities:
                entity_storage_result = self._store_extracted_entities(
                    entities, conversation_id, user_id, storage_metadata
                )
                stored_items.extend(entity_storage_result)
            
            # Store conversation insights
            insights = analysis_result.get("insights", [])
            if insights:
                insight_storage_result = self._store_conversation_insights(
                    insights, conversation_id, user_id, storage_metadata
                )
                stored_items.extend(insight_storage_result)
            
            # Store status updates detected
            status_updates = analysis_result.get("status_updates", [])
            if status_updates:
                status_storage_result = self._store_status_updates(
                    status_updates, conversation_id, user_id, storage_metadata
                )
                stored_items.extend(status_storage_result)
            
            # Store profile updates detected
            profile_updates = analysis_result.get("profile_updates", [])
            if profile_updates:
                profile_storage_result = self._store_profile_updates(
                    profile_updates, conversation_id, user_id, storage_metadata
                )
                stored_items.extend(profile_storage_result)
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "stored_items": stored_items,
                "analysis_summary": analysis_result.get("summary", {}),
                "storage_timestamp": storage_metadata["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error storing conversation analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_analysis": self._analyze_conversation_locally(conversation_text)
            }
    
    def _comprehensive_conversation_analysis(self, conversation_text: str, 
                                           user_id: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of conversation."""
        try:
            analysis = {
                "summary": {},
                "entities": [],
                "insights": [],
                "status_updates": [],
                "profile_updates": []
            }
            
            # Analyze for status updates
            status_updates = self.conversation_analyzer.analyze_status_updates(conversation_text)
            analysis["status_updates"] = [
                {
                    "type": update.type,
                    "value": update.value,
                    "confidence": update.confidence,
                    "source_text": update.source_text
                }
                for update in status_updates
            ]
            
            # Analyze for profile updates
            profile_updates = self.conversation_analyzer.analyze_profile_updates(conversation_text)
            analysis["profile_updates"] = [
                {
                    "type": update.type,
                    "category": update.category,
                    "value": update.value,
                    "metadata": update.metadata,
                    "confidence": update.confidence,
                    "source_text": update.source_text
                }
                for update in profile_updates
            ]
            
            # Extract entities (simplified)
            import re
            # Simple entity extraction patterns
            entities = []
            
            # Extract mentions of people
            people_patterns = [
                r'\b(?:my|his|her|their)\s+(?:friend|colleague|partner|spouse|boss|manager|doctor|neighbor)\s+(\w+)\b',
                r'\b(\w+)\s+(?:said|told|mentioned|asked|suggested|recommended)\b',
                r'\bI\s+(?:met|saw|talked to|called|texted|emailed)\s+(\w+)\b'
            ]
            
            for pattern in people_patterns:
                matches = re.finditer(pattern, conversation_text, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) > 0:
                        person_name = match.group(1)
                        if len(person_name) > 2 and person_name.isalpha():
                            entities.append({
                                "type": "person",
                                "value": person_name,
                                "context": match.group(0),
                                "confidence": 0.7
                            })
            
            # Extract places
            place_patterns = [
                r'\bat\s+(?:the\s+)?(\w+(?:\s+\w+){0,2})\s+(?:restaurant|cafe|store|shop|hospital|clinic|gym|office|mall|airport|station)\b',
                r'\bin\s+(\w+(?:\s+\w+){0,1}),?\s+(?:CA|California|NY|New York|TX|Texas|FL|Florida)\b',
                r'\bwent\s+to\s+(?:the\s+)?(\w+(?:\s+\w+){0,2})\b'
            ]
            
            for pattern in place_patterns:
                matches = re.finditer(pattern, conversation_text, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) > 0:
                        place_name = match.group(1)
                        if len(place_name) > 2:
                            entities.append({
                                "type": "place",
                                "value": place_name,
                                "context": match.group(0),
                                "confidence": 0.6
                            })
            
            analysis["entities"] = entities
            
            # Generate insights
            insights = []
            
            # Activity patterns
            if any(word in conversation_text.lower() for word in ['workout', 'exercise', 'gym', 'run', 'bike', 'swim']):
                insights.append({
                    "type": "activity_pattern",
                    "insight": "User discussed physical activity or exercise",
                    "confidence": 0.8
                })
            
            # Social patterns
            if any(word in conversation_text.lower() for word in ['meeting', 'lunch', 'dinner', 'party', 'hangout']):
                insights.append({
                    "type": "social_pattern", 
                    "insight": "User discussed social activities or events",
                    "confidence": 0.7
                })
            
            # Work patterns
            if any(word in conversation_text.lower() for word in ['work', 'office', 'boss', 'meeting', 'project', 'deadline']):
                insights.append({
                    "type": "work_pattern",
                    "insight": "User discussed work-related topics",
                    "confidence": 0.8
                })
            
            analysis["insights"] = insights
            
            # Generate summary
            analysis["summary"] = {
                "total_entities": len(analysis["entities"]),
                "status_updates_count": len(analysis["status_updates"]),
                "profile_updates_count": len(analysis["profile_updates"]),
                "insights_count": len(analysis["insights"]),
                "high_confidence_items": len([
                    item for sublist in [
                        analysis["entities"], 
                        analysis["status_updates"], 
                        analysis["profile_updates"]
                    ] 
                    for item in sublist 
                    if item.get("confidence", 0) > 0.7
                ]),
                "conversation_length": len(conversation_text),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive conversation analysis: {e}")
            return {"summary": {"error": str(e)}, "entities": [], "insights": [], "status_updates": [], "profile_updates": []}
    
    def _store_extracted_entities(self, entities: List[Dict[str, Any]], 
                                 conversation_id: str, user_id: str,
                                 base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Store extracted entities in vector memory."""
        stored_items = []
        
        try:
            entity_collection = collection_manager.get_collection_name("entity", "memory")
            
            # Ensure collection exists
            if not qdrant_client.collection_exists(entity_collection):
                qdrant_client.create_collection(entity_collection, vector_size=768)
            
            for i, entity in enumerate(entities):
                try:
                    # Create embedding for entity
                    entity_text = f"{entity['type']}: {entity['value']} (context: {entity.get('context', '')})"
                    entity_embedding = embedding_manager.get_text_embedding(entity_text)
                    
                    # Create point
                    point_id = f"{conversation_id}_entity_{i}"
                    payload = {
                        "entity_type": entity["type"],
                        "entity_value": entity["value"],
                        "context": entity.get("context", ""),
                        "confidence": entity.get("confidence", 0.0),
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "source": "conversation_analysis",
                        "metadata": base_metadata
                    }
                    
                    # Store in Qdrant
                    success = qdrant_client.upsert_points(
                        collection_name=entity_collection,
                        points=[{
                            "id": point_id,
                            "vector": entity_embedding,
                            "payload": payload
                        }]
                    )
                    
                    if success:
                        stored_items.append({
                            "type": "entity",
                            "id": point_id,
                            "collection": entity_collection,
                            "entity_type": entity["type"],
                            "entity_value": entity["value"]
                        })
                        
                except Exception as e:
                    logger.error(f"Error storing entity {entity}: {e}")
                    
        except Exception as e:
            logger.error(f"Error storing entities: {e}")
        
        return stored_items
    
    def _store_conversation_insights(self, insights: List[Dict[str, Any]], 
                                   conversation_id: str, user_id: str,
                                   base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Store conversation insights in vector memory."""
        stored_items = []
        
        try:
            insight_collection = collection_manager.get_collection_name("insight", "memory")
            
            # Ensure collection exists
            if not qdrant_client.collection_exists(insight_collection):
                qdrant_client.create_collection(insight_collection, vector_size=768)
            
            for i, insight in enumerate(insights):
                try:
                    # Create embedding for insight
                    insight_text = f"{insight['type']}: {insight['insight']}"
                    insight_embedding = embedding_manager.get_text_embedding(insight_text)
                    
                    # Create point
                    point_id = f"{conversation_id}_insight_{i}"
                    payload = {
                        "insight_type": insight["type"],
                        "insight": insight["insight"],
                        "confidence": insight.get("confidence", 0.0),
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "source": "conversation_analysis",
                        "metadata": base_metadata
                    }
                    
                    # Store in Qdrant
                    success = qdrant_client.upsert_points(
                        collection_name=insight_collection,
                        points=[{
                            "id": point_id,
                            "vector": insight_embedding,
                            "payload": payload
                        }]
                    )
                    
                    if success:
                        stored_items.append({
                            "type": "insight",
                            "id": point_id,
                            "collection": insight_collection,
                            "insight_type": insight["type"]
                        })
                        
                except Exception as e:
                    logger.error(f"Error storing insight {insight}: {e}")
                    
        except Exception as e:
            logger.error(f"Error storing insights: {e}")
        
        return stored_items
    
    def _store_status_updates(self, status_updates: List[Dict[str, Any]], 
                             conversation_id: str, user_id: str,
                             base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Store detected status updates in vector memory."""
        stored_items = []
        
        try:
            status_collection = collection_manager.get_collection_name("status_update", "memory")
            
            # Ensure collection exists
            if not qdrant_client.collection_exists(status_collection):
                qdrant_client.create_collection(status_collection, vector_size=768)
            
            for i, update in enumerate(status_updates):
                try:
                    # Create embedding for status update
                    update_text = f"Status {update['type']}: {update['value']} (from: {update.get('source_text', '')[:100]})"
                    update_embedding = embedding_manager.get_text_embedding(update_text)
                    
                    # Create point
                    point_id = f"{conversation_id}_status_{i}"
                    payload = {
                        "update_type": update["type"],
                        "update_value": update["value"],
                        "confidence": update.get("confidence", 0.0),
                        "source_text": update.get("source_text", ""),
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "source": "conversation_analysis",
                        "metadata": base_metadata
                    }
                    
                    # Store in Qdrant
                    success = qdrant_client.upsert_points(
                        collection_name=status_collection,
                        points=[{
                            "id": point_id,
                            "vector": update_embedding,
                            "payload": payload
                        }]
                    )
                    
                    if success:
                        stored_items.append({
                            "type": "status_update",
                            "id": point_id,
                            "collection": status_collection,
                            "update_type": update["type"]
                        })
                        
                except Exception as e:
                    logger.error(f"Error storing status update {update}: {e}")
                    
        except Exception as e:
            logger.error(f"Error storing status updates: {e}")
        
        return stored_items
    
    def _store_profile_updates(self, profile_updates: List[Dict[str, Any]], 
                              conversation_id: str, user_id: str,
                              base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Store detected profile updates in vector memory."""
        stored_items = []
        
        try:
            profile_collection = collection_manager.get_collection_name("profile_update", "memory")
            
            # Ensure collection exists
            if not qdrant_client.collection_exists(profile_collection):
                qdrant_client.create_collection(profile_collection, vector_size=768)
            
            for i, update in enumerate(profile_updates):
                try:
                    # Create embedding for profile update
                    update_text = f"Profile {update['type']}: {update.get('category', '')} - {update['value']} (from: {update.get('source_text', '')[:100]})"
                    update_embedding = embedding_manager.get_text_embedding(update_text)
                    
                    # Create point
                    point_id = f"{conversation_id}_profile_{i}"
                    payload = {
                        "update_type": update["type"],
                        "update_category": update.get("category", ""),
                        "update_value": update["value"],
                        "metadata": update.get("metadata", {}),
                        "confidence": update.get("confidence", 0.0),
                        "source_text": update.get("source_text", ""),
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "source": "conversation_analysis",
                        "base_metadata": base_metadata
                    }
                    
                    # Store in Qdrant
                    success = qdrant_client.upsert_points(
                        collection_name=profile_collection,
                        points=[{
                            "id": point_id,
                            "vector": update_embedding,
                            "payload": payload
                        }]
                    )
                    
                    if success:
                        stored_items.append({
                            "type": "profile_update",
                            "id": point_id,
                            "collection": profile_collection,
                            "update_type": update["type"]
                        })
                        
                except Exception as e:
                    logger.error(f"Error storing profile update {update}: {e}")
                    
        except Exception as e:
            logger.error(f"Error storing profile updates: {e}")
        
        return stored_items
    
    def _analyze_conversation_locally(self, conversation_text: str) -> Dict[str, Any]:
        """Fallback analysis when Qdrant is not available."""
        try:
            # Basic local analysis without storage
            status_updates = self.conversation_analyzer.analyze_status_updates(conversation_text)
            profile_updates = self.conversation_analyzer.analyze_profile_updates(conversation_text)
            
            return {
                "local_analysis": True,
                "status_updates_count": len(status_updates),
                "profile_updates_count": len(profile_updates),
                "message": "Analysis completed locally without persistent storage"
            }
        except Exception as e:
            return {"error": f"Local analysis failed: {str(e)}"}
    
    def search_conversation_memory(self, query: str, user_id: str = "default", 
                                  limit: int = 10, include_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search stored conversation memories.
        
        Args:
            query: Search query
            user_id: User identifier
            limit: Maximum number of results
            include_types: Optional list of types to include (conversation_main, entity, insight, etc.)
            
        Returns:
            Search results from conversation memory
        """
        try:
            if not self.qdrant_available:
                return {
                    "success": False,
                    "error": "Qdrant vector database not available for search"
                }
            
            # Use the vector search functionality
            search_results = vector_search.search_text(
                query=query,
                model_types=include_types or ["conversation", "entity", "insight", "status_update", "profile_update"],
                sections=["memory"],
                limit=limit,
                filter_conditions={"user_id": user_id} if user_id != "default" else None
            )
            
            return {
                "success": True,
                "query": query,
                "results": search_results,
                "result_count": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Error searching conversation memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get summary of a stored conversation.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Summary of the conversation and its analysis
        """
        try:
            if not self.qdrant_available:
                return {
                    "success": False,
                    "error": "Qdrant vector database not available"
                }
            
            # Search for all items related to this conversation
            results = vector_search.search_text(
                query=conversation_id,
                model_types=["conversation", "entity", "insight", "status_update", "profile_update"],
                sections=["memory"],
                limit=100,
                filter_conditions={"conversation_id": conversation_id}
            )
            
            # Group results by type
            summary = {
                "conversation_id": conversation_id,
                "main_conversation": None,
                "entities": [],
                "insights": [],
                "status_updates": [],
                "profile_updates": [],
                "total_items": len(results)
            }
            
            for result in results:
                payload = result.get("payload", {})
                item_type = payload.get("type")
                
                if item_type == "conversation_main":
                    summary["main_conversation"] = {
                        "content_preview": payload.get("content", "")[:200] + "...",
                        "analysis": payload.get("analysis", {}),
                        "metadata": payload.get("metadata", {})
                    }
                elif item_type in summary:
                    summary[item_type].append(payload)
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
_memory_persistence = ConversationMemoryPersistence()

# Tool functions for registry
def store_conversation_analysis(conversation_text: str, 
                               conversation_id: str = None,
                               user_id: str = "default") -> str:
    """Store conversation analysis results in vector memory."""
    result = _memory_persistence.store_conversation_analysis(conversation_text, conversation_id, user_id)
    return json.dumps(result, indent=2)

def search_conversation_memory(query: str, user_id: str = "default", 
                              limit: int = 10) -> str:
    """Search stored conversation memories."""
    result = _memory_persistence.search_conversation_memory(query, user_id, limit)
    return json.dumps(result, indent=2)

def get_conversation_summary(conversation_id: str) -> str:
    """Get summary of a stored conversation."""
    result = _memory_persistence.get_conversation_summary(conversation_id)
    return json.dumps(result, indent=2)