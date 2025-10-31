#!/usr/bin/env python3
"""
Entity Extraction and Qdrant Management Tools for CrewAI

This module provides comprehensive tools for detecting people, places, things,
projects, calendar items, and managing them in a Qdrant vector database.
"""

import os
import json
import re
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from crewai.tools import tool
import spacy
from spacy import displacy
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import dateparser
import phonenumbers
from geopy.geocoders import Nominatim

# Entity Types
class EntityType(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    PROJECT = "project"
    EVENT = "event"
    TASK = "task"
    DOCUMENT = "document"
    CONTACT = "contact"
    DATETIME = "datetime"
    MONEY = "money"
    TECHNOLOGY = "technology"

@dataclass
class ExtractedEntity:
    """Represents an extracted entity with metadata."""
    text: str
    entity_type: EntityType
    confidence: float
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    
class EntityExtractor:
    """Main entity extraction engine."""
    
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️  SpaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        # Initialize embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize geocoder
        self.geolocator = Nominatim(user_agent="crewai_entity_extractor")
        
        # Qdrant client
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333")
        )
        
        # Initialize collections
        self._setup_qdrant_collections()
    
    def _setup_qdrant_collections(self):
        """Setup Qdrant collections for different entity types."""
        collections = [
            "people", "organizations", "locations", "projects", 
            "events", "tasks", "documents", "contacts"
        ]
        
        for collection in collections:
            try:
                self.qdrant_client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"✅ Created Qdrant collection: {collection}")
            except Exception as e:
                print(f"Collection {collection} might already exist: {e}")

# === DETECTION TOOLS ===

@tool
def extract_entities_from_text(text: str) -> str:
    """
    Extract people, places, organizations, and other entities from text.
    Returns a JSON string with extracted entities and their metadata.
    """
    extractor = EntityExtractor()
    
    if not extractor.nlp:
        return "Error: SpaCy model not available"
    
    doc = extractor.nlp(text)
    entities = []
    
    # Standard NER entities
    for ent in doc.ents:
        entity_type = None
        confidence = 0.9  # SpaCy doesn't provide confidence, using default
        
        if ent.label_ in ["PERSON"]:
            entity_type = EntityType.PERSON
        elif ent.label_ in ["ORG"]:
            entity_type = EntityType.ORGANIZATION
        elif ent.label_ in ["GPE", "LOC"]:
            entity_type = EntityType.LOCATION
        elif ent.label_ in ["EVENT"]:
            entity_type = EntityType.EVENT
        elif ent.label_ in ["DATE", "TIME"]:
            entity_type = EntityType.DATETIME
        elif ent.label_ in ["MONEY"]:
            entity_type = EntityType.MONEY
        
        if entity_type:
            entity = ExtractedEntity(
                text=ent.text,
                entity_type=entity_type,
                confidence=confidence,
                start_pos=ent.start_char,
                end_pos=ent.end_char,
                metadata={
                    "label": ent.label_,
                    "context": text[max(0, ent.start_char-50):ent.end_char+50]
                }
            )
            entities.append(asdict(entity))
    
    # Custom pattern detection for projects, tasks, etc.
    entities.extend(_extract_custom_entities(text))
    
    return json.dumps(entities, indent=2)

def _extract_custom_entities(text: str) -> List[Dict]:
    """Extract custom entities like projects, tasks, etc."""
    entities = []
    
    # Project patterns
    project_patterns = [
        r"project\s+([A-Z][a-zA-Z0-9\s]{2,30})",
        r"([A-Z][a-zA-Z0-9\s]{2,30})\s+project",
        r"working on\s+([A-Z][a-zA-Z0-9\s]{2,30})",
    ]
    
    for pattern in project_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            project_name = match.group(1).strip()
            entities.append({
                "text": project_name,
                "entity_type": EntityType.PROJECT.value,
                "confidence": 0.8,
                "start_pos": match.start(1),
                "end_pos": match.end(1),
                "metadata": {
                    "pattern": pattern,
                    "context": text[max(0, match.start()-50):match.end()+50]
                }
            })
    
    # Task patterns
    task_patterns = [
        r"task:?\s+([^.!?\n]{10,100})",
        r"todo:?\s+([^.!?\n]{10,100})",
        r"need to\s+([^.!?\n]{10,100})",
        r"action item:?\s+([^.!?\n]{10,100})",
    ]
    
    for pattern in task_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            task_text = match.group(1).strip()
            entities.append({
                "text": task_text,
                "entity_type": EntityType.TASK.value,
                "confidence": 0.7,
                "start_pos": match.start(1),
                "end_pos": match.end(1),
                "metadata": {
                    "pattern": pattern,
                    "context": text[max(0, match.start()-50):match.end()+50]
                }
            })
    
    return entities

@tool
def extract_calendar_events(text: str) -> str:
    """
    Extract calendar events, meetings, and dates from text.
    Returns structured calendar information.
    """
    events = []
    
    # Date/time patterns
    date_patterns = [
        r"meeting\s+(?:on\s+)?([^.!?\n]{5,50})",
        r"scheduled\s+(?:for\s+)?([^.!?\n]{5,50})",
        r"(?:on|at)\s+([A-Z][a-z]+day[^.!?\n]{0,30})",
        r"([A-Z][a-z]+\s+\d{1,2}(?:st|nd|rd|th)?[^.!?\n]{0,30})",
    ]
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_text = match.group(1).strip()
            
            # Try to parse the date
            parsed_date = dateparser.parse(date_text)
            
            event = {
                "text": date_text,
                "entity_type": EntityType.EVENT.value,
                "confidence": 0.8,
                "start_pos": match.start(1),
                "end_pos": match.end(1),
                "metadata": {
                    "raw_date": date_text,
                    "parsed_date": parsed_date.isoformat() if parsed_date else None,
                    "context": text[max(0, match.start()-100):match.end()+100]
                }
            }
            events.append(event)
    
    return json.dumps(events, indent=2)

@tool  
def extract_contact_information(text: str) -> str:
    """
    Extract contact information like emails, phone numbers, addresses.
    Returns structured contact data.
    """
    contacts = []
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.finditer(email_pattern, text)
    
    for match in emails:
        contacts.append({
            "text": match.group(),
            "entity_type": EntityType.CONTACT.value,
            "confidence": 0.95,
            "start_pos": match.start(),
            "end_pos": match.end(),
            "metadata": {
                "type": "email",
                "context": text[max(0, match.start()-50):match.end()+50]
            }
        })
    
    # Phone number patterns
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
        r'\+\d{1,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
    ]
    
    for pattern in phone_patterns:
        phones = re.finditer(pattern, text)
        for match in phones:
            contacts.append({
                "text": match.group(),
                "entity_type": EntityType.CONTACT.value,
                "confidence": 0.9,
                "start_pos": match.start(),
                "end_pos": match.end(),
                "metadata": {
                    "type": "phone",
                    "context": text[max(0, match.start()-50):match.end()+50]
                }
            })
    
    return json.dumps(contacts, indent=2)

# === QDRANT DATABASE TOOLS ===

@tool
def search_entities_in_qdrant(query: str, entity_type: str = "all", limit: int = 10) -> str:
    """
    Search for entities in Qdrant vector database.
    
    Args:
        query: Search query text
        entity_type: Type of entity to search (people, organizations, locations, etc.)
        limit: Maximum number of results
    """
    try:
        extractor = EntityExtractor()
        
        # Generate embedding for the query
        query_embedding = extractor.embedder.encode(query).tolist()
        
        collections_to_search = []
        if entity_type == "all":
            collections_to_search = ["people", "organizations", "locations", "projects", "events", "tasks"]
        else:
            collections_to_search = [entity_type]
        
        all_results = []
        
        for collection in collections_to_search:
            try:
                results = extractor.qdrant_client.search(
                    collection_name=collection,
                    query_vector=query_embedding,
                    limit=limit
                )
                
                for result in results:
                    all_results.append({
                        "collection": collection,
                        "score": result.score,
                        "id": result.id,
                        "payload": result.payload
                    })
            except Exception as e:
                print(f"Error searching collection {collection}: {e}")
        
        # Sort by score
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        return json.dumps(all_results[:limit], indent=2)
        
    except Exception as e:
        return f"Error searching Qdrant: {str(e)}"

@tool
def store_entity_in_qdrant(entity_data: str, collection_name: str) -> str:
    """
    Store an entity in Qdrant vector database.
    
    Args:
        entity_data: JSON string containing entity information
        collection_name: Name of the collection to store in
    """
    try:
        extractor = EntityExtractor()
        entity = json.loads(entity_data)
        
        # Generate embedding
        text_to_embed = f"{entity.get('text', '')} {entity.get('metadata', {}).get('context', '')}"
        embedding = extractor.embedder.encode(text_to_embed).tolist()
        
        # Create point
        point = PointStruct(
            id=hash(entity.get('text', '') + str(datetime.now())),
            vector=embedding,
            payload={
                **entity,
                "stored_at": datetime.now().isoformat(),
                "embedding_text": text_to_embed
            }
        )
        
        # Store in Qdrant
        extractor.qdrant_client.upsert(
            collection_name=collection_name,
            points=[point]
        )
        
        return f"Successfully stored entity '{entity.get('text', 'unknown')}' in collection '{collection_name}'"
        
    except Exception as e:
        return f"Error storing entity: {str(e)}"

@tool
def update_entity_in_qdrant(entity_id: str, updated_data: str, collection_name: str) -> str:
    """
    Update an existing entity in Qdrant.
    
    Args:
        entity_id: ID of the entity to update
        updated_data: JSON string with updated information
        collection_name: Collection containing the entity
    """
    try:
        extractor = EntityExtractor()
        updated_entity = json.loads(updated_data)
        
        # Get existing entity
        existing = extractor.qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[entity_id]
        )
        
        if not existing:
            return f"Entity with ID {entity_id} not found"
        
        # Merge with existing data
        merged_payload = existing[0].payload.copy()
        merged_payload.update(updated_entity)
        merged_payload["updated_at"] = datetime.now().isoformat()
        
        # Regenerate embedding if text changed
        if "text" in updated_entity:
            text_to_embed = f"{merged_payload.get('text', '')} {merged_payload.get('metadata', {}).get('context', '')}"
            embedding = extractor.embedder.encode(text_to_embed).tolist()
            
            point = PointStruct(
                id=entity_id,
                vector=embedding,
                payload=merged_payload
            )
            
            extractor.qdrant_client.upsert(
                collection_name=collection_name,
                points=[point]
            )
        else:
            # Update only payload
            extractor.qdrant_client.set_payload(
                collection_name=collection_name,
                points=[entity_id],
                payload=merged_payload
            )
        
        return f"Successfully updated entity {entity_id} in collection {collection_name}"
        
    except Exception as e:
        return f"Error updating entity: {str(e)}"

@tool
def get_entity_relationships(entity_id: str, collection_name: str) -> str:
    """
    Find related entities based on vector similarity and metadata connections.
    """
    try:
        extractor = EntityExtractor()
        
        # Get the entity
        entity = extractor.qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[entity_id]
        )
        
        if not entity:
            return f"Entity {entity_id} not found"
        
        entity_data = entity[0]
        
        # Search for similar entities across all collections
        collections = ["people", "organizations", "locations", "projects", "events", "tasks"]
        relationships = []
        
        for coll in collections:
            if coll == collection_name:
                continue
                
            try:
                similar = extractor.qdrant_client.search(
                    collection_name=coll,
                    query_vector=entity_data.vector,
                    limit=5
                )
                
                for result in similar:
                    if result.score > 0.7:  # High similarity threshold
                        relationships.append({
                            "related_entity": result.payload.get("text"),
                            "relationship_type": f"{collection_name}_to_{coll}",
                            "similarity_score": result.score,
                            "collection": coll,
                            "id": result.id
                        })
            except Exception as e:
                print(f"Error searching {coll}: {e}")
        
        return json.dumps(relationships, indent=2)
        
    except Exception as e:
        return f"Error finding relationships: {str(e)}"

# === ANALYTICS TOOLS ===

@tool
def analyze_entity_trends(entity_type: str, time_period: str = "7d") -> str:
    """
    Analyze trends in entity creation and updates over time.
    
    Args:
        entity_type: Type of entity to analyze
        time_period: Time period (7d, 30d, 90d)
    """
    try:
        extractor = EntityExtractor()
        
        # Calculate date range
        days = int(time_period.replace('d', ''))
        start_date = datetime.now() - timedelta(days=days)
        
        # Get all entities from collection
        results = extractor.qdrant_client.scroll(
            collection_name=entity_type,
            limit=1000
        )[0]
        
        # Analyze by date
        daily_counts = {}
        for point in results:
            stored_at = point.payload.get("stored_at")
            if stored_at:
                date = datetime.fromisoformat(stored_at.replace('Z', '+00:00')).date()
                if date >= start_date.date():
                    daily_counts[str(date)] = daily_counts.get(str(date), 0) + 1
        
        # Generate trends
        analysis = {
            "entity_type": entity_type,
            "time_period": time_period,
            "total_entities": len(results),
            "daily_counts": daily_counts,
            "average_per_day": sum(daily_counts.values()) / len(daily_counts) if daily_counts else 0,
            "peak_day": max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else None
        }
        
        return json.dumps(analysis, indent=2)
        
    except Exception as e:
        return f"Error analyzing trends: {str(e)}"

# Export all tools for easy import
ENTITY_TOOLS = [
    extract_entities_from_text,
    extract_calendar_events,
    extract_contact_information,
    search_entities_in_qdrant,
    store_entity_in_qdrant,
    update_entity_in_qdrant,
    get_entity_relationships,
    analyze_entity_trends
]

if __name__ == "__main__":
    # Test the tools
    sample_text = """
    I'm working on the AI Research Project with John Smith from OpenAI. 
    We have a meeting scheduled for next Tuesday at 2 PM.
    Contact John at john.smith@openai.com or call (555) 123-4567.
    The project involves developing LLM tools for San Francisco startup.
    Action item: Review the model architecture by Friday.
    """
    
    print("Testing entity extraction:")
    print(extract_entities_from_text(sample_text))
    
    print("\nTesting calendar extraction:")
    print(extract_calendar_events(sample_text))
    
    print("\nTesting contact extraction:")
    print(extract_contact_information(sample_text))